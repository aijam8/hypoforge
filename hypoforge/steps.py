"""
The eight pipeline agents (real LLM calls via the modular router).

Each function is one step of the group's recommended workflow and is
evidence-first: claims carry provenance, hypotheses cite the evidence/gaps that
motivate them, and scores expose their reasoning.
"""
from __future__ import annotations

import os
import sys
from concurrent.futures import ThreadPoolExecutor

from . import router

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ===================================================================== 1. INTAKE
def intake(prompt: str, file_list: list[str], constraints: str = "") -> dict:
    files = "\n".join(f"- {f}" for f in file_list) or "(none)"
    p = f"""Convert this research request into a structured brief.

USER PROMPT: {prompt}
FILES PROVIDED:
{files}
EXTRA CONSTRAINTS: {constraints or '(none stated)'}

Return JSON with keys:
{{"domain": "...", "subfield": "...", "task_type": "...",
  "goal": "one-sentence research goal",
  "constraints": {{"budget": "...|unknown", "equipment": "...|unknown", "time": "...|unknown"}},
  "likely_environment": "the kind of lab/compute this user probably works in",
  "evidence_to_inspect": ["which provided files matter and why"],
  "search_topics": ["3-6 literature search topics for this goal"],
  "desired_output": "what a useful answer looks like for them"}}"""
    return router.generate_json("intake", p, "You are a research program officer who scopes projects precisely.")


# ========================================================== 3. EVIDENCE EXTRACTION
def extract_evidence(evidence_objs: list, max_workers: int = 6) -> list[dict]:
    """evidence_objs: list of ingest.Evidence. Returns evidence CARDS with provenance."""
    def one(idx_ev):
        i, ev = idx_ev
        body = _evidence_snippet(ev)
        p = f"""Read this {ev.kind} source and extract a structured evidence card.

SOURCE: {os.path.basename(ev.path)}
CONTENT (truncated):
{body}

Return JSON:
{{"source_type": "paper|dataset|lab_notes|figure|table|webpage|code|other",
  "summary": "2-3 sentences on what this source contains",
  "claims": ["factual claims or findings present (with numbers where given)"],
  "methods": ["methods/instruments/techniques mentioned or implied"],
  "assumptions": ["assumptions this source relies on"],
  "limitations": ["limitations / caveats / scope limits"],
  "entities": ["key variables, materials, organisms, or concepts"],
  "confidence": 0.0}}"""
        card = router.generate_json("extract", p, "You are a meticulous research analyst. Never invent content.")
        if not isinstance(card, dict):
            card = {}
        card["id"] = f"E{i+1}"
        card["provenance"] = ev.path
        card["kind"] = ev.kind
        return card

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        return list(ex.map(one, enumerate(evidence_objs)))


def _evidence_snippet(ev) -> str:
    if ev.dataframe is not None:
        df = ev.dataframe
        prof = ev.profile or {}
        cols = ", ".join(f"{c['name']}({c['dtype']})" for c in prof.get("columns", [])[:20])
        corr = prof.get("top_correlations", [])[:5]
        return (f"[tabular dataset] {prof.get('n_rows','?')} rows × {prof.get('n_cols','?')} cols\n"
                f"columns: {cols}\n"
                f"top correlations: {corr}\n"
                f"sample rows: {prof.get('sample_rows', [])[:3]}")
    return (ev.summary or "")[:3500]


# =========================================================== 4. LITERATURE REVIEW
def literature_review(brief: dict, evidence_cards: list[dict], allow_web: bool,
                      per_source: int = 6) -> dict:
    queries = brief.get("search_topics") or [brief.get("goal", "")]
    queries = [q for q in queries if q][:6]

    papers, fetched_urls = [], []
    if allow_web:
        try:
            from tools import lit_apis
            papers = lit_apis.search_all(queries, per_source=per_source)
            papers = [p for p in papers if not p.get("_error")]
            fetched_urls = [p.get("url", "") for p in papers if p.get("url")]
        except Exception:
            papers = []

    corpus = _format_papers(papers)
    ev_claims = "\n".join(f"[{c['id']}] " + "; ".join(c.get("claims", [])[:3])
                          for c in evidence_cards if c.get("claims"))[:2500]
    p = f"""Goal: {brief.get('goal')}
Domain: {brief.get('domain')}

USER-EVIDENCE CLAIMS (local):
{ev_claims or '(none extracted)'}

RETRIEVED LITERATURE ({len(papers)} papers):
{corpus}

Synthesize the state of knowledge. Return JSON:
{{"field_summary": "3-4 sentences",
  "claim_map": [{{"claim": "...", "support": "consensus|mixed|single-study", "sources": ["paper title or Eid"]}}],
  "contradictions": ["where sources disagree"],
  "gap_map": [{{"gap": "specific unanswered question / untested relationship", "why_open": "..."}}],
  "literature_limitations": ["methodological limits across the field"],
  "extension_points": ["concrete future-work openings this evidence base invites"]}}"""
    syn = router.generate_json("literature", p,
                               "You are a rigorous research librarian. Never invent citations.",
                               max_tokens=2200)
    if not isinstance(syn, dict):
        syn = {}
    syn["queries"] = queries
    syn["papers"] = papers
    syn["fetched_urls"] = fetched_urls
    syn["n_papers"] = len(papers)
    return syn


def _format_papers(papers: list[dict], limit: int = 24) -> str:
    rows = []
    for p in papers[:limit]:
        ab = (p.get("abstract") or "").replace("\n", " ")[:500]
        rows.append(f"- ({p.get('source')}, {p.get('year') or 'n.d.'}) {p.get('title')}: {ab}")
    return "\n".join(rows) or "(no papers retrieved)"


# ============================================================== 5. USER-CONTEXT
def user_context(brief: dict, evidence_cards: list[dict],
                 institution_text: str | None = None, local_context: str = "") -> dict:
    methods = sorted({m for c in evidence_cards for m in c.get("methods", [])})[:25]
    limitations = sorted({l for c in evidence_cards for l in c.get("limitations", [])})[:20]
    inst = (institution_text or "")[:4000]
    p = f"""Estimate this researcher's REAL experimental capabilities and, just as
importantly, what they CANNOT do. Pay careful attention to anything stating a
capability is missing ("we do NOT have…", "no access to…", budget limits).

GOAL: {brief.get('goal')}
DOMAIN: {brief.get('domain')}  ·  LIKELY ENVIRONMENT: {brief.get('likely_environment')}
STATED CONSTRAINTS: {brief.get('constraints')}

LAB MATERIALS / NOTES (their own words — trust these most):
{local_context[:3500] or '(none provided)'}

METHODS SEEN IN THEIR MATERIALS: {methods or '(none)'}
LIMITATIONS THEY NOTED: {limitations or '(none)'}
{"PUBLIC INSTITUTION PAGE (opt-in):" + chr(10) + inst if inst else "No institution page provided (infer from field)."}

Rules: If the materials say a capability is unavailable (e.g. no high-pressure /
diamond-anvil cell, no MBE, no synchrotron), DO NOT list it under equipment, and
DO list experiments that require it under `likely_infeasible`.

Return JSON:
{{"likely_equipment": ["instruments they actually have access to"],
  "techniques": ["techniques realistically available"],
  "compute_access": "none|workstation|cluster|hpc|cloud — best guess + why",
  "measurement_access": "what they can measure in-house vs needs collaboration",
  "feasible_experiment_types": ["experiment types they can really run"],
  "likely_infeasible": ["experiments too expensive/unavailable for THIS setup — be specific"],
  "confidence": 0.0,
  "basis": "what this inference is based on"}}"""
    src = "institution page (opt-in)" if inst else ("lab notes + field prior" if local_context else "field prior")
    out = router.generate_json("usercontext", p,
                               "You estimate lab capabilities soberly and take 'we do not have X' literally.")
    if isinstance(out, dict):
        out.setdefault("basis", src)
    return out if isinstance(out, dict) else {}


# =========================================================== 6. HYPOTHESIS GEN
def generate_hypotheses(brief: dict, lit: dict, capability: dict, n: int = 6) -> list[dict]:
    gaps = "\n".join(f"- {g.get('gap')}" for g in lit.get("gap_map", [])[:8]) or "(none)"
    exts = "\n".join(f"- {e}" for e in lit.get("extension_points", [])[:6]) or "(none)"
    p = f"""Generate {n} novel, testable hypotheses for this researcher.

GOAL: {brief.get('goal')}
KNOWLEDGE GAPS:
{gaps}
EXTENSION POINTS:
{exts}
WHAT THEY CAN REALISTICALLY DO: {capability.get('feasible_experiment_types')}
LIKELY INFEASIBLE: {capability.get('likely_infeasible')}

Each hypothesis MUST be grounded in a gap and aligned with their capabilities.
Return a JSON array; each element:
{{"id": "H1",
  "title": "concise name",
  "statement": "a single falsifiable claim",
  "what_it_explains": "the phenomenon/gap it would resolve",
  "prediction": "the concrete, measurable prediction if true",
  "supporting_evidence": "which gap/claim/Eid motivates it",
  "evidence_that_would_weaken": "what observation would falsify it",
  "why_it_matters": "the scientific payoff",
  "test_plan": "a concrete experiment/analysis to test it",
  "required_equipment": ["techniques/instruments needed"]}}"""
    out = router.generate_json("hypothesis", p,
                               "You are a creative but rigorous PI. Prefer the non-obvious that sits at the edge of current knowledge.",
                               max_tokens=4000, temperature=0.75)
    hyps = out if isinstance(out, list) else (out.get("hypotheses") if isinstance(out, dict) else None)
    hyps = hyps or []
    for i, h in enumerate(hyps, 1):
        h.setdefault("id", f"H{i}")
    return hyps


# ================================================================ 7. SCORING
_DIMS = ["expected_information_gain", "novelty", "feasibility", "cost_effort",
         "time_to_test", "equipment_dependence", "field_relevance", "uncertainty_reduction"]


def score_hypotheses(hyps: list[dict], capability: dict, brief: dict) -> list[dict]:
    listing = "\n".join(
        f"{h['id']}: {h['statement']} | needs: {h.get('required_equipment')}" for h in hyps)
    p = f"""Score each hypothesis on multiple objectives, RELATIVE to each other.

THIS LAB CAN USE: {capability.get('likely_equipment')}
TECHNIQUES AVAILABLE: {capability.get('techniques')}
THIS LAB CANNOT DO (infeasible): {capability.get('likely_infeasible')}
FIELD: {brief.get('domain')}

HYPOTHESES:
{listing}

CRITICAL feasibility rule: if a hypothesis requires equipment/techniques that are
in the CANNOT-DO list or clearly absent from the AVAILABLE list (e.g. high-pressure
/ diamond-anvil cell, MBE thin films, synchrotron, neutron beamline when the lab
lacks them), its feasibility MUST be ≤ 0.2 and you must name the blocker in
missing_equipment. Only experiments runnable with the available equipment score high.

For EACH hypothesis return scores in [0,1] (higher=better, EXCEPT cost_effort,
time_to_test, equipment_dependence where higher = MORE burden):
{{"scores": [
  {{"id": "H1",
    "expected_information_gain": 0.0, "novelty": 0.0, "feasibility": 0.0,
    "cost_effort": 0.0, "time_to_test": 0.0, "equipment_dependence": 0.0,
    "field_relevance": 0.0, "uncertainty_reduction": 0.0,
    "missing_equipment": ["..."], "one_line_justification": "..."}}
]}}
Be discriminating — do not give everything the same score."""
    out = router.generate_json("ranking", p,
                               "You are a crisp, calibrated multi-objective evaluator.", max_tokens=3200)
    rows = out.get("scores", []) if isinstance(out, dict) else (out if isinstance(out, list) else [])
    by_id = {r.get("id"): r for r in rows if isinstance(r, dict)}
    for h in hyps:
        s = by_id.get(h["id"], {})
        h["scores"] = {d: _clamp(s.get(d, 0.5)) for d in _DIMS}
        h["missing_equipment"] = s.get("missing_equipment", [])
        h["score_justification"] = s.get("one_line_justification", "")
        h["value"] = _composite(h["scores"])
    hyps.sort(key=lambda h: h["value"], reverse=True)
    return hyps


def _composite(s: dict) -> float:
    # value per unit effort: reward info/novelty/feasibility/relevance, penalize burden.
    benefit = (0.30 * s["expected_information_gain"] + 0.18 * s["uncertainty_reduction"]
               + 0.16 * s["novelty"] + 0.14 * s["field_relevance"])
    gate = s["feasibility"]
    burden = 1.0 + 0.6 * s["cost_effort"] + 0.5 * s["time_to_test"] + 0.7 * s["equipment_dependence"]
    return round(gate * (benefit) / burden, 4)


def _clamp(v):
    try:
        return max(0.0, min(1.0, float(v)))
    except Exception:
        return 0.5


# ====================================================== 7b. TECHNOLOGY PLAN
def technology_plan(hyp: dict, capability: dict, brief: dict) -> list[dict]:
    """Concrete technologies/instruments/methods needed to actually run the chosen
    hypothesis, each tagged by availability against the inferred lab capabilities."""
    p = f"""List the concrete technologies, instruments, and methods needed to actually
carry out this experiment — be specific (name real techniques, not vague categories).

FIELD: {brief.get('domain')}
HYPOTHESIS: {hyp.get('statement')}
TEST PLAN: {hyp.get('test_plan')}
WHAT THE LAB HAS: equipment={capability.get('likely_equipment')}, techniques={capability.get('techniques')}
WHAT THE LAB LACKS: {capability.get('likely_infeasible')}

For each technology, decide availability by comparing to what the lab has/lacks:
in_house (they have it) · acquire (buy/build, give rough cost/effort) · collaborate
(use a shared/partner facility) · unknown.

Return JSON:
{{"technologies": [
  {{"name": "specific instrument/technique (e.g. 'TEM for particle sizing', 'fixed-bed reactor + GC-MS')",
    "purpose": "the step in THIS experiment it enables",
    "availability": "in_house|acquire|collaborate|unknown",
    "note": "rough cost/effort, or an alternative if they lack it"}}
]}}
Cover the full workflow: synthesis/sample prep, the core measurement, and characterization."""
    out = router.generate_json("technology", p,
                               "You are an experimental methods engineer who knows lab instrumentation and rough costs.",
                               max_tokens=1600)
    techs = out.get("technologies") if isinstance(out, dict) else (out if isinstance(out, list) else [])
    return [t for t in (techs or []) if isinstance(t, dict) and t.get("name")][:10]


# ================================================================== 8. DEBATE
_CRITICS = {
    "critic_literature": "Literature reviewer: is each hypothesis truly grounded in the evidence/gaps, or already answered?",
    "critic_feasibility": "Feasibility critic: can THIS lab actually run it given their equipment? Flag the unrunnable.",
    "critic_novelty": "Novelty critic: is it genuinely new, or a restatement of known results? Name the nearest prior work if any.",
    "experimental_design": "Experimental designer: is the test plan sound and the prediction falsifiable? Suggest a sharper test.",
    "uncertainty_analyst": "Uncertainty analyst: which hypothesis most reduces ambiguity / best discriminates competing explanations?",
}


def debate(top: list[dict], brief: dict, lit: dict, capability: dict) -> dict:
    listing = "\n".join(f"{h['id']}: {h['title']} — {h['statement']} "
                        f"(test: {h.get('test_plan','')})" for h in top)
    ctx = (f"GOAL: {brief.get('goal')}\nCAPABILITIES: {capability.get('feasible_experiment_types')}\n"
           f"KEY GAPS: {[g.get('gap') for g in lit.get('gap_map', [])[:5]]}\n\nHYPOTHESES:\n{listing}")

    def run(role_focus):
        role, focus = role_focus
        p = (f"{ctx}\n\nYour role — {focus}\n\nReturn JSON: "
             '{"assessment": "2-4 sentences across the hypotheses", '
             '"per_hypothesis": [{"id":"H1","verdict":"strong|ok|weak","note":"...",'
             '"score_delta": 0.0}]}')
        out = router.generate_json(role, p, f"You are the {role}. Be specific and critical.")
        return role, (out if isinstance(out, dict) else {"assessment": "", "per_hypothesis": []})

    with ThreadPoolExecutor(max_workers=5) as ex:
        reviews = dict(ex.map(run, _CRITICS.items()))

    # apply net score deltas
    delta = {h["id"]: 0.0 for h in top}
    for r in reviews.values():
        for ph in r.get("per_hypothesis", []):
            if ph.get("id") in delta:
                delta[ph["id"]] += _clamp_delta(ph.get("score_delta", 0))
    for h in top:
        h["value"] = round(max(0.0, h["value"] + delta[h["id"]] * 0.1), 4)
        h["debate_delta"] = round(delta[h["id"]], 3)

    # final synthesis
    syn = router.generate_json(
        "synthesis",
        f"{ctx}\n\nCRITIC REVIEWS:\n" +
        "\n".join(f"[{k}] {v.get('assessment','')}" for k, v in reviews.items()) +
        "\n\nProduce the final 'what to test next' verdict. Return JSON: "
        '{"recommendation_id": "H?", "rationale": "why this one, now", '
        '"runner_up_id": "H?", "caveats": ["honest caveats"]}',
        "You are the final synthesizer. Decide; do not hedge.", max_tokens=1200)
    return {"reviews": reviews, "synthesis": syn if isinstance(syn, dict) else {}}


def _clamp_delta(v):
    try:
        return max(-1.0, min(1.0, float(v)))
    except Exception:
        return 0.0
