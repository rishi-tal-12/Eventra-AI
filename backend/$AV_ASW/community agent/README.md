# Community Recommendation Agent

An AI-powered module that recommends the best Reddit communities and Discord servers for promoting music events — organically, without getting banned.

Part of a larger Instagram marketing automation system for events.

---

## Stack

| Layer | Technology |
|---|---|
| LLM backend | [Ollama](https://ollama.com) (open-source, local) |
| LLM framework | LangChain |
| Validation | Pydantic v2 |
| Logging | Loguru |
| Knowledge base | Custom Python dataset |

---

## Setup

### 1. Install Ollama

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows: download from https://ollama.com
```

### 2. Start Ollama and pull a model

```bash
ollama serve                    # start the server
ollama pull mistral             # fast, good quality (~4GB)
# or
ollama pull llama3              # better quality (~8GB)
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env if needed (defaults work out of the box)
```

---

## Usage

### As a module

```python
from app.agents.community_agent import recommend_communities

result = recommend_communities({
    "event_type": "Live concert",
    "artist": "Nucleya",
    "genre": "Bass music / Electronic",
    "audience": "College students, 18-28",
    "location": "Delhi",
    "vibe": "High energy rave-style show"
})

# result["reddit"] → list of subreddit recommendations
# result["discord"] → list of Discord server type recommendations
```

### Run tests

```bash
# Quick smoke test (no LLM required)
python test_agent.py --smoke

# Full test — runs all 3 test cases
python test_agent.py

# Run a specific test case
python test_agent.py --case 1    # Nucleya / Delhi
python test_agent.py --case 2    # Arijit Singh / Mumbai
python test_agent.py --case 3    # The Local Train / Bangalore

# Save output to JSON
python test_agent.py --case 1 --save
```

---

## Project Structure

```
app/
  agents/
    community_agent/
      __init__.py          # Public API
      agent.py             # Main orchestration + Pydantic schemas
      prompts.py           # All LLM prompt templates
      community_data.py    # Knowledge base (subreddits + Discord archetypes)
      utils.py             # Tag matching, scoring, filtering

test_agent.py              # Test runner with 3 real scenarios
requirements.txt
.env.example
README.md
```

---

## Output Schema

```json
{
  "reddit": [
    {
      "subreddit": "EDM",
      "target_audience": "Ravers, club goers, 18-30",
      "why_relevant": "Nucleya's bass music has a strong EDM crossover fanbase...",
      "posting_strategy": "Post in the weekly event megathread...",
      "example_post": "Nucleya is bringing his iconic bass drops to Delhi\n\nFor anyone who...",
      "risk_level": "low",
      "artist_relevance_score": 0.82,
      "audience_match_score": 0.76,
      "engagement_score": 0.85
    }
  ],
  "discord": [
    {
      "server_type": "Indian / Desi Music & Culture Server",
      "target_audience": "South Asians, desi diaspora, Indian hip hop fans",
      "how_to_find": "Search Disboard.org with tag 'desi'...",
      "promotion_strategy": "Join, participate for 3-5 days, then post in #events...",
      "message_template": "Hey everyone! Super excited — Nucleya is coming to Delhi..."
    }
  ]
}
```

---

## Integration with LangGraph

```python
from langgraph.graph import StateGraph
from app.agents.community_agent import recommend_communities

def community_node(state: dict) -> dict:
    recommendations = recommend_communities(state["event_input"])
    return {**state, "community_recommendations": recommendations}

graph = StateGraph(...)
graph.add_node("community_agent", community_node)
```

---

## Changing the LLM Model

Edit `.env`:

```env
OLLAMA_MODEL=llama3        # better quality
OLLAMA_MODEL=mixtral       # best quality (needs GPU)
OLLAMA_MODEL=mistral       # fastest (default)
```

Or set it inline:

```python
import os
os.environ["OLLAMA_MODEL"] = "llama3"
```
