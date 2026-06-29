"""HypoForge CLI — `forge run` (real pipeline) · `demo` · `replay` · `profile`."""
from __future__ import annotations

import time
from pathlib import Path
from typing import List, Optional

import typer

from .console import UI, console
from .render import render_event
from .session import latest_session, load_transcript

app = typer.Typer(add_completion=False, help="HypoForge — an evidence-first, modular CLI research strategist.")

ROOT = Path(__file__).parent.parent
EX = ROOT / "examples"
_DEFAULT_PROMPT = ("I'm investigating which structural/compositional features most raise "
                   "superconducting critical temperature (Tc). My data is in examples/. "
                   "What novel, testable hypotheses should I prioritise?")


@app.command()
def run(
    prompt: str = typer.Argument(_DEFAULT_PROMPT, help="Your research goal / question."),
    data: Optional[List[str]] = typer.Option(None, "--data", help="Local data file/folder (repeatable)."),
    paper: Optional[List[str]] = typer.Option(None, "--paper", help="PDF/markdown literature (repeatable)."),
    institution: Optional[str] = typer.Option(None, "--institution", help="Opt-in: public lab/group URL to infer capabilities."),
    local_only: bool = typer.Option(False, "--local-only", help="Read only local files; no web literature/crawl."),
    no_internet: bool = typer.Option(False, "--no-internet", help="Zero egress: no web AND no model calls (mock)."),
    n: int = typer.Option(6, "--n", help="Number of hypotheses to generate."),
    constraints: str = typer.Option("", "--constraints", help="Budget/equipment/time constraints, free text."),
    fast: bool = typer.Option(False, "--fast", help="No typewriter pacing."),
    no_record: bool = typer.Option(False, "--no-record", help="Don't persist a session."),
):
    """Real evidence-first pipeline: intake → ingest → literature → context → hypotheses → score → debate → report."""
    from . import pipeline
    data = data or [str(EX / "superconductors.csv"), str(EX / "research_notes.md")]
    paper = paper or []
    pipeline.run(prompt, data, paper, {
        "institution": institution, "local_only": local_only, "no_internet": no_internet,
        "n": n, "constraints": constraints, "fast": fast, "record": not no_record,
    })


@app.command()
def demo(fast: bool = typer.Option(False, "--fast", help="No pacing.")):
    """The scripted, fully-offline soft-matter demo (deterministic; no keys needed)."""
    from . import orchestrator
    fix = Path(__file__).parent / "fixtures"
    orchestrator.run(
        "I study GISAXS of block-copolymer thin films at BNL. Data in ./sims; read the preprint.",
        [str(fix / "anneal_sweep.csv"), str(fix / "saxs_profile.csv")],
        [str(fix / "preprint_thermodynamic_only.md")],
        {"fast": fast, "max_rounds": 6, "debate": True, "dry_run": True, "record": True})


@app.command()
def replay(session: Optional[str] = typer.Argument(None), fast: bool = typer.Option(False, "--fast"),
           speed: float = typer.Option(1.0, "--speed")):
    """Re-stream a recorded scripted demo (the deterministic safety net)."""
    sid = session or latest_session()
    if not sid:
        console.print("[red]no sessions found.[/red]"); raise typer.Exit(1)
    events = load_transcript(sid)
    ui = UI(fast=fast)
    console.print(f"[dim]replaying {sid} ({len(events)} events)…[/dim]\n")
    for ev in events:
        render_event(ui, ev["type"], ev["payload"])
        if not fast:
            time.sleep({"banner": .4, "rule": .3, "say": .25, "kv": .4, "sparkline": .35,
                        "board": .6, "manifest": .5}.get(ev["type"], .15) / max(speed, .1))


@app.command()
def profile(url: Optional[str] = typer.Option(None, "--url", help="Public lab/group page to infer capabilities from.")):
    """Infer a researcher's capabilities from a public institution page (the wedge, standalone)."""
    from . import steps, pipeline
    if not url:
        console.print("[yellow]pass --url <lab page>. Showing the canned soft-matter profile instead.[/yellow]")
        from .capability import CapabilityProfile
        prof = CapabilityProfile.canned()
        UI(fast=True).kv(f"{prof.data['group']}", prof.summary_lines(), style="magenta")
        return
    text = pipeline._fetch_text(url)
    cap = steps.user_context({"goal": "infer capabilities", "domain": "unknown",
                              "likely_environment": "unknown", "constraints": {}}, [], institution_text=text)
    from .present import show_capability
    show_capability(cap)


def main():
    app()


if __name__ == "__main__":
    main()
