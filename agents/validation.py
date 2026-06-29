"""
Validation agent — an adversarial panel of critics.

Each hypothesis is judged independently, in parallel, by four specialist critics:
  - novelty       : is it actually new vs. the literature?
  - testability   : is it falsifiable with a concrete, feasible method?
  - grounding     : is it genuinely supported by the uploaded data?
  - plausibility  : is the proposed mechanism scientifically sound?

Scores (1-10) are aggregated into an overall verdict. A final "editor" pass turns
each critic's improvement notes into a single sharpened version of the hypothesis.
This is the "ensure they are sensible" stage.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from .llm import call_json

_CRITICS = {
    "novelty": (
        "You are a skeptical reviewer obsessed with novelty. Penalize hypotheses "
        "that merely restate established findings or the obvious.",
        "Is this genuinely novel relative to the literature gaps provided? Could it "
        "already be answered by existing work?",
    ),
    "testability": (
        "You are a hard-nosed experimentalist. You only respect falsifiable claims "
        "with a feasible, concrete test.",
        "Is the hypothesis falsifiable? Is the test plan concrete, specific and "
        "actually feasible? Are variables operationalizable?",
    ),
    "grounding": (
        "You are a data-integrity auditor. You check that claims are actually "
        "supported by the dataset at hand, not wishful thinking.",
        "Is this hypothesis genuinely grounded in the provided data (its variables, "
        "patterns, scope)? Or does it require data we do not have?",
    ),
    "plausibility": (
        "You are a domain expert checking scientific soundness.",
        "Is the proposed mechanism scientifically plausible and internally "
        "consistent? Any logical flaws or contradictions with known science?",
    ),
}

_WEIGHTS = {"novelty": 1.1, "testability": 1.2, "grounding": 1.3, "plausibility": 1.0}


def validate_all(hypotheses: list[dict], understanding: dict,
                 literature: dict, max_workers: int = 8) -> list[dict]:
    context = _shared_context(understanding, literature)
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        out = list(ex.map(lambda h: _validate_one(h, context), hypotheses))
    out.sort(key=lambda h: h["validation"]["overall_score"], reverse=True)
    return out


def _validate_one(hyp: dict, context: str) -> dict:
    hyp_text = _format_hyp(hyp)
    with ThreadPoolExecutor(max_workers=len(_CRITICS)) as ex:
        reviews = dict(ex.map(
            lambda kv: (kv[0], _run_critic(kv[0], kv[1], hyp_text, context)),
            _CRITICS.items()))

    scores = {k: r.get("score", 5) for k, r in reviews.items()}
    overall = round(
        sum(scores[k] * _WEIGHTS[k] for k in scores) / sum(_WEIGHTS.values()), 2)
    verdict = ("strong" if overall >= 7.5 else
               "promising" if overall >= 6 else
               "weak" if overall >= 4 else "rejected")
    refined = _editor(hyp_text, reviews, context) if overall >= 4 else None

    hyp = dict(hyp)
    hyp["validation"] = {
        "scores": scores,
        "overall_score": overall,
        "verdict": verdict,
        "reviews": reviews,
        "refined_hypothesis": refined,
    }
    return hyp


def _run_critic(name: str, spec, hyp_text: str, context: str) -> dict:
    persona, focus = spec
    prompt = f"""{context}

HYPOTHESIS UNDER REVIEW:
{hyp_text}

Your job ({name}): {focus}

Return JSON:
{{"score": <integer 1-10>,
  "critique": "your specific, critical assessment (2-3 sentences)",
  "red_flags": ["concrete problems, if any"],
  "improvement": "one concrete change that would most strengthen it"}}"""
    res = call_json(prompt, persona, temperature=0.3)
    if not isinstance(res, dict) or res.get("_parse_error"):
        return {"score": 5, "critique": "(critic unavailable)",
                "red_flags": [], "improvement": ""}
    try:
        res["score"] = max(1, min(10, int(round(float(res.get("score", 5))))))
    except Exception:
        res["score"] = 5
    return res


def _editor(hyp_text: str, reviews: dict, context: str) -> dict:
    notes = "\n".join(f"- {k}: {r.get('improvement', '')}"
                      for k, r in reviews.items() if r.get("improvement"))
    prompt = f"""{context}

ORIGINAL HYPOTHESIS:
{hyp_text}

CRITIC IMPROVEMENT NOTES:
{notes}

Rewrite the hypothesis incorporating the valid critiques, keeping it novel and
testable. Return JSON:
{{"statement": "sharpened falsifiable claim",
  "test_plan": "improved concrete test",
  "what_changed": "1 sentence on what you fixed"}}"""
    res = call_json(prompt, "You are a rigorous journal editor.", temperature=0.4)
    return res if isinstance(res, dict) and not res.get("_parse_error") else None


def _shared_context(understanding: dict, literature: dict) -> str:
    return f"""CONTEXT
Domain: {understanding.get('domain')}
Data: {understanding.get('description')}
Key variables: {understanding.get('key_variables')}
Literature knowledge gaps:
{chr(10).join('  - ' + g for g in literature.get('knowledge_gaps', [])) or '  (none)'}"""


def _format_hyp(h: dict) -> str:
    return (f"Title: {h.get('title')}\n"
            f"Statement: {h.get('statement')}\n"
            f"Rationale: {h.get('rationale')}\n"
            f"Gap addressed: {h.get('knowledge_gap_addressed')}\n"
            f"Data grounding: {h.get('data_grounding')}\n"
            f"Test plan: {h.get('test_plan')}\n"
            f"Predicted outcome: {h.get('predicted_outcome')}")
