"""Inspect which database the API worker is actually using and count rows."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

WORKER = Path(__file__).resolve().parents[1] / "apps" / "worker"
sys.path.insert(0, str(WORKER))

# Load root .env if present
env_path = Path(__file__).resolve().parents[1] / ".env"
if env_path.exists():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def main() -> int:
    from sqlalchemy import inspect, text

    from db.session import SessionLocal, engine, get_database_url

    url = get_database_url()
    print(json.dumps({"database_url": url, "dialect": engine.dialect.name}, indent=2))

    inspector = inspect(engine)
    tables = sorted(inspector.get_table_names())
    print(json.dumps({"tables": tables}, indent=2))

    counts = {}
    with engine.connect() as conn:
        for table in ("users", "briefs", "runs", "user_activities"):
            if table not in tables:
                counts[table] = None
                continue
            counts[table] = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
    print(json.dumps({"row_counts": counts}, indent=2))

    if engine.dialect.name == "sqlite":
        print(
            "\nDIAGNOSIS: App data is on SQLite.\n"
            "Supabase Auth still stores OAuth identities in auth.users,\n"
            "but briefs/runs/user_activities will NOT appear in Supabase Table Editor\n"
            "until DATABASE_URL points at your Supabase Postgres URI."
        )
    else:
        print("\nDIAGNOSIS: App data is on Postgres — check public.users / public.user_activities in Supabase.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
