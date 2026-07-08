"""ffmpeg compose and thumbnail extraction from real video bytes."""

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger("adproof.ffmpeg")


def _require_ffmpeg() -> str:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required for compose step in live pipeline mode")
    return ffmpeg


def compose_video(
    video_bytes: bytes,
    voiceover_bytes: bytes,
    score_bytes: bytes,
) -> bytes:
    ffmpeg = _require_ffmpeg()
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        video_path = tmp_path / "video.mp4"
        vo_path = tmp_path / "voiceover.mp3"
        score_path = tmp_path / "score.mp3"
        out_path = tmp_path / "final.mp4"

        video_path.write_bytes(video_bytes)
        vo_path.write_bytes(voiceover_bytes)
        score_path.write_bytes(score_bytes)

        cmd = [
            ffmpeg,
            "-y",
            "-i",
            str(video_path),
            "-i",
            str(vo_path),
            "-i",
            str(score_path),
            "-filter_complex",
            "[1:a][2:a]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map",
            "0:v",
            "-map",
            "[aout]",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-shortest",
            str(out_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("ffmpeg compose failed: %s", result.stderr)
            raise RuntimeError(f"ffmpeg compose failed: {result.stderr[:500]}")
        return out_path.read_bytes()


def extract_thumbnail(video_bytes: bytes, timestamp: str = "00:00:01") -> bytes:
    ffmpeg = _require_ffmpeg()
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        video_path = tmp_path / "video.mp4"
        thumb_path = tmp_path / "thumbnail.jpg"
        video_path.write_bytes(video_bytes)

        cmd = [
            ffmpeg,
            "-y",
            "-i",
            str(video_path),
            "-ss",
            timestamp,
            "-vframes",
            "1",
            "-q:v",
            "2",
            str(thumb_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("ffmpeg thumbnail failed: %s", result.stderr)
            raise RuntimeError(f"ffmpeg thumbnail failed: {result.stderr[:500]}")
        return thumb_path.read_bytes()
