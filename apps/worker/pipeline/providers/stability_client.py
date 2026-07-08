"""Stability AI audio generation — direct REST API."""

import logging
import time

import httpx

from pipeline.keys import log_key_usage

logger = logging.getLogger("adproof.stability")


class StabilityAudioClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or log_key_usage("stability", "STABILITY_API_KEY")
        if not self.api_key:
            raise RuntimeError("STABILITY_API_KEY is required for live score step")
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "audio/mpeg",
        }

    def generate_music(self, prompt: str, duration_sec: int = 10) -> tuple[bytes, dict]:
        start = time.monotonic()
        url = "https://api.stability.ai/v2beta/audio/stable-audio-2/text-to-audio"
        with httpx.Client(timeout=180) as client:
            resp = client.post(
                url,
                headers=self._headers,
                data={
                    "prompt": prompt,
                    "duration": str(duration_sec),
                    "output_format": "mp3",
                },
            )
            resp.raise_for_status()
            audio = resp.content
        latency_ms = int((time.monotonic() - start) * 1000)
        logger.info("Stability audio %d bytes latency_ms=%d", len(audio), latency_ms)
        meta = {
            "model": "stable-audio-2",
            "latency_ms": latency_ms,
            "duration_sec": duration_sec,
        }
        return audio, meta
