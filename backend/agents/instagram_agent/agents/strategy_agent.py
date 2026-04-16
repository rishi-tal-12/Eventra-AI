"""
agents/strategy_agent.py
------------------------
Strategy Agent — the first node in the LangGraph pipeline.

INPUT:  event: EventDetails  (from AgentState)
OUTPUT: calendar: ContentCalendar  (written back to AgentState)

Responsibilities:
  1. Decide how many days before the event to start posting
  2. Assign a theme to each posting day
  3. Decide post type (reel, carousel, image) per day
  4. Output a structured ContentCalendar

This agent does NOT generate copy — that's the Content Agent's job.
"""

import json
import re
from datetime import datetime, timedelta

from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from agents.instagram_agent.core.models import (
    AgentState, ContentCalendar, ContentTheme,
    EventDetails, PostType, ScheduledPost
)


# ─── Prompt ─────────────────────────────────────────────────────────────────

STRATEGY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert social media strategist specialising in
college music events and youth culture marketing. You create data-driven
Instagram content calendars that build hype progressively.

You understand:
- Attention spans on Instagram (reels > carousels > static for reach)
- Countdown psychology (urgency increases conversion as event approaches)
- College crowd behaviour: peak scroll times (8-10pm), meme culture, FOMO
- Platform algorithm: consistency beats frequency; saves + shares > likes

Always respond with ONLY valid JSON. No markdown fences, no extra text."""),

    ("human", """Create a 12-day Instagram content calendar for this event.

EVENT DETAILS:
{event_json}

Rules:
- Start 12 days before the event (day -12 to day 0)
- Day 0 = event day (1-2 posts)
- Use this theme distribution:
    • Days -12 to -10: HYPE (teasers, mystery, intrigue)
    • Days -9 to -7:  ARTIST spotlights
    • Days -6 to -4:  COUNTDOWN + social proof
    • Days -3 to -1:  BEHIND_SCENES + CTA (buy tickets urgency)
    • Day 0:          DAY_OF (excitement, arrive now)
- Mix post types for variety. Prefer reels for days -12, -7, -3, 0.
- Include 1 A/B test post (mark ab_test: true) to compare two caption styles.

Respond with this exact JSON structure:
{{
  "themes_plan": {{
    "day_-12": "rationale string",
    ...
  }},
  "posts": [
    {{
      "days_before_event": -12,
      "post_type": "reel",
      "theme": "hype",
      "image_prompt_hint": "one sentence describing the visual",
      "ab_test": false
    }},
    ...
  ]
}}"""),
])


# ─── Agent node ─────────────────────────────────────────────────────────────

def strategy_agent(state: AgentState) -> AgentState:
    """
    LangGraph node. Receives state, returns partial state update.
    LangGraph merges updates automatically — only return what changed.
    """
    event: EventDetails = state["event"]

    #llm = ChatOpenAI(model="gpt-4o", temperature=0.4)
    llm = ChatOllama(model="llama3.2", temperature=0.4)
    chain = STRATEGY_PROMPT | llm | StrOutputParser()

    raw = chain.invoke({"event_json": event.model_dump_json(indent=2)})

    # Strip stray markdown fences if the model adds them
    raw = re.sub(r"```json|```", "", raw).strip()

    try:
        plan = json.loads(raw)
    except json.JSONDecodeError as exc:
        # Graceful degradation: build a minimal default calendar
        plan = _default_plan()
        errors = list(state.get("errors", []))
        errors.append(f"Strategy JSON parse error: {exc}")
        state["errors"] = errors

    # Build the ContentCalendar Pydantic object
    posts: list[ScheduledPost] = []
    for p in plan.get("posts", []):
        days = p.get("days_before_event", -7)
        scheduled_at = event.date + timedelta(days=days)

        post_type = _safe_post_type(p.get("post_type", "single_image"))
        theme     = _safe_theme(p.get("theme", "hype"))

        posts.append(ScheduledPost(
            days_before_event=days,
            post_type=post_type,
            theme=theme,
            image_prompt=p.get("image_prompt_hint", ""),
            scheduled_at=scheduled_at,
            ab_variant="A" if not p.get("ab_test") else "A",
        ))

        # Duplicate A/B test posts with variant B
        if p.get("ab_test"):
            posts.append(ScheduledPost(
                days_before_event=days,
                post_type=post_type,
                theme=theme,
                image_prompt=p.get("image_prompt_hint", ""),
                scheduled_at=scheduled_at + timedelta(hours=4),
                ab_variant="B",
            ))

    # Sanitize themes_plan — local models sometimes return dicts instead of strings
    raw_themes = plan.get("themes_plan", {})
    clean_themes = {
    str(k): str(v) if not isinstance(v, dict) else v.get("theme", str(v))
    for k, v in raw_themes.items()
    }

    calendar = ContentCalendar(
    event=event,
    posts=posts,
    themes_plan=clean_themes,
    )

    return {
        "calendar": calendar,
        "current_post_index": 0,
    }


# ─── Helpers ────────────────────────────────────────────────────────────────

def _safe_post_type(raw: str) -> PostType:
    """Normalize whatever the local LLM returns into a valid PostType."""
    cleaned = raw.lower().strip().rstrip("s")  # carousels→carousel, reels→reel
    aliases = {
        "image":  "single_image",
        "static": "single_image",
        "photo":  "single_image",
        "video":  "reel",
        "slide":  "carousel",
    }
    cleaned = aliases.get(cleaned, cleaned)
    valid = [e.value for e in PostType]
    return PostType(cleaned) if cleaned in valid else PostType.SINGLE_IMAGE


def _safe_theme(raw: str) -> ContentTheme:
    """Normalize theme strings from local LLM into valid ContentTheme values."""
    cleaned = raw.lower().strip().replace(" ", "_").replace("-", "_")
    aliases = {
        "behind_the_scenes": "behind_scenes",
        "behind":            "behind_scenes",
        "backstage":         "behind_scenes",
        "cta":               "call_to_action",
        "social":            "social_proof",
        "testimonial":       "social_proof",
        "spotlight":         "artist",
        "day_of_event":      "day_of",
        "event_day":         "day_of",
    }
    cleaned = aliases.get(cleaned, cleaned)
    valid = [e.value for e in ContentTheme]
    return ContentTheme(cleaned) if cleaned in valid else ContentTheme.HYPE


def _default_plan() -> dict:
    """Minimal fallback if LLM JSON is malformed."""
    themes = [
        ("hype", "reel"), ("hype", "single_image"), ("artist", "carousel"),
        ("artist", "single_image"), ("countdown", "reel"),
        ("countdown", "carousel"), ("social_proof", "single_image"),
        ("behind_scenes", "carousel"), ("behind_scenes", "reel"),
        ("call_to_action", "single_image"), ("call_to_action", "reel"),
        ("day_of", "reel"),
    ]
    posts = []
    for i, (theme, ptype) in enumerate(reversed(themes)):
        posts.append({
            "days_before_event": -(len(themes) - 1 - i),
            "post_type": ptype,
            "theme": theme,
            "image_prompt_hint": f"Energetic music event visual for {theme} theme",
            "ab_test": i == 5,
        })
    return {"themes_plan": {}, "posts": posts}
