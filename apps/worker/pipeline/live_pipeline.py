"""Live pipeline — real provider HTTP calls, no silent fallback."""

import logging
import uuid
from typing import Callable

from manifest.builder import (
    build_run_manifest,
    build_step_manifest,
    build_variant_manifest,
    sha256_hex,
)
from pipeline.providers.stability_client import StabilityAudioClient
from storage.b2_client import StorageClient
from storage.key_layout import (
    run_manifest_key,
    step_asset_key,
    step_manifest_key,
    variant_final_key,
    variant_manifest_key,
    variant_thumbnail_key,
)

logger = logging.getLogger("adproof.live_pipeline")

STORYBOARD_MODEL = "seedream-5.0-lite"
ANIMATE_MODEL = "kling-image2video-v2.1-master"


def _upload_step(
    storage: StorageClient,
    run_id: str,
    step_name: str,
    step_id: str,
    ext: str,
    data: bytes,
    content_type: str,
    model: str | None = None,
) -> tuple[str, str]:
    asset_key = step_asset_key(run_id, step_name, step_id, ext, model)
    manifest_key = step_manifest_key(run_id, step_name, step_id, model)
    storage.upload(asset_key, data, content_type, object_lock=False)
    return asset_key, manifest_key


def run_live_pipeline(
    *,
    brief_id: str,
    run_id: str,
    brief_text: str,
    brand_name: str,
    storage: StorageClient,
    on_step_complete: Callable[[dict], None],
    fork_override: dict | None = None,
) -> dict:
    keys = require_live_keys()
    if not storage.uses_b2:
        raise RuntimeError(
            "LIVE pipeline requires B2 credentials (B2_KEY_ID, B2_APP_KEY). "
            "Artifacts must land in Backblaze B2 for production readiness."
        )

    gmi = GMICloudClient(api_key=keys["gmicloud"])
    eleven = ElevenLabsClient(api_key=keys["elevenlabs"])
    stability = StabilityAudioClient(api_key=keys["stability"])

    animate_model = ANIMATE_MODEL
    if fork_override and "animate" in fork_override:
        animate_model = fork_override["animate"].get("model", animate_model)

    step_manifests: list[dict] = []
    total_cost = 0.0
    storyboard_prompt = f"{brand_name}: {brief_text}"

    # --- storyboard (real GMI image) ---
    step_id = str(uuid.uuid4())
    png, gmi_meta = gmi.run_image(STORYBOARD_MODEL, storyboard_prompt)
    asset_key, manifest_key = _upload_step(
        storage, run_id, "storyboard", step_id, "png", png, "image/png"
    )
    manifest = build_step_manifest(
        run_id=run_id,
        step_id=step_id,
        step_name="storyboard",
        provider="gmicloud",
        model=STORYBOARD_MODEL,
        asset_bytes=png,
        extra={
            "pipeline_mode": "live",
            "provider_metadata": gmi_meta,
            "brief_id": brief_id,
        },
    )
    storage.upload_json(manifest_key, manifest, object_lock=True)
    step_manifests.append(manifest)
    on_step_complete(
        {
            "step_name": "storyboard",
            "provider": "gmicloud",
            "model": STORYBOARD_MODEL,
            "status": "succeeded",
            "fallback_triggered": False,
            "cost_usd": None,
            "latency_ms": gmi_meta["latency_ms"],
            "manifest_key": manifest_key,
            "asset_key": asset_key,
        }
    )

    # --- animate (real GMI image-to-video) ---
    step_id = str(uuid.uuid4())
    image_public_url = gmi.upload_bytes(png, "png")
    mp4, anim_meta = gmi.run_image_to_video(
        animate_model,
        f"Animate this ad scene: {brief_text}",
        image_public_url,
    )
    asset_key, manifest_key = _upload_step(
        storage, run_id, "animate", step_id, "mp4", mp4, "video/mp4", animate_model
    )
    manifest = build_step_manifest(
        run_id=run_id,
        step_id=step_id,
        step_name="animate",
        provider="gmicloud",
        model=animate_model,
        asset_bytes=mp4,
        extra={
            "pipeline_mode": "live",
            "provider_metadata": anim_meta,
            "input_image_url": image_public_url,
        },
    )
    storage.upload_json(manifest_key, manifest, object_lock=True)
    step_manifests.append(manifest)
    on_step_complete(
        {
            "step_name": "animate",
            "provider": "gmicloud",
            "model": animate_model,
            "status": "succeeded",
            "fallback_triggered": False,
            "cost_usd": None,
            "latency_ms": anim_meta["latency_ms"],
            "manifest_key": manifest_key,
            "asset_key": asset_key,
        }
    )

    # --- voiceover (real ElevenLabs) ---
    step_id = str(uuid.uuid4())
    vo_script = f"{brand_name}. {brief_text}"
    audio, vo_meta = eleven.text_to_speech(vo_script)
    asset_key, manifest_key = _upload_step(
        storage, run_id, "voiceover", step_id, "mp3", audio, "audio/mpeg"
    )
    manifest = build_step_manifest(
        run_id=run_id,
        step_id=step_id,
        step_name="voiceover",
        provider="elevenlabs",
        model="eleven_multilingual_v2",
        asset_bytes=audio,
        extra={"pipeline_mode": "live", "provider_metadata": vo_meta},
    )
    storage.upload_json(manifest_key, manifest, object_lock=True)
    step_manifests.append(manifest)
    on_step_complete(
        {
            "step_name": "voiceover",
            "provider": "elevenlabs",
            "model": "eleven_multilingual_v2",
            "status": "succeeded",
            "fallback_triggered": False,
            "cost_usd": None,
            "latency_ms": vo_meta["latency_ms"],
            "manifest_key": manifest_key,
            "asset_key": asset_key,
        }
    )

    # --- score (real Stability) ---
    step_id = str(uuid.uuid4())
    score, score_meta = stability.generate_music(f"Background music for: {brief_text}")
    score_provider = "stability-audio"
    score_model = "stable-audio-2"
    asset_key, manifest_key = _upload_step(
        storage, run_id, "score", step_id, "mp3", score, "audio/mpeg"
    )
    manifest = build_step_manifest(
        run_id=run_id,
        step_id=step_id,
        step_name="score",
        provider=score_provider,
        model=score_model,
        asset_bytes=score,
        extra={"pipeline_mode": "live", "provider_metadata": score_meta},
    )
    storage.upload_json(manifest_key, manifest, object_lock=True)
    step_manifests.append(manifest)
    on_step_complete(
        {
            "step_name": "score",
            "provider": score_provider,
            "model": score_model,
            "status": "succeeded",
            "fallback_triggered": False,
            "cost_usd": None,
            "latency_ms": score_meta["latency_ms"],
            "manifest_key": manifest_key,
            "asset_key": asset_key,
        }
    )

    # --- compose (real ffmpeg) ---
    import time

    step_id = str(uuid.uuid4())
    t0 = time.monotonic()
    final_bytes = compose_video(mp4, audio, score)
    compose_latency = int((time.monotonic() - t0) * 1000)

    variant_id = str(uuid.uuid4())
    final_key = variant_final_key(run_id, variant_id)
    thumb_key = variant_thumbnail_key(run_id, variant_id)
    thumb_bytes = extract_thumbnail(final_bytes)

    storage.upload(final_key, final_bytes, "video/mp4")
    storage.upload(thumb_key, thumb_bytes, "image/jpeg")

    run_man = build_run_manifest(run_id=run_id, step_manifests=step_manifests)
    run_man["pipeline_mode"] = "live"
    storage.upload_json(run_manifest_key(run_id), run_man, object_lock=True)

    provider_summary = f"{animate_model.split('-')[0]} + elevenlabs + {score_provider}"
    variant_man = build_variant_manifest(
        run_id=run_id,
        variant_id=variant_id,
        final_bytes=final_bytes,
        run_manifest=run_man,
        provider_summary=provider_summary,
    )
    variant_man["pipeline_mode"] = "live"
    var_manifest_key = variant_manifest_key(run_id, variant_id)
    storage.upload_json(var_manifest_key, variant_man, object_lock=True)

    compose_manifest_key = step_manifest_key(run_id, "compose", step_id)
    compose_manifest = build_step_manifest(
        run_id=run_id,
        step_id=step_id,
        step_name="compose",
        provider="ffmpeg",
        model="compose",
        asset_bytes=final_bytes,
        extra={"pipeline_mode": "live", "latency_ms": compose_latency},
    )
    storage.upload_json(compose_manifest_key, compose_manifest, object_lock=True)
    on_step_complete(
        {
            "step_name": "compose",
            "provider": "ffmpeg",
            "model": "compose",
            "status": "succeeded",
            "fallback_triggered": False,
            "cost_usd": None,
            "latency_ms": compose_latency,
            "manifest_key": compose_manifest_key,
            "asset_key": final_key,
        }
    )

    final_hash = sha256_hex(final_bytes)
    logger.info("Live pipeline complete run_id=%s sha256=%s", run_id, final_hash)

    return {
        "variant_id": variant_id,
        "asset_key": final_key,
        "thumbnail_key": thumb_key,
        "manifest_key": var_manifest_key,
        "sha256_hash": final_hash,
        "provider_summary": provider_summary,
        "total_cost_usd": str(total_cost) if total_cost else None,
        "pipeline_mode": "live",
    }
