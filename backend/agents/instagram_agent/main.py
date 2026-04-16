"""
main.py
-------
CLI entry point using Typer.

Usage:
  python main.py generate     # Run full pipeline (no posting)
  python main.py post         # Post scheduled content now
  python main.py feedback     # Run feedback analysis
  python main.py serve        # Start FastAPI server
  python main.py demo         # Run with demo event (no API keys needed)
"""
from dotenv import load_dotenv
import json
import logging
from datetime import datetime, timedelta
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from agents.instagram_agent.core.config import settings
from agents.instagram_agent.core.database import init_db, SessionLocal, PostRecord
from agents.instagram_agent.core.models import EventDetails

load_dotenv()

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s | %(name)-20s | %(levelname)s | %(message)s",
)

app    = typer.Typer(help="Instagram Marketing Agent CLI")
console = Console()


# ─── Commands ────────────────────────────────────────────────────────────────

@app.command()
def generate(
    event_file: Optional[str] = typer.Option(None, "--event", "-e",
        help="Path to event JSON file"),
    dry_run: bool = typer.Option(False, "--dry-run",
        help="Generate content but skip image gen and DB writes"),
):
    """
    Run the full content generation pipeline.
    Produces a content calendar with captions, hashtags, and images.
    Does NOT post to Instagram.
    """
    init_db()

    event = _load_event(event_file) or _prompt_event()

    console.print(f"\n[bold cyan]🎵 Generating campaign for: {event.name}[/bold cyan]")
    console.print(f"   Event date: {event.date.strftime('%B %d, %Y')}")
    console.print(f"   Target audience: {event.target_audience}\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running agent pipeline...", total=None)

        from core.graph import run_pipeline
        final_state = run_pipeline(event)
        progress.stop()

    calendar = final_state.get("calendar")
    if not calendar:
        console.print("[red]Pipeline failed — no calendar produced[/red]")
        raise typer.Exit(1)

    # Display results
    table = Table(title=f"Content Calendar — {event.name}", show_header=True)
    table.add_column("Day", style="cyan", width=6)
    table.add_column("Theme", style="magenta", width=14)
    table.add_column("Type", style="yellow", width=12)
    table.add_column("Hook", style="white", width=40)
    table.add_column("Virality", style="green", width=8)
    table.add_column("Image?", width=6)

    for post in sorted(calendar.posts, key=lambda p: p.days_before_event):
        hook = (post.caption or "")[:80].split("\n")[0]
        table.add_row(
            str(post.days_before_event),
            post.theme.value,
            post.post_type.value,
            hook,
            str(post.virality_score),
            "✓" if post.image_url else "✗",
        )

    console.print(table)

    if final_state.get("errors"):
        console.print(f"\n[yellow]⚠ Errors:[/yellow] {final_state['errors']}")

    console.print(f"\n[green]✅ Done![/green] {len(calendar.posts)} posts ready.")
    console.print("Run [bold]python main.py serve[/bold] to start the posting server.\n")


@app.command()
def demo():
    """
    Run with a demo event — no API keys required for content generation.
    Uses mock responses instead of calling OpenAI or Instagram.
    """
    console.print("\n[bold yellow]🎭 Demo mode — using mock AI responses[/bold yellow]\n")

    event = EventDetails(
        name             = "Neon Beats Festival",
        date             = datetime.now() + timedelta(days=12),
        venue            = "IIT Roorkee Convocation Hall",
        artists          = ["DJ KRVN", "The Local Roots", "Electra Wave"],
        genres           = ["electronic", "indie", "hip-hop"],
        target_audience  = "college students 18-24",
        vibe             = "electric, euphoric, underground yet polished",
        ticket_url       = "https://example.com/tickets",
        ticket_price     = "₹299",
        capacity         = 800,
        instagram_handle = "@neonbeats.iitr",
        location_hashtags= ["#Roorkee", "#IITRoorkee", "#Uttarakhand"],
    )

    _print_event(event)
    _run_mock_demo(event)


@app.command()
def serve(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = True,
):
    """Start the FastAPI server with the background scheduler."""
    import uvicorn
    console.print(f"\n[bold green]🚀 Starting server on http://{host}:{port}[/bold green]\n")
    uvicorn.run("api.server:app", host=host, port=port, reload=reload)


@app.command()
def feedback():
    """Run the engagement feedback analysis cycle manually."""
    init_db()
    console.print("\n[bold cyan]📊 Running feedback analysis...[/bold cyan]")
    from agents.feedback_agent import run_feedback_cycle
    result = run_feedback_cycle()
    console.print_json(json.dumps(result.get("engagement_report", {}), indent=2))


@app.command()
def list_posts(status: Optional[str] = None):
    """List all posts in the database."""
    init_db()
    db = SessionLocal()
    q  = db.query(PostRecord).order_by(PostRecord.scheduled_at)
    if status:
        q = q.filter(PostRecord.status == status)

    posts = q.all()
    db.close()

    if not posts:
        console.print("No posts found.")
        return

    table = Table(title="Scheduled Posts")
    table.add_column("ID", width=8)
    table.add_column("Event")
    table.add_column("Day", width=5)
    table.add_column("Type", width=12)
    table.add_column("Status", width=12)
    table.add_column("Scheduled")
    table.add_column("Virality")

    for p in posts:
        table.add_row(
            p.id[:8],
            p.event_name,
            str(p.days_before),
            p.post_type,
            p.status,
            p.scheduled_at.strftime("%m/%d %H:%M") if p.scheduled_at else "-",
            str(p.virality_score),
        )
    console.print(table)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _load_event(path: Optional[str]) -> Optional[EventDetails]:
    if not path:
        return None
    with open(path) as f:
        return EventDetails.model_validate_json(f.read())


def _prompt_event() -> EventDetails:
    console.print("[yellow]No event file provided. Enter event details:[/yellow]")
    name    = typer.prompt("Event name")
    days    = int(typer.prompt("Days until event", default="12"))
    venue   = typer.prompt("Venue")
    artists = typer.prompt("Artists (comma-separated)").split(",")
    genres  = typer.prompt("Genres (comma-separated)", default="electronic,indie").split(",")
    audience= typer.prompt("Target audience", default="college students 18-24")
    vibe    = typer.prompt("Event vibe", default="electric, euphoric")
    handle  = typer.prompt("Instagram handle", default="@yourhandle")
    price   = typer.prompt("Ticket price", default="Free")
    url     = typer.prompt("Ticket URL", default="")

    return EventDetails(
        name             = name,
        date             = datetime.now() + timedelta(days=days),
        venue            = venue,
        artists          = [a.strip() for a in artists],
        genres           = [g.strip() for g in genres],
        target_audience  = audience,
        vibe             = vibe,
        ticket_url       = url,
        ticket_price     = price,
        instagram_handle = handle,
        location_hashtags= [],
    )


def _print_event(event: EventDetails):
    console.print(f"  Event:    [bold]{event.name}[/bold]")
    console.print(f"  Date:     {event.date.strftime('%B %d, %Y')}")
    console.print(f"  Venue:    {event.venue}")
    console.print(f"  Artists:  {', '.join(event.artists)}")
    console.print(f"  Audience: {event.target_audience}\n")


def _run_mock_demo(event: EventDetails):
    """Simplified demo showing what the system would generate."""
    from core.models import ContentTheme, PostType, ScheduledPost

    themes_by_day = {
        -12: (ContentTheme.HYPE,    "reel",         "🔥 Something's coming. You're not ready."),
        -10: (ContentTheme.HYPE,    "single_image", "We've been quiet for a reason... 👀"),
        -8:  (ContentTheme.ARTIST,  "carousel",     f"Meet the artists taking over {event.venue} ✨"),
        -6:  (ContentTheme.COUNTDOWN, "reel",       f"6 days. {event.capacity} spots. Move."),
        -4:  (ContentTheme.BEHIND,  "carousel",     "The stage is being set. Come see what we're building 🎛️"),
        -3:  (ContentTheme.CTA,     "single_image", f"₹299 is all that stands between you and this night."),
        -1:  (ContentTheme.CTA,     "reel",         "Tomorrow. Be there or explain yourself. 🎵"),
        0:   (ContentTheme.DAY_OF,  "reel",         "TODAY. TONIGHT. NOW. Doors open 7PM 🚀"),
    }

    table = Table(title="[Demo] Content Calendar Preview", show_header=True)
    table.add_column("Day", style="cyan", width=6)
    table.add_column("Theme", style="magenta", width=16)
    table.add_column("Type", style="yellow", width=12)
    table.add_column("Sample Hook", style="white")

    for day, (theme, ptype, hook) in themes_by_day.items():
        table.add_row(str(day), theme.value, ptype, hook)

    console.print(table)
    console.print("\n[green]In production mode, each post gets:[/green]")
    console.print("  • AI-generated caption (300-500 chars)")
    console.print("  • 25 curated hashtags")
    console.print("  • DALL-E generated poster image")
    console.print("  • A/B caption variant")
    console.print("  • Virality score 0-100")
    console.print("  • Auto-scheduled to peak engagement time\n")


if __name__ == "__main__":
    app()
