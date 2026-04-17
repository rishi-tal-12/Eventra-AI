"""
Configuration module — loads environment variables and defines project-wide settings.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM Config ──────────────────────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# ── Twilio Config ───────────────────────────────────────────────────────────
NGROK_HOST = os.environ.get("NGROK_HOST")
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.environ.get("TWILIO_FROM")
TWILIO_TO = os.environ.get("TWILIO_TO")

# ── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SEED_DIR = os.path.join(DATA_DIR, "seed")
SCRAPED_DIR = os.path.join(DATA_DIR, "scraped")
OUTPUT_DIR = os.path.join(DATA_DIR, "output")

# Ensure directories exist
for d in [DATA_DIR, SEED_DIR, SCRAPED_DIR, OUTPUT_DIR]:
    os.makedirs(d, exist_ok=True)

# ── Scraper Config ──────────────────────────────────────────────────────────
REQUEST_TIMEOUT = 15          # seconds
REQUEST_DELAY = 1.0           # polite delay between requests (seconds)
MAX_RETRIES = 3
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

# ── Fixed Currency Conversion (to USD) ──────────────────────────────────────
# Rates: 1 USD = X local currency
CURRENCY_TABLE = {
    "India":     {"code": "INR", "rate": 84.0},
    "USA":       {"code": "USD", "rate": 1.0},
    "Europe":    {"code": "EUR", "rate": 0.92},
    "Singapore": {"code": "SGD", "rate": 1.35},
    "UK":        {"code": "GBP", "rate": 0.79},
}

# ── Ticket Tier Definitions ─────────────────────────────────────────────────
# User-confirmed tiers: Regular, Workshop Only, Student
TICKET_TIERS = [
    {
        "name": "Regular",
        "description": "Full conference access (all sessions, networking, keynotes)",
        "allocation_pct": 60,      # % of total tickets allocated to this tier
        "base_multiplier": 1.0,    # price multiplier relative to base price
    },
    {
        "name": "Workshop Only",
        "description": "Access to hands-on workshop sessions only",
        "allocation_pct": 20,
        "base_multiplier": 0.6,
    },
    {
        "name": "Student",
        "description": "Discounted access for students with valid ID",
        "allocation_pct": 20,
        "base_multiplier": 0.35,
    },
]

# ── Category Pricing Profiles ───────────────────────────────────────────────
# Base price ranges (USD) and demand elasticity by event category
CATEGORY_PROFILES = {
    "AI": {
        "base_price_range": (80, 250),
        "demand_elasticity": -0.8,   # inelastic (tech professionals pay)
        "avg_conversion_rate": 0.10,
    },
    "Web3": {
        "base_price_range": (60, 200),
        "demand_elasticity": -1.0,
        "avg_conversion_rate": 0.08,
    },
    "ClimateTech": {
        "base_price_range": (50, 180),
        "demand_elasticity": -0.9,
        "avg_conversion_rate": 0.09,
    },
    "Music Festival": {
        "base_price_range": (30, 150),
        "demand_elasticity": -1.5,   # elastic (price-sensitive audience)
        "avg_conversion_rate": 0.15,
    },
    "Sports": {
        "base_price_range": (25, 120),
        "demand_elasticity": -1.3,
        "avg_conversion_rate": 0.12,
    },
}

# Fallback for unknown categories
DEFAULT_CATEGORY_PROFILE = {
    "base_price_range": (50, 200),
    "demand_elasticity": -1.0,
    "avg_conversion_rate": 0.10,
}

# ── Geography PPP Adjustments ───────────────────────────────────────────────
# Purchasing Power Parity factor: multiply USD prices by this
GEOGRAPHY_PPP = {
    "India":     0.45,   # prices ~45% of US level
    "USA":       1.0,
    "Europe":    0.90,
    "Singapore": 0.85,
    "UK":        0.95,
}

# ── Operational Defaults ────────────────────────────────────────────────────
DEFAULT_OPS_OVERHEAD_PCT = 0.15    # 15% of total costs for misc operations
DEFAULT_MARKETING_PCT = 0.10       # 10% of budget for marketing

# ── Venue Config ────────────────────────────────────────────────────────────
VENUELOOK_BASE_URL = os.getenv("VENUELOOK_BASE_URL", "https://www.venuelook.com").strip()

CITY_COORDS: dict[str, tuple[float, float]] = {
    "bangalore": (12.9716, 77.5946),
    "mumbai": (19.0760, 72.8777),
    "delhi": (28.6139, 77.2090),
    "hyderabad": (17.3850, 78.4867),
    "pune": (18.5204, 73.8567),
    "chennai": (13.0827, 80.2707),
    "new york": (40.7128, -74.0060),
    "san francisco": (37.7749, -122.4194),
    "singapore": (1.3521, 103.8198),
    "london": (51.5074, -0.1278),
    "berlin": (52.5200, 13.4050),
}

DEFAULT_COORDS = (20.5937, 78.9629)
