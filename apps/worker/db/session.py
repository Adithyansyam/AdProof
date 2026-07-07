"""Database session management."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "")

if not DATABASE_URL or DATABASE_URL.startswith("postgresql"):
    try:
        if DATABASE_URL:
            engine = create_engine(DATABASE_URL)
            with engine.connect() as conn:
                conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        else:
            raise ConnectionError("no url")
    except Exception:
        _sqlite_path = os.path.join(
            os.path.dirname(__file__), "..", "adproof_local.db"
        )
        DATABASE_URL = f"sqlite:///{os.path.abspath(_sqlite_path)}"
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
