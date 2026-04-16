#!/usr/bin/env python3
# run_agent.py
# ─────────────────────────────────────────────────────────────────────────────
# Inter-Agent Entry Point — Community Recommendation Agent
#
# This script is the PRODUCTION interface for this agent when used as part
# of a larger multi-agent ecosystem.
#
# It accepts JSON input via THREE methods (in priority order):
#   1. --input-file path/to/input.json     → read from a JSON file
#   2. --input '{"artist": ...}'           → inline JSON string via CLI arg
#   3. stdin pipe                          → echo '{}' | python run_agent.py
#
# Output is always written to stdout as clean JSON.
# Errors are written to stderr so they don't pollute the output pipe.
#
# ── Usage Examples ────────────────────────────────────────────────────────────
#
#   # From a file (most common in agent pipelines):
#   python run_agent.py --input-file event.json
#
#   # Inline JSON:
#   python run_agent.py --input '{"event_type":"Concert","artist":"Nucleya",...}'
#
#   # Piped from another agent (Unix/PowerShell):
#   echo '{"event_type":"Concert","artist":"Nucleya",...}' | python run_agent.py
#
#   # From another Python agent:
#   import subprocess, json
#   result = subprocess.run(
#       ["python", "run_agent.py", "--input-file", "event.json"],
#       capture_output=True, text=True
#   )
#   data = json.loads(result.stdout)
#
#   # Save output to file:
#   python run_agent.py --input-file event.json --output-file recommendations.json
#
# ─────────────────────────────────────────────────────────────────────────────

import json
import sys
import os
import argparse
import traceback

# ── Path bootstrap ─────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def stderr(msg: str):
    """Write a message to stderr (never pollutes stdout JSON output)."""
    print(f"[community_agent] {msg}", file=sys.stderr)


def exit_error(message: str, code: int = 1):
    """
    Output a structured error JSON to stdout and exit.
    Keeps the output contract consistent — callers always get JSON back,
    even on failure. They can check the 'success' field.
    """
    error_payload = {
        "success": False,
        "error": message,
        "reddit": [],
        "discord": [],
    }
    print(json.dumps(error_payload, indent=2, ensure_ascii=False))
    sys.exit(code)


def load_input(args) -> dict:
    """
    Load JSON input from whichever source was provided.
    Priority: --input-file > --input > stdin
    """

    # ── Method 1: Input file ──────────────────────────────────────────────────
    if args.input_file:
        path = os.path.abspath(args.input_file)
        if not os.path.isfile(path):
            exit_error(f"Input file not found: {path}")
        stderr(f"Reading input from file: {path}")
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                exit_error(f"Invalid JSON in file '{path}': {e}")

    # ── Method 2: Inline --input argument ─────────────────────────────────────
    if args.input:
        stderr("Reading input from --input argument")
        try:
            return json.loads(args.input)
        except json.JSONDecodeError as e:
            exit_error(f"Invalid JSON in --input argument: {e}")

    # ── Method 3: stdin pipe ───────────────────────────────────────────────────
    if not sys.stdin.isatty():
        stderr("Reading input from stdin pipe")
        raw = sys.stdin.read().strip()
        if not raw:
            exit_error("stdin was empty. Provide JSON input via --input-file, --input, or pipe.")
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            exit_error(f"Invalid JSON from stdin: {e}")

    # ── Nothing provided ───────────────────────────────────────────────────────
    exit_error(
        "No input provided. Use one of:\n"
        "  --input-file event.json\n"
        "  --input '{\"event_type\": \"...\"}'\n"
        "  echo '{...}' | python run_agent.py"
    )


def validate_input(data: dict) -> dict:
    """
    Validates required fields and fills optional ones with defaults.
    Returns a clean, safe input dict.
    """
    required = ["event_type", "artist", "genre", "audience", "location"]
    missing = [field for field in required if not data.get(field, "").strip()]

    if missing:
        exit_error(
            f"Missing required fields: {', '.join(missing)}. "
            f"Required: {required}"
        )

    return {
        "event_type": data["event_type"].strip(),
        "artist":     data["artist"].strip(),
        "genre":      data["genre"].strip(),
        "audience":   data["audience"].strip(),
        "location":   data["location"].strip(),
        "vibe":       data.get("vibe", "").strip(),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Community Recommendation Agent — JSON-in, JSON-out interface",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--input-file", "-f",
        metavar="PATH",
        help="Path to a JSON file containing event input data",
    )
    parser.add_argument(
        "--input", "-i",
        metavar="JSON",
        help="Inline JSON string with event input data",
    )
    parser.add_argument(
        "--output-file", "-o",
        metavar="PATH",
        help="Optional: save output JSON to this file (still prints to stdout)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        default=True,
        help="Pretty-print output JSON (default: True)",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Output compact single-line JSON (overrides --pretty)",
    )
    args = parser.parse_args()

    # ── Load and validate input ───────────────────────────────────────────────
    raw_input = load_input(args)
    clean_input = validate_input(raw_input)

    stderr(f"Input OK — artist={clean_input['artist']} | location={clean_input['location']}")

    # ── Import and run agent ──────────────────────────────────────────────────
    try:
        from app.agents.community_agent import recommend_communities
    except ImportError as e:
        exit_error(
            f"Could not import agent: {e}\n"
            "Make sure you're running from the project root and app/ folder exists."
        )

    stderr("Running community recommendation agent...")

    try:
        result = recommend_communities(clean_input)
    except ValueError as e:
        # Input validation error from Pydantic inside agent
        exit_error(f"Input validation error: {e}")
    except Exception as e:
        stderr(f"Unexpected error: {traceback.format_exc()}")
        exit_error(f"Agent failed: {str(e)}")

    # ── Build output payload ──────────────────────────────────────────────────
    output = {
        "success": True,
        "input":   clean_input,
        "reddit":  result.get("reddit", []),
        "discord": result.get("discord", []),
        "meta": {
            "reddit_count":  len(result.get("reddit", [])),
            "discord_count": len(result.get("discord", [])),
        }
    }

    # ── Serialize ─────────────────────────────────────────────────────────────
    indent = None if args.compact else 2
    output_str = json.dumps(output, indent=indent, ensure_ascii=False)

    # ── Write to stdout (always) ──────────────────────────────────────────────
    print(output_str)

    # ── Optionally save to file ───────────────────────────────────────────────
    if args.output_file:
        out_path = os.path.abspath(args.output_file)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(output_str)
        stderr(f"Output saved to: {out_path}")

    stderr(f"Done — {output['meta']['reddit_count']} Reddit + {output['meta']['discord_count']} Discord recommendations")


if __name__ == "__main__":
    main()
