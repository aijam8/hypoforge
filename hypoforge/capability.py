"""
Institution capability profiling — the differentiator.

For the hackathon this loads a CANNED, human-ratified CapabilityProfile from
fixtures/ (a live crawl would be attempted with a short timeout, then fall back
to this). The profile turns each hypothesis's required techniques into a hard
feasibility veto + difficulty + work-weeks estimate — "can THIS lab actually run
it?".
"""
from __future__ import annotations

import json
from pathlib import Path

_FIX = Path(__file__).parent / "fixtures" / "bnl_softmatter_profile.json"

# status -> capability weight (infeasible hard-vetoes)
_WEIGHT = {"in_house": 1.0, "shared": 0.7, "collaborator": 0.4,
           "acquirable": 0.25, "infeasible": 0.0}


class CapabilityProfile:
    def __init__(self, data: dict):
        self.data = data
        self.instruments = data.get("instruments", [])
        self._by_technique = {i["technique"]: i for i in self.instruments}

    @classmethod
    def canned(cls) -> "CapabilityProfile":
        return cls(json.loads(_FIX.read_text()))

    def lookup(self, technique: str) -> dict | None:
        if technique in self._by_technique:
            return self._by_technique[technique]
        # loose contains-match fallback
        for t, inst in self._by_technique.items():
            if technique.lower() in t.lower() or t.lower() in technique.lower():
                return inst
        return None

    def feasibility(self, required: list[str]) -> dict:
        """Return F in [0,1], plus difficulty(1-5), work_weeks, and missing items."""
        weights, confs, weeks, missing, statuses = [], [], [], [], []
        for tech in required:
            inst = self.lookup(tech)
            if inst is None:
                weights.append(0.0); confs.append(0.2); weeks.append(26)
                missing.append(tech); statuses.append("infeasible")
                continue
            st = inst.get("status", "infeasible")
            weights.append(_WEIGHT.get(st, 0.0))
            confs.append(inst.get("confidence", 0.5))
            weeks.append(inst.get("access_weeks", 4))
            statuses.append(st)
            if st in ("collaborator", "acquirable", "infeasible"):
                missing.append(f"{tech} ({st})")

        vetoed = any(w == 0.0 for w in weights)
        F = 0.04 if vetoed else (sum(weights) / len(weights))
        conf = sum(confs) / len(confs) if confs else 0.3
        work_weeks = int(max(weeks)) + len(required)            # rough serial cost
        # difficulty 1-5 from access friction + number of non-in-house pieces
        friction = max(weeks) / 6.0
        n_hard = sum(1 for s in statuses if s != "in_house")
        difficulty = int(min(5, max(1, round(1 + friction + 0.7 * n_hard))))
        return {
            "F": round(F, 3),
            "confidence": round(conf, 2),
            "difficulty": difficulty,
            "work_weeks": work_weeks,
            "missing": missing,
            "statuses": statuses,
            "vetoed": vetoed,
        }

    def summary_lines(self) -> list[tuple[str, str]]:
        rows = []
        for i in self.instruments:
            tag = {"in_house": "[green]in-house[/green]",
                   "shared": "[yellow]shared[/yellow]",
                   "collaborator": "[yellow]collaborator[/yellow]",
                   "acquirable": "[yellow]acquirable[/yellow]",
                   "infeasible": "[red]UNAVAILABLE[/red]"}.get(i["status"], i["status"])
            rows.append((i["name"], f"{i['technique']} — {tag} ({int(i['confidence']*100)}%)"))
        return rows
