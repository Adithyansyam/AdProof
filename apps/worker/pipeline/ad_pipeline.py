"""Genblaze pipeline definition — see docs/pipeline.md."""

FALLBACK_CHAINS = {
    "storyboard": ["flux-kontext-pro", "imagen-4"],
    "animate": ["runway-gen4-turbo", "luma-ray-2"],
    "voiceover": ["nvidia-magpie-tts"],
    "score": ["gmicloud-minimax"],
}

PIPELINE_STEPS = [
    {
        "name": "storyboard",
        "provider": "gmicloud",
        "fallback_models": FALLBACK_CHAINS["storyboard"],
    },
    {
        "name": "animate",
        "provider": "gmicloud",
        "models": [
            "kling-image2video-v2.1-master",
            "wan2.6-i2v",
            "pixverse-v5.6-i2v",
        ],
        "concurrent": True,
        "fallback_models": FALLBACK_CHAINS["animate"],
    },
    {
        "name": "voiceover",
        "provider": "elevenlabs",
        "fallback_models": FALLBACK_CHAINS["voiceover"],
    },
    {
        "name": "score",
        "provider": "stability-audio",
        "fallback_models": FALLBACK_CHAINS["score"],
    },
    {"name": "compose", "type": "ffmpeg"},
]


def run_pipeline(brief_id: str, run_id: str, brief_text: str, **kwargs):
    """Execute the full ad pipeline. TODO: wire up Genblaze SDK."""
    raise NotImplementedError("Implement with genblaze Pipeline")
