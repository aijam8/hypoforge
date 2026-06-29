"""
The rails. A deterministic state machine that renders like an autonomous agent:
the control flow is scripted Python (reliable on stage); the LLM only fills
*content* (and offline, fixtures do). Sequence:

    ingest(local) → profile(web) → warm-up → closed loop → debate → ranked board → /planes
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

from . import capability, debate as debate_mod, engine as engine_mod, evaluate, ingest as ingest_mod, router
from .console import UI
from .planes import PlaneLedger
from .render import Emitter
from .session import Transcript

FIX = Path(__file__).parent / "fixtures"


def run(prompt: str, data_paths: list[str], paper_paths: list[str], opts: dict):
    ui = UI(fast=opts.get("fast", False))
    sid = opts.get("session_id") or _sid(prompt, data_paths)
    tr = Transcript(sid, record=opts.get("record", True))
    em = Emitter(ui, tr, live=True)
    ledger = PlaneLedger()
    paced = not opts.get("fast", False)

    em.emit("banner", text="🔬  HypoForge",
            subtitle="not what's novel, but what's worth running on the bench you own")
    backend = "mock (offline)" if router.is_offline() else "openrouter/deepseek (live)"
    em.emit("say", role="system",
            text=f'prompt: "{prompt}"', stream=False)
    em.emit("say", role="system",
            text=f"models: per-role router · backend = {backend} · session {sid}",
            stream=False)
    em.emit("kv", title="plan", style="cyan", pairs=[
        ["1 ingest", "open & profile local data (LOCAL plane)"],
        ["2 profile", "infer the lab's instruments from the public web (WEB plane)"],
        ["3 warm-up", "seed principles from the literature, fit surrogate"],
        ["4 loop", "information-directed experiments, minimize uncertainty"],
        ["5 debate", "proponent vs skeptic vs referee on the top hypotheses"],
        ["6 report", "rank by info-gain × feasibility; recommend the next experiment"],
    ])

    # ---------------------------------------------------------------- 1. INGEST
    em.emit("rule", title="1 · Ingest  (LOCAL plane — raw data stays on disk)")
    evidence = ingest_mod.ingest(data_paths + paper_paths, plane="local")
    n_bytes = sum(e.bytes_read for e in evidence)
    ledger.record_local(len(evidence), n_bytes)
    for e in evidence:
        em.emit("say", role="ingest",
                text=f"{Path(e.path).name}  →  {e.kind}: {e.summary.splitlines()[0]}",
                stream=False)
    em.emit("checkpoint", label="LOCAL plane sealed",
            detail=f"{len(evidence)} files, {n_bytes} bytes read, 0 sent", pause=0.3 if paced else 0)

    anneal_df, claim = _extract(evidence)

    # ---------------------------------------------------------------- 2. PROFILE
    em.emit("rule", title="2 · Profile the lab  (WEB plane — metadata only)")
    em.emit("say", role="profile",
            text="parsing identity hints from the prompt … 'BNL', 'GISAXS', 'block copolymers'")
    em.emit("think", role="profile")
    for url in ["https://api.openalex.org/authors", "https://ror.org/02ex6cf31",
                "https://www.bnl.gov/cmpmsd/"]:
        ledger.record_web(url)
    em.emit("say", role="profile",
            text="matched: Soft Matter & Self-Assembly Group, Brookhaven National Lab "
                 "(CMPMS). crawling facilities + recent methods sections …", stream=False)
    profile = capability.CapabilityProfile.canned()
    em.emit("kv", title="inferred capability profile  (human-ratify ↓)",
            style="magenta", pairs=profile.summary_lines())
    em.emit("checkpoint", label="confirm-lab checkpoint",
            detail="[Enter] accepted (--auto)", pause=0.4 if paced else 0)

    # ---------------------------------------------------------------- 3. WARM-UP
    em.emit("rule", title="3 · Warm-up  (seed principles from the literature)")
    em.emit("say", role="principle",
            text="seeding principle P0 from the retrieved preprint: "
                 "“equilibrium domain spacing is set by temperature alone (thermodynamic).”")
    eng = engine_mod.DiscoveryEngine(anneal_df, anomaly_theta=opts.get("theta", 0.70))
    warm = eng.warmup(shear_max=1.0)
    H0 = engine_mod._entropy(eng.state.posterior)
    eng.state.entropies.append(H0)
    em.emit("kv", title="principle posterior (prior)", style="yellow", pairs=[
        ["P0  thermodynamic (T only)", f"{eng.state.posterior[0]:.2f}"],
        ["P1  shear-dependent (T, shear)", f"{eng.state.posterior[1]:.2f}"],
        ["fit", f"GP surrogate on {len(warm)} low-shear points · σ_obs≈{eng.state.sigma_obs:.2f} nm"],
        ["entropy H", f"{H0:.2f} nats"],
    ])

    # ---------------------------------------------------------------- 4. LOOP
    em.emit("rule", title="4 · Closed loop  (information-directed, uncertainty-minimizing)")
    rounds = eng.run_loop(n_rounds=opts.get("max_rounds", 6))
    entropies = [H0]
    fired_done = False
    for r in rounds:
        T, shear = r.x
        em.emit("say", role="hypothesis",
                text=f"round {r.t+1}: propose probing (T={T:.0f}°C, shear={shear:.1f}/s) "
                     f"— a high-uncertainty regime", stream=False)
        em.emit("say", role="ids",
                text=f"IDS picks it: info-gain {eng.info_gain(T, shear):.2f} nats / "
                     f"feasible in-house → run", stream=False)
        tag = "PIPELINE TEST — NOT EVIDENCE" if opts.get("dry_run", True) else "measured"
        em.emit("say", role="experiment",
                text=f"run GISAXS-under-shear → domain spacing {r.y:.2f} nm  [{tag}]",
                stream=False)
        if r.anomaly and not fired_done:
            fired_done = True
            em.emit("anomaly", S=r.anomaly_S, theta=eng.theta,
                    message="your local data contradicts the published consensus "
                            "(spacing rises with shear)")
            em.emit("say", role="principle",
                    text="anomaly-driven augmentation → spawning principle P1: "
                         "“spacing depends on temperature AND shear.”", stream=False)
            em.emit("checkpoint", label="approve-new-principle checkpoint",
                    detail="residual is physical, not a units bug → [Enter] approved",
                    pause=0.4 if paced else 0)
        entropies.append(r.entropy)
        em.emit("sparkline", label="uncertainty H(principles)", values=[round(x, 2) for x in entropies],
                note="↓ collapsing onto the shear-dependent principle" if r.entropy < H0 - 0.1 else "",
                pause=0.18 if paced else 0)
    mp = eng.map_principle()
    em.emit("say", role="principle",
            text=f"posterior now favors {mp['name']} "
                 f"(P={max(eng.state.posterior):.2f}). worldview updated.", stream=False)

    # ---------------------------------------------------------------- 5. DEBATE
    hyps = evaluate.load_hypotheses()
    evaluate.evaluate(hyps, eng, profile)              # provisional ranking
    if opts.get("debate", True):
        em.emit("rule", title="5 · Debate  (proponent · skeptic · referee)")
        for d in debate_mod.debate_top(hyps, k=3):
            em.emit("say", role="proponent", text=f"[{d['id']}] {d['proponent']}", stream=False)
            em.emit("say", role="skeptic", text=f"[{d['id']}] {d['skeptic']}", stream=False)
            ruling = d["ruling"]
            moved = ruling["action"] == "novelty_downgraded"
            em.emit("say", role="referee",
                    text=f"[{d['id']}] RULING: {ruling['rationale']}", stream=False)
            if moved:
                em.emit("checkpoint", label="referee moved a score",
                        detail=f"{d['id']} novelty 0.82 → {ruling['to']} — re-ranking",
                        pause=0.3 if paced else 0)
        evaluate.evaluate(hyps, eng, profile)          # re-rank after debate

    # ---------------------------------------------------------------- 6. REPORT
    em.emit("rule", title="6 · Report  (value per unit effort on YOUR bench)")
    ranked = sorted(hyps, key=lambda h: h["V"], reverse=True)
    recommended, moonshot = evaluate.split_recommended_and_moonshot(ranked)
    rows = [_row(h, recommended, moonshot) for h in ranked]
    em.emit("board",
            rows=rows,
            recommended=_brief(recommended),
            moonshot=_brief(moonshot) if moonshot else None)

    # ---------------------------------------------------------------- /planes
    em.emit("blank")
    manifest = ledger.manifest()
    em.emit("manifest", manifest=manifest)
    tr.write_manifest(manifest)

    em.emit("say", role="system",
            text=f"done · session saved to .forge/sessions/{sid}/ · "
                 f"replay with:  forge replay {sid}", stream=False)
    tr.close()
    return {"session_id": sid, "ranked": ranked, "recommended": recommended,
            "moonshot": moonshot, "entropies": entropies, "manifest": manifest}


# --------------------------------------------------------------------- helpers
def _extract(evidence):
    anneal_df, claim = None, ""
    for e in evidence:
        if e.dataframe is not None:
            cols = [str(c).lower() for c in e.dataframe.columns]
            if any("domain_spacing" in c for c in cols):
                anneal_df = e.dataframe
        if e.kind == "document" and e.claims:
            claim = e.claims[0]
    if anneal_df is None:                       # fall back to the canned fixture
        anneal_df = pd.read_csv(FIX / "anneal_sweep.csv")
    return anneal_df, claim


def _row(h, rec, moon):
    f = h["feasibility"]
    return {"title": h["title"], "info_gain": h["info_gain"], "F": f["F"],
            "difficulty": f["difficulty"], "work_weeks": f["work_weeks"],
            "novelty": h["novelty"], "V": h["V"],
            "recommended": h["id"] == rec["id"],
            "demoted": bool(moon and h["id"] == moon["id"])}


def _brief(h):
    return {"id": h["id"], "title": h["title"], "technique": h["technique"],
            "info_gain": h["info_gain"], "work_weeks": h["feasibility"]["work_weeks"],
            "what_it_explains": h["what_it_explains"],
            "missing": h["feasibility"]["missing"]}


def _sid(prompt: str, paths: list[str]) -> str:
    h = hashlib.sha1((prompt + "|".join(paths)).encode()).hexdigest()[:8]
    return f"run-{h}"
