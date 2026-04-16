"""
api/server.py
-------------
FastAPI server — the HTTP interface to the agent system.

Endpoints:
  POST /campaign/create    Run the full pipeline for an event
  GET  /campaign/{id}      Get campaign status and calendar
  GET  /posts              List all scheduled/posted posts
  POST /posts/{id}/approve Manually approve a post before it goes live
  GET  /posts/{id}/preview Preview a generated post
  POST /feedback/run       Manually trigger the feedback agent
  GET  /health             Health check

Run with:
  uvicorn api.server:app --reload --port 8000
"""

import uuid
import logging
from datetime import datetime
from typing import Optional

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.config import settings
from core.database import PostRecord, RunLog, SessionLocal, get_db, init_db
from core.graph import run_pipeline
from core.models import EventDetails, PostStatus
from agents.feedback_agent import run_feedback_cycle
from agents.scheduler_agent import SchedulerService


log = logging.getLogger(__name__)
app = FastAPI(title="Instagram Marketing Agent", version="1.0.0")

# Singleton scheduler (starts with the app)
_scheduler: Optional[SchedulerService] = None


# ─── Startup / shutdown ──────────────────────────────────────────────────────

@app.on_event("startup")
def startup():
    global _scheduler
    init_db()
    _scheduler = SchedulerService()
    _scheduler.start()
    log.info("App started — scheduler running")


@app.on_event("shutdown")
def shutdown():
    if _scheduler:
        _scheduler.stop()


# ─── Request / Response schemas ──────────────────────────────────────────────

class CreateCampaignRequest(BaseModel):
    event: EventDetails


class PostPreview(BaseModel):
    id: str
    theme: str
    post_type: str
    caption: str
    hashtags: list[str]
    image_url: str
    scheduled_at: Optional[datetime]
    virality_score: float
    status: str
    ab_variant: str


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


@app.post("/campaign/create", status_code=202)
def create_campaign(
    req: CreateCampaignRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Kick off the full agent pipeline in the background.
    Returns a run_id immediately; poll /campaign/{run_id} for status.
    """
    run_id = str(uuid.uuid4())

    # Log the run
    run_log = RunLog(
        id=run_id,
        event_name=req.event.name,
        status="running",
    )
    db.add(run_log)
    db.commit()

    background_tasks.add_task(_run_pipeline_task, run_id, req.event)

    return {"run_id": run_id, "status": "started"}


@app.get("/campaign/{run_id}")
def get_campaign(run_id: str, db: Session = Depends(get_db)):
    """Get the status of a pipeline run and its generated posts."""
    run_log = db.query(RunLog).get(run_id)
    if not run_log:
        raise HTTPException(404, "Run not found")

    posts = (
        db.query(PostRecord)
        .filter(PostRecord.event_name == run_log.event_name)
        .order_by(PostRecord.scheduled_at)
        .all()
    )

    return {
        "run_id":     run_id,
        "status":     run_log.status,
        "event_name": run_log.event_name,
        "started_at": run_log.started_at,
        "ended_at":   run_log.ended_at,
        "summary":    run_log.summary,
        "posts":      [_post_to_preview(p) for p in posts],
    }


@app.get("/posts")
def list_posts(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all posts, optionally filtered by status."""
    q = db.query(PostRecord).order_by(PostRecord.scheduled_at)
    if status:
        q = q.filter(PostRecord.status == status)
    return [_post_to_preview(p) for p in q.all()]


@app.get("/posts/{post_id}/preview")
def preview_post(post_id: str, db: Session = Depends(get_db)):
    """Get full details for a single post."""
    post = db.query(PostRecord).get(post_id)
    if not post:
        raise HTTPException(404, "Post not found")
    return _post_to_preview(post)


@app.post("/posts/{post_id}/approve")
def approve_post(post_id: str, db: Session = Depends(get_db)):
    """
    Manually approve a draft post.
    Useful if REQUIRE_APPROVAL=true is set in settings.
    """
    post = db.query(PostRecord).get(post_id)
    if not post:
        raise HTTPException(404, "Post not found")
    if post.status != PostStatus.DRAFT.value:
        raise HTTPException(400, f"Post is {post.status}, not draft")

    post.status = PostStatus.SCHEDULED.value
    db.commit()
    return {"status": "approved", "post_id": post_id}


@app.post("/feedback/run", status_code=202)
def trigger_feedback(background_tasks: BackgroundTasks):
    """Manually trigger the feedback analysis cycle."""
    background_tasks.add_task(run_feedback_cycle)
    return {"status": "feedback cycle started"}


# ─── Background task ─────────────────────────────────────────────────────────

def _run_pipeline_task(run_id: str, event: EventDetails):
    """Runs in FastAPI BackgroundTasks thread."""
    db = SessionLocal()
    try:
        final_state = run_pipeline(event)
        calendar    = final_state.get("calendar")
        errors      = final_state.get("errors", [])

        run_log = db.query(RunLog).get(run_id)
        if run_log:
            run_log.status   = "done" if not errors else "done_with_errors"
            run_log.ended_at = datetime.utcnow()
            run_log.summary  = (
                f"Generated {len(calendar.posts) if calendar else 0} posts. "
                + (f"Errors: {'; '.join(errors)}" if errors else "")
            )
            db.commit()

    except Exception as e:
        log.exception("Pipeline failed for run %s: %s", run_id, e)
        run_log = db.query(RunLog).get(run_id)
        if run_log:
            run_log.status   = "error"
            run_log.ended_at = datetime.utcnow()
            run_log.summary  = str(e)
            db.commit()
    finally:
        db.close()


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _post_to_preview(p: PostRecord) -> dict:
    return {
        "id":            p.id,
        "theme":         p.theme,
        "post_type":     p.post_type,
        "caption":       p.caption,
        "hashtags":      p.hashtags,
        "image_url":     p.image_url,
        "scheduled_at":  p.scheduled_at.isoformat() if p.scheduled_at else None,
        "virality_score": p.virality_score,
        "status":        p.status,
        "ab_variant":    p.ab_variant,
        "ig_post_id":    p.ig_post_id,
        "posted_at":     p.posted_at.isoformat() if p.posted_at else None,
    }
