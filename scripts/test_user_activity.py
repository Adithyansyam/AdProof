"""Scripts to verify auth sync + activity inserts hit the app database."""

from __future__ import annotations

import json
import os
import sys
import uuid
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / "apps" / "worker"
sys.path.insert(0, str(WORKER))

API_URL = os.environ.get("NEXT_PUBLIC_API_URL") or os.environ.get("API_BASE_URL") or "http://localhost:8000"


def _print(title: str, payload: object) -> None:
    print(f"\n=== {title} ===")
    print(json.dumps(payload, indent=2, default=str))


def run_api_flow() -> dict:
    client = httpx.Client(base_url=API_URL, timeout=30.0)
    provider_user_id = f"test-supabase-{uuid.uuid4()}"
    email = f"activity-test-{uuid.uuid4().hex[:8]}@adproof.test"

    auth = client.post(
        "/auth/supabase",
        json={
            "email": email,
            "provider_user_id": provider_user_id,
            "name": "Activity Test User",
            "picture": None,
        },
    )
    auth.raise_for_status()
    auth_body = auth.json()
    token = auth_body["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    brief = client.post(
        "/briefs",
        headers=headers,
        json={
            "brand_name": "Activity Co",
            "brief_text": "Track that this brief creation is stored as user activity",
        },
    )
    brief.raise_for_status()
    brief_body = brief.json()

    listed = client.get("/briefs", headers=headers)
    listed.raise_for_status()

    activities = client.get("/auth/activities", headers=headers)
    activities.raise_for_status()
    activities_body = activities.json()

    me = client.get("/auth/me", headers=headers)
    me.raise_for_status()

    return {
        "api_url": API_URL,
        "auth": auth_body,
        "brief": {"id": brief_body["id"], "status": brief_body["status"]},
        "briefs_total": listed.json().get("total"),
        "activities_total": activities_body.get("total"),
        "activity_actions": [a["action"] for a in activities_body.get("items", [])],
        "me": me.json(),
    }


def run_db_check(user_id: str) -> dict:
    from db.models import Brief, User, UserActivity
    from db.session import SessionLocal, get_database_url

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        briefs = db.query(Brief).filter(Brief.user_id == user_id).count()
        activities = (
            db.query(UserActivity)
            .filter(UserActivity.user_id == user_id)
            .order_by(UserActivity.created_at.desc())
            .all()
        )
        return {
            "database_url": get_database_url(),
            "user_found": bool(user),
            "user_email": user.email if user else None,
            "briefs_count": briefs,
            "activities_count": len(activities),
            "activity_actions": [a.action for a in activities],
        }
    finally:
        db.close()


def main() -> int:
    print(f"Testing against API: {API_URL}")
    try:
        flow = run_api_flow()
    except Exception as exc:
        print(f"API flow failed: {exc}")
        print("Is the API running? Try: infra\\start-api.bat")
        return 1

    _print("API flow", flow)
    db = run_db_check(flow["auth"]["user_id"])
    _print("DB check", db)

    ok = (
        db["user_found"]
        and db["briefs_count"] >= 1
        and db["activities_count"] >= 1
        and "login" in db["activity_actions"]
        and "brief.create" in db["activity_actions"]
    )
    if not ok:
        print("\nFAIL: user/activity rows missing from app database")
        return 1

    print("\nPASS: user, brief, and activity rows are stored")
    if "sqlite" in str(db["database_url"]).lower():
        print(
            "NOTE: API is on SQLite. OAuth users also appear in Supabase Auth, "
            "but briefs/activities only appear in Supabase Postgres when "
            "DATABASE_URL points at your Supabase connection string."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
