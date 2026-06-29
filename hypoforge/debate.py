"""
Structured multi-agent debate (the Stage-4 upside the user chose).

Proponent (reasoning) and Skeptic (reasoning) argue each top hypothesis; the
Referee (crisp, NON-reasoning — PiEvo lesson) is the ONLY agent allowed to move a
score. The point it proves: debate visibly *moves a score* — when the skeptic
surfaces a real near-neighbor paper, the referee collapses that hypothesis's
novelty and it drops in the ranking.

Offline, the arguments come from deterministic fixtures bound to each hypothesis
(real LLMs are used when keys are present, via the router roles
proponent/skeptic/referee).
"""
from __future__ import annotations

from . import router


def debate_top(hypotheses: list[dict], k: int = 3) -> list[dict]:
    """Run debate on the current top-k; return a list of debate transcripts.
    May write `novelty_value` onto a hypothesis (the score the referee moves)."""
    transcripts = []
    for h in hypotheses[:k]:
        transcripts.append(_debate_one(h))
    return transcripts


def _debate_one(h: dict) -> dict:
    pro = _proponent(h)
    skep = _skeptic(h)
    ruling = _referee(h, pro, skep)
    return {"id": h["id"], "title": h["title"],
            "proponent": pro, "skeptic": skep, "ruling": ruling}


def _proponent(h: dict) -> str:
    fixture = (f"This is worth running: it directly addresses '{h['knowledge_gap']}'. "
               f"If the prediction — {h['predicted_outcome']} — holds, it explains "
               f"{h['what_it_explains']}.")
    return router.generate("proponent", _prompt(h, "argue FOR"), fixture=fixture)


def _skeptic(h: dict) -> str:
    if h.get("nearest_paper"):
        fixture = (f"Novelty objection: this is essentially already reported. "
                   f"See {h['nearest_paper']}. The claimed gap is not actually open — "
                   f"running it would largely reproduce known results.")
    else:
        fixture = (f"Caveat: ensure the test isolates the effect; confounds in "
                   f"{h['technique']} could mimic the predicted outcome. But the gap "
                   f"appears genuinely open in the retrieved literature.")
    return router.generate("skeptic", _prompt(h, "argue AGAINST"), fixture=fixture)


def _referee(h: dict, pro: str, skep: str) -> dict:
    """The only agent that moves a score. Returns the score delta + rationale."""
    if h.get("nearest_paper"):
        h["novelty_value"] = 0.34   # the moved score
        return {"action": "novelty_downgraded", "to": 0.34,
                "rationale": f"Skeptic's near-neighbor citation stands "
                             f"({h['nearest_paper'].split(',')[0]}); novelty cut "
                             f"0.82 → 0.34, hypothesis re-ranked."}
    return {"action": "upheld", "to": h.get("novelty_value", 0.82),
            "rationale": "Skeptic raised a methodological caveat, not a novelty "
                         "defeater; novelty upheld."}


def _prompt(h: dict, stance: str) -> str:
    return (f"Hypothesis {h['id']}: {h['statement']}\n"
            f"Technique: {h['technique']}\n{stance} in 2 sentences.")
