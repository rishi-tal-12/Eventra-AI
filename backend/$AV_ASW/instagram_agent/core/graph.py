"""
core/graph.py
-------------
The LangGraph orchestration graph — the heart of the system.

Architecture:
  event_input
      │
      ▼
  strategy_agent          (builds content calendar)
      │
      ▼
  ┌── for_each_post loop ──────────────────────────────────┐
  │   content_agent        (generates captions/hashtags)   │
  │       │                                                 │
  │       ▼                                                 │
  │   creative_agent       (generates image)               │
  │       │                                                 │
  │       ▼                                                 │
  │   advance_post_index   (move to next post or exit loop)│
  └────────────────────────────────────────────────────────┘
      │
      ▼
  schedule_posts           (write all posts to DB)
      │
      ▼
  END

The feedback_agent runs as a separate scheduled job (not in this graph).

LangGraph key concepts used here:
  - StateGraph with TypedDict state
  - Conditional edges (route to next post or finish)
  - add_node / add_edge / add_conditional_edges
"""

import uuid
import logging
from typing import Literal

from langgraph.graph import StateGraph, END

from agents.content_agent   import content_agent
from agents.creative_agent  import creative_agent
from agents.feedback_agent  import feedback_agent
from agents.scheduler_agent import schedule_posts_node
from agents.strategy_agent  import strategy_agent
from core.models import AgentState, EventDetails


log = logging.getLogger(__name__)


# ─── Helper nodes ────────────────────────────────────────────────────────────

def advance_post_index(state: AgentState) -> AgentState:
    """
    Move the pipeline pointer to the next post.
    The router below uses this to decide whether to loop or exit.
    """
    current = state.get("current_post_index", 0)
    return {"current_post_index": current + 1}


def should_continue(state: AgentState) -> Literal["continue", "done"]:
    """
    Conditional edge: loop if more posts remain, else exit to scheduling.
    """
    calendar     = state.get("calendar")
    current_idx  = state.get("current_post_index", 0)

    if calendar and current_idx < len(calendar.posts):
        return "continue"
    return "done"


# ─── Graph builder ───────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    """
    Construct and compile the LangGraph StateGraph.
    Call this once at startup; the returned graph is reusable.
    """
    graph = StateGraph(AgentState)

    # ── Register nodes ──────────────────────────────────────────────────────
    graph.add_node("strategy",        strategy_agent)
    graph.add_node("content",         content_agent)
    graph.add_node("creative",        creative_agent)
    graph.add_node("advance_index",   advance_post_index)
    graph.add_node("schedule_posts",  schedule_posts_node)

    # ── Set entry point ──────────────────────────────────────────────────────
    graph.set_entry_point("strategy")

    # ── Linear edges ────────────────────────────────────────────────────────
    graph.add_edge("strategy",      "content")
    graph.add_edge("content",       "creative")
    graph.add_edge("creative",      "advance_index")

    # ── Conditional edge: loop or exit ──────────────────────────────────────
    graph.add_conditional_edges(
        "advance_index",
        should_continue,
        {
            "continue": "content",        # back to content for next post
            "done":     "schedule_posts", # all posts processed → schedule
        },
    )

    # ── Terminal edge ────────────────────────────────────────────────────────
    graph.add_edge("schedule_posts", END)

    return graph.compile()


# ─── Runner ──────────────────────────────────────────────────────────────────

def run_pipeline(event: EventDetails, memory: dict = None) -> dict:
    """
    High-level entry point. Build the graph, inject event details, run.
    Returns the final state dict.
    """
    graph = build_graph()

    initial_state: AgentState = {
        "event":               event,
        "current_post_index":  0,
        "errors":              [],
        "run_id":              str(uuid.uuid4()),
    }

    log.info("Starting pipeline run %s for event: %s",
             initial_state["run_id"], event.name)

    final_state = graph.invoke(initial_state)

    if final_state.get("errors"):
        log.warning("Pipeline completed with errors: %s", final_state["errors"])

    calendar = final_state.get("calendar")
    if calendar:
        log.info(
            "Pipeline complete. Generated %d posts for '%s'",
            len(calendar.posts), event.name
        )

    return final_state
