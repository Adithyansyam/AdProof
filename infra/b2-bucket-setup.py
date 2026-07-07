#!/usr/bin/env python3
"""
One-time Backblaze B2 bucket setup for AdProof.

Creates bucket, configures:
  - Object Lock on *.manifest.json (governance, 30-day retention)
  - Lifecycle rules (delete runs/*/steps/ after 7 days)
  - Event notifications on variants/*/final.mp4 PUT

Usage:
    python infra/b2-bucket-setup.py

Requires B2_KEY_ID, B2_APP_KEY, B2_BUCKET_NAME in environment or .env.
"""

import os
import sys


def load_env():
    """Load .env from repo root if present."""
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    os.environ.setdefault(key.strip(), val.strip())


def main():
    load_env()

    key_id = os.environ.get("B2_KEY_ID")
    app_key = os.environ.get("B2_APP_KEY")
    bucket_name = os.environ.get("B2_BUCKET_NAME", "adproof-assets")
    webhook_url = os.environ.get("B2_WEBHOOK_URL", "")

    if not key_id or not app_key:
        print("ERROR: Set B2_KEY_ID and B2_APP_KEY in .env")
        sys.exit(1)

    print(f"Setting up B2 bucket: {bucket_name}")
    print()
    print("TODO: Implement with boto3 / B2 SDK:")
    print("  1. Create bucket with Object Lock enabled")
    print("  2. Set lifecycle rule: delete runs/*/steps/** after 7 days")
    print("  3. Set Object Lock default retention: governance, 30 days")
    print("  4. Configure event notification:")
    if webhook_url:
        print(f"     → {webhook_url}")
    else:
        print("     → Set B2_WEBHOOK_URL in .env first")
    print()
    print("See docs/b2-storage.md for full specification.")


if __name__ == "__main__":
    main()
