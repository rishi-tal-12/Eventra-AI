"""
core/database.py
----------------
SQLAlchemy setup. SQLite for development, swap DATABASE_URL for
Postgres in production. Stores posts, engagement logs, and run history.
"""

import json
from datetime import datetime

from sqlalchemy import (
    Column, DateTime, Float, Integer, String, Text, create_engine
)
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings


# ─── Engine & Session ───────────────────────────────────────────────────────

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite-only
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# ─── ORM Models ─────────────────────────────────────────────────────────────

class PostRecord(Base):
    """Persisted record for every scheduled/posted item."""
    __tablename__ = "posts"

    id              = Column(String, primary_key=True)
    event_name      = Column(String, nullable=False)
    days_before     = Column(Integer)
    post_type       = Column(String)
    theme           = Column(String)
    caption         = Column(Text)
    hashtags_json   = Column(Text)       # JSON list
    image_prompt    = Column(Text)
    image_url       = Column(String)
    ig_media_id     = Column(String)
    ig_post_id      = Column(String)
    status          = Column(String, default="draft")
    scheduled_at    = Column(DateTime)
    posted_at       = Column(DateTime)
    virality_score  = Column(Float, default=0.0)
    ab_variant      = Column(String, default="A")
    created_at      = Column(DateTime, default=datetime.utcnow)
    updated_at      = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def hashtags(self) -> list[str]:
        return json.loads(self.hashtags_json or "[]")

    @hashtags.setter
    def hashtags(self, value: list[str]):
        self.hashtags_json = json.dumps(value)


class EngagementRecord(Base):
    """Snapshot of engagement metrics fetched from Instagram Insights."""
    __tablename__ = "engagement"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    post_id     = Column(String, nullable=False)   # FK to PostRecord.id
    ig_post_id  = Column(String)
    likes       = Column(Integer, default=0)
    comments    = Column(Integer, default=0)
    reach       = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    saves       = Column(Integer, default=0)
    shares      = Column(Integer, default=0)
    fetched_at  = Column(DateTime, default=datetime.utcnow)


class RunLog(Base):
    """Audit trail for every agent pipeline run."""
    __tablename__ = "run_logs"

    id         = Column(String, primary_key=True)
    event_name = Column(String)
    status     = Column(String)          # "running" | "done" | "error"
    summary    = Column(Text)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at   = Column(DateTime)


def init_db():
    """Create all tables. Call once at startup."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency: yields a DB session and closes it after request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
