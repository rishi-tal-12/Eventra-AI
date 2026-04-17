with open('backend/app.py', 'r') as f:
    content = f.read()

prefix = """import sys, os
backend_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, backend_dir)
for a in ["sponsor_agent", "artist_agent", "exhibitor_agent", "venue_agent", "pricing_agent", "community_agent", "instagram_agent"]:
    sys.path.append(os.path.join(backend_dir, "agents", a))

"""
with open('backend/app.py', 'w') as f:
    f.write(prefix + content)
