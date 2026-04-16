# utils.py
# ─────────────────────────────────────────────────────────────────────────────
# Utility Layer: Matching, Scoring, Filtering
# All deterministic logic lives here — no LLM calls.
# This layer runs BEFORE the LLM to reduce token usage and improve precision.
# ─────────────────────────────────────────────────────────────────────────────

import json
import re
from loguru import logger

from .community_data import (
    SUBREDDITS,
    DISCORD_ARCHETYPES,
    GENRE_ALIASES,
    AUDIENCE_ALIASES,
    LOCATION_ALIASES,
    SubredditEntry,
    DiscordArchetype,
)


# ─────────────────────────────────────────────────────────────────────────────
# Tag Expansion
# Converts raw user input strings into normalized internal tag lists
# using the alias taxonomy defined in community_data.py
# ─────────────────────────────────────────────────────────────────────────────

def expand_genre_tags(genre_input: str) -> list[str]:
    """
    Normalize and expand a genre string into a list of matching internal tags.
    E.g. "bass music" → ["bass", "edm", "electronic"]
    """
    normalized = genre_input.lower().strip()
    expanded: set[str] = {normalized}

    for key, aliases in GENRE_ALIASES.items():
        if key in normalized or any(a in normalized for a in aliases):
            expanded.update(aliases)
            expanded.add(key)

    logger.debug(f"Genre '{genre_input}' → tags: {expanded}")
    return list(expanded)


def expand_audience_tags(audience_input: str) -> list[str]:
    """
    Normalize and expand an audience string into matching internal tags.
    E.g. "college students" → ["students", "college students", "18-24", ...]
    """
    normalized = audience_input.lower().strip()
    expanded: set[str] = {normalized}

    for key, aliases in AUDIENCE_ALIASES.items():
        if key in normalized or any(a in normalized for a in aliases):
            expanded.update(aliases)
            expanded.add(key)

    logger.debug(f"Audience '{audience_input}' → tags: {expanded}")
    return list(expanded)


def expand_location_tags(location_input: str) -> list[str]:
    """
    Normalize and expand a location string into matching internal tags.
    Always includes "global" as a fallback.
    E.g. "Mumbai" → ["mumbai", "india", "global indians", "global"]
    """
    normalized = location_input.lower().strip()
    expanded: set[str] = {normalized, "global"}  # always include global

    for key, aliases in LOCATION_ALIASES.items():
        if key in normalized:
            expanded.update(aliases)
            expanded.add(key)

    logger.debug(f"Location '{location_input}' → tags: {expanded}")
    return list(expanded)


def extract_artist_tags(artist: str, genre: str) -> list[str]:
    """
    Create a set of artist-derived tags for matching.
    Combines the artist name (lowercased, split) with genre-derived artist types.
    """
    tags: set[str] = set()

    # Add artist name parts (handles e.g. "Billie Eilish" → ["billie", "eilish"])
    for part in artist.lower().split():
        if len(part) > 2:
            tags.add(part)

    # Add genre-derived artist type tags
    genre_lower = genre.lower()
    if any(g in genre_lower for g in ["edm", "electronic", "house", "techno", "bass", "trance"]):
        tags.update(["dj", "electronic artist", "producer"])
    if any(g in genre_lower for g in ["hip hop", "rap", "trap"]):
        tags.update(["rapper", "hip hop artist"])
    if any(g in genre_lower for g in ["indie", "alternative"]):
        tags.update(["indie artist", "singer-songwriter"])
    if any(g in genre_lower for g in ["bollywood", "desi", "bhangra"]):
        tags.update(["bollywood artist", "desi artist", "indian musician"])
    if any(g in genre_lower for g in ["metal", "punk", "hardcore"]):
        tags.update(["metal band", "punk band"])
    if any(g in genre_lower for g in ["jazz", "classical", "folk"]):
        tags.update(["jazz musician", "classical musician", "folk artist"])

    # Always add generic fallback
    tags.update(["emerging", "all", "all artists"])

    logger.debug(f"Artist '{artist}' → tags: {tags}")
    return list(tags)


# ─────────────────────────────────────────────────────────────────────────────
# Tag Overlap Scoring
# Computes normalized Jaccard-style overlap between two tag sets.
# ─────────────────────────────────────────────────────────────────────────────

def tag_overlap_score(user_tags: list[str], community_tags: list[str]) -> float:
    """
    Returns a 0.0–1.0 score for how much the user's expanded tags
    overlap with a community's tags. Uses substring matching for flexibility.
    """
    if not user_tags or not community_tags:
        return 0.0

    user_set = {t.lower() for t in user_tags}
    comm_set = {t.lower() for t in community_tags}

    matches = 0
    for ut in user_set:
        for ct in comm_set:
            if ut in ct or ct in ut:
                matches += 1
                break  # count each user tag at most once

    score = matches / max(len(user_set), 1)
    return round(min(score, 1.0), 3)


# ─────────────────────────────────────────────────────────────────────────────
# Subreddit Scoring & Filtering
# ─────────────────────────────────────────────────────────────────────────────

def score_subreddit(
    sub: SubredditEntry,
    genre_tags: list[str],
    audience_tags: list[str],
    location_tags: list[str],
    artist_tags: list[str],
    artist_intel: dict,
) -> dict:
    """
    Scores a subreddit across three dimensions:
    - audience_match_score: how well the subreddit audience matches
    - engagement_score: adjusted engagement based on promotion friendliness
    - artist_relevance_score: preliminary estimate (LLM will refine this)

    Returns a dict merging the subreddit entry with computed scores.
    """
    audience_score = tag_overlap_score(audience_tags, sub["audience_tags"])
    genre_score = tag_overlap_score(genre_tags, sub["genre_tags"])
    location_score = tag_overlap_score(location_tags, sub["location_tags"])
    artist_score = tag_overlap_score(artist_tags, sub["artist_tags"])

    # Check if LLM artist intel mentions this subreddit explicitly
    known_subs = [s.lower() for s in artist_intel.get("known_subreddits", [])]
    if sub["name"].lower() in known_subs:
        artist_score = min(artist_score + 0.4, 1.0)  # boost for explicit match
        logger.debug(f"  r/{sub['name']}: artist intel boost applied")

    # Promotion friendliness multiplier on engagement
    friendliness_multiplier = {"high": 1.0, "medium": 0.8, "low": 0.5}.get(
        sub["promotion_friendliness"], 0.7
    )
    engagement_score = round(sub["base_engagement_score"] * friendliness_multiplier, 3)

    # Composite relevance = weighted combination
    composite = (
        audience_score * 0.30
        + genre_score * 0.30
        + location_score * 0.20
        + artist_score * 0.20
    )

    return {
        **sub,
        "audience_match_score": round(audience_score, 3),
        "engagement_score": engagement_score,
        "artist_relevance_score": round(artist_score, 3),
        "_composite_score": round(composite, 3),
    }


def filter_and_rank_subreddits(
    genre_tags: list[str],
    audience_tags: list[str],
    location_tags: list[str],
    artist_tags: list[str],
    artist_intel: dict,
    top_n: int = 6,
    min_composite: float = 0.15,
) -> list[dict]:
    """
    Scores all subreddits in the knowledge base, filters out low-relevance ones,
    and returns the top N sorted by composite score.
    """
    scored = []
    for sub in SUBREDDITS:
        result = score_subreddit(
            sub, genre_tags, audience_tags, location_tags, artist_tags, artist_intel
        )
        if result["_composite_score"] >= min_composite:
            scored.append(result)
        else:
            logger.debug(f"  r/{sub['name']} filtered out (composite={result['_composite_score']})")

    scored.sort(key=lambda x: x["_composite_score"], reverse=True)
    top = scored[:top_n]

    logger.info(f"Subreddit filter: {len(SUBREDDITS)} → {len(scored)} eligible → top {len(top)} selected")
    for s in top:
        logger.debug(f"  r/{s['name']} | composite={s['_composite_score']} | promo={s['promotion_friendliness']}")

    return top


# ─────────────────────────────────────────────────────────────────────────────
# Discord Archetype Scoring & Filtering
# ─────────────────────────────────────────────────────────────────────────────

def score_discord_archetype(
    archetype: DiscordArchetype,
    genre_tags: list[str],
    audience_tags: list[str],
    location_tags: list[str],
    artist_intel: dict,
) -> dict:
    """
    Scores a Discord archetype for relevance to the event.
    """
    audience_score = tag_overlap_score(audience_tags, archetype["audience_tags"])
    genre_score = tag_overlap_score(genre_tags, archetype["genre_tags"])
    location_score = tag_overlap_score(location_tags, archetype["location_tags"])

    friendliness_multiplier = {"high": 1.0, "medium": 0.8, "low": 0.5}.get(
        archetype["friendliness"], 0.7
    )

    composite = (
        audience_score * 0.35
        + genre_score * 0.35
        + location_score * 0.30
    ) * friendliness_multiplier

    return {
        **archetype,
        "_composite_score": round(composite, 3),
    }


def filter_and_rank_discord(
    genre_tags: list[str],
    audience_tags: list[str],
    location_tags: list[str],
    artist_intel: dict,
    top_n: int = 4,
    min_composite: float = 0.10,
) -> list[dict]:
    """
    Scores all Discord archetypes, filters low-relevance ones,
    returns top N sorted by composite score.
    """
    scored = []
    for arch in DISCORD_ARCHETYPES:
        result = score_discord_archetype(arch, genre_tags, audience_tags, location_tags, artist_intel)
        if result["_composite_score"] >= min_composite:
            scored.append(result)

    scored.sort(key=lambda x: x["_composite_score"], reverse=True)
    top = scored[:top_n]

    logger.info(f"Discord filter: {len(DISCORD_ARCHETYPES)} → {len(scored)} eligible → top {len(top)} selected")
    return top


# ─────────────────────────────────────────────────────────────────────────────
# JSON Parsing Utilities
# ─────────────────────────────────────────────────────────────────────────────

def safe_parse_json(raw: str) -> list | dict | None:
    """
    Safely parses a JSON string from the LLM response.
    Handles common LLM quirks:
    - Markdown code fences (```json ... ```)
    - Leading/trailing whitespace
    - Occasional preamble text before the JSON
    """
    # Strip markdown fences if present
    clean = re.sub(r"```(?:json)?", "", raw).strip()
    clean = clean.rstrip("`").strip()

    # If the LLM added preamble text, try to find JSON start
    json_start = clean.find("[")
    obj_start = clean.find("{")

    if json_start == -1 and obj_start == -1:
        logger.error("No JSON structure found in LLM response")
        return None

    # Use whichever comes first
    if json_start != -1 and (obj_start == -1 or json_start < obj_start):
        clean = clean[json_start:]
    elif obj_start != -1:
        clean = clean[obj_start:]

    try:
        return json.loads(clean)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}\nRaw (first 500 chars): {clean[:500]}")
        return None


def serialize_for_prompt(data: list[dict]) -> str:
    """
    Serializes a list of dicts to a clean JSON string for inclusion in prompts.
    Removes internal scoring keys (prefixed with _) to reduce noise.
    """
    clean = []
    for item in data:
        clean.append({k: v for k, v in item.items() if not k.startswith("_")})
    return json.dumps(clean, indent=2, ensure_ascii=False)
