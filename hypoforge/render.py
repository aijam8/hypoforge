"""
Single event renderer used by BOTH the live run and `forge replay`.

The orchestrator never draws directly — it `emit`s semantic events. The Emitter
(a) records each event to the transcript and (b) renders it via `render_event`.
Replay reads the transcript and calls the SAME `render_event`, so a recording
looks identical to a live run — the demo safety net.
"""
from __future__ import annotations

import time

from rich.table import Table

from .console import UI, console


class Emitter:
    def __init__(self, ui: UI, transcript=None, live: bool = True):
        self.ui = ui
        self.transcript = transcript
        self.live = live

    def emit(self, etype: str, pause: float = 0.0, **payload):
        if self.transcript is not None:
            self.transcript.emit(etype, **payload)
        render_event(self.ui, etype, payload)
        if self.live and pause and not self.ui.fast:
            time.sleep(pause)


def render_event(ui: UI, etype: str, p: dict):
    if etype == "banner":
        ui.banner(p["text"], p.get("subtitle", ""))
    elif etype == "rule":
        ui.rule(p["title"], p.get("style", "cyan"))
    elif etype == "say":
        ui.say(p["role"], p["text"], stream=p.get("stream", True))
    elif etype == "step":
        ui.step(p["label"], p.get("status", "•"))
    elif etype == "think":
        ui.think(p["role"], p.get("n", 3))
    elif etype == "kv":
        ui.kv(p["title"], [tuple(x) for x in p["pairs"]], p.get("style", "cyan"))
    elif etype == "panel":
        ui.panel(p["body"], p.get("title", ""), p.get("style", "cyan"))
    elif etype == "checkpoint":
        console.print(f"   [bold green]✓[/bold green] {p['label']} "
                      f"[dim]{p.get('detail', '')}[/dim]")
    elif etype == "sparkline":
        spark = ui.sparkline(p["values"])
        vals = " → ".join(f"{v:.2f}" for v in p["values"])
        console.print(f"   [bold]{p['label']}[/bold]  [bright_cyan]{spark}[/bright_cyan]"
                      f"   [dim]{vals}[/dim]  {p.get('note', '')}")
    elif etype == "anomaly":
        console.print(f"   [bold red]⚠ ANOMALY[/bold red]  S={p['S']:.2f} > θ={p['theta']:.2f}  "
                      f"[red]{p['message']}[/red]")
    elif etype == "board":
        render_board(ui, p)
    elif etype == "manifest":
        render_manifest(p["manifest"])
    elif etype == "blank":
        ui.blank()
    else:
        console.print(f"[dim]{etype}: {p}[/dim]")


def render_board(ui: UI, p: dict):
    t = Table(title="Ranked hypotheses — value per unit effort on YOUR bench",
              title_style="bold cyan", expand=False)
    t.add_column("rank", justify="right")
    t.add_column("hyp")
    t.add_column("info-gain\n(proxy nats)", justify="right")
    t.add_column("feasible?", justify="center")
    t.add_column("diff", justify="right")
    t.add_column("work", justify="right")
    t.add_column("novelty", justify="right")
    t.add_column("V", justify="right")
    for i, r in enumerate(p["rows"], 1):
        rec = r.get("recommended")
        demo = r.get("demoted")
        name = r["title"]
        if rec:
            name = f"[bold green]★ {name}[/bold green]"
        elif demo:
            name = f"[strike dim]{name}[/strike dim]"
        feas = ("[green]yes[/green]" if r["F"] >= 0.6 else
                "[red]NO[/red]" if r["F"] < 0.2 else "[yellow]partial[/yellow]")
        ig = f"{r['info_gain']:.2f}"
        if demo:
            ig = f"[bold]{ig}[/bold]"   # highlight: highest info but demoted
        t.add_row(str(i), name, ig, feas, str(r["difficulty"]),
                  f"{r['work_weeks']}w", f"{r['novelty']:.2f}",
                  f"[bold]{r['V']:.3f}[/bold]")
    console.print(t)
    console.print("")
    rec = p["recommended"]
    console.print(f"   [bold green]★ NEXT EXPERIMENT[/bold green]  "
                  f"[green]{rec['title']}[/green] — {rec['technique']}")
    console.print(f"      [dim]why:[/dim] highest information-gain you can actually "
                  f"run in-house ({rec['info_gain']:.2f} nats, "
                  f"~{rec['work_weeks']}w). Explains: {rec['what_it_explains']}")
    moon = p.get("moonshot")
    if moon:
        console.print(f"   [dim]✗ demoted[/dim]  [strike]{moon['title']}[/strike] — "
                      f"most raw info ([bold]{moon['info_gain']:.2f} nats[/bold]) but "
                      f"[red]needs {', '.join(moon['missing']) or 'unavailable equipment'}[/red] "
                      f"(~{moon['work_weeks']}w). A brainstorm, not a research plan.")


def render_manifest(m: dict):
    loc, web = m["local"], m["web"]
    body = (f"[bold]LOCAL[/bold]  : {loc['files_read']} files read, "
            f"[bold green]{loc['bytes_left_machine']} bytes left the machine[/bold green]\n"
            f"[bold]WEB[/bold]    : {web['pages_fetched']} pages fetched "
            f"({', '.join(web['domains']) or 'none'}) — metadata only\n"
            f"[dim]audit  : .forge/sessions/<id>/manifest.json   ·   forge forget wipes it[/dim]")
    console.print(Table.grid())  # spacer
    from rich.panel import Panel
    console.print(Panel(body, title="/planes — data firewall", border_style="green"))
