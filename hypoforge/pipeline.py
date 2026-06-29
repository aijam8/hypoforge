"""
The REAL pipeline (`forge run`) — implements the group's 8-step, evidence-first,
modular workflow with live model calls.

  intake → context-mode → ingest+extract → literature review → user-context
         → hypothesis generation → multi-objective scoring → debate → report

Privacy modes:
  --local-only   : read only local files; no web literature / no institution crawl.
  --no-internet  : the above AND no model egress (router forced to mock) — zero egress.
  --institution URL : opt-in public page fetched to ground the capability profile.
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
import sys
from pathlib import Path

import requests

from . import ingest as ingest_mod, present, router, steps
from .console import UI, console
from .planes import PlaneLedger
from .session import Transcript


def _status(msg: str):
    """Spinner on a real terminal; a plain line otherwise (keeps captured logs clean)."""
    if sys.stdout.isatty():
        return console.status(msg)
    console.print(f"  [dim]… {msg}[/dim]")
    return contextlib.nullcontext()


def _local_context(paths: list[str], limit: int = 3500) -> str:
    """Full text of small local notes/markdown so the capability agent sees real constraints."""
    chunks = []
    for p in paths:
        if p.lower().endswith((".md", ".txt", ".rst")) and os.path.isfile(p):
            try:
                chunks.append(f"### {os.path.basename(p)}\n" + Path(p).read_text("utf-8", "ignore")[:limit])
            except Exception:
                pass
    return "\n\n".join(chunks)[: limit * 2]


def run(prompt: str, data_paths: list[str], paper_paths: list[str], opts: dict):
    ui = UI(fast=opts.get("fast", False))
    no_internet = opts.get("no_internet", False)
    local_only = opts.get("local_only", False) or no_internet
    router.FORCE_MOCK = no_internet
    router.reset_usage()

    sid = opts.get("session_id") or _sid(prompt, data_paths)
    tr = Transcript(sid, record=opts.get("record", True))
    ledger = PlaneLedger(no_internet=no_internet)

    console.rule("[bold cyan]🔬 HypoForge")
    console.print(f'  [dim]prompt:[/dim] "{prompt}"')
    mode = ("no-internet (zero egress, mock models)" if no_internet else
            "local-only (no web)" if local_only else "institution-aware" if opts.get("institution")
            else "hosted-model + web")
    console.print(f"  [dim]mode:[/dim] {mode}   [dim]router:[/dim] per-role models "
                  f"(intake={router.model_label('intake')}, hypothesis={router.model_label('hypothesis')})\n")

    # ① INTAKE -------------------------------------------------------------
    console.rule("① intake")
    all_files = data_paths + paper_paths
    with _status("scoping the research brief…"):
        brief = steps.intake(prompt, all_files, opts.get("constraints", ""))
    present.show_brief(brief)
    tr.emit("brief", brief=brief)

    # ③ INGEST + EXTRACT (local plane) ------------------------------------
    console.rule("③ ingest + evidence extraction  (LOCAL plane)")
    evidence_objs = ingest_mod.ingest(all_files, plane="local")
    ledger.record_local(len(evidence_objs), sum(e.bytes_read for e in evidence_objs))
    console.print(f"  read {len(evidence_objs)} local source(s); extracting structured evidence…")
    with _status("extracting claims / methods / limitations…"):
        cards = steps.extract_evidence(evidence_objs) if evidence_objs else []
    present.show_evidence(cards)
    tr.emit("evidence", cards=cards)

    # ④ LITERATURE REVIEW (web plane, unless local-only) ------------------
    console.rule("④ literature review")
    allow_web = not local_only
    if not allow_web:
        console.print("  [yellow]local-only mode — skipping web literature search[/yellow]")
    with _status("searching + synthesizing the literature…" if allow_web
                        else "synthesizing from local evidence only…"):
        lit = steps.literature_review(brief, cards, allow_web=allow_web)
    for u in lit.get("fetched_urls", []):
        ledger.record_web(u)
    present.show_litmaps(lit)
    tr.emit("literature", literature={k: v for k, v in lit.items() if k != "papers"})

    # ⑤ USER-CONTEXT (optional institution page) --------------------------
    console.rule("⑤ user-context  (capability inference)")
    inst_text = None
    inst_url = opts.get("institution")
    if inst_url and not no_internet:
        console.print(f"  [magenta]institution-aware:[/magenta] fetching {inst_url}")
        inst_text = _fetch_text(inst_url)
        ledger.record_web(inst_url)
    lab_ctx = _local_context(all_files)
    with _status("inferring this lab's realistic capabilities…"):
        cap = steps.user_context(brief, cards, institution_text=inst_text, local_context=lab_ctx)
    present.show_capability(cap)
    tr.emit("capability", capability=cap)

    # ⑥ HYPOTHESIS GENERATION ---------------------------------------------
    console.rule("⑥ hypothesis generation")
    with _status(f"generating hypotheses (model={router.model_label('hypothesis')})…"):
        hyps = steps.generate_hypotheses(brief, lit, cap, n=opts.get("n", 6))
    if not hyps:
        console.print("  [yellow]hypothesis model returned nothing parseable; retrying once…[/yellow]")
        hyps = steps.generate_hypotheses(brief, lit, cap, n=max(3, opts.get("n", 6) - 2))
    console.print(f"  generated {len(hyps)} candidate hypotheses.")

    # ⑦ SCORING ------------------------------------------------------------
    console.rule("⑦ multi-objective scoring")
    with _status("scoring info-gain / novelty / feasibility / effort…"):
        hyps = steps.score_hypotheses(hyps, cap, brief)
    present.show_scored(hyps)
    tr.emit("scored", hypotheses=hyps)

    # ⑧ DEBATE + SYNTHESIS -------------------------------------------------
    console.rule("⑧ critique panel + synthesis")
    top = hyps[: min(3, len(hyps))]
    with _status("five critics debating the top hypotheses…"):
        deb = steps.debate(top, brief, lit, cap)
    present.show_critiques(deb)
    hyps.sort(key=lambda h: h["value"], reverse=True)
    rec = present.recommended(hyps, deb)
    if rec:
        with _status("mapping the technologies needed to run the chosen experiment…"):
            rec["technologies"] = steps.technology_plan(rec, cap, brief)
    console.print("")
    present.show_final(hyps, deb, brief)
    tr.emit("debate", synthesis=deb.get("synthesis", {}))

    # /planes --------------------------------------------------------------
    console.print("")
    ledger.sync_model(router.USAGE)
    manifest = ledger.manifest()
    present.show_manifest(manifest)
    tr.write_manifest(manifest)

    result = {"session_id": sid, "brief": brief, "evidence": cards, "literature":
              {k: v for k, v in lit.items() if k != "papers"}, "capability": cap,
              "hypotheses": hyps, "debate": deb.get("synthesis", {}), "manifest": manifest}
    if opts.get("record", True):
        (Path(".forge") / "sessions" / sid / "result.json").write_text(
            json.dumps(result, indent=2, default=str))
    tr.close()
    console.print(f"\n  [dim]session saved to .forge/sessions/{sid}/ (brief, evidence, result.json)[/dim]")
    return result


def _fetch_text(url: str) -> str | None:
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "HypoForge/1.0"})
        r.raise_for_status()
        html = r.text
        html = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", html)
        text = re.sub(r"(?s)<[^>]+>", " ", html)
        return re.sub(r"\s+", " ", text)[:6000]
    except Exception:
        return None


def _sid(prompt: str, paths: list[str]) -> str:
    return "run-" + hashlib.sha1((prompt + "|".join(paths)).encode()).hexdigest()[:8]
