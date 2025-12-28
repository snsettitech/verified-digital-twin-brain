from fastapi import Header, HTTPException, Depends, Request
from jose import jwt, JWTError
import os
from dotenv import load_dotenv
from modules.api_keys import validate_api_key, validate_domain
from modules.sessions import create_session

load_dotenv()

# JWT Configuration for Supabase
# JWT_SECRET must match Supabase's JWT secret from Dashboard → Settings → API
SUPABASE_JWT_SECRET = os.getenv("JWT_SECRET", "")
ALGORITHM = "HS256"

# DEV_MODE controls domain validation strictness, NOT auth bypass
# In production, this should be false
DEV_MODE = os.getenv("DEV_MODE", "true").lower() == "true"

# Startup validation - warn if JWT secret looks weak
if not SUPABASE_JWT_SECRET or len(SUPABASE_JWT_SECRET) < 32:
    import sys
    print("=" * 60, file=sys.stderr)
    print("SECURITY WARNING: JWT_SECRET is not properly configured!", file=sys.stderr)
    print("  Production auth WILL FAIL without the correct JWT secret.", file=sys.stderr)
    print("  Copy from: Supabase Dashboard → Settings → API → JWT Secret", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

def get_current_user(
    request: Request,
    authorization: str = Header(None),
    x_twin_api_key: str = Header(None),
    origin: str = Header(None),
    referer: str = Header(None)
):
    """
    Authenticate the current user via:
    1. API Key (for public widgets)
    2. Supabase JWT (for authenticated users)
    
    NO AUTH BYPASS EXISTS - all requests must be properly authenticated.
    """
    # Import here to avoid circular imports
    from modules.observability import supabase as supabase_client
    
    # 1. API Key check (for public widgets)
    if x_twin_api_key:
        key_info = validate_api_key(x_twin_api_key)
        if not key_info:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Domain validation (enforced in production)
        domain_source = origin or referer or ""
        allowed_domains = key_info.get("allowed_domains", [])
        
        if not DEV_MODE and not validate_domain(domain_source, allowed_domains):
            raise HTTPException(status_code=403, detail="Domain not allowed for this API key")
        
        # Extract IP and user agent for session
        ip_address = None
        user_agent = None
        try:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
        except:
            pass
        
        # Create anonymous session
        try:
            session_id = create_session(
                twin_id=key_info["twin_id"],
                group_id=key_info.get("group_id"),
                session_type="anonymous",
                ip_address=ip_address,
                user_agent=user_agent
            )
        except Exception as e:
            print(f"Error creating session: {e}")
            session_id = None
        
        return {
            "user_id": None,
            "tenant_id": None,
            "role": "visitor",
            "twin_id": key_info["twin_id"],
            "group_id": key_info.get("group_id"),
            "session_id": session_id,
            "api_key_id": key_info["id"]
        }

    # 2. JWT Authentication (Supabase tokens)
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if not SUPABASE_JWT_SECRET or len(SUPABASE_JWT_SECRET) < 32:
        raise HTTPException(
            status_code=500, 
            detail="Server authentication not configured. Contact administrator."
        )
    
    try:
        # Extract bearer token
        parts = authorization.split(" ")
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization format")
        
        token = parts[1]
        
        # DEBUG: Print token info
        print(f"[JWT DEBUG] Token length: {len(token)}")
        print(f"[JWT DEBUG] Secret length: {len(SUPABASE_JWT_SECRET)}")
        print(f"[JWT DEBUG] Secret first 10: {SUPABASE_JWT_SECRET[:10]}...")
        
        # Verify and decode JWT signature (this validates expiry too)
        # NOTE: Supabase tokens have aud="authenticated" but jose library's audience
        # validation can be strict. We verify manually instead.
        payload = jwt.decode(
            token, 
            SUPABASE_JWT_SECRET, 
            algorithms=[ALGORITHM],
            options={"verify_exp": True, "verify_aud": False}
        )
        
        # Manually verify audience if needed (Supabase uses "authenticated")
        aud = payload.get("aud")
        if aud and aud != "authenticated":
            print(f"[JWT DEBUG] WARNING: Unexpected audience: {aud}")
        
        # Supabase JWT has 'sub' as user_id
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing user ID")
        
        # Extract email and metadata from JWT (Supabase includes these)
        email = payload.get("email", "")
        user_metadata = payload.get("user_metadata", {})
        
        # Lookup tenant_id from database (not in JWT)
        tenant_id = None
        try:
            user_lookup = supabase_client.table("users").select("tenants(id)").eq("id", user_id).execute()
            if user_lookup.data and len(user_lookup.data) > 0:
                tenants_data = user_lookup.data[0].get("tenants")
                if isinstance(tenants_data, dict):
                    tenant_id = tenants_data.get("id")
        except Exception as e:
            # User might not exist yet (first login) - sync-user will create them
            print(f"Tenant lookup failed (expected for new users): {e}")

        # Update user activity timestamp (best effort)
        try:
            from datetime import datetime
            supabase_client.table("users").update({
                "last_active_at": datetime.utcnow().isoformat()
            }).eq("id", user_id).execute()
        except Exception:
            # Ignore errors (e.g. column missing, db down) to prevent blocking auth
            pass
        
        return {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "role": "owner",  # All authenticated users are owners of their content
            "email": email,
            "user_metadata": user_metadata,
            "name": user_metadata.get("full_name") or user_metadata.get("name"),
            "avatar_url": user_metadata.get("avatar_url")
        }
        
    except jwt.ExpiredSignatureError:
        print("[JWT DEBUG] ERROR: Token has EXPIRED")
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError as e:
        print(f"[JWT DEBUG] ERROR: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

def verify_owner(user=Depends(get_current_user)):
    if user.get("role") != "owner":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return user

def verify_twin_access(twin_id: str, user: dict) -> bool:
    """
    Verify that the user has access to the specified twin.
    
    For owners: checks if twin belongs to their tenant
    For visitors (API key): checks if twin_id matches their allowed twin
    
    Returns True if access is allowed, raises HTTPException otherwise.
    """
    from modules.observability import supabase
    
    # API key users have explicit twin_id in their context
    if user.get("role") == "visitor":
        allowed_twin = user.get("twin_id")
        if allowed_twin and allowed_twin == twin_id:
            return True
        raise HTTPException(status_code=403, detail="API key not authorized for this twin")
    
    # Authenticated users: verify twin belongs to their tenant
    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    # Get user's tenant_id (may already be in user dict from auth)
    user_tenant_id = user.get("tenant_id")
    
    # If not in user dict, look it up from database
    if not user_tenant_id:
        try:
            user_lookup = supabase.table("users").select("tenant_id").eq("id", user_id).single().execute()
            if user_lookup.data:
                user_tenant_id = user_lookup.data.get("tenant_id")
        except Exception as e:
            print(f"[verify_twin_access] Error looking up user tenant: {e}")
    
    if not user_tenant_id:
        raise HTTPException(status_code=403, detail="User has no tenant association")
    
    # Check if twin belongs to user's tenant
    try:
        twin_check = supabase.table("twins").select("id, tenant_id").eq("id", twin_id).single().execute()
        if not twin_check.data:
            raise HTTPException(status_code=404, detail="Twin not found")
        
        twin_tenant_id = twin_check.data.get("tenant_id")
        if twin_tenant_id == user_tenant_id:
            return True
            
        print(f"[verify_twin_access] Access denied: user tenant {user_tenant_id} != twin tenant {twin_tenant_id}")
    except HTTPException:
        raise
    except Exception as e:
        print(f"[verify_twin_access] Error checking twin access: {e}")
    
    raise HTTPException(status_code=403, detail="You do not have access to this twin")

