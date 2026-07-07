"""Briefs API — POST /briefs, GET /briefs/:id. See docs/api-spec.md."""

from fastapi import APIRouter

router = APIRouter()


@router.post("")
async def create_brief():
  # TODO: create brief, enqueue run
  raise NotImplementedError


@router.get("/{brief_id}")
async def get_brief(brief_id: str):
  # TODO: brief + latest run status
  raise NotImplementedError
