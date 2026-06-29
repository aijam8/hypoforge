"""Rich presentation for the real pipeline outputs (evidence-first, provenance shown)."""
from __future__ import annotations

from rich.panel import Panel
from rich.table import Table

from .console import console


def show_brief(b: dict):
    c = b.get("constraints", {})
    body = (f"[bold]Goal[/bold]  {b.get('goal','')}\n"
            f"[bold]Domain[/bold]  {b.get('domain','?')} · {b.get('subfield','')}   "
            f"[bold]Task[/bold]  {b.get('task_type','?')}\n"
            f"[bold]Environment[/bold]  {b.get('likely_environment','?')}\n"
            f"[bold]Constraints[/bold]  budget={c.get('budget','?')} · "
            f"equip={c.get('equipment','?')} · time={c.get('time','?')}\n"
            f"[bold]Search topics[/bold]  {', '.join(b.get('search_topics', [])[:6])}")
    console.print(Panel(body, title="① research brief", border_style="cyan"))


def show_evidence(cards: list[dict]):
    t = Table(title="③ evidence (each card carries provenance)", title_style="bold green",
              show_lines=False, expand=False)
    t.add_column("id"); t.add_column("source"); t.add_column("type")
    t.add_column("claims", justify="right"); t.add_column("limitations", justify="right")
    t.add_column("conf", justify="right")
    for c in cards:
        import os
        t.add_row(c.get("id", "?"), os.path.basename(c.get("provenance", "")),
                  c.get("source_type", c.get("kind", "?")),
                  str(len(c.get("claims", []))), str(len(c.get("limitations", []))),
                  f"{c.get('confidence', 0):.2f}")
    console.print(t)


def show_litmaps(lit: dict):
    console.print(Panel(lit.get("field_summary", ""),
                        title=f"④ literature — state of the field "
                              f"({lit.get('n_papers',0)} papers)", border_style="blue"))
    gaps = lit.get("gap_map", [])
    if gaps:
        body = "\n".join(f"• [bold]{g.get('gap','')}[/bold]\n    [dim]{g.get('why_open','')}[/dim]"
                         for g in gaps[:6])
        console.print(Panel(body, title="gap map — what hasn't been tested", border_style="blue"))
    if lit.get("contradictions"):
        console.print(Panel("\n".join(f"• {x}" for x in lit["contradictions"][:5]),
                            title="contradictions in the literature", border_style="yellow"))


def show_capability(cap: dict):
    body = (f"[bold]Likely equipment[/bold]  {', '.join(cap.get('likely_equipment', [])[:10])}\n"
            f"[bold]Techniques[/bold]  {', '.join(cap.get('techniques', [])[:10])}\n"
            f"[bold]Compute[/bold]  {cap.get('compute_access','?')}\n"
            f"[bold]In-house vs collaboration[/bold]  {cap.get('measurement_access','?')}\n"
            f"[bold]Feasible[/bold]  {', '.join(cap.get('feasible_experiment_types', [])[:6])}\n"
            f"[bold red]Likely infeasible[/bold red]  {', '.join(cap.get('likely_infeasible', [])[:6])}\n"
            f"[dim]basis: {cap.get('basis','?')} · confidence {cap.get('confidence',0)}[/dim]")
    console.print(Panel(body, title="⑤ inferred research context (the wedge)", border_style="magenta"))


def show_scored(hyps: list[dict]):
    t = Table(title="⑦ hypotheses — multi-objective ranking", title_style="bold cyan", expand=False)
    for col in ["rank", "id", "hypothesis", "info-gain", "novelty", "feasible", "effort", "value"]:
        t.add_column(col, justify="right" if col not in ("hypothesis", "id") else "left")
    for i, h in enumerate(hyps, 1):
        s = h["scores"]
        feas = ("[green]%.2f[/green]" % s["feasibility"] if s["feasibility"] >= 0.6
                else "[red]%.2f[/red]" % s["feasibility"])
        effort = (s["cost_effort"] + s["time_to_test"] + s["equipment_dependence"]) / 3
        name = h["title"][:40]
        if i == 1:
            name = f"[bold green]★ {name}[/bold green]"
        t.add_row(str(i), h["id"], name, f"{s['expected_information_gain']:.2f}",
                  f"{s['novelty']:.2f}", feas, f"{effort:.2f}", f"[bold]{h['value']:.3f}[/bold]")
    console.print(t)


def show_critiques(deb: dict):
    for role, r in deb.get("reviews", {}).items():
        console.print(f"  [bold]{role}[/bold]: [dim]{r.get('assessment','')[:300]}[/dim]")


def recommended(hyps: list[dict], deb: dict) -> dict | None:
    """The single chosen hypothesis (synthesizer's pick, else top-ranked)."""
    if not hyps:
        return None
    rec_id = (deb.get("synthesis", {}) or {}).get("recommendation_id")
    return next((h for h in hyps if h["id"] == rec_id), hyps[0])


_AVAIL = {"in_house": "[green]in-house[/green]", "acquire": "[yellow]acquire[/yellow]",
          "collaborate": "[yellow]collaborate[/yellow]", "unknown": "[dim]unknown[/dim]"}


def _tech_block(rec: dict) -> str:
    techs = rec.get("technologies") or []
    if not techs:
        return ""
    lines = ["", "[bold]Technologies you'd need[/bold]"]
    for t in techs[:10]:
        tag = _AVAIL.get(t.get("availability", "unknown"), _AVAIL["unknown"])
        note = f" [dim]— {t['note']}[/dim]" if t.get("note") else ""
        lines.append(f"  • [bold]{t.get('name','')}[/bold] ({tag}) — {t.get('purpose','')}{note}")
    return "\n".join(lines) + "\n"


def show_final(hyps: list[dict], deb: dict, brief: dict):
    syn = deb.get("synthesis", {})
    rec = recommended(hyps, deb)
    if not rec:
        return
    s = rec["scores"]
    body = (f"[bold green]★ TEST NEXT — {rec['title']}[/bold green]\n\n"
            f"[bold]Hypothesis[/bold]  {rec['statement']}\n"
            f"[bold]Explains[/bold]  {rec.get('what_it_explains','')}\n"
            f"[bold]Prediction[/bold]  {rec.get('prediction','')}\n"
            f"[bold]How to test[/bold]  {rec.get('test_plan','')}\n"
            f"[bold]Grounded in[/bold]  {rec.get('supporting_evidence','')}\n"
            f"[bold]Falsified if[/bold]  {rec.get('evidence_that_would_weaken','')}\n"
            f"{_tech_block(rec)}\n"
            f"[dim]info-gain {s['expected_information_gain']:.2f} · novelty {s['novelty']:.2f} · "
            f"feasibility {s['feasibility']:.2f} · value {rec['value']:.3f}[/dim]\n"
            f"[italic]{syn.get('rationale','')}[/italic]")
    console.print(Panel(body, title="⑧ what to test next — and why", border_style="green"))
    if syn.get("caveats"):
        console.print("  [dim]caveats: " + " · ".join(syn["caveats"][:4]) + "[/dim]")


def show_manifest(m: dict):
    loc, mod, web = m["local"], m["model"], m["web"]
    body = (f"[bold]mode[/bold]   {m['mode']}\n"
            f"[bold]LOCAL[/bold]  {loc['files_read']} files read · "
            f"[bold green]{loc['raw_bytes_transmitted']} raw bytes transmitted[/bold green]\n"
            f"[bold]MODEL[/bold]  {mod['llm_calls']} LLM calls · "
            f"{mod['derived_chars_sent']:,} derived chars sent to provider\n"
            f"[bold]WEB[/bold]    {web['pages_fetched']} pages fetched "
            f"({', '.join(web['domains'][:6]) or 'none'})")
    console.print(Panel(body, title="/planes — honest data-flow manifest", border_style="green"))
