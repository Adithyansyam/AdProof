"""Manifest verification — re-compute SHA-256 and compare with manifest claim."""


def verify_run(run_id: str) -> dict:
    """Download manifest + final asset from B2, verify SHA-256 match."""
    raise NotImplementedError
