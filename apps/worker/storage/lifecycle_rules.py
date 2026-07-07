"""B2 lifecycle rules — see docs/b2-storage.md."""

LIFECYCLE_RULES = [
    {
        "id": "delete-intermediate-steps",
        "prefix": "runs/",
        "tag_filter": "steps/",
        "days": 7,
        "action": "delete",
        "description": "Auto-delete intermediate pipeline artifacts after 7 days",
    },
]


def ensure_configured(client) -> None:
    """Apply lifecycle rules to the B2 bucket. Called on boot or via b2-bucket-setup.py."""
    raise NotImplementedError("Wire up B2 lifecycle API via boto3")
