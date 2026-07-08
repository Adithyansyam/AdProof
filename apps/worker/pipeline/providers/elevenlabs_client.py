"""ElevenLabs TTS — direct REST API."""

import logging
import time

import httpx

from pipeline.keys import log_key_usage

logger = logging.getLogger("adproof.elevenlabs")

DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel


class ElevenLabsClient:
    def __init__(self, api_key: str | None = None, voice_id: str = DEFAULT_VOICE_ID):
        self.api_key = api_key or log_key_usage("elevenlabs", "ELEVENLABS_API_KEY")
        if not self.api_key:
            raise RuntimeError("ELEVENLABS_API_KEY is required for live voiceover step")
        self.voice_id = voice_id
        self._headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }

    def text_to_speech(self, text: str) -> tuple[bytes, dict]:
        start = time.monotonic()
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        with httpx.Client(timeout=120) as client:
            resp = client.post(
                url,
                headers=self._headers,
                json={
                    "text": text,
                    "model_id": "eleven_multilingual_v2",
                },
            )
            resp.raise_for_status()
            audio = resp.content
        latency_ms = int((time.monotonic() - start) * 1000)
        logger.info("ElevenLabs TTS %d bytes latency_ms=%d", len(audio), latency_ms)
        meta = {
            "voice_id": self.voice_id,
            "model": "eleven_multilingual_v2",
            "latency_ms": latency_ms,
            "character_count": len(text),
        }
        return audio, meta
