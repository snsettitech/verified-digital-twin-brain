# Known Failures and Fixes

This document catalogs the domino failures we expect to encounter during system verification, starting with the confirmed blocker.

---

## 🔴 BLOCKER 1: Missing avatar_url Column (CONFIRMED)

### Symptom
```
POST /auth/sync-user → 500 Internal Server Error
postgrest.exceptions.APIError: 
{'message': "Could not find the 'avatar_url' column of 'users' in the schema cache", 'code': 'PGRST204'}
```

### Root Cause
The `users` table in Supabase is missing the `avatar_url` column, but the backend code in `routers/auth.py` tries to INSERT into this column during user sync.

### Impact
- User creation fails completely
- No valid user record exists in database
- All subsequent API calls fail with 403 Forbidden (user not recognized as owner)
- Frontend cannot proceed past login

### Fix
**Option A (Add Column):**
```sql
ALTER TABLE users ADD COLUMN avatar_url TEXT;
```

**Option B (Remove from Code):**
Edit `backend/routers/auth.py` line 91 and remove `avatar_url` from INSERT statement.

### Verification
```bash
# After fix, run:
export TEST_TOKEN="your-jwt-token"
curl -X POST http://localhost:8000/auth/sync-user -H "Authorization: Bearer $TEST_TOKEN"

# Expected: 200 OK with user object
```

---

## 🟡 PROBABLE FAILURE 2: Missing interview_sessions Table

### Symptom (IF BLOCKER 1 is fixed)
```
POST /cognitive/interview/{twin_id} → 500
Error calling RPC function 'get_or_create_interview_session'
```

### Root Cause
The `interview_sessions` table migration was never run in the database.

### Impact
- Interview endpoint crashes
- Cannot track interview state
- Stage-based routing fails

### Fix
```bash
# Run migration
psql $DATABASE_URL -f backend/database/migrations/migration_interview_sessions.sql
```

### Verification
```sql
SELECT table_name FROM information_schema.tables WHERE table_name = 'interview_sessions';
-- Expected: 1 row
```

---

## 🟡 PROBABLE FAILURE 3: Missing RPC Functions

### Symptom
```
Error: function get_nodes_system(uuid, integer) does not exist
```

### Root Cause
RLS bypass functions not created (required for backend to query with anon key).

### Impact
- Graph retrieval fails
- Node/edge creation fails
- Interview logic cannot persist data

### Fix
```bash
# Run RPC migrations
psql $DATABASE_URL -f backend/database/migrations/migration_phase3_5_gate3_fix_rls.sql
```

### Verification
```sql
SELECT proname FROM pg_proc WHERE proname LIKE '%system%';
-- Expected: get_nodes_system, create_node_system, get_edges_system, create_edge_system, etc.
```

---

## 🟢 POSSIBLE FAILURE 4: CORS Misconfiguration

### Symptom
```
Access to fetch at 'http://localhost:8000/...' from origin 'http://localhost:3000' 
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header
```

### Root Cause
Backend `main.py` has incorrect `allowed_origins` setting.

### Impact
- Frontend cannot make API requests
- All endpoints appear unreachable from browser

### Fix
Edit `backend/main.py`:
```python
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
```

Or set environment variable:
```bash
export ALLOWED_ORIGINS="http://localhost:3000,http://127.0.0.1:3000"
```

### Verification
```bash
curl -i -X OPTIONS http://localhost:8000/auth/sync-user \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST"

# Expected: access-control-allow-origin header present
```

---

## 🟢 POSSIBLE FAILURE 5: Invalid JWT Secret

### Symptom
```
GET /auth/me → 401 Unauthorized
Error: Invalid JWT signature
```

### Root Cause
`JWT_SECRET` in backend `.env` doesn't match Supabase project secret.

### Impact
- Token validation fails
- All authenticated endpoints return 401
- User cannot access any protected resources

### Fix
Get correct secret from Supabase:
1. Go to Supabase Dashboard → Project Settings → API
2. Copy "JWT Secret"
3. Update `backend/.env`:
```
JWT_SECRET=your-actual-secret-from-supabase
```

### Verification
```bash
export TEST_TOKEN="valid-jwt-from-browser"
curl http://localhost:8000/auth/me -H "Authorization: Bearer $TEST_TOKEN"
# Expected: 200 or 404 (not 401)
```

---

## 🟢 POSSIBLE FAILURE 6: Missing OpenAI API Key

### Symptom
```
Interview responses are empty or error: "OpenAI API key not configured"
```

### Root Cause
`OPENAI_API_KEY` not set in backend `.env`.

### Impact
- LLM integration fails
- Agent cannot generate responses
- Interview flow returns generic fallback messages

### Fix
```bash
# Add to backend/.env
OPENAI_API_KEY=sk-your-key-here
```

### Verification
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
# Expected: List of available models
```

---

## 🟢 POSSIBLE FAILURE 7: Twin Ownership Mismatch

### Symptom
```
GET /twins/{twin_id}/graph → 403 Forbidden
GET /cognitive/interview/{twin_id} → 403 Forbidden
```

### Root Cause
The twin ID being accessed doesn't belong to the logged-in user.

### Impact
- Cannot access twins from different sessions
- Common after database reset or using copy-pasted twin IDs

### Fix
Either:
- Create a new twin for this user
- Or verify ownership in database:
```sql
SELECT id, owner_id, tenant_id FROM twins WHERE id = 'the-twin-id';
-- Verify owner_id matches your user_id
```

### Verification
```bash
# List your twins
curl http://localhost:8000/twins -H "Authorization: Bearer $TEST_TOKEN"
# Use an ID from this response
```

---

## 🟢 POSSIBLE FAILURE 8: Stale PostgREST Schema Cache

### Symptom
```
Error: Could not find column 'X' in schema cache (even after adding column)
```

### Root Cause
Supabase PostgREST caches schema and doesn't auto-refresh after migrations.

### Impact
- New columns not recognized
- New tables not accessible
- RPCs not found

### Fix
**For Supabase Cloud:**
Go to Project Settings → Database → Trigger Schema Cache Reload

**For Local Supabase:**
```bash
docker restart supabase-kong
# or
supabase db reset
```

### Verification
Re-run the failing query after cache refresh.

---

## Failure Dependency Chain

```
avatar_url missing (BLOCKER 1)
    ↓ blocks
User Sync (can't create user)
    ↓ blocks
Auth Guard (no user = 403)
    ↓ blocks
    ├─→ Interview Access
    ├─→ Graph Access
    └─→ Twin Management

SEPARATELY:
interview_sessions missing (PROBABLE 2)
    ↓ blocks
Interview Flow
    ↓ blocks
    ├─→ Stage Routing
    └─→ Session Tracking

RPC functions missing (PROBABLE 3)
    ↓ blocks
    ├─→ Node Creation
    ├─→ Edge Creation
    └─→ Graph Queries
```

**Key Insight**: Fix failures in this order:
1. BLOCKER 1 (avatar_url)
2. PROBABLE 2 (interview_sessions table)
3. PROBABLE 3 (RPC functions)
4. Then address any POSSIBLE failures as they appear

---

## Quick Diagnostic Commands

### Check if avatar_url exists:
```sql
SELECT column_name FROM information_schema.columns 
WHERE table_name='users' AND column_name='avatar_url';
```

### Check if interview_sessions exists:
```sql
SELECT EXISTS (SELECT FROM information_schema.tables 
WHERE table_name='interview_sessions');
```

### Check RPC functions:
```sql
SELECT COUNT(*) FROM pg_proc 
WHERE proname IN ('get_or_create_interview_session', 'get_nodes_system');
-- Expected: 2
```

### Check backend is running:
```bash
curl http://localhost:8000/health
```

### Check user exists after sync:
```sql
SELECT id, email, avatar_url FROM users ORDER BY created_at DESC LIMIT 1;
```

---

## How to Use This Document

1. **Start at BLOCKER 1** - Fix it first
2. **Run verification** - Use commands from VERIFICATION_PLAN.md
3. **When you hit an error** - Search this doc for the symptom
4. **Apply the fix** - Follow the exact commands
5. **Verify the fix** - Use the verification command
6. **Continue** - Move to next layer

**Remember**: One fix at a time, verify each fix before proceeding.
