# Instagram Marketing Agent

An AI-powered system that automates Instagram marketing for musical events using LangGraph multi-agent orchestration.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy and fill env file
cp .env.example .env
# Edit .env with your API keys

# 3. Run the demo (no API keys needed)
python main.py demo

# 4. Generate a real campaign
python main.py generate --event example_event.json

# 5. Start the posting server
python main.py serve
```

## Project Structure

```
instagram_agent/
├── agents/
│   ├── strategy_agent.py    # Builds 12-day content calendar
│   ├── content_agent.py     # Generates captions, hashtags, A/B variants
│   ├── creative_agent.py    # DALL-E image generation + upload
│   ├── scheduler_agent.py   # DB persistence + APScheduler posting
│   └── feedback_agent.py    # Engagement analysis + strategy adaptation
├── api/
│   ├── instagram_client.py  # Instagram Graph API wrapper
│   └── server.py            # FastAPI REST server
├── core/
│   ├── models.py            # Pydantic models + LangGraph AgentState
│   ├── database.py          # SQLAlchemy ORM + SQLite
│   ├── config.py            # Settings from .env
│   └── graph.py             # LangGraph StateGraph (orchestrator)
├── docs/
│   └── instagram_setup.md   # Full API auth guide
├── main.py                  # Typer CLI
├── requirements.txt
└── .env.example
```

## MVP Roadmap

### Stage 1 — Content Generator (Week 1)
- [x] Strategy agent with LLM calendar
- [x] Content agent with captions + hashtags
- [x] A/B caption variants
- [x] Virality scoring
- [ ] Test with `python main.py demo`

### Stage 2 — Scheduling System (Week 2)
- [x] Database persistence
- [x] APScheduler background jobs
- [x] FastAPI server
- [ ] Set up Cloudinary image hosting
- [ ] Test with `python main.py serve`

### Stage 3 — Full Instagram Automation (Week 3)
- [ ] Instagram Business Account setup
- [ ] Long-lived token auth
- [ ] End-to-end post publishing
- [ ] Feedback agent running daily
- [ ] Token refresh cron job

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/campaign/create` | Start full pipeline |
| GET | `/campaign/{run_id}` | Check pipeline status |
| GET | `/posts` | List all posts |
| GET | `/posts/{id}/preview` | Preview one post |
| POST | `/posts/{id}/approve` | Approve a draft |
| POST | `/feedback/run` | Run engagement analysis |
| GET | `/health` | Health check |

## Real-World Constraints

See `docs/instagram_setup.md` for:
- Full auth setup walkthrough
- Rate limits and posting rules
- How to avoid account restrictions
- Token refresh automation
