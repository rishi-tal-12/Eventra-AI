"""
agents/creative_agent.py
------------------------
Creative Agent — generates poster/image for a post and uploads it to
a publicly accessible URL (required by Instagram Graph API).

INPUT:  state["calendar"], state["current_post_index"]
OUTPUT: state["image_url"]  (public URL Instagram can fetch)

Flow:
  1. Build a detailed image prompt from event details + post theme
  2. Call DALL-E 3 (or Stable Diffusion) to generate the image
  3. Upload to Cloudinary (or S3) → get a public URL
  4. Store the URL on the ScheduledPost object

IMPORTANT: Instagram API requires the image URL to be publicly
accessible for at least 1 hour. Local file paths won't work.
"""

import io
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
import requests
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from openai import OpenAI

from agents.instagram_agent.core.config import settings
from agents.instagram_agent.core.models import AgentState, ContentTheme, ScheduledPost


# ─── Image prompt builder ───────────────────────────────────────────────────

IMAGE_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", """You are a creative director for a music event design agency.
You write DALL-E 3 image generation prompts that produce stunning posters.

Rules:
- Describe composition, lighting, color palette, mood
- Include text overlay instructions as a note (DALL-E often ignores text)
- Never mention copyrighted characters or real people
- Lean into the event vibe: {vibe}
- Output ONE concise prompt paragraph, max 200 words. No JSON, no fences."""),

    ("human", """Create a DALL-E 3 prompt for an Instagram post with these details:

Event: {event_name}
Theme: {theme}
Post type: {post_type}
Genres: {genres}
Artists (abstract reference only): {artist_count} performers
Venue vibe: {venue}
Days before event: {days_before}
Extra hints from strategy: {image_prompt_hint}

Make it feel premium, electric, and perfect for college Instagram."""),
])


# ─── Agent node ─────────────────────────────────────────────────────────────

def creative_agent(state: AgentState) -> AgentState:
    """
    Generates an image for the current post and returns its public URL.
    If image generation fails, returns an empty URL (Scheduler handles fallback).
    """
    calendar = state["calendar"]
    idx      = state.get("current_post_index", 0)
    post: ScheduledPost = calendar.posts[idx]
    event = calendar.event

    # Step 1: Build a rich image prompt
    image_prompt = _build_image_prompt(post, event)
    post.image_prompt = image_prompt

    # Step 2: Generate image
    image_bytes: Optional[bytes] = None
    try:
        image_bytes = _generate_with_dalle(image_prompt)
    except Exception as e:
        errors = list(state.get("errors", []))
        errors.append(f"DALL-E error for post {post.id}: {e}")
        state["errors"] = errors

    # Step 3: Upload to public hosting
    public_url = ""
    if image_bytes:
        try:
            public_url = _upload_to_cloudinary(image_bytes, post.id)
        except Exception as e:
            # Fallback: save locally (won't work with IG API in prod)
            local_path = _save_locally(image_bytes, post.id)
            errors = list(state.get("errors", []))
            errors.append(f"Cloudinary upload failed, saved locally: {local_path}. Error: {e}")
            state["errors"] = errors

    post.image_url = public_url

    return {
        "image_prompt": image_prompt,
        "image_url":    public_url,
    }


# ─── Image generation backends ──────────────────────────────────────────────

def _generate_with_dalle(prompt: str) -> bytes:
    """
    Call DALL-E 3 and return raw image bytes.
    Cost: ~$0.04 per image (1024x1024 standard quality).
    """
    #client = OpenAI(api_key=settings.OPENAI_API_KEY)

    '''response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024",
        quality="standard",   # "hd" costs 2x but looks better for hero posts
        response_format="url",
    )

    image_url = response.data[0].url
    image_bytes = httpx.get(image_url, timeout=30).content
    return image_bytes'''
    raise NotImplementedError("Image generation disabled in offline mode")


def _generate_with_stable_diffusion(prompt: str) -> bytes:
    """
    Alternative: Use Stability AI API (cheaper, more control).
    Requires STABILITY_API_KEY in .env
    """
    import base64
    api_key = os.getenv("STABILITY_API_KEY", "")
    if not api_key:
        raise ValueError("STABILITY_API_KEY not set")

    response = requests.post(
        "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        json={
            "text_prompts": [
                {"text": prompt, "weight": 1},
                {"text": "blurry, low quality, text, watermark", "weight": -1},
            ],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "steps": 30,
            "samples": 1,
        },
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    return base64.b64decode(data["artifacts"][0]["base64"])


# ─── Image upload ────────────────────────────────────────────────────────────

def _upload_to_cloudinary(image_bytes: bytes, post_id: str) -> str:
    """
    Upload image to Cloudinary and return a permanent public URL.
    Free tier: 25 credits/month — more than enough for 15 posts.
    """
    import cloudinary
    import cloudinary.uploader

    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
    )

    result = cloudinary.uploader.upload(
        image_bytes,
        public_id=f"instagram_agent/{post_id}",
        folder="instagram_posts",
        resource_type="image",
        format="jpg",
    )

    return result["secure_url"]


def _save_locally(image_bytes: bytes, post_id: str) -> str:
    """Dev fallback: save image to disk."""
    output_dir = Path("generated_images")
    output_dir.mkdir(exist_ok=True)
    path = output_dir / f"{post_id}.jpg"
    path.write_bytes(image_bytes)
    return str(path)


# ─── Prompt builder ─────────────────────────────────────────────────────────

def _build_image_prompt(post: ScheduledPost, event) -> str:
    """Use LLM to expand the strategy hint into a full DALL-E prompt."""
    #llm   = ChatOpenAI(model="gpt-4o", temperature=0.6)
    llm = ChatOllama(model="llama3.2", temperature=0.75)
    chain = IMAGE_PROMPT_TEMPLATE | llm | StrOutputParser()

    return chain.invoke({
        "vibe":              event.vibe,
        "event_name":        event.name,
        "theme":             post.theme.value,
        "post_type":         post.post_type.value,
        "genres":            ", ".join(event.genres) or "electronic",
        "artist_count":      len(event.artists),
        "venue":             event.venue,
        "days_before":       post.days_before_event,
        "image_prompt_hint": post.image_prompt or "energetic crowd scene",
    })
