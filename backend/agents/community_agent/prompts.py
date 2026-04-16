# prompts.py
# ─────────────────────────────────────────────────────────────────────────────
# Prompt Engineering Layer
# All LLM prompt templates are centralized here for easy tuning.
# Prompts are designed to be:
#   - Non-spammy and Reddit-safe
#   - Artist-aware and context-sensitive
#   - Focused on organic, community-first promotion
# ─────────────────────────────────────────────────────────────────────────────

from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate


# ─── System Prompt ─────────────────────────────────────────────────────────────
# Sets the agent's persona and guardrails for all LLM calls.

SYSTEM_PROMPT = """You are a senior community marketing strategist specializing in organic promotion for live music events on Reddit and Discord.

Your core philosophy:
- Communities first, promotion second. You never suggest spammy or direct "buy tickets" tactics.
- Every recommendation must feel like a natural part of the community, not an ad.
- You are deeply aware of how Reddit moderation works and what triggers spam filters or bans.
- You understand artist fanbases, their culture, language, and online behavior.
- You write like a passionate music fan, not a marketer.

Hard rules you always follow:
1. Never suggest posting in subreddits where the self-promo rules explicitly disallow it without a workaround.
2. Always suggest organic framing (e.g. "excited to share" vs "BUY TICKETS NOW").
3. Reddit post titles must not contain promotional language — they should feel like genuine community contributions.
4. Discord messages must be warm, fan-to-fan in tone — never a press release.
5. Flag high-risk subreddits clearly and explain why.

Output format: Always return valid, parseable JSON with no markdown fences, no preamble, no explanation outside the JSON object."""


# ─── Reddit Refinement Prompt ─────────────────────────────────────────────────
# Takes pre-filtered subreddits from the knowledge base and has the LLM
# generate posting strategies, example posts, and relevance scoring.

REDDIT_REFINEMENT_TEMPLATE = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
    HumanMessagePromptTemplate.from_template("""
You are given a list of pre-filtered subreddits relevant to an upcoming music event.
Your job is to enrich each subreddit with:
1. A tailored posting strategy (organic, community-safe)
2. A realistic example post title + first paragraph
3. An artist_relevance_score from 0.0 to 1.0 based on how closely this community aligns with the artist

EVENT CONTEXT:
- Event type: {event_type}
- Artist: {artist}
- Genre / vibe: {genre}
- Target audience: {audience}
- Location: {location}
- Additional vibe notes: {vibe}

PRE-FILTERED SUBREDDITS (with base data):
{subreddits_json}

INSTRUCTIONS:
- For each subreddit, generate a "posting_strategy" that respects the community's self-promo rules.
- The "example_post" should be a complete, ready-to-use Reddit post (title + opening paragraph).
  - Post title must NOT contain words like "buy", "tickets", "promo", "discount"
  - Post body must feel like a community member sharing something they're genuinely excited about
  - Reference the artist naturally, as if you're a fan
- "artist_relevance_score" should reflect: does this artist's fanbase actually live in this subreddit?
  Score 0.9+ = artist has a dedicated following here
  Score 0.5-0.8 = genre overlap but not artist-specific
  Score <0.5 = loose connection, audience overlap only
- "why_relevant" must be specific to THIS artist + THIS subreddit, not generic

Return a JSON array with this exact schema per item:
{{
  "subreddit": "string",
  "target_audience": "string",
  "why_relevant": "string (artist-specific, not generic)",
  "posting_strategy": "string (step-by-step, community-safe)",
  "example_post": "string (title\\n\\nbody paragraph)",
  "risk_level": "low | medium | high",
  "artist_relevance_score": float,
  "audience_match_score": float,
  "engagement_score": float
}}

Return ONLY the JSON array. No markdown. No explanation. No preamble.
""")
])


# ─── Discord Refinement Prompt ────────────────────────────────────────────────
# Generates Discord promotion strategies and message templates for each archetype.

DISCORD_REFINEMENT_TEMPLATE = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
    HumanMessagePromptTemplate.from_template("""
You are given a list of Discord server archetypes relevant to an upcoming music event.
Your job is to generate a personalized promotion strategy and message template for each server type.

EVENT CONTEXT:
- Event type: {event_type}
- Artist: {artist}
- Genre / vibe: {genre}
- Target audience: {audience}
- Location: {location}
- Additional vibe notes: {vibe}

PRE-FILTERED DISCORD ARCHETYPES:
{discord_json}

INSTRUCTIONS:
- For each server type, write a "promotion_strategy" that explains HOW to engage authentically
  before dropping any event info. E.g. join, participate for a few days, then share in promo channel.
- The "message_template" must be:
  - Written in fan-to-fan language (no corporate tone)
  - Short (under 100 words)
  - Include a call to action that feels like genuine excitement, not a sales pitch
  - Mention the artist name and location naturally
  - Should fit in a Discord server's #events or #announcements or #self-promo channel
- "how_to_find" should be specific and actionable — not just "search Google"

Return a JSON array with this exact schema per item:
{{
  "server_type": "string",
  "target_audience": "string",
  "how_to_find": "string (specific, actionable steps)",
  "promotion_strategy": "string (step-by-step authentic approach)",
  "message_template": "string (ready-to-send Discord message)"
}}

Return ONLY the JSON array. No markdown. No explanation. No preamble.
""")
])


# ─── Artist Analysis Prompt ───────────────────────────────────────────────────
# Used in a quick pre-pass to extract artist metadata that improves matching.
# This runs first and informs the filtering logic.

ARTIST_ANALYSIS_TEMPLATE = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
    HumanMessagePromptTemplate.from_template("""
Analyze the following music artist and extract community intelligence that will help target the right online communities for event promotion.

Artist: {artist}
Genre: {genre}
Location context: {location}

Provide a JSON object with:
{{
  "artist_tags": ["list of tags describing artist type and style"],
  "fanbase_description": "one sentence describing who the typical fan is",
  "known_subreddits": ["list of subreddit names (without r/) where this artist's fans are active — be specific"],
  "fanbase_age_range": "e.g. 18-28",
  "fanbase_culture_keywords": ["keywords that describe fan culture, e.g. 'streetwear', 'festival', 'underground'"],
  "similar_artists": ["2-3 similar artists that fans also follow"],
  "popularity_tier": "emerging | mid-tier | mainstream | legendary"
}}

Return ONLY the JSON object. No markdown. No explanation.
""")
])
