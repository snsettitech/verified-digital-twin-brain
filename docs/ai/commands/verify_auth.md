# Verify Auth: How to Run Auth Verification Locally

> Reusable command card for verifying authentication functionality.

## Purpose

Verify that authentication flows work correctly before pushing changes that touch auth code.

## Quick Verification

### 1. Start Services

**Backend:**
```bash
cd backend
python main.py
# Should start on http://localhost:8000
```

**Frontend:**
```bash
cd frontend
npm run dev
# Should start on http://localhost:3000
```

### 2. Basic Auth Flow

**Test Sign In:**
1. Navigate to `http://localhost:3000`
2. Click "Sign In"
3. Complete Supabase auth flow
4. Should redirect to dashboard

**Test Protected Route:**
1. While signed in, navigate to `/dashboard`
2. Should see dashboard content
3. If redirected to login, auth is broken

**Test Sign Out:**
1. Click sign out
2. Should redirect to login page
3. Try accessing `/dashboard` directly
4. Should redirect to login (protected)

### 3. Backend API Auth

**Get JWT Token:**
1. Open browser DevTools → Application → Local Storage
2. Find key `sb-<project-id>-auth-token`
3. Copy the `access_token` value

**Test Sync User:**
```bash
export TOKEN="<your-jwt-token>"
curl -X POST http://localhost:8000/auth/sync-user \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"

# Expected: 200 OK with user object
# If 401: JWT secret mismatch
# If 500: Database error (check logs)
```

**Test Get Me:**
```bash
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Expected: 200 OK with user object
# If 401: Token invalid or expired
```

**Test Get Twins:**
```bash
curl http://localhost:8000/twins \
  -H "Authorization: Bearer $TOKEN"

# Expected: 200 OK with twins array
# If 403: Auth guard not working
```

### 4. Common Issues

**401 Unauthorized:**
- Check `JWT_SECRET` in `backend/.env` matches Supabase JWT Secret
- Verify token is valid (not expired)
- Check auth header format: `Bearer <token>`

**403 Forbidden:**
- User doesn't own the resource
- Check `tenant_id` matches in database
- Verify auth guard is checking ownership correctly

**500 Server Error:**
- Check backend logs for error details
- Common: Missing database column (check migrations)
- Common: PostgREST schema cache stale (reload in Supabase)

## Detailed Debugging

### Enable Debug Logging

Add to `backend/modules/auth_guard.py`:
```python
print(f"[AUTH DEBUG] Token length: {len(token)}")
print(f"[AUTH DEBUG] Secret length: {len(JWT_SECRET)}")
print(f"[AUTH DEBUG] Error: {str(e)}")
```

### Check Database

**Verify user exists:**
```sql
SELECT id, email, tenant_id FROM users ORDER BY created_at DESC LIMIT 5;
```

**Verify twin ownership:**
```sql
SELECT id, name, tenant_id FROM twins WHERE tenant_id = '<your-tenant-id>';
```

### Reference Documents

- **Auth Troubleshooting**: `docs/ops/AUTH_TROUBLESHOOTING.md`
- **Known Failures**: `docs/KNOWN_FAILURES.md`
- **Auth Guard Code**: `backend/modules/auth_guard.py`

## Checklist

Before pushing auth changes:
- [ ] Sign in flow works
- [ ] Sign out flow works
- [ ] Protected routes require auth
- [ ] `/auth/sync-user` returns 200
- [ ] `/auth/me` returns 200
- [ ] `/twins` returns 200 (with auth)
- [ ] No 401/403 errors in browser console
- [ ] No 401/403 errors in backend logs

