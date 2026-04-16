"""
agents/feedback_agent.py
------------------------
Feedback Agent — the intelligence loop.

Responsibilities:
  1. Fetch engagement data from Instagram Insights for posted content
  2. Run A/B test analysis (which caption variant performed better?)
  3. Update virality scores in the DB
  4. Generate strategy adjustments for remaining scheduled posts
  5. Score future posts (re-rank or reschedule based on engagement trends)

This agent runs on a schedule (every 24h) AFTER posts go live,
not as part of the initial content generation pipeline.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from sqlalchemy.orm import Session

from agents.instagram_agent.api.instagram_client import InstagramClient
from agents.instagram_agent.core.database import EngagementRecord, PostRecord, SessionLocal
from agents.instagram_agent.core.models import AgentState, PostStatus


log = logging.getLogger(__name__)


# ─── Analysis prompt ─────────────────────────────────────────────────────────

ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a data-driven social media analyst.
You interpret Instagram engagement data and give actionable advice.
You understand college audience behaviour patterns.
Output ONLY valid JSON."""),

    ("human", """Analyze this engagement data from our Instagram posts.

EVENT: {event_name}
DAYS UNTIL EVENT: {days_until_event}

RECENT POST PERFORMANCE:
{posts_json}

A/B TEST RESULTS (if any):
{ab_results}

Provide:
1. Top 3 insights (what's working / not working)
2. 3 concrete adjustments for the next 3 posts
3. Best posting time recommendation (based on engagement patterns)
4. Whether to increase/decrease posting frequency
5. Recommended hashtag tweaks

JSON format:
{{
  "insights": ["insight 1", "insight 2", "insight 3"],
  "next_post_adjustments": ["adj 1", "adj 2", "adj 3"],
  "best_post_hour": 20,
  "frequency_change": "increase" | "decrease" | "maintain",
  "hashtag_tweaks": "One sentence recommendation",
  "overall_health": "good" | "needs_work" | "critical"
}}"""),
])


# ─── Agent node (for LangGraph) ──────────────────────────────────────────────

def feedback_agent(state: AgentState) -> AgentState:
    """
    Pull insights for all posted content, run analysis, return adjustments.
    Can be run mid-campaign to adapt strategy for remaining posts.
    """
    db  = SessionLocal()
    ig  = InstagramClient()

    try:
        calendar = state.get("calendar")
        event    = calendar.event if calendar else None

        # Step 1: Fetch engagement for all posted posts
        posted = (
            db.query(PostRecord)
            .filter(
                PostRecord.status == PostStatus.POSTED.value,
                PostRecord.ig_post_id.isnot(None),
            )
            .all()
        )

        if not posted:
            log.info("No posted content yet — feedback agent skipping")
            return {"engagement_report": {}, "strategy_adjustments": []}

        # Step 2: Fetch insights from Instagram & store in DB
        engagement_data = []
        for post in posted:
            insights = _fetch_and_store_insights(post, ig, db)
            if insights:
                engagement_data.append({
                    "post_id":       post.id,
                    "theme":         post.theme,
                    "post_type":     post.post_type,
                    "days_before":   post.days_before,
                    "ab_variant":    post.ab_variant,
                    "virality_score": post.virality_score,
                    "insights":      insights,
                    "engagement_rate": _calc_engagement_rate(insights),
                })

        # Step 3: A/B test analysis
        ab_results = _analyze_ab_tests(db)

        # Step 4: LLM strategy analysis
        if not event:
            return {"engagement_report": {"raw": engagement_data}}

        llm   = ChatOpenAI(model="gpt-4o", temperature=0.3)
        chain = ANALYSIS_PROMPT | llm | StrOutputParser()

        raw = chain.invoke({
            "event_name":      event.name,
            "days_until_event": (event.date - datetime.utcnow()).days,
            "posts_json":       json.dumps(engagement_data, indent=2),
            "ab_results":       json.dumps(ab_results, indent=2),
        })

        import re
        raw = re.sub(r"```json|```", "", raw).strip()
        analysis = json.loads(raw)

        log.info("Feedback analysis: %s", analysis.get("overall_health"))

        return {
            "engagement_report":    analysis,
            "strategy_adjustments": analysis.get("next_post_adjustments", []),
        }

    finally:
        db.close()


# ─── Engagement helpers ──────────────────────────────────────────────────────

def _fetch_and_store_insights(
    post: PostRecord,
    ig: InstagramClient,
    db: Session,
) -> Optional[dict]:
    """Fetch insights from IG API and persist in engagement table."""
    try:
        insights = ig.get_post_insights(post.ig_post_id)

        record = EngagementRecord(
            post_id     = post.id,
            ig_post_id  = post.ig_post_id,
            likes       = insights.get("likes", 0),
            comments    = insights.get("comments", 0),
            reach       = insights.get("reach", 0),
            impressions = insights.get("impressions", 0),
            saves       = insights.get("saved", 0),
            shares      = insights.get("shares", 0),
        )
        db.add(record)
        db.commit()
        return insights

    except Exception as e:
        log.warning("Could not fetch insights for %s: %s", post.ig_post_id, e)
        return None


def _calc_engagement_rate(insights: dict) -> float:
    """
    ER = (likes + comments + saves + shares) / reach * 100
    Industry benchmark: >3% is good, >6% is excellent for music events.
    """
    reach = insights.get("reach", 1) or 1
    interactions = (
        insights.get("likes", 0)
        + insights.get("comments", 0)
        + insights.get("saved", 0)
        + insights.get("shares", 0)
    )
    return round(interactions / reach * 100, 2)


def _analyze_ab_tests(db: Session) -> list[dict]:
    """Compare A vs B variants of the same theme."""
    results = []

    # Get themes that have both A and B posted
    from sqlalchemy import func
    ab_pairs = (
        db.query(PostRecord.theme, PostRecord.ab_variant, func.avg(EngagementRecord.likes))
        .join(EngagementRecord, PostRecord.id == EngagementRecord.post_id)
        .group_by(PostRecord.theme, PostRecord.ab_variant)
        .all()
    )

    # Group by theme
    by_theme: dict[str, dict] = {}
    for theme, variant, avg_likes in ab_pairs:
        if theme not in by_theme:
            by_theme[theme] = {}
        by_theme[theme][variant] = float(avg_likes or 0)

    for theme, variants in by_theme.items():
        if "A" in variants and "B" in variants:
            winner = "A" if variants["A"] >= variants["B"] else "B"
            results.append({
                "theme":   theme,
                "A_likes": variants["A"],
                "B_likes": variants["B"],
                "winner":  winner,
            })

    return results


# ─── Standalone runner (cron / manual) ──────────────────────────────────────

def run_feedback_cycle():
    """
    Call this from a cron job or CLI to run feedback analysis independently
    of the main pipeline.
    """
    # Minimal state for standalone run
    state: AgentState = {}
    result = feedback_agent(state)
    log.info("Feedback cycle complete: %s", result.get("engagement_report", {}).get("overall_health"))
    return result
