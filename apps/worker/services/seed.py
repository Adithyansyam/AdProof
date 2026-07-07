"""Seed demo user for hackathon MVP."""

from sqlalchemy.orm import Session

from config import get_settings
from db.models import User


def get_or_create_demo_user(db: Session) -> User:
    settings = get_settings()
    user = db.query(User).filter(User.email == settings.demo_user_email).first()
    if user:
        return user
    user = User(email=settings.demo_user_email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
