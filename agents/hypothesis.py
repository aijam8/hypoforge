"""
Hypothesis-generation agent.

Given (a) the data understanding/profile and (b) the literature's knowledge gaps,
it proposes novel, *testable* hypotheses — each one grounded in a specific gap and
in observable features of the data, with a concrete test plan.

To get diversity ("many agents"), we generate from several distinct framings in
parallel and pool the results.
"""
from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor

from .llm import call_json

_SYSTEM = (
    "You are a creative but rigorous principal investigator. You propose novel, "
    "falsifiable hypotheses that sit precisely at the boundary of current knowledge. "
    "Every hypothesis must be (1) testable with a concrete method, (2) grounded in "
    "the actual data provided, and (3) tied to a real gap in the literature. "
    "Avoid the obvious and the already-answered."
)

_FRAMINGS = [
    ("mechanistic", "Focus on underlying causal mechanisms linking the variables."),
    ("predictive", "Focus on what can predict or forecast what, and under which conditions."),
    ("comparative", "Focus on differences across subgroups, regimes, or conditions in the data."),
    ("cross-domain", "Borrow a mechanism from an adjacent field and apply it to this data."),
]


def generate(understanding: dict, literature: dict,
             n_total: int | None = None) -> list[dict]:
    n_total = n_total or int(os.getenv("NUM_HYPOTHESES", "6"))
    per_framing = max(1, round(n_total / len(_FRAMINGS)))

    ctx = _context(understanding, literature)
    with ThreadPoolExecutor(max_workers=len(_FRAMINGS)) as ex:
        batches = list(ex.map(
            lambda fr: _generate_one_framing(fr, ctx, per_framing), _FRAMINGS))

    hypotheses: list[dict] = []
    for (name, _), batch in zip(_FRAMINGS, batches):
        for h in batch:
            if isinstance(h, dict) and h.get("statement"):
                h["framing"] = name
                hypotheses.append(h)
    # assign stable ids, trim to target (+a little headroom)
    for i, h in enumerate(hypotheses, 1):
        h["id"] = f"H{i}"
    return hypotheses[: n_total + 2]


def _generate_one_framing(framing, ctx: str, k: int) -> list[dict]:
    name, instruction = framing
    prompt = f"""{ctx}

FRAMING: {name} — {instruction}

Generate {k} novel, testable hypotheses using THIS framing. Return a JSON array;
each element:
{{
  "title": "concise hypothesis name",
  "statement": "a single falsifiable claim (If/then or X relates to Y under Z)",
  "rationale": "why this is plausible, citing the data feature and the knowledge gap",
  "knowledge_gap_addressed": "which specific gap from the literature this targets",
  "data_grounding": "what in the provided data motivates this (columns/patterns)",
  "test_plan": "a concrete experiment or analysis that would confirm/refute it",
  "required_data": "what additional data or measurements are needed, if any",
  "predicted_outcome": "the expected result if the hypothesis is true",
  "novelty_basis": "why this isn't already answered by the retrieved literature"
}}
Return ONLY the JSON array."""
    res = call_json(prompt, _SYSTEM, temperature=0.75)
    if isinstance(res, list):
        return res
    if isinstance(res, dict):
        for v in res.values():
            if isinstance(v, list):
                return v
    return []


def _context(understanding: dict, literature: dict) -> str:
    gaps = literature.get("knowledge_gaps", [])
    return f"""DATA UNDERSTANDING
Domain: {understanding.get('domain')}
Description: {understanding.get('description')}
Key variables: {understanding.get('key_variables')}
Observed patterns: {understanding.get('observed_patterns')}

LITERATURE STATE
Field summary: {literature.get('field_summary')}
Established findings: {literature.get('established_findings')}
KNOWLEDGE GAPS (target these):
{_bullets(gaps)}
Open questions: {literature.get('open_questions')}"""


def _bullets(items) -> str:
    return "\n".join(f"  - {g}" for g in (items or [])) or "  (none identified)"
