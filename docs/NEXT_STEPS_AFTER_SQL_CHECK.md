# Next Steps After Running SQL Diagnostic

**Date:** 2025-01-27  
**Status:** Action plan based on SQL diagnostic results

---

## Step 1: Review Your SQL Results

Based on what you found, use this guide:

### If Tables Count < 25: **🔴 MISSING MIGRATIONS**

You need to run migrations. See **Step 2** below.

### If Critical Tables Missing: **🔴 MISSING SPECIFIC MIGRATIONS**

Check which tables are missing and run the corresponding migrations:

- `users`, `tenants`, `twins` → Base schema
- `verified_qna` → Phase 4 migration
- `interview_sessions` → Phase 3.5 interview migration
- `nodes`, `edges` → Phase 3.5 graph migration
- `access_groups` → Phase 5 migration
- `metrics` → Phase 10 migration

### If RPC Functions Missing: **🔴 MISSING RPC FUNCTIONS**

Run: `migration_phase3_5_gate3_fix_rls.sql` and `migration_interview_sessions.sql`

---

## Step 2: Run Missing Migrations

### Migration Order (CRITICAL - Must run in this order):

1. **Base Schema** (if starting fresh):
   ```sql
   -- Run: backend/database/schema/supabase_schema.sql
   ```

2. **Phase 4 - Verified QnA**:
   ```sql
   -- Run: backend/database/migrations/migration_phase4_verified_qna.sql
   ```

3. **Phase 5 - Access Groups**:
   ```sql
   -- Run: backend/database/migrations/migration_phase5_access_groups.sql
   ```

4. **Phase 6 - Mind Ops**:
   ```sql
   -- Run: backend/database/migrations/migration_phase6_mind_ops.sql
   ```

5. **Phase 7 - Omnichannel**:
   ```sql
   -- Run: backend/database/migrations/migration_phase7_omnichannel.sql
   ```

6. **Phase 8 - Actions Engine**:
   ```sql
   -- Run: backend/database/migrations/migration_phase8_actions_engine.sql
   ```

7. **Phase 9 - Governance**:
   ```sql
   -- Run: backend/database/migrations/migration_phase9_governance.sql
   ```

8. **Phase 3.5 - Cognitive Features** (run all):
   ```sql
   -- Run: backend/database/migrations/migration_phase3_5_gate1_specialization.sql
   -- Run: backend/database/migrations/migration_phase3_5_gate2_tenant_guard.sql
   -- Run: backend/database/migrations/migration_phase3_5_gate3_fix_rls.sql
   -- Run: backend/database/migrations/migration_phase3_5_gate3_graph.sql
   -- Run: backend/database/migrations/migration_interview_sessions.sql
   -- Run: backend/database/migrations/migration_gate5_versioning.sql
   ```

9. **RLS Security**:
   ```sql
   -- Run: backend/migrations/enable_rls_all_tables.sql
   ```

10. **Phase 10 - Metrics** (optional but recommended):
   ```sql
   -- Run: backend/migrations/phase10_metrics.sql
   ```

### How to Run Migrations:

1. Open Supabase Dashboard → SQL Editor
2. Copy content of each migration file (from `backend/database/migrations/`)
3. Paste into SQL Editor
4. Click "Run" (or press Ctrl+Enter)
5. Check for errors (should see "Success. No rows returned")
6. Move to next migration
7. **After all migrations, reload schema cache** (see Step 3)

---

## Step 3: Reload Schema Cache

**CRITICAL** - Supabase caches schema, so new tables/functions won't be recognized until cache reloads.

### Option A: Supabase Cloud (Recommended)
1. Go to Supabase Dashboard
2. Settings → Database
3. Scroll down to "Schema Cache"
4. Click **"Reload Schema Cache"** button

### Option B: Supabase CLI (if using local)
```bash
supabase db reset
# OR
docker restart supabase-kong
```

---

## Step 4: Verify Environment Variables

### Backend Environment Variables

Check `backend/.env` file exists and contains:

```bash
# Required - Core
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGci...  # anon key
SUPABASE_SERVICE_KEY=eyJhbGci...  # service_role key
JWT_SECRET=your-jwt-secret-here  # From Supabase Dashboard → Settings → API → JWT Secret

# Required - External Services
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=digital-twin  # or your index name

# Required - CORS
ALLOWED_ORIGINS=http://localhost:3000  # or your production domain

# Required - Production
DEV_MODE=false

# Optional
PORT=8000
HOST=0.0.0.0
```

### Frontend Environment Variables

Check `frontend/.env.local` file exists and contains:

```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...  # anon key (same as SUPABASE_KEY)
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000  # or your backend URL
```

### Where to Get Values:

1. **Supabase URL & Keys:**
   - Dashboard → Settings → API
   - Copy "Project URL" → `SUPABASE_URL`
   - Copy "anon public" key → `SUPABASE_KEY` / `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - Copy "service_role" key → `SUPABASE_SERVICE_KEY`

2. **JWT Secret:**
   - Dashboard → Settings → API
   - Copy "JWT Secret" → `JWT_SECRET`

3. **OpenAI API Key:**
   - Get from OpenAI Dashboard: https://platform.openai.com/api-keys

4. **Pinecone API Key & Index:**
   - Get from Pinecone Dashboard: https://app.pinecone.io
   - Create index if doesn't exist (dimension: 3072, metric: cosine)

---

## Step 5: Verify Pinecone Index

### Check if Index Exists:

1. Go to Pinecone Dashboard: https://app.pinecone.io
2. Navigate to "Indexes"
3. Look for index matching `PINECONE_INDEX_NAME` env var

### If Index Doesn't Exist - Create It:

1. Click "Create Index"
2. **Index Name:** `digital-twin` (or match your env var)
3. **Dimensions:** `3072` (CRITICAL - for text-embedding-3-large)
4. **Metric:** `cosine`
5. **Environment:** Your Pinecone environment
6. Click "Create Index"

### Verify Configuration:

- ✅ Index name matches `PINECONE_INDEX_NAME` env var
- ✅ Dimension = 3072
- ✅ Metric = cosine

---

## Step 6: Test Backend Health

### Start Backend:

```bash
cd backend
python -m venv .venv  # if not already created
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt  # if not already installed
python main.py
```

### Check Health Endpoint:

```bash
# In another terminal
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "verified-digital-twin-brain-api",
  "version": "1.0.0"
}
```

### Check Enhanced Health (if Phase 10 migration applied):

```bash
curl http://localhost:8000/metrics/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "services": {
    "supabase": "healthy",
    "pinecone": "healthy",
    "openai": "healthy"
  }
}
```

### If Health Check Fails:

- Check backend logs for errors
- Verify environment variables are set correctly
- Check database connection (Supabase URL/key)
- Check Pinecone connection (API key/index name)

---

## Step 7: Test Frontend

### Start Frontend:

```bash
cd frontend
npm install  # if not already installed
npm run dev
```

### Check Browser Console:

1. Open browser: http://localhost:3000
2. Open Developer Tools (F12)
3. Check Console tab for errors
4. Check Network tab for failed requests

### Common Frontend Issues:

- **CORS errors** → Check `ALLOWED_ORIGINS` in backend `.env`
- **401 errors** → Check JWT_SECRET matches Supabase
- **500 errors** → Check backend logs
- **Cannot connect** → Check `NEXT_PUBLIC_BACKEND_URL` is correct

---

## Step 8: Test Critical User Flow

### Test 1: Login

1. Go to http://localhost:3000/auth/login
2. Click "Sign in with Google" (or your auth method)
3. Complete OAuth flow
4. **Check:** Should redirect to dashboard or onboarding

### Test 2: User Sync

After login, check backend logs for:
```
[SYNC DEBUG] User created successfully
```

Or verify in database:
```sql
SELECT id, email, tenant_id FROM users ORDER BY created_at DESC LIMIT 1;
```

### Test 3: Create Twin (if onboarding)

1. Complete onboarding flow
2. Create a twin
3. **Check:** Twin appears in dashboard

### Test 4: Send Chat Message

1. Go to dashboard → Chat
2. Type a message
3. **Check:** AI responds (may say "I don't know" if no knowledge base)

---

## Step 9: Troubleshooting Common Issues

### Issue: "Column not found" errors

**Fix:** Reload schema cache (Step 3)

### Issue: "Function does not exist" errors

**Fix:** Run RPC function migrations (Phase 3.5 migrations)

### Issue: 401 Unauthorized errors

**Fix:** 
- Verify JWT_SECRET matches Supabase Dashboard
- Check token is being sent in Authorization header
- Verify user exists in database

### Issue: 403 Forbidden errors

**Fix:**
- Check user has `tenant_id` set
- Check twin belongs to user's tenant
- Verify RLS policies are correct

### Issue: Chat returns "I don't know" always

**Fix:**
- Check Pinecone index exists and configured correctly
- Verify documents are ingested (check `sources` table)
- Check OpenAI API key is valid

### Issue: CORS errors

**Fix:**
- Update `ALLOWED_ORIGINS` in backend `.env`
- Restart backend server
- Check browser console for exact error

---

## Step 10: Verify Everything Works

### Final Checklist:

- [ ] Database has 25+ tables
- [ ] All critical tables exist
- [ ] RPC functions exist (5+ functions)
- [ ] RLS is enabled on critical tables
- [ ] Environment variables all set
- [ ] Backend health check passes
- [ ] Frontend starts without errors
- [ ] User can login
- [ ] User sync creates user record
- [ ] Twin creation works
- [ ] Chat sends/receives messages (even if "I don't know")
- [ ] No console errors in browser
- [ ] No 500 errors in backend logs

---

## Next Steps After Setup Complete

Once everything is working:

1. **Ingest Knowledge:** Upload documents to build knowledge base
2. **Test Chat:** Ask questions, verify answers
3. **Test Escalation:** Ask question system doesn't know
4. **Test Verified QnA:** Resolve escalation, verify answer is saved
5. **Test Cognitive Features:** Use interview flow (if applicable)

---

## Need Help?

If you're stuck:

1. Check `docs/KNOWN_FAILURES.md` for known issues
2. Check backend logs for error messages
3. Check browser console for frontend errors
4. Verify each step above was completed
5. Review error messages carefully - they usually point to the issue

