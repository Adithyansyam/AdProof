"""Build provenance manifest JSON for pipeline steps and variants."""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_step_manifest(
    *,
    run_id: str,
    step_id: str,
    step_name: str,
    provider: str,
    model: str,
    asset_bytes: bytes,
    fallback_triggered: bool = False,
    parent_manifest: dict | None = None,
    extra: dict | None = None,
) -> dict[str, Any]:
    manifest = {
        "version": "1.0",
        "type": "adproof-step-manifest",
        "run_id": run_id,
        "step_id": step_id,
        "step_name": step_name,
        "provider": provider,
        "model": model,
        "sha256": sha256_hex(asset_bytes),
        "fallback_triggered": fallback_triggered,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if parent_manifest:
        manifest["parent_manifest_sha256"] = sha256_hex(
            json.dumps(parent_manifest, sort_keys=True).encode()
        )
    if extra:
        manifest.update(extra)
    return manifest


def build_run_manifest(*, run_id: str, step_manifests: list[dict]) -> dict[str, Any]:
    return {
        "version": "1.0",
        "type": "adproof-run-manifest",
        "run_id": run_id,
        "steps": step_manifests,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def build_variant_manifest(
    *,
    run_id: str,
    variant_id: str,
    final_bytes: bytes,
    run_manifest: dict,
    provider_summary: str,
) -> dict[str, Any]:
    return {
        "version": "1.0",
        "type": "adproof-variant-manifest",
        "run_id": run_id,
        "variant_id": variant_id,
        "sha256": sha256_hex(final_bytes),
        "provider_summary": provider_summary,
        "run_manifest": run_manifest,
        "replayable": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
