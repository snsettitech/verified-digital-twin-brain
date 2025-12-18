from fastapi import Header, HTTPException, Depends
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET", "secret")
ALGORITHM = "HS256"
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"
DEV_TOKEN = "development_token"

def get_current_user(authorization: str = Header(None)):
    # Development bypass
    if DEV_MODE and authorization == f"Bearer {DEV_TOKEN}":
        return {
            "user_id": "b415a7a9-c8f8-43b3-8738-a0062a90c016", 
            "tenant_id": "986f270e-2d5c-4f88-ad88-7d2a15ea8ab1", 
            "role": "owner"
        }

    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id")
        if user_id is None or tenant_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return {"user_id": user_id, "tenant_id": tenant_id, "role": payload.get("role")}
    except (JWTError, IndexError):
        raise HTTPException(status_code=401, detail="Could not validate credentials")

def verify_owner(user=Depends(get_current_user)):
    if user.get("role") != "owner":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return user
