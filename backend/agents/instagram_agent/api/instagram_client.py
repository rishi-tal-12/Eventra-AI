"""
api/instagram_client.py
-----------------------
Thin wrapper around the Instagram Graph API.

Instagram posting flow (MANDATORY - can't skip steps):
  1. Create a media container  →  returns ig_container_id
  2. Wait for container to be ready (poll status)
  3. Publish the container      →  returns ig_post_id

Posting limits (as of 2024):
  - 50 API-created posts per 24-hour rolling window
  - 25 stories per day
  - Rate limit: 200 calls per hour per token

Auth requirements:
  - Instagram Business or Creator account
  - Facebook Page linked to the IG account
  - A User Access Token with these permissions:
      instagram_basic, instagram_content_publish,
      instagram_manage_insights, pages_show_list
  - Convert to a Long-Lived Token (valid 60 days, refresh before expiry)
"""

import time
from typing import Optional

import requests

from agents.instagram_agent.core.config import settings


BASE = "https://graph.facebook.com/v19.0"


class InstagramAPIError(Exception):
    pass


class InstagramClient:
    def __init__(
        self,
        access_token: str   = "",
        account_id: str     = "",
    ):
        self.token      = access_token or settings.IG_ACCESS_TOKEN
        self.account_id = account_id   or settings.IG_BUSINESS_ACCOUNT_ID

        if not self.token or not self.account_id:
            raise ValueError(
                "Set IG_ACCESS_TOKEN and IG_BUSINESS_ACCOUNT_ID in .env"
            )

    # ─── Core posting flow ─────────────────────────────────────────────────

    def post_image(
        self,
        image_url: str,
        caption: str,
        hashtags: list[str],
    ) -> str:
        """
        Full flow: create container → wait → publish.
        Returns the published post ID.
        """
        full_caption = self._format_caption(caption, hashtags)

        container_id = self._create_image_container(image_url, full_caption)
        self._wait_for_container(container_id)
        post_id = self._publish_container(container_id)

        return post_id

    def post_carousel(
        self,
        image_urls: list[str],
        caption: str,
        hashtags: list[str],
    ) -> str:
        """
        Carousel: create child containers → create parent → publish.
        Max 10 images per carousel.
        """
        if len(image_urls) > 10:
            image_urls = image_urls[:10]

        full_caption = self._format_caption(caption, hashtags)

        # Step 1: Create a container for each child image
        child_ids = []
        for url in image_urls:
            child_id = self._create_image_container(url, "", is_carousel_item=True)
            child_ids.append(child_id)

        # Step 2: Create the carousel container
        carousel_id = self._create_carousel_container(child_ids, full_caption)
        self._wait_for_container(carousel_id)

        # Step 3: Publish
        return self._publish_container(carousel_id)

    def post_reel(
        self,
        video_url: str,
        caption: str,
        hashtags: list[str],
        cover_url: Optional[str] = None,
    ) -> str:
        """
        Reel posting requires a video URL (mp4, H.264, AAC audio).
        Video specs: max 90s, 9:16 aspect ratio, min 720p.
        """
        full_caption = self._format_caption(caption, hashtags)

        payload = {
            "media_type":  "REELS",
            "video_url":   video_url,
            "caption":     full_caption,
            "access_token": self.token,
        }
        if cover_url:
            payload["cover_url"] = cover_url

        resp = self._post(f"/{self.account_id}/media", payload)
        container_id = resp["id"]

        # Reels take longer to process (video encoding)
        self._wait_for_container(container_id, max_wait=300, interval=10)
        return self._publish_container(container_id)

    # ─── Container management ───────────────────────────────────────────────

    def _create_image_container(
        self,
        image_url: str,
        caption: str,
        is_carousel_item: bool = False,
    ) -> str:
        payload = {
            "image_url":    image_url,
            "caption":      caption,
            "access_token": self.token,
        }
        if is_carousel_item:
            payload["is_carousel_item"] = "true"

        resp = self._post(f"/{self.account_id}/media", payload)
        return resp["id"]

    def _create_carousel_container(
        self,
        child_ids: list[str],
        caption: str,
    ) -> str:
        payload = {
            "media_type":   "CAROUSEL",
            "children":     ",".join(child_ids),
            "caption":      caption,
            "access_token": self.token,
        }
        resp = self._post(f"/{self.account_id}/media", payload)
        return resp["id"]

    def _wait_for_container(
        self,
        container_id: str,
        max_wait: int = 60,
        interval: int = 3,
    ):
        """Poll until container status is FINISHED."""
        elapsed = 0
        while elapsed < max_wait:
            status = self._get_container_status(container_id)
            if status == "FINISHED":
                return
            if status == "ERROR":
                raise InstagramAPIError(f"Container {container_id} processing failed")
            time.sleep(interval)
            elapsed += interval

        raise InstagramAPIError(
            f"Container {container_id} not ready after {max_wait}s"
        )

    def _get_container_status(self, container_id: str) -> str:
        resp = self._get(f"/{container_id}", {"fields": "status_code"})
        return resp.get("status_code", "IN_PROGRESS")

    def _publish_container(self, container_id: str) -> str:
        payload = {
            "creation_id":  container_id,
            "access_token": self.token,
        }
        resp = self._post(f"/{self.account_id}/media_publish", payload)
        return resp["id"]

    # ─── Insights (for Feedback Agent) ─────────────────────────────────────

    def get_post_insights(self, ig_post_id: str) -> dict:
        """
        Fetch engagement metrics for a published post.
        Available metrics: impressions, reach, likes, comments, saves, shares.
        Note: insights become available ~30 minutes after posting.
        """
        metrics = "impressions,reach,likes,comments,saved,shares"
        resp = self._get(
            f"/{ig_post_id}/insights",
            {"metric": metrics, "period": "lifetime"},
        )

        result = {}
        for item in resp.get("data", []):
            result[item["name"]] = item["values"][0]["value"]
        return result

    def get_account_insights(self) -> dict:
        """Fetch account-level metrics (follower growth, reach, impressions)."""
        metrics = "follower_count,impressions,reach,profile_views"
        return self._get(
            f"/{self.account_id}/insights",
            {"metric": metrics, "period": "day"},
        )

    # ─── Token management ──────────────────────────────────────────────────

    def exchange_for_long_lived_token(
        self,
        short_token: str,
        app_id: str,
        app_secret: str,
    ) -> dict:
        """
        One-time: exchange a short-lived token (1h) for a long-lived one (60d).
        Store the returned token in IG_ACCESS_TOKEN in your .env.
        """
        resp = self._get("/oauth/access_token", {
            "grant_type":        "fb_exchange_token",
            "client_id":         app_id,
            "client_secret":     app_secret,
            "fb_exchange_token": short_token,
        })
        return resp  # {"access_token": "...", "token_type": "bearer", "expires_in": 5183944}

    # ─── HTTP helpers ───────────────────────────────────────────────────────

    def _get(self, path: str, params: dict = {}) -> dict:
        params = {**params, "access_token": self.token}
        r = requests.get(f"{BASE}{path}", params=params, timeout=30)
        return self._handle(r)

    def _post(self, path: str, data: dict) -> dict:
        r = requests.post(f"{BASE}{path}", data=data, timeout=30)
        return self._handle(r)

    @staticmethod
    def _handle(r: requests.Response) -> dict:
        try:
            data = r.json()
        except Exception:
            raise InstagramAPIError(f"Non-JSON response: {r.text}")

        if "error" in data:
            err = data["error"]
            raise InstagramAPIError(
                f"[{err.get('code')}] {err.get('message')} "
                f"(subcode {err.get('error_subcode')})"
            )
        return data

    # ─── Formatting ─────────────────────────────────────────────────────────

    @staticmethod
    def _format_caption(caption: str, hashtags: list[str]) -> str:
        """
        Instagram best practice: put hashtags in first comment OR at the
        bottom separated by dots. We use the separator method here.
        """
        if not hashtags:
            return caption
        hashtag_block = " ".join(hashtags[:30])  # IG allows max 30
        return f"{caption}\n.\n.\n.\n{hashtag_block}"
