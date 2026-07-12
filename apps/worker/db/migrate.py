"""Lightweight DB migrations for auth + activity columns/tables."""

from sqlalchemy import inspect, text

from db.session import engine


def ensure_user_auth_columns() -> None:
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    if "users" not in tables:
        return
    columns = {col["name"] for col in inspector.get_columns("users")}
    alters = []
    if "google_id" not in columns:
        alters.append("ALTER TABLE users ADD COLUMN google_id TEXT")
    if "name" not in columns:
        alters.append("ALTER TABLE users ADD COLUMN name TEXT")
    if "avatar_url" not in columns:
        alters.append("ALTER TABLE users ADD COLUMN avatar_url TEXT")
    if "last_login_at" not in columns:
        alters.append("ALTER TABLE users ADD COLUMN last_login_at TIMESTAMP")
    if not alters:
        return
    with engine.begin() as conn:
        for stmt in alters:
            conn.execute(text(stmt))


def ensure_user_activities_table() -> None:
    inspector = inspect(engine)
    if "user_activities" in inspector.get_table_names():
        return
    dialect = engine.dialect.name
    if dialect == "sqlite":
        ddl = """
        CREATE TABLE user_activities (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) NOT NULL REFERENCES users(id),
            action VARCHAR(80) NOT NULL,
            resource_type VARCHAR(50),
            resource_id VARCHAR(36),
            metadata_json TEXT,
            created_at TIMESTAMP NOT NULL
        )
        """
    else:
        ddl = """
        CREATE TABLE IF NOT EXISTS user_activities (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) NOT NULL REFERENCES users(id),
            action VARCHAR(80) NOT NULL,
            resource_type VARCHAR(50),
            resource_id VARCHAR(36),
            metadata_json TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    with engine.begin() as conn:
        conn.execute(text(ddl))
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_user_activities_user_id "
                "ON user_activities (user_id)"
            )
        )
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_user_activities_action "
                "ON user_activities (action)"
            )
        )
