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

# add a key for the real pipeline (OpenRouter or DeepSeek)
cp .env.example .env && echo "OPENROUTER_API_KEY=sk-or-..." >> .env

./forge run                                   # real pipeline on the bundled example
./forge run --data mydata.csv --paper ref.pdf "my research question"
./forge run --local-only                      # no web; read only local files
./forge run --no-internet                     # zero egress: no web AND no model calls
./forge demo                                  # scripted, fully-offline demo (no key needed)
```

The router (`hypoforge/config/models.yaml`) maps each subtask to its own model —
swap DeepSeek / Llama / Qwen / Gemini per slot without touching code.

## `forge run` — the real pipeline

An evidence-first implementation of the 8-step workflow, every step a live model call:

```
① intake        prompt + files → a structured research brief
② context mode   local-first / institution-aware / no-internet (your choice)
③ ingest         each file → an Evidence card: claims · methods · assumptions · limitations · confidence (with provenance)
④ literature     real search (Semantic Scholar / arXiv / OpenAlex / web) → claim map · gap map · contradictions · extension points
⑤ user-context   infer the lab's real equipment & what it CANNOT do → feasibility veto
⑥ generate       novel, testable hypotheses grounded in the gaps and the lab's constraints
⑦ score          multi-objective: info-gain · novelty · feasibility · cost · time · equipment · relevance · uncertainty-reduction
⑧ debate         5 critics (literature · feasibility · novelty · design · uncertainty) → synthesizer → "what to test next"
```

Inputs can be **CSV/Excel/Parquet/HDF5/NumPy, PDF, Markdown/TXT, and images** —
anything the parser registry can open. Every claim keeps its source; every
hypothesis cites the gap it addresses; the feasibility score reflects *your* bench.

**Honest data-flow manifest** (`/planes`): raw files never leave the machine
(`0 raw bytes transmitted`); it reports exactly how much *derived* text went to the
model provider and which public pages were fetched. `--no-internet` makes egress
truly zero (mock models).

## `forge demo` — the scripted offline showcase

A deterministic, no-API-key soft-matter walkthrough (real GP + info-gain + anomaly
engine under scripted narration) used for a bulletproof live demo. `forge replay`
re-streams a recorded run.

## Architecture

| Module | Role |
|---|---|
| `hypoforge/cli.py` | `forge run / demo / replay / profile` |
| `hypoforge/pipeline.py` | **the real 8-step pipeline** (`forge run`) |
| `hypoforge/steps.py` | the 8 agents: intake · extract · literature · user-context · generate · score · debate |
| `hypoforge/router.py` | modular per-role model routing (OpenRouter / DeepSeek / mock) + usage accounting |
| `hypoforge/planes.py` | honest 3-plane firewall (local-raw / model-derived / web) + `/planes` manifest |
| `hypoforge/present.py` | rich rendering of briefs, evidence, maps, scores, the final report |
| `parsers/`, `tools/lit_apis.py` | multi-format ingestion + real literature APIs (Semantic Scholar/arXiv/OpenAlex/web) |
| `hypoforge/orchestrator.py`, `engine.py`, `capability.py`, `evaluate.py`, `render.py` | the scripted `forge demo` (GP + info-gain + anomaly engine) |

Design rationale and the full build plan are in [`DESIGN.md`](DESIGN.md); the demo
runbook is in [`DEMO.md`](DEMO.md).

## Legacy

`app.py` is an earlier Streamlit prototype (upload → parse → lit-review →
hypotheses → validate). It's retired in favor of the CLI but kept for reference;
its parsers and literature clients are reused by HypoForge.

---

<p align="center"><sub>Hackathon project · inspired by PiEvo · MIT-licensed</sub></p>
