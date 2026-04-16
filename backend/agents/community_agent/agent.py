# agent.py
# ─────────────────────────────────────────────────────────────────────────────
# Community Recommendation Agent — Main Orchestration Layer
#
# Pipeline:
#   1. Validate input (Pydantic)
#   2. Run artist analysis (LLM pre-pass)
#   3. Expand tags and score/filter communities (deterministic)
#   4. Refine with LLM — generate strategies, posts, Discord messages
#   5. Validate & return structured output (Pydantic)
#
# LLM backend: Ollama (open-source, local) via LangChain's ChatOllama.
# Fallback model config is in the environment / .env file.
# ─────────────────────────────────────────────────────────────────────────────

import os
import json
from typing import Optional

from loguru import logger
from pydantic import BaseModel, Field, field_validator

# LangChain — Ollama (open-source, runs locally via Ollama server)
# Install: https://ollama.com  |  Run: ollama pull mistral or llama3
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

from .prompts import (
    SYSTEM_PROMPT,
    REDDIT_REFINEMENT_TEMPLATE,
    DISCORD_REFINEMENT_TEMPLATE,
    ARTIST_ANALYSIS_TEMPLATE,
)
from .utils import (
    expand_genre_tags,
    expand_audience_tags,
    expand_location_tags,
    extract_artist_tags,
    filter_and_rank_subreddits,
    filter_and_rank_discord,
    safe_parse_json,
    serialize_for_prompt,
)


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

# Default Ollama model — change to any model you have pulled locally.
# Recommended options:
#   "mistral"        → fast, good instruction following (~4GB)
#   "llama3"         → best quality (~8GB)
#   "llama3:8b-instruct-q4_0" → quantized, faster
#   "mixtral"        → highest quality (~26GB, needs strong GPU)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# How many communities to fetch per category
TOP_SUBREDDITS = int(os.getenv("TOP_SUBREDDITS", "5"))
TOP_DISCORD = int(os.getenv("TOP_DISCORD", "4"))


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic Schemas — Input
# ─────────────────────────────────────────────────────────────────────────────

class CommunityAgentInput(BaseModel):
    """Validated input for the community recommendation agent."""

    event_type: str = Field(..., min_length=2, description="Type of event, e.g. 'Live concert', 'DJ night'")
    artist: str = Field(..., min_length=1, description="Artist or performer name")
    genre: str = Field(..., min_length=2, description="Music genre or style")
    audience: str = Field(..., min_length=2, description="Target audience description")
    location: str = Field(..., min_length=2, description="City or region of the event")
    vibe: str = Field(default="", description="Optional additional vibe/mood notes")

    @field_validator("artist", "genre", "location", "audience", "event_type")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic Schemas — Output
# ─────────────────────────────────────────────────────────────────────────────

class SubredditRecommendation(BaseModel):
    subreddit: str
    target_audience: str
    why_relevant: str
    posting_strategy: str
    example_post: str
    risk_level: str = Field(pattern="^(low|medium|high)$")
    artist_relevance_score: float = Field(ge=0.0, le=1.0)
    audience_match_score: float = Field(ge=0.0, le=1.0)
    engagement_score: float = Field(ge=0.0, le=1.0)


class DiscordRecommendation(BaseModel):
    server_type: str
    target_audience: str
    how_to_find: str
    promotion_strategy: str
    message_template: str


class CommunityAgentOutput(BaseModel):
    reddit: list[SubredditRecommendation]
    discord: list[DiscordRecommendation]


# ─────────────────────────────────────────────────────────────────────────────
# LLM Client Factory
# ─────────────────────────────────────────────────────────────────────────────

def get_llm() -> ChatOllama:
    """
    Returns a configured ChatOllama instance.
    ChatOllama connects to a locally running Ollama server.
    Make sure Ollama is running: `ollama serve`
    And the model is pulled: `ollama pull mistral`
    """
    logger.info(f"Initializing LLM: model={OLLAMA_MODEL} base_url={OLLAMA_BASE_URL}")
    return ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.7,      # slightly creative but stable
        format="json",        # enforce JSON output mode (Ollama feature)
        num_predict=2048,     # max tokens per response
    )


# ─────────────────────────────────────────────────────────────────────────────
# Step 1 — Artist Intelligence Pre-Pass
# ─────────────────────────────────────────────────────────────────────────────

def run_artist_analysis(llm: ChatOllama, artist: str, genre: str, location: str) -> dict:
    """
    Runs a lightweight LLM call to extract artist community intelligence.
    This enriches the tag-matching step with artist-specific subreddit knowledge.
    Returns empty dict gracefully if LLM call fails.
    """
    logger.info(f"Running artist analysis for: {artist}")

    try:
        prompt = ARTIST_ANALYSIS_TEMPLATE.format_messages(
            artist=artist,
            genre=genre,
            location=location,
        )
        response = llm.invoke(prompt)
        result = safe_parse_json(response.content)

        if isinstance(result, dict):
            logger.info(
                f"Artist intel: tier={result.get('popularity_tier')} | "
                f"known_subs={result.get('known_subreddits', [])}"
            )
            return result
        else:
            logger.warning("Artist analysis returned unexpected format. Using empty intel.")
            return {}

    except Exception as e:
        logger.warning(f"Artist analysis failed (non-fatal): {e}")
        return {}


# ─────────────────────────────────────────────────────────────────────────────
# Step 2 — Reddit Refinement
# ─────────────────────────────────────────────────────────────────────────────

def run_reddit_refinement(
    llm: ChatOllama,
    input_data: CommunityAgentInput,
    candidate_subreddits: list[dict],
) -> list[SubredditRecommendation]:
    """
    Sends pre-filtered subreddits to the LLM for deep refinement:
    - Personalized posting strategies
    - Organic example posts
    - Refined artist relevance scoring
    """
    logger.info(f"Refining {len(candidate_subreddits)} subreddits with LLM...")

    subreddits_json = serialize_for_prompt(candidate_subreddits)

    try:
        prompt = REDDIT_REFINEMENT_TEMPLATE.format_messages(
            event_type=input_data.event_type,
            artist=input_data.artist,
            genre=input_data.genre,
            audience=input_data.audience,
            location=input_data.location,
            vibe=input_data.vibe or "No additional vibe notes.",
            subreddits_json=subreddits_json,
        )
        response = llm.invoke(prompt)
        raw = safe_parse_json(response.content)

        if not isinstance(raw, list):
            logger.error("Reddit refinement did not return a list. Falling back to base scores.")
            return _fallback_reddit(candidate_subreddits)

        results = []
        for item in raw:
            try:
                results.append(SubredditRecommendation(**_sanitize_reddit_item(item)))
            except Exception as e:
                logger.warning(f"Skipping malformed subreddit item: {e} | item={item}")

        logger.info(f"Reddit refinement: {len(results)} valid recommendations")
        return results

    except Exception as e:
        logger.error(f"Reddit refinement LLM call failed: {e}")
        return _fallback_reddit(candidate_subreddits)


def _sanitize_reddit_item(item: dict) -> dict:
    """Ensures all required fields exist and types are correct."""
    return {
        "subreddit": str(item.get("subreddit", "unknown")),
        "target_audience": str(item.get("target_audience", "")),
        "why_relevant": str(item.get("why_relevant", "")),
        "posting_strategy": str(item.get("posting_strategy", "")),
        "example_post": str(item.get("example_post", "")),
        "risk_level": str(item.get("risk_level", "medium")).lower(),
        "artist_relevance_score": float(item.get("artist_relevance_score", 0.5)),
        "audience_match_score": float(item.get("audience_match_score", 0.5)),
        "engagement_score": float(item.get("engagement_score", 0.5)),
    }


def _fallback_reddit(candidates: list[dict]) -> list[SubredditRecommendation]:
    """
    Fallback: if LLM fails, return base-scored subreddits with placeholder strategies.
    Ensures the agent always returns something useful.
    """
    results = []
    for s in candidates:
        results.append(SubredditRecommendation(
            subreddit=s["name"],
            target_audience=", ".join(s["audience_tags"]),
            why_relevant=s["description"],
            posting_strategy=s["self_promo_rules"],
            example_post="[LLM refinement unavailable — generate manually]",
            risk_level={"high": "high", "medium": "medium", "low": "low"}.get(
                s["promotion_friendliness"], "medium"
            ),
            artist_relevance_score=s.get("artist_relevance_score", 0.5),
            audience_match_score=s.get("audience_match_score", 0.5),
            engagement_score=s.get("engagement_score", 0.5),
        ))
    return results


# ─────────────────────────────────────────────────────────────────────────────
# Step 3 — Discord Refinement
# ─────────────────────────────────────────────────────────────────────────────

def run_discord_refinement(
    llm: ChatOllama,
    input_data: CommunityAgentInput,
    candidate_archetypes: list[dict],
) -> list[DiscordRecommendation]:
    """
    Sends pre-filtered Discord archetypes to the LLM for deep refinement:
    - Specific server discovery instructions
    - Authentic promotion strategies
    - Ready-to-send message templates
    """
    logger.info(f"Refining {len(candidate_archetypes)} Discord archetypes with LLM...")

    discord_json = serialize_for_prompt(candidate_archetypes)

    try:
        prompt = DISCORD_REFINEMENT_TEMPLATE.format_messages(
            event_type=input_data.event_type,
            artist=input_data.artist,
            genre=input_data.genre,
            audience=input_data.audience,
            location=input_data.location,
            vibe=input_data.vibe or "No additional vibe notes.",
            discord_json=discord_json,
        )
        response = llm.invoke(prompt)
        raw = safe_parse_json(response.content)

        if not isinstance(raw, list):
            logger.error("Discord refinement did not return a list. Falling back to base data.")
            return _fallback_discord(candidate_archetypes)

        results = []
        for item in raw:
            try:
                results.append(DiscordRecommendation(**_sanitize_discord_item(item)))
            except Exception as e:
                logger.warning(f"Skipping malformed Discord item: {e} | item={item}")

        logger.info(f"Discord refinement: {len(results)} valid recommendations")
        return results

    except Exception as e:
        logger.error(f"Discord refinement LLM call failed: {e}")
        return _fallback_discord(candidate_archetypes)


def _sanitize_discord_item(item: dict) -> dict:
    return {
        "server_type": str(item.get("server_type", "")),
        "target_audience": str(item.get("target_audience", "")),
        "how_to_find": str(item.get("how_to_find", "")),
        "promotion_strategy": str(item.get("promotion_strategy", "")),
        "message_template": str(item.get("message_template", "")),
    }


def _fallback_discord(candidates: list[dict]) -> list[DiscordRecommendation]:
    results = []
    for a in candidates:
        results.append(DiscordRecommendation(
            server_type=a["server_type"],
            target_audience=", ".join(a["audience_tags"]),
            how_to_find=a["how_to_find"],
            promotion_strategy="[LLM refinement unavailable — generate manually]",
            message_template="[LLM refinement unavailable — generate manually]",
        ))
    return results


# ─────────────────────────────────────────────────────────────────────────────
# Main Public API
# ─────────────────────────────────────────────────────────────────────────────

def recommend_communities(input_data: dict, memory: dict = None) -> dict:
    """
    Main entry point for the Community Recommendation Agent.

    Args:
        input_data: dict with keys:
            - event_type (str)
            - artist (str)
            - genre (str)
            - audience (str)
            - location (str)
            - vibe (str, optional)

    Returns:
        dict with keys:
            - reddit: list of SubredditRecommendation dicts
            - discord: list of DiscordRecommendation dicts

    Raises:
        ValueError: if input validation fails
        RuntimeError: if both LLM and fallback fail
    """
    logger.info("=" * 60)
    logger.info("Community Recommendation Agent — START")
    logger.info("=" * 60)

    # ── 1. Validate Input ───────────────────────────────────────────
    try:
        validated = CommunityAgentInput(**input_data)
        logger.info(f"Input validated: artist={validated.artist} | location={validated.location}")
    except Exception as e:
        logger.error(f"Input validation failed: {e}")
        raise ValueError(f"Invalid input: {e}")

    # ── 2. Initialize LLM ───────────────────────────────────────────
    llm = get_llm()

    # ── 3. Artist Intelligence Pre-Pass ────────────────────────────
    artist_intel = run_artist_analysis(llm, validated.artist, validated.genre, validated.location)

    # ── 4. Expand Tags ──────────────────────────────────────────────
    genre_tags = expand_genre_tags(validated.genre)
    audience_tags = expand_audience_tags(validated.audience)
    location_tags = expand_location_tags(validated.location)
    artist_tags = extract_artist_tags(validated.artist, validated.genre)

    logger.info(f"Tags expanded | genre={len(genre_tags)} | audience={len(audience_tags)} | location={len(location_tags)} | artist={len(artist_tags)}")

    # ── 5. Score & Filter Communities ──────────────────────────────
    candidate_subreddits = filter_and_rank_subreddits(
        genre_tags, audience_tags, location_tags, artist_tags, artist_intel,
        top_n=TOP_SUBREDDITS,
    )
    candidate_discord = filter_and_rank_discord(
        genre_tags, audience_tags, location_tags, artist_intel,
        top_n=TOP_DISCORD,
    )

    if not candidate_subreddits:
        logger.warning("No subreddits passed the filter threshold. Lowering threshold and retrying...")
        candidate_subreddits = filter_and_rank_subreddits(
            genre_tags, audience_tags, location_tags, artist_tags, artist_intel,
            top_n=TOP_SUBREDDITS, min_composite=0.05,
        )

    # ── 6. LLM Refinement ──────────────────────────────────────────
    reddit_recs = run_reddit_refinement(llm, validated, candidate_subreddits)
    discord_recs = run_discord_refinement(llm, validated, candidate_discord)

    # ── 7. Build & Validate Output ─────────────────────────────────
    output = CommunityAgentOutput(reddit=reddit_recs, discord=discord_recs)

    logger.info(f"Agent complete | reddit={len(output.reddit)} | discord={len(output.discord)}")
    logger.info("=" * 60)

    return output.model_dump()
