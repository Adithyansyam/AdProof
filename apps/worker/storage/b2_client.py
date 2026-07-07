"""Backblaze B2 client wrapper — uses genblaze_s3 when available."""

import os

BUCKET_NAME = os.environ.get("B2_BUCKET_NAME", "adproof-assets")


class B2Client:
    """S3-compatible B2 storage client.

    TODO: Replace with genblaze_s3.S3StorageBackend.for_backblaze() when SDK is installed.
    """

    def __init__(self, bucket_name: str = BUCKET_NAME):
        self.bucket_name = bucket_name

    def upload(self, key: str, data: bytes, content_type: str, object_lock: bool = False):
        raise NotImplementedError("Wire up boto3 or genblaze_s3")

    def download(self, key: str) -> bytes:
        raise NotImplementedError("Wire up boto3 or genblaze_s3")

    def signed_url(self, key: str, expires_in: int = 3600) -> str:
        raise NotImplementedError("Wire up boto3 or genblaze_s3")

    def delete(self, key: str):
        raise NotImplementedError("Wire up boto3 or genblaze_s3")
