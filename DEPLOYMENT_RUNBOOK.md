# Deployment Runbook

**Target Stack:** Vercel (Frontend) | Render/Railway (Backend) | Supabase | Pinecone

---

## Pre-Deployment Checklist

- [ ] Supabase project created with Google OAuth enabled
- [ ] Pinecone index created (dimension: 1536, metric: cosine)
- [ ] OpenAI API key obtained
- [ ] Domain configured for frontend (e.g., `yourapp.com`)
- [ ] Backend deployment URL known (or will be after deploy)

---

## Step 1: Supabase Configuration

### 1.1 Enable Google OAuth

1. Go to **Supabase Dashboard → Authentication → Providers**
2. Enable **Google**
3. Add Google OAuth credentials:
   - Client ID
   - Client Secret
4. In **Google Cloud Console**, add authorized redirect:
   ```
   https://YOUR_SUPABASE_PROJECT.supabase.co/auth/v1/callback
   ```

### 1.2 Configure Redirect URLs

1. Go to **Supabase Dashboard → Authentication → URL Configuration**
2. Set:
   ```
   Site URL: https://yourapp.com
   
   Redirect URLs:
   - https://yourapp.com/auth/callback
   - http://localhost:3000/auth/callback
   ```

### 1.3 Copy API Keys

From **Supabase Dashboard → Settings → API**, copy:

| Key | Use For |
|-----|---------|
| Project URL | Both frontend and backend |
| anon/public key | Frontend + Backend |
| service_role key | Backend only |
| JWT Secret | Backend JWT_SECRET env var |

---

## Step 2: Backend Deployment (Render/Railway)

### 2.1 Create New Web Service

**Render:**
1. New → Web Service
2. Connect to GitHub repo
3. Root Directory: `backend`
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Railway:**
1. New Project → Deploy from GitHub
2. Root Directory: `backend`
3. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 2.2 Set Environment Variables

```bash
# Required
SUPABASE_URL=https://xyz.supabase.co
SUPABASE_KEY=eyJhbGci...
SUPABASE_SERVICE_KEY=eyJhbGci...
JWT_SECRET=<from Supabase Settings → API → JWT Secret>
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=digital-twin

# Production settings
DEV_MODE=false
ALLOWED_ORIGINS=https://yourapp.com,https://www.yourapp.com
HOST=0.0.0.0
PORT=8000
```

### 2.3 Verify Health Check

After deploy completes:

```bash
curl https://your-backend.onrender.com/health
```

**Expected response:**
```json
{"status": "healthy", "service": "verified-digital-twin-brain-api", "version": "1.0.0"}
```

---

## Step 3: Frontend Deployment (Vercel)

### 3.1 Import Project

1. Vercel → New Project → Import Git Repository
2. Root Directory: `frontend`
3. Framework Preset: Next.js

### 3.2 Set Environment Variables

```bash
# Required
NEXT_PUBLIC_SUPABASE_URL=https://xyz.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...
NEXT_PUBLIC_BACKEND_URL=https://your-backend.onrender.com

# Optional
NEXT_PUBLIC_FRONTEND_URL=https://yourapp.com
```

**⚠️ DO NOT SET:**
- `NEXT_PUBLIC_DEV_TOKEN` (must not exist in production)

### 3.3 Deploy

Click **Deploy** and wait for build to complete.

---

## Step 4: Post-Deploy Smoke Tests

### Test 1: Health Check

```bash
curl https://your-backend.onrender.com/health
```

✅ Expected: `{"status": "healthy"}`

### Test 2: Frontend Loads

1. Navigate to `https://yourapp.com`
2. ✅ Landing page renders without errors

### Test 3: Login Flow

1. Click "Login with Google"
2. Complete Google OAuth
3. ✅ Redirected to `/dashboard`
4. Check Supabase: User appears in `auth.users`
5. Check Supabase: Row appears in `public.users`
6. Check Supabase: Row appears in `public.tenants`

### Test 4: Twin Loading

1. Complete onboarding (create twin)
2. Navigate to **Right Brain**
3. ✅ Twin loads dynamically (not hardcoded)
4. ✅ Graph visualization appears

### Test 5: Chat Interaction

1. Type a question in chat
2. ✅ Response streams back
3. Check Supabase: `conversations` and `messages` have new rows

---

## Step 5: Rollback Plan

### If Auth Breaks

1. **Immediately:** Check Supabase → Authentication → Logs
2. **Check:** Is `JWT_SECRET` correct in backend?
3. **Check:** Are redirect URLs configured correctly?
4. **Temporary fix:** Set `DEV_MODE=true` on backend (INSECURE, dev only)

### If Backend Crashes

1. Check Render/Railway logs
2. Common issues:
   - Missing env var → Add it
   - Pinecone connection failed → Verify API key and index name
   - Supabase connection failed → Verify URL and key

### If Frontend 500s

1. Check Vercel function logs
2. Common issues:
   - Missing `NEXT_PUBLIC_SUPABASE_URL`
   - Missing `NEXT_PUBLIC_BACKEND_URL`
   - Backend not responding (check backend health first)

### Emergency: Disable Auth

If auth is completely broken and you need the app accessible:

1. On backend, set `DEV_MODE=true` (TEMPORARY, INSECURE)
2. This enables `development_token` bypass
3. Fix the root cause ASAP
4. Set `DEV_MODE=false` again

---

## Troubleshooting Quick Reference

| Symptom | Check | Fix |
|---------|-------|-----|
| 401 on API calls | JWT_SECRET mismatch | Copy exact value from Supabase |
| 403 on twin access | verify_twin_access failing | User doesn't own the twin |
| CORS error | ALLOWED_ORIGINS missing frontend | Add frontend URL to ALLOWED_ORIGINS |
| OAuth redirect fails | Redirect URL not in Supabase | Add to Authentication → URL Config |
| "Invalid API key" | PINECONE_API_KEY wrong | Verify in Pinecone console |
| Chat doesn't respond | OpenAI key invalid | Verify OPENAI_API_KEY |

---

## DNS & SSL

### Vercel (Frontend)
- Automatic SSL
- Add custom domain in Vercel project settings

### Render/Railway (Backend)
- Automatic SSL on `*.onrender.com` / `*.railway.app`
- For custom domain, configure in platform settings

---

## Monitoring

### Minimal Monitoring (P0)

1. **Backend:** Use Render/Railway built-in logs
2. **Frontend:** Use Vercel function logs
3. **Auth:** Supabase → Authentication → Logs
4. **Database:** Supabase → SQL Editor → Check table counts

### Health Check Endpoint

Set up uptime monitoring (e.g., UptimeRobot, Better Uptime):

```
URL: https://your-backend.onrender.com/health
Interval: 5 minutes
Alert: Status != 200
```

---

## Definition of Done

| Check | Status |
|-------|--------|
| Backend responds to /health | ⬜ |
| Frontend loads without errors | ⬜ |
| Google OAuth login works | ⬜ |
| User + Tenant created on login | ⬜ |
| Twin loads dynamically | ⬜ |
| Chat sends and receives messages | ⬜ |

**Deployment is complete when all boxes are checked.**
