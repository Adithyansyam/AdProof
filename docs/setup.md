# AdProof — Project Setup

Local development guide for teammates.

---

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | 20+ | Next.js frontend |
| Python | 3.11+ | FastAPI worker + Genblaze |
| Docker & Docker Compose | Latest | Postgres + Redis locally |
| ffmpeg | Latest | Compose step (install on host or use Docker) |
| Backblaze B2 account | — | Object storage (free tier: 10 GB) |
| Genblaze / provider API keys | — | See `.env.example` |

---

## 1. Clone & Environment

```bash
git clone <repo-url> adproof
cd adproof
cp .env.example .env
# Fill in all values in .env (see docs/env-vars.md)
```

---

## 2. Start Infrastructure (Postgres + Redis)

```bash
cd infra
docker compose up -d
```

This starts:

- **Postgres** on `localhost:5432` (user: `adproof`, db: `adproof`)
- **Redis** on `localhost:6379`

Verify:

```bash
docker compose ps
```

---

## 3. Backblaze B2 Bucket Setup (One-Time)

```bash
# From repo root, with B2 credentials in .env
python infra/b2-bucket-setup.py
```

This script:

1. Creates bucket `adproof-assets` (or name from `B2_BUCKET_NAME`)
2. Configures lifecycle rules (delete `runs/*/steps/` after 7 days)
3. Enables Object Lock on `*.manifest.json` (governance mode, 30-day retention)
4. Configures event notifications on `variants/*/final.mp4` PUT

See [b2-storage.md](./b2-storage.md) for key layout details.

---

## 4. Database Migrations

```bash
cd apps/worker
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run Alembic migrations
alembic upgrade head
```

---

## 5. Start the Worker (FastAPI + Job Consumer)

Terminal 1 — API server:

```bash
cd apps/worker
source .venv/bin/activate
uvicorn main:app --reload --port 8000
```

Terminal 2 — Job worker:

```bash
cd apps/worker
source .venv/bin/activate
python -m jobs.worker
```

API available at `http://localhost:8000`. OpenAPI docs at `http://localhost:8000/docs`.

---

## 6. Start the Frontend

```bash
cd apps/web
npm install
npm run dev
```

Frontend at `http://localhost:3000`.

Set in `apps/web/.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 7. Run Pipeline in Isolation (No API)

Useful for testing Genblaze + B2 without the full stack:

```bash
cd apps/worker
python -m pipeline.ad_pipeline --brief "30-sec ad for cold brew brand, upbeat, TikTok-native"
```

One brief in → one variant out, manifests landing in B2 with correct key layout.

---

## 8. Verify the Stack

| Check | Command / URL |
|-------|---------------|
| API health | `curl http://localhost:8000/health` |
| Postgres | `docker compose exec postgres psql -U adproof -c '\dt'` |
| Redis | `docker compose exec redis redis-cli ping` |
| Frontend | Open `http://localhost:3000` |
| B2 upload | Run pipeline isolation script, check B2 console |

---

## 9. Project Layout Quick Reference

```
apps/web/          → Next.js frontend
apps/worker/       → FastAPI + Genblaze pipeline + job worker
packages/shared-types/  → Shared TypeScript types
infra/             → Docker Compose, Dockerfile, B2 setup script
docs/              → All team documentation
```

---

## 10. Common Issues

| Problem | Fix |
|---------|-----|
| `DATABASE_URL` connection refused | Ensure `docker compose up -d` is running |
| B2 upload 403 | Check `B2_KEY_ID` and `B2_APP_KEY` in `.env` |
| ffmpeg not found | Install ffmpeg or run worker inside Docker (`Dockerfile.worker`) |
| Provider timeout on animate | Fallback should kick in — check `run_steps.fallback_triggered` in DB |
| Frontend can't reach API | Confirm `NEXT_PUBLIC_API_URL` and CORS settings in `main.py` |

---

## Next Steps

- Read [build-order.md](./build-order.md) for implementation sequence
- Read [deployment.md](./deployment.md) before going to production
- See [frontend-spec.md](./frontend-spec.md) and [backend-spec.md](./backend-spec.md) for feature specs
