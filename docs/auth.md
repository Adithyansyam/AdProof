# Authentication

AdProof uses **Supabase Auth (Google OAuth)** on the frontend and **JWT bearer tokens** on the API. Each user's briefs, runs, library items, and activity events are isolated by `user_id`.

## Two databases people confuse

| Store | What you see | Who writes it |
|-------|--------------|---------------|
| **Supabase Auth** (`auth.users`) | OAuth user id / email after Google login | Supabase Auth (automatic) |
| **App DB** (`public.users`, `briefs`, `runs`, `user_activities`) | Profiles, briefs, pipeline runs, activity log | AdProof API via `DATABASE_URL` |

If `DATABASE_URL` is SQLite (local default) or silently not pointed at Supabase Postgres, you will see the OAuth identity in Supabase Auth **but no briefs/activities in the Supabase Table Editor**. Point `DATABASE_URL` at your Supabase connection string and run `infra/supabase-schema.sql`.

## Flow

1. User clicks **Sign in with Google** on `/login` or `/signup`.
2. Supabase completes the Google OAuth flow.
3. Frontend calls `POST /auth/supabase` to upsert `public.users` and insert a `login` row in `user_activities`.
4. API returns a JWT (`access_token`) stored in the browser session.
5. Mutating actions (`brief.create`, `run.fork`, `run.replay`, `run.verify`) insert into `user_activities`.
6. FastAPI scopes all queries to the authenticated `user_id`.

## Environment variables

| Variable | Where | Purpose |
|----------|-------|---------|
| `NEXT_PUBLIC_SUPABASE_URL` | Vercel / `apps/web` | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Vercel / `apps/web` | Supabase anon / publishable key |
| `NEXTAUTH_SECRET` | Vercel / `apps/web` | Shared secret helper |
| `NEXTAUTH_URL` | Vercel / `apps/web` | Public app URL |
| `AUTH_JWT_SECRET` | Backend API | Signs API JWTs |
| `DATABASE_URL` | Backend API | **Must** be Supabase Postgres URI for data to appear in Supabase |

## Activity tracking

| Action | When |
|--------|------|
| `login` | `POST /auth/supabase` |
| `brief.create` | User submits a brief |
| `run.replay` | Replay button |
| `run.fork` | Fork with model override |
| `run.verify` | Manifest verify |

List activities: `GET /auth/activities` (bearer token required).

## Protected routes

**Frontend (middleware):** `/dashboard`, `/brief/*`, `/library`, `/run/*`

**Backend:** `POST /briefs`, `GET /briefs`, `GET /briefs/:id`, all `/runs/*`, `GET /library`, `GET /auth/activities`

Public: `GET /health`, `POST /auth/supabase`, static assets.

## Local setup checklist

1. Set Supabase keys in `apps/web/.env.local` (see `.env.example`).
2. Set `AUTH_JWT_SECRET` in root `.env` or `start-api.bat`.
3. Optional (production data in Supabase): set `DATABASE_URL` to Supabase Postgres and run `infra/supabase-schema.sql`.
4. Restart API and web. Verify with:
   - `python scripts/inspect_app_db.py`
   - `python scripts/test_user_activity.py` (API must be running)
5. Sign in at http://localhost:3000/login — dashboard shows only your briefs.
