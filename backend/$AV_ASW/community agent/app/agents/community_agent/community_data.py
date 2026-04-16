# community_data.py
# ─────────────────────────────────────────────────────────────────────────────
# Knowledge Base Layer
# Contains static datasets for subreddits and Discord server archetypes.
# Each entry is pre-tagged with audience, genre affinities, and promotion rules.
# This layer feeds the matching logic in agent.py before the LLM refinement pass.
# ─────────────────────────────────────────────────────────────────────────────

from typing import TypedDict


class SubredditEntry(TypedDict):
    name: str                        # subreddit name (no r/)
    description: str                 # what the community is about
    audience_tags: list[str]         # e.g. ["students", "young adults", "enthusiasts"]
    genre_tags: list[str]            # e.g. ["hip hop", "indie", "edm"]
    location_tags: list[str]         # e.g. ["india", "mumbai", "global"]
    artist_tags: list[str]           # artist names or artist-type tags e.g. ["bollywood", "desi"]
    promotion_friendliness: str      # "high" | "medium" | "low"
    base_engagement_score: float     # 0.0 – 1.0, reflects typical post activity
    self_promo_rules: str            # human-readable rule summary
    audience_size: str               # "small" | "medium" | "large" | "massive"


class DiscordArchetype(TypedDict):
    server_type: str                 # human label e.g. "Artist Fan Server"
    audience_tags: list[str]
    genre_tags: list[str]
    location_tags: list[str]
    how_to_find: str                 # concrete discovery method
    friendliness: str                # "high" | "medium" | "low"


# ─── Subreddit Knowledge Base ─────────────────────────────────────────────────

SUBREDDITS: list[SubredditEntry] = [

    # ── Music Discovery & General ──────────────────────────────────────────────
    {
        "name": "listentothis",
        "description": "Music discovery community — share underrated tracks and artists.",
        "audience_tags": ["music lovers", "young adults", "explorers"],
        "genre_tags": ["indie", "alternative", "experimental", "all genres"],
        "location_tags": ["global"],
        "artist_tags": ["emerging", "underground", "indie"],
        "promotion_friendliness": "medium",
        "base_engagement_score": 0.75,
        "self_promo_rules": "No self-promotion. Must be framed as discovery post. Artist account sharing own music is banned.",
        "audience_size": "large",
    },
    {
        "name": "Music",
        "description": "General music discussion subreddit for all genres and artists.",
        "audience_tags": ["general public", "music fans", "all ages"],
        "genre_tags": ["all genres"],
        "location_tags": ["global"],
        "artist_tags": ["mainstream", "popular", "all"],
        "promotion_friendliness": "low",
        "base_engagement_score": 0.55,
        "self_promo_rules": "Very strict. Direct event promotion heavily downvoted. Discussion posts about artist work OK.",
        "audience_size": "massive",
    },
    {
        "name": "WeAreTheMusicMakers",
        "description": "Community for music producers, composers, and musicians.",
        "audience_tags": ["producers", "musicians", "audio engineers", "creatives"],
        "genre_tags": ["edm", "hip hop", "electronic", "all genres"],
        "location_tags": ["global"],
        "artist_tags": ["dj", "producer", "electronic artist"],
        "promotion_friendliness": "medium",
        "base_engagement_score": 0.70,
        "self_promo_rules": "Allowed in weekly threads only. Full self-promo posts removed.",
        "audience_size": "large",
    },

    # ── Genre-Specific ─────────────────────────────────────────────────────────
    {
        "name": "EDM",
        "description": "Electronic dance music fans, events, and culture.",
        "audience_tags": ["ravers", "club goers", "young adults", "festival fans"],
        "genre_tags": ["edm", "electronic", "house", "techno", "trance", "bass"],
        "location_tags": ["global"],
        "artist_tags": ["dj", "electronic artist", "producer"],
        "promotion_friendliness": "high",
        "base_engagement_score": 0.85,
        "self_promo_rules": "Event promotion allowed in weekly megathread. Organic posts about lineup/venue work well.",
        "audience_size": "massive",
    },
    {
        "name": "aves",
        "description": "Rave culture, events, and community for underground electronic music.",
        "audience_tags": ["ravers", "underground scene fans", "18-30"],
        "genre_tags": ["techno", "house", "dnb", "underground electronic"],
        "location_tags": ["global", "usa", "europe"],
        "artist_tags": ["underground dj", "techno artist"],
        "promotion_friendliness": "medium",
        "base_engagement_score": 0.80,
        "self_promo_rules": "Event flyers allowed. Must contribute to community otherwise. No pure promo accounts.",
        "audience_size": "large",
    },
    {
        "name": "hiphopheads",
        "description": "Hip hop culture, releases, and discussion.",
        "audience_tags": ["hip hop fans", "18-35", "urban culture"],
        "genre_tags": ["hip hop", "rap", "trap", "r&b"],
        "location_tags": ["global", "usa"],
        "artist_tags": ["rapper", "hip hop artist", "trap artist"],
        "promotion_friendliness": "medium",
        "base_engagement_score": 0.85,
        "self_promo_rules": "Self-promo only in designated weekly thread. Community-first approach required.",
        "audience_size": "massive",
    },
    {
        "name": "IndieHeads",
        "description": "Indie, alternative, and art rock music fans.",
        "audience_tags": ["indie fans", "college students", "20-35", "music nerds"],
        "genre_tags": ["indie", "alternative", "art rock", "dream pop", "shoegaze"],
        "location_tags": ["global"],
        "artist_tags": ["indie artist", "alternative band", "singer-songwriter"],
        "promotion_friendliness": "medium",
        "base_engagement_score": 0.78,
        "self_promo_rules": "Discussion posts OK. Direct promo not welcome. Mention upcoming shows naturally.",
        "audience_size": "large",
    },
    {
        "name": "Metal",
        "description": "All sub-genres of metal music.",
        "audience_tags": ["metalheads", "18-40", "hardcore fans"],
        "genre_tags": ["metal", "heavy metal", "death metal", "black metal", "prog metal"],
        "location_tags": ["global"],
        "artist_tags": ["metal band", "heavy artist"],
        "promotion_friendliness": "medium",
        "base_engagement_score": 0.80,
        "self_promo_rules": "Band self-promo allowed on weekends only via pinned thread.",
        "audience_size": "large",
    },
    {
        "name": "Jazz",
        "description": "Jazz music appreciation and discussion.",
        "audience_tags": ["jazz enthusiasts", "musicians", "25-55"],
        "genre_tags": ["jazz", "bebop", "fusion", "nu jazz"],
        "location_tags": ["global"],
        "artist_tags": ["jazz musician", "jazz band"],
        "promotion_friendliness": "high",
        "base_engagement_score": 0.70,
        "self_promo_rules": "Relatively relaxed. Concert announcements welcomed if framed as community updates.",
        "audience_size": "medium",
    },
    {
        "name": "punkrock",
        "description": "Punk rock culture, bands, and events.",
        "audience_tags": ["punk fans", "teenagers", "young adults", "scene kids"],
        "genre_tags": ["punk", "punk rock", "hardcore", "post-punk"],
        "location_tags": ["global"],
        "artist_tags": ["punk band", "hardcore artist"],
        "promotion_friendliness": "high",
        "base_engagement_score": 0.72,
        "self_promo_rules": "Band/show promotion actively welcomed. Authentic scene participation required.",
        "audience_size": "medium",
    },

    # ── India / South Asia Specific ────────────────────────────────────────────
    {
        "name": "india",
        "description": "General India subreddit covering culture, news, and events.",
        "audience_tags": ["indians", "south asians", "all ages", "urban indians"],
        "genre_tags": ["bollywood", "desi", "indie indian", "all genres"],
        "location_tags": ["india", "global indians"],
        "artist_tags": ["bollywood artist", "desi artist", "indian musician"],
        "promotion_friendliness": "low",
        "base_engagement_score": 0.60,
        "self_promo_rules": "Heavy moderation. Event posts must be in megathread. Discussion angle works better.",
        "audience_size": "massive",
    },
    {
        "name": "mumbai",
        "description": "Mumbai city community — events, culture, lifestyle.",
        "audience_tags": ["mumbaikars", "urban professionals", "18-40"],
        "genre_tags": ["bollywood", "electronic", "indie indian", "all"],
        "location_tags": ["mumbai", "india"],
        "artist_tags": ["bollywood", "desi", "local artist"],
        "promotion_friendliness": "high",
        "base_engagement_score": 0.75,
        "self_promo_rules": "Event announcements explicitly allowed. Keep it local and community-relevant.",
        "audience_size": "medium",
    },
    {
        "name": "bangalore",
        "description": "Bangalore city subreddit — tech culture, events, lifestyle.",
        "audience_tags": ["bangaloreans", "tech workers", "20-35", "expats"],
        "genre_tags": ["electronic", "indie", "metal", "all"],
        "location_tags": ["bangalore", "india"],
        "artist_tags": ["local artist", "indie indian"],
        "promotion_friendliness": "high",
        "base_engagement_score": 0.78,
        "self_promo_rules": "Active events culture. Gig and concert posts regularly welcomed.",
        "audience_size": "medium",
    },
    {
        "name": "delhi",
        "description": "Delhi/NCR city subreddit — events, culture, city life.",
        "audience_tags": ["delhiites", "students", "young professionals", "18-35"],
        "genre_tags": ["hip hop", "electronic", "bollywood", "all"],
        "location_tags": ["delhi", "ncr", "india"],
        "artist_tags": ["local artist", "desi artist"],
        "promotion_friendliness": "high",
        "base_engagement_score": 0.74,
        "self_promo_rules": "Event posts allowed. Tag properly. Must be genuinely local.",
        "audience_size": "medium",
    },
    {
        "name": "IndianHipHop",
        "description": "Indian hip hop music, artists, and culture.",
        "audience_tags": ["desi hip hop fans", "18-30", "urban youth"],
        "genre_tags": ["hip hop", "rap", "desi rap", "trap"],
        "location_tags": ["india", "global indians"],
        "artist_tags": ["indian rapper", "desi hip hop artist"],
        "promotion_friendliness": "high",
        "base_engagement_score": 0.82,
        "self_promo_rules": "Artist self-promotion welcomed. Community loves discovering new talent.",
        "audience_size": "small",
    },
    {
        "name": "IndianClassicalMusic",
        "description": "Indian classical, folk, and traditional music.",
        "audience_tags": ["classical music fans", "25-60", "musicians"],
        "genre_tags": ["classical", "folk", "carnatic", "hindustani", "fusion"],
        "location_tags": ["india", "global indians"],
        "artist_tags": ["classical musician", "folk artist"],
        "promotion_friendliness": "high",
        "base_engagement_score": 0.65,
        "self_promo_rules": "Event and concert announcements warmly welcomed.",
        "audience_size": "small",
    },

    # ── Events & Concerts ──────────────────────────────────────────────────────
    {
        "name": "Concerts",
        "description": "Concert experiences, setlists, and event discussions.",
        "audience_tags": ["concert goers", "live music fans", "all ages"],
        "genre_tags": ["all genres"],
        "location_tags": ["global"],
        "artist_tags": ["all artists"],
        "promotion_friendliness": "medium",
        "base_engagement_score": 0.75,
        "self_promo_rules": "Upcoming show posts OK if framed as information sharing, not selling.",
        "audience_size": "large",
    },
    {
        "name": "festivals",
        "description": "Music festival culture, lineups, and experiences.",
        "audience_tags": ["festival goers", "20-35", "adventure seekers"],
        "genre_tags": ["edm", "indie", "rock", "all genres"],
        "location_tags": ["global"],
        "artist_tags": ["festival headliner", "dj", "live band"],
        "promotion_friendliness": "high",
        "base_engagement_score": 0.80,
        "self_promo_rules": "Festival and event promotion is the community's purpose. Be informative.",
        "audience_size": "medium",
    },

    # ── Lifestyle & Nightlife ──────────────────────────────────────────────────
    {
        "name": "nightlife",
        "description": "Clubbing, bars, and urban nightlife discussions.",
        "audience_tags": ["club goers", "21+", "urban adults"],
        "genre_tags": ["edm", "house", "hip hop", "all club genres"],
        "location_tags": ["global"],
        "artist_tags": ["dj", "club artist"],
        "promotion_friendliness": "high",
        "base_engagement_score": 0.70,
        "self_promo_rules": "Venue and event posts regularly appear. Frame as recommendations.",
        "audience_size": "medium",
    },
    {
        "name": "college",
        "description": "College life, events, and student culture.",
        "audience_tags": ["college students", "18-24", "campus community"],
        "genre_tags": ["pop", "hip hop", "edm", "all genres"],
        "location_tags": ["global"],
        "artist_tags": ["pop artist", "mainstream", "trending"],
        "promotion_friendliness": "medium",
        "base_engagement_score": 0.68,
        "self_promo_rules": "Campus event promotion welcome when framed as peer recommendation.",
        "audience_size": "large",
    },
]


# ─── Discord Server Archetypes ────────────────────────────────────────────────

DISCORD_ARCHETYPES: list[DiscordArchetype] = [
    {
        "server_type": "Official Artist Fan Server",
        "audience_tags": ["dedicated fans", "superfans", "collectors"],
        "genre_tags": ["all genres"],
        "location_tags": ["global"],
        "how_to_find": "Search '[artist name] Discord' on Google. Check artist's Instagram bio, Twitter/X pinned post, or Linktree. Also search Disboard.org with the artist name.",
        "friendliness": "high",
    },
    {
        "server_type": "Genre-Specific Music Server",
        "audience_tags": ["genre enthusiasts", "music nerds", "18-35"],
        "genre_tags": ["edm", "hip hop", "indie", "metal", "jazz", "all genres"],
        "location_tags": ["global"],
        "how_to_find": "Search Disboard.org with genre keywords (e.g. 'EDM', 'indie music', 'hip-hop'). Filter by member count 1000+.",
        "friendliness": "medium",
    },
    {
        "server_type": "City / Regional Events Server",
        "audience_tags": ["locals", "event-goers", "residents"],
        "genre_tags": ["all genres"],
        "location_tags": ["city-specific"],
        "how_to_find": "Search '[city name] events Discord' on Google. Check Facebook event pages for Discord links. Search Disboard with city name tag.",
        "friendliness": "high",
    },
    {
        "server_type": "Music Production & DJ Community",
        "audience_tags": ["producers", "djs", "beatmakers", "audio engineers"],
        "genre_tags": ["edm", "hip hop", "electronic", "all genres"],
        "location_tags": ["global"],
        "how_to_find": "Disboard.org tags: 'music production', 'beatmaking', 'DJ'. Also check r/WeAreTheMusicMakers sidebar for Discord links.",
        "friendliness": "medium",
    },
    {
        "server_type": "Rave & Festival Culture Server",
        "audience_tags": ["ravers", "festival goers", "club culture"],
        "genre_tags": ["techno", "house", "dnb", "edm", "underground"],
        "location_tags": ["global"],
        "how_to_find": "Search 'rave Discord server' or 'festival Discord' on Disboard.org. r/aves sidebar often links active servers.",
        "friendliness": "high",
    },
    {
        "server_type": "Indian / Desi Music & Culture Server",
        "audience_tags": ["south asians", "desi diaspora", "bollywood fans", "desi hip hop fans"],
        "genre_tags": ["bollywood", "desi", "indian hip hop", "classical", "all"],
        "location_tags": ["india", "global indians"],
        "how_to_find": "Disboard.org tags: 'desi', 'bollywood', 'india'. Search 'desi music Discord' on Google. Check IndianHipHop subreddit sidebar.",
        "friendliness": "high",
    },
    {
        "server_type": "College / University Student Server",
        "audience_tags": ["college students", "18-24", "campus community"],
        "genre_tags": ["pop", "hip hop", "edm"],
        "location_tags": ["city-specific", "campus-specific"],
        "how_to_find": "Search '[university name] Discord' or '[city] students Discord'. Check university Facebook groups and subreddits for Discord links.",
        "friendliness": "medium",
    },
    {
        "server_type": "Music Enthusiast General Server",
        "audience_tags": ["music lovers", "all ages", "casual listeners"],
        "genre_tags": ["all genres"],
        "location_tags": ["global"],
        "how_to_find": "Disboard.org tag: 'music'. Filter 1000+ members. Top results like 'Music Café', 'The Lounge' etc. are large hubs.",
        "friendliness": "medium",
    },
    {
        "server_type": "Streaming & Content Creator Server",
        "audience_tags": ["streamers", "content creators", "young adults", "18-28"],
        "genre_tags": ["gaming music", "lo-fi", "edm", "hip hop"],
        "location_tags": ["global"],
        "how_to_find": "Search Disboard with tags 'streaming', 'content creator'. Check Twitch music category sidebar links.",
        "friendliness": "low",
    },
    {
        "server_type": "Nightlife & Club Scene Server",
        "audience_tags": ["club goers", "21+", "nightlife enthusiasts"],
        "genre_tags": ["house", "techno", "hip hop", "edm"],
        "location_tags": ["city-specific"],
        "how_to_find": "Search '[city] nightlife Discord' on Google. Check club/venue Instagram pages for Discord links in bio.",
        "friendliness": "high",
    },
]


# ─── Genre taxonomy (maps user input → internal tags) ─────────────────────────
# This allows fuzzy matching even when the user writes "bass music" vs "bass"

GENRE_ALIASES: dict[str, list[str]] = {
    "edm": ["edm", "electronic", "dance"],
    "electronic": ["edm", "electronic", "house", "techno"],
    "house": ["house", "edm", "electronic"],
    "techno": ["techno", "edm", "underground electronic"],
    "hip hop": ["hip hop", "rap", "trap"],
    "rap": ["hip hop", "rap"],
    "trap": ["hip hop", "trap", "rap"],
    "indie": ["indie", "alternative", "indie pop"],
    "pop": ["pop", "mainstream"],
    "rock": ["rock", "alternative"],
    "metal": ["metal", "heavy metal"],
    "punk": ["punk", "punk rock"],
    "jazz": ["jazz", "nu jazz", "fusion"],
    "classical": ["classical", "hindustani", "carnatic"],
    "bollywood": ["bollywood", "desi", "indian"],
    "desi": ["desi", "bollywood", "indian"],
    "bhangra": ["bhangra", "desi", "bollywood"],
    "bass": ["bass", "edm", "electronic"],
    "dnb": ["dnb", "drum and bass", "electronic"],
    "trance": ["trance", "edm", "electronic"],
    "ambient": ["ambient", "electronic", "experimental"],
    "folk": ["folk", "singer-songwriter", "acoustic"],
    "r&b": ["r&b", "soul", "hip hop"],
    "soul": ["soul", "r&b"],
}


# ─── Audience taxonomy ────────────────────────────────────────────────────────

AUDIENCE_ALIASES: dict[str, list[str]] = {
    "students": ["students", "college students", "young adults", "18-24"],
    "college": ["college students", "students", "18-24", "campus community"],
    "young adults": ["young adults", "18-35", "20-35"],
    "professionals": ["young professionals", "25-40", "urban adults"],
    "music fans": ["music lovers", "music nerds", "enthusiasts"],
    "ravers": ["ravers", "club goers", "festival fans"],
    "desi": ["south asians", "indians", "desi diaspora"],
    "indians": ["indians", "south asians", "urban indians"],
    "musicians": ["musicians", "producers", "audio engineers", "creatives"],
}


# ─── Location taxonomy ────────────────────────────────────────────────────────

LOCATION_ALIASES: dict[str, list[str]] = {
    "mumbai": ["mumbai", "india", "global indians"],
    "delhi": ["delhi", "ncr", "india", "global indians"],
    "bangalore": ["bangalore", "india", "global indians"],
    "india": ["india", "global indians", "south asia"],
    "usa": ["usa", "global"],
    "uk": ["uk", "europe", "global"],
    "global": ["global"],
}
