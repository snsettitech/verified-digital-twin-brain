# Day 5: Integration Testing & Staging Deployment Checklist

## Overview
This checklist ensures all P0 reliability and security hardening changes are tested and ready for staging deployment.

## Pre-Deployment Verification

### ✅ P0-A: CI/CD Alignment
- [x] CI uses version files (`.nvmrc`, `.python-version`)
- [x] CI build commands match production (Vercel/Render)
- [x] Lockfiles validated (`npm ci` enforces `package-lock.json`)
- [x] Preflight scripts aligned with CI

**Verification Command:**
```bash
./scripts/preflight.ps1  # Windows
# OR
./scripts/preflight.sh   # Linux/Mac
```

### ✅ P0-B: Auth Correctness
- [x] All twin-scoped endpoints use `verify_twin_ownership()`
- [x] All source-scoped endpoints use `verify_source_ownership()`
- [x] All conversation-scoped endpoints use `verify_conversation_ownership()`
- [x] No per-router JWT parsing (all use `Depends(get_current_user)`)
- [x] Bulk operations verify ownership of all resources

**Verification:**
```bash
cd backend
pytest tests/test_auth_comprehensive.py -v
pytest tests/test_p0_integration.py::test_tenant_isolation -v
pytest tests/test_p0_integration.py::test_source_ownership_verification -v
```

### ✅ P0-C: SECURITY DEFINER Hardening
- [x] All SECURITY DEFINER functions have `SET search_path = ''`
- [x] All table references are fully qualified (`public.table_name`)
- [x] Execution permissions restricted (REVOKE FROM PUBLIC, GRANT TO service_role/authenticated)

**Verification:**
1. Run migration: `backend/database/migrations/migration_security_definer_hardening.sql`
2. Check Supabase Dashboard → Database → Advisors
3. Verify zero "function_search_path_mutable" findings

**Migration Command:**
```sql
-- Run in Supabase SQL Editor
\i backend/database/migrations/migration_security_definer_hardening.sql
```

### ✅ P0-D: Graph Extraction Jobs
- [x] Graph extraction moved from fire-and-forget to job queue
- [x] Idempotency implemented (conversation_id + content hash)
- [x] Job status endpoint exists: `GET /twins/{twin_id}/graph-job-status`
- [x] Worker processes graph_extraction jobs
- [x] Retry logic with exponential backoff

**Verification:**
```bash
# Test job enqueue
pytest tests/test_p0_integration.py::test_graph_extraction_job_enqueue -v

# Test idempotency
pytest tests/test_p0_integration.py::test_graph_extraction_idempotency -v

# Test job processing
pytest tests/test_p0_integration.py::test_graph_extraction_job_processing -v
```

## Integration Tests

### Run All Integration Tests
```bash
cd backend
pytest tests/test_p0_integration.py -v
```

### Golden Flow Tests
1. **Flow 1: Tenant Isolation**
   ```bash
   pytest tests/test_p0_integration.py::test_tenant_isolation -v
   ```

2. **Flow 2: Twin Creation**
   ```bash
   pytest tests/test_p0_integration.py::test_create_twin_flow -v
   ```

3. **Flow 3: Ingestion & Retrieval**
   ```bash
   pytest tests/test_p0_integration.py::test_ingestion_retrieval_flow -v
   ```

4. **Flow 4: Chat with Fallback**
   ```bash
   pytest tests/test_p0_integration.py::test_chat_retrieval_fallback -v
   ```

5. **Flow 5: Graph Extraction**
   ```bash
   pytest tests/test_p0_integration.py::test_graph_extraction_job_enqueue -v
   pytest tests/test_p0_integration.py::test_graph_extraction_idempotency -v
   ```

## Database Migrations

### Required Migrations (Run in Order)
1. `migration_security_definer_hardening.sql` (if not already applied)
2. `migration_add_graph_extraction_job_type.sql` (new)

**Apply Migrations:**
```sql
-- In Supabase SQL Editor, run:
\i backend/database/migrations/migration_security_definer_hardening.sql
\i backend/database/migrations/migration_add_graph_extraction_job_type.sql
```

**Verify:**
```sql
-- Check job_type constraint includes 'graph_extraction'
SELECT constraint_name, check_clause 
FROM information_schema.check_constraints 
WHERE table_name = 'jobs' AND constraint_name = 'valid_job_type';

-- Check SECURITY DEFINER functions have search_path = ''
SELECT routine_name, security_type, 
       (SELECT setting FROM pg_settings WHERE name = 'search_path') as search_path
FROM information_schema.routines
WHERE routine_schema = 'public' 
  AND security_type = 'DEFINER'
  AND routine_name LIKE '%_system';
```

## Staging Deployment Steps

### 1. Backend (Render/Railway)
- [ ] Verify environment variables are set:
  - `JWT_SECRET` (from Supabase Dashboard)
  - `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_SERVICE_KEY`
  - `OPENAI_API_KEY`
  - `PINECONE_API_KEY`, `PINECONE_INDEX_NAME`
- [ ] Run migrations in Supabase SQL Editor
- [ ] Deploy backend code
- [ ] Verify health endpoint: `GET /health`
- [ ] Check worker is running (if separate process)

### 2. Frontend (Vercel)
- [ ] Verify environment variables:
  - `NEXT_PUBLIC_SUPABASE_URL`
  - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
  - `NEXT_PUBLIC_BACKEND_URL`
- [ ] Deploy frontend
- [ ] Verify build succeeds
- [ ] Test login flow

### 3. Post-Deployment Verification

**Health Checks:**
```bash
# Backend health
curl https://staging-backend.example.com/health

# Frontend (should load)
curl https://staging-frontend.vercel.app
```

**Golden Flow Smoke Tests:**
1. **Login** → Should redirect to dashboard
2. **Create Twin** → Should create and show in list
3. **Upload Document** → Should show in sources list
4. **Chat** → Should return response with citations
5. **Graph Status** → `GET /twins/{twin_id}/graph-job-status` should return status

**API Tests:**
```bash
# Test auth (replace with actual token)
TOKEN="your-jwt-token"
TWIN_ID="your-twin-id"

# Test twin access
curl -H "Authorization: Bearer $TOKEN" \
  https://staging-backend.example.com/twins/$TWIN_ID

# Test graph job status
curl -H "Authorization: Bearer $TOKEN" \
  https://staging-backend.example.com/twins/$TWIN_ID/graph-job-status

# Test source ownership (should fail for wrong tenant)
curl -H "Authorization: Bearer $TOKEN" \
  https://staging-backend.example.com/sources/wrong-source-id/health
```

## Rollback Plan

If deployment fails:

1. **Backend Rollback:**
   - Render Dashboard → Events → Rollback to previous deployment
   - OR: Revert git commit and redeploy

2. **Frontend Rollback:**
   - Vercel Dashboard → Deployments → Promote previous deployment

3. **Database Rollback:**
   - Migrations are additive (no destructive changes)
   - If needed, manually revert:
     ```sql
     -- Revert job_type constraint (if needed)
     ALTER TABLE jobs DROP CONSTRAINT IF EXISTS valid_job_type;
     ALTER TABLE jobs ADD CONSTRAINT valid_job_type CHECK (
         job_type IN ('ingestion', 'reindex', 'health_check', 'other')
     );
     ```

## Success Criteria

After staging deployment, verify:

- [ ] ✅ 10 consecutive successful deployments (track in CI)
- [ ] ✅ Zero SECURITY DEFINER vulnerabilities (Supabase Advisors)
- [ ] ✅ Graph jobs visible in dashboard (`/twins/{twin_id}/graph-job-status`)
- [ ] ✅ Auth tests pass (wrong tenant → 404)
- [ ] ✅ All 5 golden flows work end-to-end
- [ ] ✅ No silent failures (all errors logged)

## Monitoring

### Key Metrics to Watch
1. **Deployment Success Rate**: Should be 100% after fixes
2. **Graph Job Success Rate**: Should be > 95%
3. **Auth Failures**: Wrong tenant access should return 404 (not 500)
4. **Job Backlog**: Should not exceed 100 jobs per twin

### Alerts to Set Up
- Job failure rate > 5% over 1 hour
- Backlog > 100 jobs
- Last graph extraction success > 1 hour ago (for active twins)

## Next Steps (P1 Tasks)

After P0 is validated in staging:
- P1-A: LangGraph Durability (checkpointer)
- P1-B: GraphRAG-Lite (entity-centric retrieval)
- P1-C: Retrieval Quality Gates (timeouts, empty context handling)

---

**Last Updated**: Day 5 - Integration Testing & Staging Deployment
**Status**: ✅ Ready for Staging

