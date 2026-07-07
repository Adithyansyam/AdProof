# AdProof — Genblaze Pipeline Specification

The pipeline is the core product. One Pipeline, five steps, fan-out on the expensive one.

---

## 1. Pipeline Definition

Location: `apps/worker/pipeline/ad_pipeline.py`

```python
from genblaze import Pipeline, Step
from genblaze_s3 import S3StorageBackend, ObjectStorageSink

storage = S3StorageBackend.for_backblaze("adproof-assets")
sink = ObjectStorageSink(storage)

pipeline = Pipeline(sink=sink, chain=True)

pipeline.step(
    "storyboard",
    provider="gmicloud",       # seedream-5.0-lite, fallback to flux
    fallback_models=["flux-kontext-pro", "imagen-4"],
)

pipeline.step(
    "animate",
    provider="gmicloud",       # fan out concurrently, pick best/fastest
    models=["kling-image2video-v2.1-master", "wan2.6-i2v", "pixverse-v5.6-i2v"],
    concurrent=True,
    fallback_models=["runway-gen4-turbo", "luma-ray-2"],
)

pipeline.step("voiceover", provider="elevenlabs", fallback_models=["nvidia-magpie-tts"])
pipeline.step("score", provider="stability-audio", fallback_models=["gmicloud-minimax"])
pipeline.step("compose", type="ffmpeg")  # built-in compose/upscale step
```

---

## 2. Step Breakdown

| Step | Input | Output | Provider(s) | Notes |
|------|-------|--------|-------------|-------|
| `storyboard` | Brief text (+ optional ref image) | Keyframe PNG(s) | GMI Cloud (Seedream), fallback FLUX/Imagen | Text → visual plan |
| `animate` | Keyframe image | Video clip(s) | Kling, Wan, Pixverse (concurrent); fallback Runway, Luma | **Fan-out** — run all models in parallel |
| `voiceover` | Brief text / script | MP3 audio | ElevenLabs, fallback NVIDIA Magpie TTS | Narration |
| `score` | Brief mood/style | Background music MP3 | Stability Audio, fallback MiniMax | Background score |
| `compose` | Video + voiceover + score | Final MP4 | ffmpeg (built-in) | Assembly, upscale if needed |

---

## 3. Step Modules

Each step lives in `apps/worker/pipeline/steps/`:

```
steps/
├── storyboard.py    # text -> keyframes (Seedream/FLUX/Imagen)
├── animate.py       # image -> video, concurrent fan-out
├── voiceover.py     # ElevenLabs / NVIDIA Magpie TTS
├── score.py         # Stability Audio / MiniMax
└── compose.py       # ffmpeg final assembly
```

### `storyboard.py`

- Input: `brief_text`, optional `reference_image_key` from B2
- Output: PNG keyframe(s) uploaded to `runs/{run_id}/steps/storyboard/{step_id}.png`
- Writes: `{step_id}.manifest.json` alongside

### `animate.py`

- Input: storyboard PNG
- **Concurrent fan-out** across `models` list
- Each model branch produces its own clip under `runs/{run_id}/steps/animate/{model_name}/{step_id}.mp4`
- On stall/timeout: `fallback_models` chain kicks in
- Best/fastest result selected for compose (or all become separate variants)

### `voiceover.py`

- Input: script derived from brief
- Output: `runs/{run_id}/steps/voiceover/{step_id}.mp3`

### `score.py`

- Input: mood/style from brief
- Output: `runs/{run_id}/steps/score/{step_id}.mp3`

### `compose.py`

- Input: animate clip + voiceover + score
- Output: `runs/{run_id}/variants/{variant_id}/final.mp4`
- Uses ffmpeg — requires long-running worker process

---

## 4. Fallback Configuration

`apps/worker/pipeline/fallback_config.py` — centralized fallback chains per step.

```python
FALLBACK_CHAINS = {
    "storyboard": ["flux-kontext-pro", "imagen-4"],
    "animate": ["runway-gen4-turbo", "luma-ray-2"],
    "voiceover": ["nvidia-magpie-tts"],
    "score": ["gmicloud-minimax"],
}
```

When fallback triggers:

- `run_steps.fallback_triggered = True`
- `run_steps.status = 'fallback_used'`
- Manifest records original attempt + fallback provider

**Demo value:** Show judges a run where one provider stalls, fallback kicks in, manifest records exactly what happened.

---

## 5. Manifests (Per Run)

Every run produces:

| Manifest | Location | Purpose |
|----------|----------|---------|
| Per-step | `runs/{run_id}/steps/{step}/{step_id}.manifest.json` | SHA-256 of step output, provider, model, latency |
| Run-level | `runs/{run_id}/run.manifest.json` | References all step manifests |
| Variant (rolled-up) | `runs/{run_id}/variants/{variant_id}/manifest.json` | Final asset hash, full provenance chain |

All `*.manifest.json` files have **B2 Object Lock** (governance mode, 30-day minimum retention).

---

## 6. Provenance & Replay

Every run:

1. Writes SHA-256 manifest per step + rolled-up manifest for final asset
2. Carries `parent_run_id` in DB for fork traceability
3. Is replayable via `genblaze replay manifest.json`

### Replay

```bash
genblaze replay runs/{run_id}/run.manifest.json
```

Wrapped in `apps/worker/manifest/replay.py` → `POST /runs/{id}/replay`.

### Fork

Same as replay but with one step's provider/model overridden → `POST /runs/{id}/fork`.

---

## 7. Isolation Testing (No API)

```bash
cd apps/worker
python -m pipeline.ad_pipeline \
  --brief "30-sec ad for cold brew brand, upbeat, TikTok-native" \
  --brand "ColdBrew Co"
```

Expected output:

- One variant MP4 in B2
- All manifests in correct key layout
- `run.manifest.json` at `runs/{run_id}/run.manifest.json`

---

## 8. Provider API Keys

| Provider | Env Var | Steps |
|----------|---------|-------|
| GMI Cloud | `GMICLOUD_API_KEY` | storyboard, animate, score fallback |
| OpenAI | `OPENAI_API_KEY` | optional |
| ElevenLabs | `ELEVENLABS_API_KEY` | voiceover |
| Stability AI | `STABILITY_API_KEY` | score |
| Runway | `RUNWAY_API_KEY` | animate fallback (optional) |
| Luma | `LUMA_API_KEY` | animate fallback (optional) |

---

## 9. Cost Tracking

Each step reports `cost_usd` from provider billing metadata. Aggregated into `runs.total_cost_usd` on completion. Surfaced in frontend via `CostBadge`.

---

## 10. Logging

Pipeline logs written to B2: `logs/{run_id}/pipeline.log`

Includes: step start/end, provider selection, fallback events, errors.
