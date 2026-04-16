import sqlite3, json

conn = sqlite3.connect("instagram_agent.db")
posts = conn.execute(
    "SELECT theme, post_type, caption, hashtags_json, virality_score, scheduled_at FROM posts ORDER BY scheduled_at"
).fetchall()

for i, (theme, ptype, caption, hashtags, score, scheduled) in enumerate(posts, 1):
    print(f"\n{'='*60}")
    print(f"POST {i} | {theme.upper()} | {ptype} | Virality: {score}")
    print(f"Scheduled: {scheduled}")
    print(f"\nCAPTION:\n{caption}")
    print(f"\nHASHTAGS:\n{' '.join(json.loads(hashtags or '[]'))}")

conn.close()