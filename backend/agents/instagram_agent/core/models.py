"""
core/models.py
--------------
Shared Pydantic models and the central LangGraph state TypedDict.
Every agent reads from and writes to AgentState — it is the single
source of truth that flows through the LangGraph graph.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field
from typing_extensions import TypedDict


# ─── Enums ─────────────────────────────────────────────────────────────────

class PostType(str, Enum):
    REEL         = "reel"
    CAROUSEL     = "carousel"
    SINGLE_IMAGE = "single_image"
    STORY        = "story"


class PostStatus(str, Enum):
    DRAFT      = "draft"
    SCHEDULED  = "scheduled"
    POSTED     = "posted"
    FAILED     = "failed"


class ContentTheme(str, Enum):
    HYPE       = "hype"          # Early buzz / teaser
    ARTIST     = "artist"        # Spotlight on performers
    COUNTDOWN  = "countdown"     # X days left
    BEHIND     = "behind_scenes" # Setup / backstage
    SOCIAL     = "social_proof"  # Testimonials / past events
    CTA        = "call_to_action" # Buy tickets / register
    DAY_OF     = "day_of"        # Event day posts


# ─── Input / Config ─────────────────────────────────────────────────────────

class EventDetails(BaseModel):
    """User-provided event information that seeds the entire pipeline."""
    name: str                       = Field(..., description="Event name, e.g. 'Neon Beats Fest'")
    date: datetime                  = Field(..., description="Event date & time")
    venue: str                      = Field(..., description="Venue name and city")
    artists: list[str]              = Field(default_factory=list)
    genres: list[str]               = Field(default_factory=list)
    target_audience: str            = Field(..., description="e.g. 'college students 18-24'")
    vibe: str                       = Field(..., description="e.g. 'electric, euphoric, underground'")
    ticket_url: str                 = Field(default="")
    ticket_price: str               = Field(default="Free")
    capacity: int                   = Field(default=500)
    instagram_handle: str           = Field(..., description="@yourhandle")
    location_hashtags: list[str]    = Field(default_factory=list,
                                            description="e.g. ['#Roorkee', '#IITRoorkee']")


# ─── Calendar / Schedule ────────────────────────────────────────────────────

class ScheduledPost(BaseModel):
    """One entry in the content calendar."""
    id: str                = Field(default_factory=lambda: str(uuid.uuid4()))
    days_before_event: int = Field(..., description="Negative = after event")
    post_type: PostType    = PostType.SINGLE_IMAGE
    theme: ContentTheme    = ContentTheme.HYPE
    caption: str           = ""
    hashtags: list[str]    = Field(default_factory=list)
    image_prompt: str      = ""          # Prompt sent to image gen API
    image_url: str         = ""          # Public URL after upload
    ig_media_id: str       = ""          # Returned by Instagram after creation
    ig_post_id: str        = ""          # After publish
    status: PostStatus     = PostStatus.DRAFT
    scheduled_at: Optional[datetime] = None
    posted_at:    Optional[datetime] = None
    engagement:   dict[str, Any]     = Field(default_factory=dict)
    virality_score: float  = 0.0
    ab_variant: str        = "A"         # "A" or "B" for A/B testing


class ContentCalendar(BaseModel):
    """Full 10–15 day calendar produced by the Strategy Agent."""
    event: EventDetails
    posts: list[ScheduledPost] = Field(default_factory=list)
    themes_plan: dict[str, Any] = Field(
        default_factory=dict,
        description="day_label -> theme rationale"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ─── LangGraph State ────────────────────────────────────────────────────────

class AgentState(TypedDict, total=False):
    """
    The shared state dict that flows through every node in the LangGraph.
    Agents read what they need and write their outputs back here.
    LangGraph merges partial updates automatically.
    """
    # Input
    event: EventDetails

    # Strategy agent output
    calendar: ContentCalendar
    current_post_index: int          # Which post the pipeline is currently processing

    # Content agent output (for the current post)
    caption: str
    hashtags: list[str]
    hook: str                        # First line / hook of the caption
    reel_script: str
    ab_captions: dict[str, str]      # {"A": "...", "B": "..."}

    # Creative agent output
    image_prompt: str
    image_url: str                   # Public URL after upload

    # Feedback agent output
    virality_score: float
    engagement_report: dict[str, Any]
    strategy_adjustments: list[str]

    # Orchestration control
    next_agent: str                  # Used by conditional edges
    errors: list[str]
    run_id: str
