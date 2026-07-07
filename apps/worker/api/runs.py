"""Runs API — GET /runs/:id, replay, fork, verify, manifest. See docs/api-spec.md."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/{run_id}")
async def get_run(run_id: str):
  raise NotImplementedError


@router.post("/{run_id}/replay")
async def replay_run(run_id: str):
  raise NotImplementedError


@router.post("/{run_id}/fork")
async def fork_run(run_id: str):
  raise NotImplementedError


@router.get("/{run_id}/manifest")
async def get_manifest(run_id: str):
  raise NotImplementedError


@router.get("/{run_id}/verify")
async def verify_run(run_id: str):
  raise NotImplementedError
