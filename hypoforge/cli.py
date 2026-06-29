"""HypoForge CLI — `forge run / replay / profile`."""
from __future__ import annotations

import time
from pathlib import Path
from typing import List, Optional

import typer

from . import orchestrator
from .capability import CapabilityProfile
from .console import UI, console
from .render import render_event
from .session import latest_session, load_transcript

app = typer.Typer(add_completion=False, help="HypoForge — an agentic CLI research strategist.")

FIX = Path(__file__).parent / "fixtures"
_DEFAULT_PROMPT = ("I study GISAXS of block-copolymer thin films at BNL. "
                   "Data is in ./sims; read the attached preprint. What should I test next?")


@app.command()
def run(
    prompt: str = typer.Argument(_DEFAULT_PROMPT, help="Your research prompt / question."),
    data: Optional[List[str]] = typer.Option(None, "--data", help="Local data file/folder (repeatable)."),
    paper: Optional[List[str]] = typer.Option(None, "--paper", help="PDF/markdown literature (repeatable)."),
    rounds: int = typer.Option(6, "--rounds", help="Closed-loop rounds."),
    debate: bool = typer.Option(True, "--debate/--no-debate", help="Run the proponent/skeptic/referee debate."),
    dry_run: bool = typer.Option(True, "--dry-run/--live-experiments", help="Don't run real experiments."),
    fast: bool = typer.Option(False, "--fast", help="Disable typewriter pacing (for testing)."),
    no_record: bool = typer.Option(False, "--no-record", help="Don't write a transcript."),
):
    """Ingest local data + literature, profile the lab, run the closed loop, recommend the next experiment."""
    data = data or [str(FIX / "anneal_sweep.csv"), str(FIX / "saxs_profile.csv")]
    paper = paper or [str(FIX / "preprint_thermodynamic_only.md")]
    orchestrator.run(prompt, data, paper, {
        "fast": fast, "max_rounds": rounds, "debate": debate, "dry_run": dry_run,
        "record": not no_record, "auto": True,
    })


@app.command()
def replay(
    session: Optional[str] = typer.Argument(None, help="Session id (default: latest)."),
    fast: bool = typer.Option(False, "--fast", help="No pacing."),
    speed: float = typer.Option(1.0, "--speed", help="Playback speed multiplier."),
):
    """Re-stream a recorded run — deterministic, no keys, no network. The demo safety net."""
    sid = session or latest_session()
    if not sid:
        console.print("[red]no sessions found. run `forge run` first.[/red]")
        raise typer.Exit(1)
    events = load_transcript(sid)
    ui = UI(fast=fast)
    console.print(f"[dim]replaying session {sid} ({len(events)} events)…[/dim]\n")
    delay = {"banner": 0.4, "rule": 0.3, "say": 0.25, "kv": 0.4, "sparkline": 0.35,
             "anomaly": 0.6, "checkpoint": 0.3, "board": 0.6, "manifest": 0.5}
    for ev in events:
        render_event(ui, ev["type"], ev["payload"])
        if not fast:
            time.sleep(delay.get(ev["type"], 0.15) / max(speed, 0.1))


@app.command()
def profile(url: Optional[str] = typer.Option(None, "--url", help="Lab homepage (canned for the demo).")):
    """Show the inferred institution capability profile (the wedge, standalone)."""
    ui = UI(fast=True)
    prof = CapabilityProfile.canned()
    ui.kv(f"{prof.data['group']} — {prof.data['institution']}",
          prof.summary_lines(), style="magenta")
    console.print(f"   [dim]confidence {int(prof.data['confidence_overall']*100)}% · "
                  f"{prof.data['source_note']}[/dim]")


def main():
    app()


if __name__ == "__main__":
    main()
