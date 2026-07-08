"""API key validation and masked logging for provider calls."""

import logging
import os

from config import get_settings

logger = logging.getLogger("adproof.pipeline")

REQUIRED_LIVE_KEYS = {
    "gmicloud": ("GMICLOUD_API_KEY", "GMI_API_KEY"),
    "b2": ("B2_KEY_ID", "B2_APP_KEY"),
    "elevenlabs": ("ELEVENLABS_API_KEY",),
}


def _first_env(*names: str) -> str:
    for name in names:
        val = os.environ.get(name, "").strip()
        if val:
            return val
    settings = get_settings()
    mapping = {
        "GMICLOUD_API_KEY": getattr(settings, "gmicloud_api_key", ""),
        "GMI_API_KEY": getattr(settings, "gmicloud_api_key", ""),
        "B2_KEY_ID": settings.b2_key_id,
        "B2_APP_KEY": settings.b2_app_key,
        "ELEVENLABS_API_KEY": getattr(settings, "elevenlabs_api_key", ""),
        "STABILITY_API_KEY": getattr(settings, "stability_api_key", ""),
    }
    for name in names:
        val = str(mapping.get(name, "")).strip()
        if val:
            return val
    return ""


def mask_key(key: str) -> str:
    if not key:
        return "<missing>"
    if len(key) <= 8:
        return "****"
    return f"{key[:4]}...{key[-4:]}"


def log_key_usage(provider: str, *env_names: str) -> str:
    key = _first_env(*env_names)
    logger.info("Provider %s using key %s", provider, mask_key(key))
    return key


def require_live_keys() -> dict[str, str]:
    """Validate all keys required for live mode. Raises RuntimeError if any missing."""
    resolved: dict[str, str] = {}
    missing: list[str] = []

    gmi = _first_env("GMICLOUD_API_KEY", "GMI_API_KEY")
    if not gmi:
        missing.append("GMICLOUD_API_KEY")
    else:
        resolved["gmicloud"] = gmi

    b2_id = _first_env("B2_KEY_ID")
    b2_key = _first_env("B2_APP_KEY")
    if not b2_id or not b2_key:
        missing.append("B2_KEY_ID/B2_APP_KEY")
    else:
        resolved["b2_key_id"] = b2_id
        resolved["b2_app_key"] = b2_key

    el = _first_env("ELEVENLABS_API_KEY")
    if not el:
        missing.append("ELEVENLABS_API_KEY")
    else:
        resolved["elevenlabs"] = el

    stability = _first_env("STABILITY_API_KEY")
    if not stability:
        missing.append("STABILITY_API_KEY")
    else:
        resolved["stability"] = stability

    if missing:
        raise RuntimeError(
            f"LIVE pipeline mode requires API keys: {', '.join(missing)}. "
            "Set PIPELINE_MODE=mock for local demo without provider calls."
        )
    return resolved
