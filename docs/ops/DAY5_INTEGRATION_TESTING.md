# Day 5: Integration Testing & Staging Deployment

## Overview

This document outlines the integration testing and staging deployment process for the P0-P1 Reliability & Security Hardening work.

## Pre-Deployment Checklist

### ✅ Completed P0 Tasks

- [x] **P0-A**: CI/CD Alignment
  - CI uses version files (`.nvmrc`, `.python-version`)
  - Build steps match production
  - Lockfile validation in place

- [x] **P0-B**: Auth Correctness
  - All endpoints use `verify_twin_ownership()`
  - Source ownership verification added (`verify_source_ownership()`)
  - Conversation ownership verification added (`verify_conversation_ownership()`)
  - Bulk operations verify ownership

- [x] **P0-C**: SECURITY DEFINER Hardening
  - All SECURITY DEFINER functions have `SET search_path = ''`
  - All table references fully qualified (`public.table_name`)
  - Execution permissions restricted

- [x] **P0-D**: Graph Extraction Job Queue
  - Fire-and-forget replaced with job queue
  - Idempotency checks implemented
  - Retry logic with exponential backoff
  - Job logging and status tracking

## Integration Tests

### Test Execution

Run the comprehensive test suite:

```bash
# Backend tests
cd backend
python -m pytest tests/test_p0_integration.py -v

# Auth tests
python -m pytest tests/test_auth_comprehensive.py -v

# Preflight checks (full suite)
./scripts/preflight.ps1  # Windows
./scripts/preflight.sh   # Linux/Mac
```

### Test Coverage

1. **Auth Correctness (P0-B)**
   - ✅ Wrong tenant access → 404
   - ✅ Revoked user → 401
   - ✅ Expired token → 401
   - ✅ Share link validation
   - ✅ API key validation
   - ✅ Source ownership verification
   - ✅ Conversation ownership verification

2. **Graph Extraction (P0-D)**
   - ✅ Job enqueueing
   - ✅ Idempotency checks
   - ✅ Job processing with retries
   - ✅ Job logging

3. **Security (P0-C)**
   - ✅ SECURITY DEFINER functions hardened
   - ✅ Search path isolation
   - ✅ Table reference qualification

## Staging Deployment Steps

### 1. Database Migrations

Apply migrations in order:

```sql
-- Run in Supabase SQL Editor
-- 1. Graph extraction job type
\i backend/database/migrations/migration_add_graph_extraction_job_type.sql

-- 2. SECURITY DEFINER hardening (if not already applied)
\i backend/database/migrations/migration_security_definer_hardening.sql
```

### 2. Environment Variables

Verify staging environment variables:

**Backend (.env):**
- `JWT_SECRET` - Supabase JWT secret
- `SUPABASE_URL` - Staging Supabase URL
- `SUPABASE_KEY` - Staging anon key
- `SUPABASE_SERVICE_KEY` - Staging service key
- `OPENAI_API_KEY` - OpenAI API key
- `PINECONE_API_KEY` - Pinecone API key
- `PINECONE_INDEX_NAME` - Pinecone index name

**Frontend (.env.local):**
- `NEXT_PUBLIC_SUPABASE_URL` - Staging Supabase URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Staging anon key
- `NEXT_PUBLIC_BACKEND_URL` - Staging backend URL

### 3. Build Verification

```bash
# Frontend
cd frontend
npm ci
npm run lint
npm run typecheck
npm run build

# Backend
cd backend
pip install -r requirements.txt
python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
python -m pytest -v --tb=short -m "not network"
```

### 4. Deployment

**Vercel (Frontend):**
1. Push to staging branch
2. Vercel auto-deploys
3. Verify build succeeds
4. Test health endpoint: `https://staging.yourapp.com/health`

**Render/Railway (Backend):**
1. Deploy from staging branch
2. Verify health check: `GET /health`
3. Check logs for startup errors
4. Verify migrations applied

### 5. Post-Deployment Verification

#### Health Checks

```bash
# Backend health
curl https://staging-backend.yourapp.com/health

# Frontend (should return 200)
curl -I https://staging.yourapp.com
```

#### Smoke Tests

1. **Auth Flow**
   - [ ] Sign up works
   - [ ] Login works
   - [ ] JWT token valid
   - [ ] Token refresh works

2. **Twin Operations**
   - [ ] Create twin
   - [ ] List twins (only own)
   - [ ] Get twin by ID (ownership check)
   - [ ] Cross-tenant access blocked (404)

3. **Source Operations**
   - [ ] Upload source
   - [ ] List sources (twin-scoped)
   - [ ] Approve source (ownership check)
   - [ ] Get source health (ownership check)
   - [ ] Cross-tenant source access blocked

4. **Chat & Graph Extraction**
   - [ ] Send chat message
   - [ ] Graph extraction job enqueued
   - [ ] Job appears in jobs table
   - [ ] Worker processes job (if enabled)
   - [ ] Graph nodes/edges created

5. **Conversations**
   - [ ] List conversations (twin-scoped)
   - [ ] Get messages (conversation-scoped)
   - [ ] Cross-tenant conversation access blocked

#### Database Verification

```sql
-- Check SECURITY DEFINER functions are hardened
SELECT 
    p.proname as function_name,
    pg_get_functiondef(p.oid) as definition
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname = 'public'
AND p.prosecdef = true  -- SECURITY DEFINER
AND pg_get_functiondef(p.oid) NOT LIKE '%SET search_path = ''%';

-- Should return 0 rows (all functions hardened)

-- Check graph extraction jobs
SELECT COUNT(*) as graph_jobs_count
FROM jobs
WHERE job_type = 'graph_extraction'
AND created_at > NOW() - INTERVAL '1 hour';

-- Should show jobs if chat was used
```

### 6. Monitoring

Monitor for:
- [ ] Error rates < 1%
- [ ] p95 latency < 3.0s (time-to-first-token)
- [ ] Graph extraction job success rate > 95%
- [ ] No auth failures (401/403 spikes)
- [ ] No database connection errors

### 7. Rollback Plan

If issues are detected:

**Backend:**
```bash
# Render/Railway: Use dashboard to rollback to previous deployment
# Or: git revert and redeploy
git revert HEAD
git push origin staging
```

**Frontend:**
```bash
# Vercel: Use dashboard to promote previous deployment
# Or: git revert and redeploy
git revert HEAD
git push origin staging
```

**Database:**
```sql
-- Only if migrations caused issues (rare)
-- Revert migrations in reverse order
-- Contact database admin if needed
```

## Success Criteria

✅ **All preflight checks pass**
✅ **Integration tests pass (100%)**
✅ **Staging deployment successful**
✅ **Smoke tests pass (all critical flows)**
✅ **No errors in logs**
✅ **Health checks return 200**
✅ **Graph extraction jobs process successfully**
✅ **Cross-tenant isolation verified**

## Next Steps

After successful staging deployment:

1. **Monitor for 24 hours**
   - Watch error rates
   - Check job processing
   - Verify auth flows

2. **Performance Testing**
   - Load test critical endpoints
   - Verify p95 latency targets
   - Check concurrent user handling

3. **Production Deployment**
   - Follow same process
   - Deploy during low-traffic window
   - Monitor closely for first hour

## Notes

- Worker must be running to process graph extraction jobs
- If Redis unavailable, jobs use in-memory queue (single-instance only)
- Database migrations are idempotent (safe to re-run)
- SECURITY DEFINER hardening is backward compatible

