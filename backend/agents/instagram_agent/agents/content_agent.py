"""
agents/content_agent.py
-----------------------
Content Agent — generates all copy for one post at a time.

INPUT:  state["calendar"], state["current_post_index"]
OUTPUT: state["caption"], state["hashtags"], state["hook"],
        state["reel_script"], state["ab_captions"]

Key features:
  - Theme-specific prompt templates
  - A/B caption variants
  - Virality scoring heuristics
  - Hashtag strategy (mix of niche + broad)
  - Countdown-aware copy (changes tone based on days_before_event)
"""

import json
import re
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from agents.instagram_agent.core.models import AgentState, ContentTheme, PostType, ScheduledPost

from config import GROQ_API_KEY


# ─── Theme-specific system prompts ─────────────────────────────────────────

THEME_PERSONAS = {
    ContentTheme.HYPE: "You are a hype-builder. Use mystery, FOMO, and anticipation. Short sentences. Emojis allowed.",
    ContentTheme.ARTIST: "You are a music journalist. Write artist-spotlights that feel personal and genuine.",
    ContentTheme.COUNTDOWN: "You are creating urgency. Numbers, deadlines, 'X days left' psychology.",
    ContentTheme.BEHIND: "You are authentic and raw. Behind-the-scenes feels real, not polished.",
    ContentTheme.SOCIAL: "You are social proof builder. Drop testimonials, numbers, past event energy.",
    ContentTheme.CTA: "You are a conversion specialist. Every word drives to ticket purchase. Create loss aversion.",
    ContentTheme.DAY_OF: "You are pure excitement. TODAY IS THE DAY energy. Short, punchy, electric.",
}

# ─── Main prompt ────────────────────────────────────────────────────────────

CONTENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """{persona}

You write Instagram captions for college music events.
Target audience: {audience}
Event vibe: {vibe}

CAPTION RULES:
- Hook (first line): Must stop the scroll. Max 10 words. No generic openers.
- Body: 2-4 short paragraphs. White space = readability.
- CTA line: Always end with one clear action.
- Hashtags: Return as a separate list (NOT in the caption body).
- Keep caption under 220 words total.
- For reels: also write a 30-second reel script.

Respond ONLY with valid JSON, no markdown fences."""),

    ("human", """Generate content for this specific post:

EVENT: {event_name} on {event_date} at {venue}
ARTISTS: {artists}
THEME: {theme}
POST TYPE: {post_type}
DAYS BEFORE EVENT: {days_before}
TICKET URL: {ticket_url}
PRICE: {ticket_price}

Also generate:
1. Variant B caption (different angle, same theme) for A/B testing
2. 25 hashtags (mix: 5 mega >1M, 10 mid 100k-1M, 10 niche <100k)
   Include location tags: {location_hashtags}
3. Virality score 0-100 for caption A (judge: hook strength, shareability,
   emotion, CTA clarity)

JSON structure:
{{
  "hook": "First line of caption A",
  "caption_a": "Full caption text for variant A",
  "caption_b": "Full caption text for variant B",
  "reel_script": "30-second script if post_type is reel, else empty string",
  "hashtags": ["#tag1", "#tag2", ...],
  "virality_score": 72,
  "virality_reasoning": "One sentence explaining the score"
}}"""),
])


# ─── Agent node ─────────────────────────────────────────────────────────────

def content_agent(state: AgentState) -> AgentState:
    """
    Processes the current post (state["current_post_index"]) in the calendar
    and writes generated copy back into both the state and the post object.
    """
    calendar = state["calendar"]
    idx      = state.get("current_post_index", 0)
    post: ScheduledPost = calendar.posts[idx]
    event = calendar.event

    persona = THEME_PERSONAS.get(post.theme, THEME_PERSONAS[ContentTheme.HYPE])

    #llm   = ChatOpenAI(model="gpt-4o", temperature=0.75)
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=GROQ_API_KEY,
        temperature=0.7,
    )

    chain = CONTENT_PROMPT | llm | StrOutputParser()

    raw = chain.invoke({
        "persona":           persona,
        "audience":          event.target_audience,
        "vibe":              event.vibe,
        "event_name":        event.name,
        "event_date":        event.date.strftime("%B %d, %Y at %I:%M %p"),
        "venue":             event.venue,
        "artists":           ", ".join(event.artists) or "TBA",
        "theme":             post.theme.value,
        "post_type":         post.post_type.value,
        "days_before":       post.days_before_event,
        "ticket_url":        event.ticket_url or "Link in bio",
        "ticket_price":      event.ticket_price,
        "location_hashtags": " ".join(event.location_hashtags),
    })

    raw = re.sub(r"```json|```", "", raw).strip()

    try:
        content = json.loads(raw)
    except json.JSONDecodeError:
        content = _fallback_content(event.name, post.theme)

    # Determine which caption variant to use for this post
    caption = content["caption_a"] if post.ab_variant == "A" else content["caption_b"]

    # Mutate the post object in-place (calendar is mutable)
    post.caption       = caption
    post.hashtags      = content.get("hashtags", [])
    post.virality_score = float(content.get("virality_score", 50))

    return {
        "caption":     caption,
        "hook":        content.get("hook", ""),
        "hashtags":    content.get("hashtags", []),
        "reel_script": content.get("reel_script", ""),
        "ab_captions": {
            "A": content.get("caption_a", ""),
            "B": content.get("caption_b", ""),
        },
        "virality_score": float(content.get("virality_score", 50)),
    }


# ─── Scoring helpers (standalone utility) ───────────────────────────────────

def score_virality(caption: str, hashtag_count: int, post_type: PostType) -> float:
    """
    Rule-based virality scorer — supplements the LLM score.
    Returns 0–100. Use to rank multiple caption drafts.
    """
    score = 50.0

    # Hook analysis
    first_line = caption.split("\n")[0]
    if len(first_line) <= 60:       score += 10
    if any(c in first_line for c in ["?", "!", "…"]): score += 5
    if any(w in first_line.lower() for w in ["you", "your", "we"]): score += 5

    # Emoji presence
    emoji_count = sum(1 for c in caption if ord(c) > 127)
    score += min(emoji_count * 1.5, 10)

    # CTA presence
    cta_words = ["link in bio", "grab your", "tickets", "register", "swipe up"]
    if any(w in caption.lower() for w in cta_words): score += 10

    # Post type bonus
    if post_type == PostType.REEL: score += 8

    # Hashtag sweet spot: 20-30
    if 20 <= hashtag_count <= 30: score += 7

    return min(round(score, 1), 100.0)


def _fallback_content(event_name: str, theme: ContentTheme) -> dict:
    return {
        "hook": f"Something big is coming. 👀",
        "caption_a": f"Get ready for {event_name}. This is the one you can't miss.\n\nLink in bio for tickets. 🎵",
        "caption_b": f"You asked for it. {event_name} is here.\n\nGrab your spot. Link in bio.",
        "reel_script": "",
        "hashtags": ["#music", "#event", "#college", "#vibes", "#livemusic"],
        "virality_score": 45,
        "virality_reasoning": "Fallback content — LLM parse failed",
    }
