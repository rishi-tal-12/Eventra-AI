"""
Exhibitor Agent — recommends relevant exhibitors to invite to an event.

Pipeline:
  1. Load past event data (past.json) at startup
  2. Build an index of exhibitors aggregated across all historical events
  3. On each run, filter and score exhibitors by category, geography, and audience fit
  4. Return a ranked list of exhibitor recommendations
"""

import json
import math
import os
from collections import defaultdict
from typing import Any, Dict, List, Optional

from .models import (
    ExhibitorRecommendation,
    RecommendationRequest,
    RecommendationResponse,
)

# Path to the curated past events data
DATA_PATH = os.path.join(
    os.path.dirname(__file__), "data", "output", "past.json"
)

# Output directory for persisted results
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data", "output")


class ExhibitorAgent:
    """
    AI agent that discovers and recommends exhibitors for events
    based on historical past-event data.
    """

    def __init__(self):
        self.name = "exhibitor_agent"
        self.raw_events: List[Dict[str, Any]] = []
        self.exhibitor_index: Dict[str, Dict[str, Any]] = {}
        self._loaded = False

    # ── Data loading ────────────────────────────────────────────────────

    def load_data(self, path: Optional[str] = None):
        """
        Load the past.json event data and build an internal exhibitor index.

        The index is keyed by exhibitor name and aggregates:
          - type: exhibitor type (Enterprise, Startup, etc.)
          - booth_sizes: list of booth sizes across events
          - categories: set of event categories they've appeared in
          - subcategories: set of event subcategories
          - countries: set of countries
          - locations: set of locations
          - events: list of event names they exhibited at
          - audience_sizes: list of audience sizes of those events
          - event_count: total appearances
        """
        data_path = path or DATA_PATH

        if not os.path.exists(data_path):
            print(f"[ExhibitorAgent] WARNING: Data file not found at {data_path}")
            self._loaded = True
            return

        print(f"[ExhibitorAgent] Loading data from {data_path} ...")
        with open(data_path, "r", encoding="utf-8") as f:
            self.raw_events = json.load(f)
        print(f"[ExhibitorAgent] Loaded {len(self.raw_events)} past event records.")

        self._build_index()
        self._loaded = True

    def _build_index(self):
        """
        Build an exhibitor index from the past event records.

        Each record has an 'exhibitors' array with {name, type, booth_size}.
        We aggregate across all events to build a profile per exhibitor.
        """
        index: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "type": "",
                "booth_sizes": [],
                "categories": set(),
                "subcategories": set(),
                "countries": set(),
                "locations": set(),
                "events": [],
                "audience_sizes": [],
                "event_count": 0,
            }
        )

        for event in self.raw_events:
            category = event.get("category", "")
            subcategory = event.get("subcategory", "")
            country = event.get("country", "")
            location = event.get("location", "")
            audience_size = event.get("audience_size", 0)
            event_name = event.get("event_name", "")

            for exhibitor in event.get("exhibitors", []):
                name = exhibitor.get("name", "").strip()
                if not name:
                    continue

                entry = index[name]
                entry["type"] = exhibitor.get("type", entry["type"])
                entry["booth_sizes"].append(exhibitor.get("booth_size", "small"))
                entry["categories"].add(category)
                entry["subcategories"].add(subcategory)
                entry["countries"].add(country)
                entry["locations"].add(location)
                entry["events"].append(event_name)
                entry["audience_sizes"].append(audience_size)
                entry["event_count"] += 1

        # Convert sets to lists for serializability
        for name, info in index.items():
            self.exhibitor_index[name] = {
                "type": info["type"],
                "booth_sizes": info["booth_sizes"],
                "categories": list(info["categories"]),
                "subcategories": list(info["subcategories"]),
                "countries": list(info["countries"]),
                "locations": list(info["locations"]),
                "events": info["events"],
                "audience_sizes": info["audience_sizes"],
                "event_count": info["event_count"],
            }

        print(
            f"[ExhibitorAgent] Built index with {len(self.exhibitor_index)} unique exhibitors "
            f"from {len(self.raw_events)} events."
        )

    # ── Scoring / ranking ───────────────────────────────────────────────

    def _score_exhibitor(
        self,
        name: str,
        info: Dict[str, Any],
        request: RecommendationRequest,
    ) -> float:
        """
        Compute a relevance score (0-1) for an exhibitor relative to the request.

        Scoring breakdown (weights sum to 1.0):
          - Category match   : 0.40  (exact category match in their history)
          - Geography match  : 0.25  (country or location substring match)
          - Popularity        : 0.15  (how many events they've exhibited at)
          - Audience fit      : 0.10  (how close their typical audience is)
          - Booth size        : 0.10  (larger booths = more serious exhibitors)
        """
        score = 0.0
        cat_lower = request.category.lower()
        geo_lower = request.geography.lower()

        # ── Category match (0.40) ──
        exhibitor_categories = [c.lower() for c in info.get("categories", [])]
        exhibitor_subcategories = [s.lower() for s in info.get("subcategories", [])]

        if cat_lower in exhibitor_categories:
            score += 0.40
        else:
            # Partial keyword match across categories and subcategories
            cat_keywords = set(cat_lower.split())
            all_cat_text = " ".join(exhibitor_categories + exhibitor_subcategories)
            hits = sum(1 for kw in cat_keywords if kw in all_cat_text)
            if cat_keywords:
                score += 0.25 * (hits / len(cat_keywords))

        # ── Geography match (0.25) ──
        for loc in info.get("locations", []):
            if loc and geo_lower in loc.lower():
                score += 0.25
                break
        else:
            for country in info.get("countries", []):
                if country and geo_lower in country.lower():
                    score += 0.15
                    break

        # ── Popularity (0.15) ──
        event_count = info.get("event_count", 1)
        score += 0.15 * min(1.0, math.log1p(event_count) / math.log1p(10))

        # ── Audience size fit (0.10) ──
        audience_sizes = info.get("audience_sizes", [])
        if audience_sizes:
            avg_audience = sum(audience_sizes) / len(audience_sizes)
            # Closer the audience sizes, higher the score
            ratio = min(request.audience_size, avg_audience) / max(request.audience_size, avg_audience, 1)
            score += 0.10 * ratio

        # ── Booth size signal (0.10) ──
        booth_sizes = info.get("booth_sizes", [])
        booth_score_map = {"large": 1.0, "medium": 0.6, "small": 0.3}
        if booth_sizes:
            avg_booth = sum(booth_score_map.get(b, 0.3) for b in booth_sizes) / len(booth_sizes)
            score += 0.10 * avg_booth

        return round(min(score, 1.0), 4)

    def _generate_reason(
        self,
        name: str,
        info: Dict[str, Any],
        request: RecommendationRequest,
    ) -> str:
        """Generate a short human-readable reason for the recommendation."""
        parts = []

        exhibitor_type = info.get("type", "Exhibitor")
        parts.append(f"{name} ({exhibitor_type})")

        # Category match info
        categories = info.get("categories", [])
        if request.category.lower() in [c.lower() for c in categories]:
            parts.append(f"has exhibited at {request.category} events before")
        elif categories:
            parts.append(f"active in {', '.join(categories[:3])}")

        # Geography info
        geo_lower = request.geography.lower()
        matching_locs = [l for l in info.get("locations", []) if l and geo_lower in l.lower()]
        if matching_locs:
            parts.append(f"with presence in {matching_locs[0]}")

        # Event history
        event_count = info.get("event_count", 0)
        events = info.get("events", [])
        if event_count > 0:
            parts.append(f"exhibited at {event_count} past event(s) including {events[0]}")

        return "; ".join(parts) + "."

    # ── Main entry point ────────────────────────────────────────────────

    def run(
        self,
        request: RecommendationRequest,
        memory: Optional[dict] = None,
    ) -> RecommendationResponse:
        """
        Execute the exhibitor recommendation pipeline.

        Args:
            request: A RecommendationRequest with category, geography, audience_size, top_n.
            memory: Optional shared orchestrator memory dict.

        Returns:
            A RecommendationResponse with ranked exhibitor recommendations.
        """
        if not self._loaded:
            self.load_data()

        print(f"\n{'='*60}")
        print(f"  [AGENT] EXHIBITOR AGENT — Starting")
        print(f"  Category : {request.category}")
        print(f"  Geography: {request.geography}")
        print(f"  Audience : {request.audience_size:,}")
        print(f"  Top N    : {request.top_n}")
        print(f"{'='*60}")

        # Score every exhibitor
        scored: List[tuple] = []
        for name, info in self.exhibitor_index.items():
            relevance = self._score_exhibitor(name, info, request)
            scored.append((name, info, relevance))

        # Sort descending by score
        scored.sort(key=lambda x: x[2], reverse=True)

        # Take top_n
        top = scored[: request.top_n]

        recommendations = []
        for name, info, relevance in top:
            rec = ExhibitorRecommendation(
                name=name,
                category=info.get("type", "General"),
                relevance_score=relevance,
                reason=self._generate_reason(name, info, request),
                past_events=info.get("events", [])[:5],
                contact_email=None,
                contact_phone=None,
                website=None,
            )
            recommendations.append(rec)

        response = RecommendationResponse(
            event_category=request.category,
            event_geography=request.geography,
            total_found=len(scored),
            recommendations=recommendations,
        )

        # Persist output locally
        self._save_output(response, request)

        print(f"\n  [OK] EXHIBITOR AGENT — Returning {len(recommendations)} recommendations")
        print(f"{'='*60}\n")

        return response

    # ── Persistence ─────────────────────────────────────────────────────

    def _save_output(
        self,
        response: RecommendationResponse,
        request: RecommendationRequest,
    ):
        """Save results to a local JSON file."""
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        filename = (
            f"exhibitors_{request.category.lower().replace(' ', '_')}"
            f"_{request.geography.lower().replace(' ', '_').replace(',', '')}.json"
        )
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, ensure_ascii=False)
        print(f"  [SAVED] Results saved to {filepath}")
