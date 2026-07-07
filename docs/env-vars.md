# AdProof — Environment Variables Reference

All environment variables needed for local dev and production.

---

## Backend (`apps/worker/.env` or host env)

### Database

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | `postgresql://adproof:adproof@localhost:5432/adproof` | Postgres connection string |

### Redis / Job Queue

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `REDIS_URL` | Yes | `redis://localhost:6379/0` | Redis for job queue |

### Backblaze B2

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `B2_KEY_ID` | Yes | — | B2 application key ID |
| `B2_APP_KEY` | Yes | — | B2 application key |
| `B2_BUCKET_NAME` | Yes | `adproof-assets` | Target bucket name |
| `B2_ENDPOINT` | No | `https://s3.us-west-004.backblazeb2.com` | S3-compatible endpoint (region-specific) |

### AI Providers

| Variable | Required | Steps | Description |
|----------|----------|-------|-------------|
| `GMICLOUD_API_KEY` | Yes | storyboard, animate, score fallback | GMI Cloud (Seedream, Kling, etc.) |
| `OPENAI_API_KEY` | No | optional | OpenAI models if needed |
| `ELEVENLABS_API_KEY` | Yes | voiceover | ElevenLabs TTS |
| `STABILITY_API_KEY` | Yes | score | Stability Audio |
| `RUNWAY_API_KEY` | No | animate fallback | Runway Gen-4 Turbo |
| `LUMA_API_KEY` | No | animate fallback | Luma Ray 2 |

### App Config

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `CORS_ORIGINS` | No | `http://localhost:3000,https://adproof.vercel.app` | Allowed frontend origins |
| `B2_WEBHOOK_URL` | No | `https://adproof.vercel.app/api/webhooks/b2` | For b2-bucket-setup.py |

---

## Frontend (`apps/web/.env.local`)

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | `http://localhost:8000` | Backend API base URL |
| `B2_WEBHOOK_SECRET` | No | — | Validate incoming B2 webhook requests |

---

## Local Defaults (Docker Compose)

When using `infra/docker-compose.yml`:

```env
DATABASE_URL=postgresql://adproof:adproof@localhost:5432/adproof
REDIS_URL=redis://localhost:6379/0
```

---

## Production Notes

- Never commit `.env` files — use host secret managers (Vercel env, Render secrets, etc.)
- `NEXT_PUBLIC_*` vars are exposed to the browser — never put secrets there
- B2 keys and provider API keys are backend-only
