# AdProof — Deployment & Hosting Guide

Where to host each component in production.

---

## 1. Architecture Overview (Production)

```
                    ┌─────────────┐
                    │   Vercel    │  ← Frontend (Next.js)
                    │  apps/web   │
                    └──────┬──────┘
                           │ REST / SSE
                           ▼
                    ┌─────────────┐
                    │ Render /    │  ← Backend API + Worker
                    │ Railway /   │     (FastAPI + ffmpeg)
                    │ Fly.io      │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │  Neon /  │ │ Upstash  │ │ Backblaze│
        │ Supabase │ │  Redis   │ │    B2    │
        │ Postgres │ │          │ │          │
        └──────────┘ └──────────┘ └──────────┘
```

---

## 2. Frontend — Vercel

| Setting | Value |
|---------|-------|
| **Platform** | [Vercel](https://vercel.com) |
| **Root directory** | `apps/web` |
| **Framework** | Next.js (auto-detected) |
| **Build command** | `npm run build` |
| **Output** | Next.js default |

### Vercel Setup Steps

1. Connect Git repository to Vercel
2. Set **Root Directory** to `apps/web`
3. Add environment variables:

```env
NEXT_PUBLIC_API_URL=https://api.your-domain.com
B2_WEBHOOK_SECRET=your-webhook-secret
```

4. Deploy — Vercel auto-deploys on push to main
5. Note your Vercel domain: `https://adproof.vercel.app`

### B2 Webhook URL

After deploy, configure B2 event notification:

```
https://adproof.vercel.app/api/webhooks/b2
```

Re-run `infra/b2-bucket-setup.py` with updated webhook URL, or configure manually in B2 console.

### Why Vercel for Frontend

- Native Next.js support (App Router, API routes, edge)
- Free tier sufficient for hackathon demo
- Automatic HTTPS, CDN, preview deployments per PR

---

## 3. Backend API + Worker — Render / Railway / Fly.io

| Setting | Value |
|---------|-------|
| **Platform** | Render, Railway, or Fly.io |
| **Why NOT serverless** | ffmpeg compose step needs long-running process (minutes); serverless timeouts will kill it |
| **Dockerfile** | `infra/Dockerfile.worker` |
| **Port** | 8000 |

### Option A: Render

1. Create **Web Service** from repo
2. Set Dockerfile path: `infra/Dockerfile.worker`
3. Add environment variables (all from `.env.example`)
4. Create **Background Worker** service for `python -m jobs.worker` (same image, different start command)
5. Custom domain: `api.your-domain.com`

### Option B: Railway

1. Deploy from GitHub repo
2. Set root to `apps/worker` or use Dockerfile
3. Add Postgres plugin (or use Neon externally)
4. Add Redis plugin (or use Upstash externally)
5. Two services: API (`uvicorn`) + Worker (`python -m jobs.worker`)

### Option C: Fly.io

```bash
fly launch --dockerfile infra/Dockerfile.worker
fly secrets set DATABASE_URL=... REDIS_URL=... B2_KEY_ID=...
fly deploy
```

Scale worker separately if needed.

### Required Env Vars (Backend)

```env
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
B2_KEY_ID=...
B2_APP_KEY=...
B2_BUCKET_NAME=adproof-assets
GMICLOUD_API_KEY=...
ELEVENLABS_API_KEY=...
STABILITY_API_KEY=...
# optional fallbacks
RUNWAY_API_KEY=...
LUMA_API_KEY=...
CORS_ORIGINS=https://adproof.vercel.app
```

---

## 4. PostgreSQL — Neon or Supabase

| Platform | Free Tier | Connection |
|----------|-----------|------------|
| [Neon](https://neon.tech) | 0.5 GB, serverless | `DATABASE_URL` with `?sslmode=require` |
| [Supabase](https://supabase.com) | 500 MB | Dashboard → Settings → Database URL |

### Setup

1. Create project
2. Copy connection string to `DATABASE_URL`
3. Run migrations from local or CI:

```bash
cd apps/worker
alembic upgrade head
```

---

## 5. Redis — Upstash

| Platform | Free Tier |
|----------|-----------|
| [Upstash](https://upstash.com) | 10,000 commands/day |

1. Create Redis database
2. Copy `REDIS_URL` (TLS endpoint)
3. Set in backend env vars

---

## 6. Backblaze B2

Already cloud-hosted. No deploy needed.

1. Run `infra/b2-bucket-setup.py` once with production credentials
2. Configure event notification → Vercel webhook URL
3. Verify Object Lock and lifecycle rules in B2 console

---

## 7. DNS & Custom Domains (Optional)

| Subdomain | Points To |
|-----------|-----------|
| `adproof.app` or `www` | Vercel |
| `api.adproof.app` | Render/Railway/Fly backend |

---

## 8. CI/CD Recommendations

| Trigger | Action |
|---------|--------|
| Push to `main` | Vercel auto-deploys frontend |
| Push to `main` | Render/Railway auto-deploys backend |
| PR opened | Vercel preview deployment |

Optional GitHub Actions:

```yaml
# .github/workflows/migrate.yml
on:
  push:
    branches: [main]
    paths: ['apps/worker/db/migrations/**']
jobs:
  migrate:
    runs-on: ubuntu-latest
    steps:
      - run: alembic upgrade head
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

---

## 9. Production Checklist

### Infrastructure
- [ ] Postgres provisioned (Neon/Supabase), migrations run
- [ ] Redis provisioned (Upstash)
- [ ] B2 bucket created with Object Lock, lifecycle, event notifications
- [ ] All env vars set on Vercel and backend host

### Backend
- [ ] API health check returns 200
- [ ] Worker process running and consuming queue
- [ ] ffmpeg available in container
- [ ] CORS allows Vercel domain

### Frontend
- [ ] `NEXT_PUBLIC_API_URL` points to production API
- [ ] B2 webhook route deployed and receiving events
- [ ] SSE/streaming works through Vercel

### Demo
- [ ] End-to-end: brief → pipeline → variant → verify
- [ ] Fork/replay demo ready
- [ ] README updated with live URLs

---

## 10. Cost Estimate (Hackathon / Demo)

| Service | Cost |
|---------|------|
| Vercel | Free |
| Render/Railway (hobby) | Free–$7/mo |
| Neon Postgres | Free |
| Upstash Redis | Free |
| Backblaze B2 | Free (10 GB) |
| Provider API calls | Variable (biggest cost) |

---

## 11. What NOT to Use

| Avoid | Why |
|-------|-----|
| Vercel/Netlify serverless for worker | ffmpeg timeout (10–60s limit) |
| Postgres for binary storage | Architecture principle — B2 only |
| Polling-only frontend | Use B2 webhooks → SSE for demo polish |
