<h1 align="center">🔬 HypoForge</h1>

<p align="center"><em>Not what's novel — but what's worth running on the bench you actually own.</em></p>

HypoForge is an **ultra-agentic command-line research strategist**. Point it at your
local data and a research prompt; it ingests the data, profiles *your lab's real
instruments* from public web sources, reviews the literature, and runs a closed
**Bayesian discovery loop** that proposes, debates, and self-tests hypotheses —
then ranks them by **information-gain per unit of effort on the bench you can
actually use**, while guaranteeing your raw data never leaves the machine.

Built for an AI hackathon, inspired by **PiEvo** (*Principle-Evolvable Scientific
Discovery via Uncertainty Minimization*, ICML 2026, [arXiv:2602.06448](https://arxiv.org/abs/2602.06448)).

---

## Why it's different

Every "agents for science" tool ranks hypotheses by novelty. HypoForge ranks them
by **feasibility-weighted information gain**, on a hard veto:

> The flashiest hypothesis has the most information — but if your lab can't run it,
> HypoForge **demotes it** and recommends the most informative experiment you *can*
> run. That's the difference between a brainstorm and a research plan.

Three things no other tool combines:
1. **Institution capability profiling** — infers your real equipment/expertise and uses it as a feasibility veto.
2. **A visible data firewall** — raw experimental data stays local (`0 bytes left the machine`); only field/institution metadata is web-queried. It's code, not a promise.
3. **Quantitative next-experiment selection** — a PiEvo-style closed loop that minimizes uncertainty over competing *principles*, with the entropy visibly collapsing as evidence arrives.

## Quickstart

```bash
git clone https://github.com/aijam8/hypoforge.git
cd hypoforge
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
chmod +x forge

./forge run        # full agentic run — fully offline, no API keys, deterministic
./forge replay     # re-stream a recorded run (the bulletproof demo path)
./forge profile    # the inferred lab-capability profile, standalone
```

> Runs out-of-the-box with **no API keys** (mock LLM + canned profile + seeded
> fixtures). For live models, drop `OPENROUTER_API_KEY` or `DEEPSEEK_API_KEY` in
> `.env`; the per-role router (`hypoforge/config/models.yaml`) does the rest.

## What a run does

```
ingest (LOCAL) → profile the lab (WEB) → warm-up → closed loop → debate → ranked board → /planes
```

1. **Ingest** local data + literature into a unified `Evidence` model (CSV/PDF/HDF5/… via a graceful parser registry).
2. **Profile the lab** — discover the group's site, infer instruments → a `CapabilityProfile` feasibility veto.
3. **Warm-up** — seed competing *principles* from the literature; fit a Gaussian-process surrogate.
4. **Closed loop** — information-directed experiment selection; when your local data contradicts the literature prior, an **anomaly fires** and a new principle is spawned. The **principle-posterior entropy bends toward zero** as belief concentrates.
5. **Debate** — proponent / skeptic / referee; the referee is the only agent allowed to *move a score*.
6. **Report** — a ranked board: `★ NEXT EXPERIMENT` (highest info-gain you can run) vs the demoted moonshot (most info, but unrunnable).

The information-gain number is honestly labeled *expected model-discrimination
(proxy, nats)* — a transparent decision-support heuristic, not a claim of
calibrated information about nature.

## Architecture

| Module | Role |
|---|---|
| `hypoforge/cli.py` | `forge run / replay / profile` |
| `hypoforge/orchestrator.py` | the rails — scripted control flow rendered agentically |
| `hypoforge/engine.py` | GP surrogate + variance-reduction info-gain + 2-principle posterior + anomaly detection |
| `hypoforge/capability.py` | institution profiling → feasibility veto (the wedge) |
| `hypoforge/evaluate.py` | `V(h) = gate(F,T) · quality` ranking |
| `hypoforge/debate.py` | proponent / skeptic / referee |
| `hypoforge/router.py` | modular per-role model routing (OpenRouter / DeepSeek / mock) |
| `hypoforge/render.py` | one event renderer shared by live run **and** replay |
| `hypoforge/planes.py` | the two-data-plane firewall + `/planes` manifest |
| `parsers/`, `tools/lit_apis.py` | salvaged multi-format ingestion + literature APIs |

Design rationale and the full build plan are in [`DESIGN.md`](DESIGN.md); the demo
runbook is in [`DEMO.md`](DEMO.md).

## Legacy

`app.py` is an earlier Streamlit prototype (upload → parse → lit-review →
hypotheses → validate). It's retired in favor of the CLI but kept for reference;
its parsers and literature clients are reused by HypoForge.

---

<p align="center"><sub>Hackathon project · inspired by PiEvo · MIT-licensed</sub></p>
