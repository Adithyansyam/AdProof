"""Application configuration."""

import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./adproof_local.db"
    redis_url: str = "redis://localhost:6379/0"
    b2_key_id: str = ""
    b2_app_key: str = ""
    b2_bucket_name: str = "adproof-assets"
    b2_endpoint: str = "https://s3.us-west-004.backblazeb2.com"
    cors_origins: str = "http://localhost:3000"
    demo_mode: bool = True
    local_storage_path: str = "./local_storage"
    demo_user_email: str = "demo@adproof.local"
    api_base_url: str = "http://localhost:8000"
    use_rq_worker: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def has_b2_credentials(self) -> bool:
        return bool(self.b2_key_id and self.b2_app_key)

    @property
    def effective_demo_mode(self) -> bool:
        if os.environ.get("ADPROOF_DEMO_MODE", "").lower() in ("1", "true", "yes"):
            return True
        if self.demo_mode and not self.has_b2_credentials:
            return True
        return self.demo_mode


@lru_cache
def get_settings() -> Settings:
    return Settings()
