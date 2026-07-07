"""Library API — GET /library. See docs/api-spec.md."""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_library(page: int = 1, limit: int = 20):
  raise NotImplementedError
