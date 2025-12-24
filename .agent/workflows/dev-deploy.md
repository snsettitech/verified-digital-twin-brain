---
description: Switch between local development and production deployment modes
---

# Development Mode Workflow

## Commands

| User Says | Action |
|-----------|--------|
| **"Local testing done, deploy to production"** | Switch to production → Preflight → Push |
| **"Back to local development"** | Switch to local mode |

---

## Switch to Local Development

```powershell
# Update frontend to use local backend
Copy-Item "frontend\.env.local.production" "frontend\.env.local.production.bak" -Force -ErrorAction SilentlyContinue
$content = Get-Content "frontend\.env.local" -Raw
$content = $content -replace 'NEXT_PUBLIC_BACKEND_URL=.*', 'NEXT_PUBLIC_BACKEND_URL=http://localhost:8000'
$content | Set-Content "frontend\.env.local"
```

Then start dev servers:
```powershell
./scripts/dev.ps1
```

---

## Switch to Production & Deploy

// turbo-all

1. Restore production URL:
```powershell
$content = Get-Content "frontend\.env.local" -Raw
$content = $content -replace 'NEXT_PUBLIC_BACKEND_URL=.*', 'NEXT_PUBLIC_BACKEND_URL=https://verified-digital-twin-brains.onrender.com'
$content | Set-Content "frontend\.env.local"
```

2. Run preflight:
```powershell
./scripts/preflight.ps1
```

3. Commit and push:
```powershell
git add -A
git commit -m "Deploy: [describe changes]"
git push origin main
```

---

## Current State Indicators

- **Local Mode**: `NEXT_PUBLIC_BACKEND_URL=http://localhost:8000`
- **Production Mode**: `NEXT_PUBLIC_BACKEND_URL=https://verified-digital-twin-brains.onrender.com`

Check current mode:
```powershell
Get-Content "frontend\.env.local" | Select-String "BACKEND_URL"
```
