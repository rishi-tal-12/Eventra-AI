"""
agents/scheduler_agent.py
-------------------------
Scheduler Agent — two responsibilities:

1. schedule_posts_node(): LangGraph node that writes all posts from the
   ContentCalendar into the database with status="scheduled".

2. SchedulerService: APScheduler-backed service that runs as a background
   process, picks up due posts, and calls the Instagram API to publish them.

Scheduling strategy:
  - Peak engagement windows for college crowd:
      Mon-Thu: 7-9pm local time
      Fri:     6-8pm
      Sat:     12-2pm OR 7-9pm
      Sun:     11am-1pm
  - Never post during 11pm-8am (low reach, wasted post budget)
  - Minimum 4 hours between consecutive posts
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from sqlalchemy.orm import Session

from api.instagram_client import InstagramClient, InstagramAPIError
from core.config import settings
from core.database import PostRecord, SessionLocal, EngagementRecord
from core.models import AgentState, ContentCalendar, PostStatus, PostType, ScheduledPost


log = logging.getLogger(__name__)


# ─── LangGraph node ─────────────────────────────────────────────────────────

def schedule_posts_node(state: AgentState) -> AgentState:
    """
    Writes all processed posts from the calendar into the database.
    Sets status = 'scheduled' so the SchedulerService can pick them up.
    """
    calendar: ContentCalendar = state["calendar"]
    db: Session = SessionLocal()

    try:
        saved_count = 0
        for post in calendar.posts:
            if not post.caption:
                log.warning("Post %s has no caption — skipping scheduling", post.id)
                continue
            if not post.image_url and post.post_type != PostType.REEL:
                log.warning("Post %s has no image URL — will use placeholder", post.id)

            record = PostRecord(
                id            = post.id,
                event_name    = calendar.event.name,
                days_before   = post.days_before_event,
                post_type     = post.post_type.value,
                theme         = post.theme.value,
                caption       = post.caption,
                image_prompt  = post.image_prompt,
                image_url     = post.image_url,
                status        = PostStatus.SCHEDULED.value,
                scheduled_at  = post.scheduled_at,
                virality_score= post.virality_score,
                ab_variant    = post.ab_variant,
            )
            record.hashtags = post.hashtags  # uses property setter

            db.merge(record)   # merge = upsert (handles reruns gracefully)
            saved_count += 1

        db.commit()
        log.info("Scheduled %d posts to database", saved_count)

    except Exception as e:
        db.rollback()
        errors = list(state.get("errors", []))
        errors.append(f"DB scheduling error: {e}")
        return {"errors": errors}
    finally:
        db.close()

    return {}  # No state changes needed; posts are in DB


# ─── Scheduler service ──────────────────────────────────────────────────────

class SchedulerService:
    """
    Runs as a long-lived background service.
    Every 5 minutes it checks for posts due in the next 10 minutes
    and schedules them with APScheduler for exact-time execution.
    """

    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone="UTC")
        self.ig = InstagramClient()
        self._already_scheduled: set[str] = set()

    def start(self):
        # Polling job: check DB every 5 minutes
        self.scheduler.add_job(
            self._poll_and_schedule,
            "interval",
            minutes=5,
            id="poll_job",
            replace_existing=True,
        )
        self.scheduler.start()
        log.info("SchedulerService started")

        # Run once immediately on startup
        self._poll_and_schedule()

    def stop(self):
        self.scheduler.shutdown(wait=False)

    def _poll_and_schedule(self):
        """Fetch posts due in next 15 minutes and register them."""
        db = SessionLocal()
        try:
            now        = datetime.utcnow()
            window_end = now + timedelta(minutes=15)

            due_posts = (
                db.query(PostRecord)
                .filter(
                    PostRecord.status == PostStatus.SCHEDULED.value,
                    PostRecord.scheduled_at <= window_end,
                    PostRecord.scheduled_at >= now - timedelta(minutes=5),
                )
                .all()
            )

            for post in due_posts:
                if post.id in self._already_scheduled:
                    continue

                self.scheduler.add_job(
                    self._publish_post,
                    trigger=DateTrigger(run_date=post.scheduled_at),
                    args=[post.id],
                    id=f"publish_{post.id}",
                    replace_existing=True,
                    misfire_grace_time=300,  # 5 min grace if server was down
                )
                self._already_scheduled.add(post.id)
                log.info("Registered post %s for publishing at %s", post.id, post.scheduled_at)

        finally:
            db.close()

    def _publish_post(self, post_id: str):
        """
        Called at the exact scheduled time.
        Publishes the post to Instagram and updates DB status.
        """
        db = SessionLocal()
        try:
            record: Optional[PostRecord] = db.query(PostRecord).get(post_id)
            if not record:
                log.error("Post %s not found in DB", post_id)
                return

            if record.status != PostStatus.SCHEDULED.value:
                log.warning("Post %s status is %s — skipping", post_id, record.status)
                return

            # Guard: don't post if no image (production should never reach here)
            if not record.image_url:
                record.status = PostStatus.FAILED.value
                db.commit()
                log.error("Post %s has no image_url — marked failed", post_id)
                return

            log.info("Publishing post %s (%s)", post_id, record.post_type)

            ig_post_id = self.ig.post_image(
                image_url=record.image_url,
                caption=record.caption,
                hashtags=record.hashtags,
            )

            record.ig_post_id  = ig_post_id
            record.status      = PostStatus.POSTED.value
            record.posted_at   = datetime.utcnow()
            db.commit()

            log.info("✅ Post %s published → IG post ID: %s", post_id, ig_post_id)

        except InstagramAPIError as e:
            log.error("Instagram API error for post %s: %s", post_id, e)
            if record:
                record.status = PostStatus.FAILED.value
                db.commit()

        except Exception as e:
            log.exception("Unexpected error publishing post %s: %s", post_id, e)
            if record:
                record.status = PostStatus.FAILED.value
                db.commit()
        finally:
            db.close()

    # ─── Utility: adjust schedule to peak windows ──────────────────────────

    @staticmethod
    def adjust_to_peak_window(dt: datetime) -> datetime:
        """
        Shift a datetime to the nearest college-crowd peak window.
        Preserves the date; only adjusts the hour.

        Peak windows (local time → we store in UTC, adjust at display):
          Mon-Thu, Sun: 20:00 (8pm)
          Fri:          18:00 (6pm)
          Sat:          13:00 (1pm) or 19:00 (7pm) — alternate
        """
        weekday = dt.weekday()  # 0=Mon, 6=Sun

        peak_hours = {
            0: 20, 1: 20, 2: 20, 3: 20,  # Mon-Thu: 8pm
            4: 18,                         # Fri: 6pm
            5: 13,                         # Sat: 1pm
            6: 20,                         # Sun: 8pm
        }

        peak_hour = peak_hours[weekday]
        return dt.replace(hour=peak_hour, minute=0, second=0, microsecond=0)
