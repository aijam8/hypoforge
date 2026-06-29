"""
Hypothesis evaluation & ranking.

V(h) = "research value per unit effort on THIS bench":

    quality = w_I·Î + w_E·E + w_N·N + w_D·D̂ + w_W·Ŵ      (merit)
    gate    = F^γF · T^γT                                  (feasibility & testability VETO)
    V(h)    = gate · quality

Î is the engine's information-gain (normalized). F is the capability feasibility
(a hard veto: an unrunnable hypothesis is *killed*, not averaged down). The
flashiest hypothesis (max Î) therefore gets DEMOTED below a runnable one — the
whole thesis in one number.
"""
from __future__ import annotations

import json
from pathlib import Path

_FIX = Path(__file__).parent / "fixtures" / "hypotheses.json"

W = {"I": 0.40, "E": 0.15, "N": 0.18, "D": 0.12, "Wk": 0.15}
GAMMA_F, GAMMA_T = 1.0, 0.7


def load_hypotheses() -> list[dict]:
    return json.loads(_FIX.read_text())


def evaluate(hypotheses: list[dict], engine, profile) -> list[dict]:
    # 1) raw info-gain (nats) from the engine at each design point
    for h in hypotheses:
        x = h["x_target"]
        h["info_gain"] = round(engine.info_gain(x["temperature_C"], x["shear_rate"]), 3)
    max_I = max((h["info_gain"] for h in hypotheses), default=1.0) or 1.0

    for h in hypotheses:
        feas = profile.feasibility(h["required_equipment"])
        h["feasibility"] = feas
        I_hat = h["info_gain"] / max_I
        E = h.get("_E", 0.7)                       # explanatory scope (rubric)
        N = _novelty(h)
        D_hat = (6 - feas["difficulty"]) / 5.0     # easier -> higher
        W_hat = 1.0 / (1.0 + feas["work_weeks"] / 4.0)
        T = h.get("_T", 0.85)                      # testability (rubric)

        quality = (W["I"] * I_hat + W["E"] * E + W["N"] * N
                   + W["D"] * D_hat + W["Wk"] * W_hat)
        gate = (feas["F"] ** GAMMA_F) * (T ** GAMMA_T)
        h["scores"] = {"I_hat": round(I_hat, 2), "E": E, "N": round(N, 2),
                       "D_hat": round(D_hat, 2), "W_hat": round(W_hat, 2),
                       "T": T, "F": feas["F"], "gate": round(gate, 3),
                       "quality": round(quality, 3)}
        h["novelty"] = round(N, 2)
        h["V"] = round(gate * quality, 4)

    hypotheses.sort(key=lambda h: h["V"], reverse=True)
    return hypotheses


def _novelty(h: dict) -> float:
    # embedding-distance spine would go here. Provisionally everything looks novel;
    # the DEBATE is what collapses novelty when the skeptic surfaces a near-neighbor
    # paper (it writes `novelty_value`). This is how debate visibly moves a score.
    return h.get("novelty_value", h.get("_N", 0.82))


def split_recommended_and_moonshot(ranked: list[dict]) -> tuple[dict, dict | None]:
    """#1 by V is the recommendation; the highest-info hypothesis that ISN'T #1
    (because it was vetoed/demoted) is the 'moonshot' contrast."""
    recommended = ranked[0]
    moonshot = None
    best_I = -1.0
    for h in ranked:
        if h["id"] != recommended["id"] and h["info_gain"] > best_I:
            best_I = h["info_gain"]
            moonshot = h
    # only call it a moonshot if it actually out-informs the recommendation
    if moonshot and moonshot["info_gain"] <= recommended["info_gain"]:
        moonshot = None
    return recommended, moonshot
