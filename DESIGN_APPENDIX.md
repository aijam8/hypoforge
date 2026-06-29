# HypoForge CLI — Design Dossier (agent outputs)


---

# Competitive landscape & differentiation

# Competitive Landscape: Agentic Scientific Discovery & Hypothesis Generation

## Per-system scan

**Google "AI co-scientist" / Gemini Hypothesis Generation** — Multi-agent system on Gemini 2.0 (Generation, Reflection, Ranking, Proximity, Evolution, Meta-review agents) that runs a "tournament of ideas," self-critiques, and ranks novel hypotheses. *Sources:* literature + web search; *Loop:* no autonomous execution — humans run wet-lab (validated ripasudil/AML targets at Stanford/Imperial). *Weakness:* closed, cloud-only, biomedical-leaning; no feasibility grounding to a specific lab; expensive; doesn't run its own experiments. ([deepmind.google](https://deepmind.google/blog/co-scientist-a-multi-agent-ai-partner-to-accelerate-research/), [rdworldonline](https://www.rdworldonline.com/google-ai-co-scientist-can-reduce-early-hypothesis-generation-from-weeks-to-days-in-some-cases/))

**Sakana AI Scientist v1/v2** — End-to-end autonomous ML research: ideation → code → experiments → paper, via best-first agentic tree search; one paper passed ICLR-workshop peer review. *Sources:* its own generated code/results, ML literature. *Loop:* yes, but only for *computational ML* experiments. *Weakness:* confined to ML/code experiments — "physical experiments cannot be automated"; no external data/equipment grounding; known to produce shallow papers. ([arxiv 2504.08066](https://arxiv.org/abs/2504.08066), [github](https://github.com/SakanaAI/AI-Scientist-v2))

**FutureHouse (Robin, PaperQA2, Aviary)** — PaperQA2 = superhuman literature QA; Aviary = training env for science agents; Robin orchestrates them to hypothesize→design→analyze (found ripasudil for dry AMD). *Sources:* full-text literature, clinical trials, Open Targets. *Loop:* partial — humans execute physical assays. *Weakness:* lit-review-centric; Robin is biology-specific; no user-data ingestion or equipment-feasibility layer. ([futurehouse.org](https://www.futurehouse.org/research-announcements/demonstrating-end-to-end-scientific-discovery-with-robin-a-multi-agent-system))

**SciAgents (MIT/Buehler)** — Multi-agent reasoning over a ~33k-node ontological knowledge graph built from ~1,000 papers; generates+refines bioinspired-materials hypotheses with mechanisms. *Sources:* KG from literature. *Loop:* no execution. *Weakness:* static KG, materials-only, no data/feasibility/closed loop. ([arxiv 2409.05556](https://arxiv.org/abs/2409.05556))

**MOOSE-Chem / MOOSE-Chem2** — Decompose chemistry hypothesis discovery into inspiration-retrieval → composition → ranking; v2 adds hierarchical search for fine-grained, experimentally-actionable detail. *Sources:* research-background text + literature corpus. *Loop:* no. *Weakness:* benchmark-bound (rediscovery), chemistry-only, no real data or execution. ([arxiv 2410.07076](https://arxiv.org/abs/2410.07076), [2505.19209](https://arxiv.org/abs/2505.19209))

**Ai2 Asta DataVoyager** — Planner/programmer/data-expert/critic agents that analyze *uploaded structured data* (CSV/Parquet/HDF5) and return cited, code-backed answers + hypotheses. *Sources:* user's local/structured datasets. *Loop:* no experimentation; verification weak. *Weakness:* data-analysis assistant, not a discovery loop; documented p-hacking risk, no literature synthesis or feasibility. ([allenai.org](https://allenai.org/blog/asta-datavoyager), [DiscoveryBench](https://arxiv.org/pdf/2407.01725))

**Self-driving labs (CMU Coscientist, LBNL A-Lab)** — Genuine closed loops: LLM + robotics autonomously plan, run, and refine real experiments (A-Lab: 41/58 materials in 17 days, Bayesian active learning). *Sources:* Materials Project DFT + live instrument data. *Loop:* yes, physical. *Weakness:* require dedicated robotic hardware/$$$; narrow chemistry/materials; inaccessible to a generic researcher at a CLI. ([A-Lab/SDL review](https://royalsocietypublishing.org/rsos/article/12/7/250646/235354/))

**PiEvo (ICML 2026)** — Bayesian optimization over an *evolving principle space*; Principle/Hypothesis/Experiment agents, GP-based uncertainty, IDS selection; +30% SQ, 83% faster convergence. *Loop:* yes, but on **high-fidelity surrogates only**, never real labs; no user-data/literature/feasibility layer. ([arxiv 2602.06448](https://arxiv.org/abs/2602.06448), [github](https://github.com/amair-lab/PiEvo))

**Closest prior art to our wedge:** "Goal-Driven and Constraint-Guided LLM Agents" (NAACL 2025) injects *resource/lab-feasibility constraints* into ranking — but constraints are manually specified, materials-only, no auto-discovery of the user's institution. ([arxiv 2501.13299](https://arxiv.org/html/2501.13299v1))

## Who-does-what

| System | Local user data | Lit review | Closed loop | Feasibility/equipment grounding | Form |
|---|---|---|---|---|---|
| Google co-scientist | No | Yes (search) | No (human lab) | No | Cloud/web |
| Sakana v2 | No | ML only | Yes (ML/code) | No | Code/cloud |
| FutureHouse Robin | No | Strong | Partial | No | Platform/API |
| SciAgents | No | KG | No | No | Research code |
| MOOSE-Chem 1/2 | No | Corpus | No | No | Research code |
| Asta DataVoyager | **Yes** | No | No | No | Web/app |
| SDL (A-Lab) | Instrument | Recipe extract | **Yes (physical)** | Implicit (its own rig) | Robotic lab |
| PiEvo | No | No | Yes (surrogate) | No | CLI (AutoGen) |
| **Ours** | **Yes (local)** | **Yes** | **Yes (surrogate/compute)** | **Yes (auto-profiled)** | **CLI** |

## White space nobody owns

1. **Institution-aware, equipment-grounded feasibility ranking — genuinely white space.** Every system ranks on novelty/plausibility; only NAACL-2025 touches feasibility, and that's *hand-specified*. **Nobody auto-discovers a user's lab/group website, crawls it, and infers realistic instruments/expertise to score "can *this* researcher actually test it?"** This is a defensible wedge: it personalizes output and exploits a clean data-plane split (local raw data never uploaded; only field/institution metadata hits the web).

2. **One CLI that fuses local data + literature → closed-loop info-gain experiments.** The pieces exist but are siloed: DataVoyager has local data but no loop/lit; co-scientist/Robin have lit but no local data or execution; PiEvo/SDL have loops but no data+lit ingestion and need surrogates or robots. **No single Claude-Code-style CLI spans all four** with PiEvo-style IDS/uncertainty-minimization over *pluggable software* experiments (simulations/surrogates) — runnable on a laptop, no robotic rig.

3. **Actionable guidance per hypothesis** (difficulty, effort, what-it-explains, quantitative information-gain) + explicit agent debate. Co-scientist debates but emits a ranked list, not effort/feasibility economics. Pairing **IDS info-gain numbers with effort/equipment cost** is unoccupied.

## Sharpest wedge to bet on

**Equipment-grounded feasibility as the ranking objective.** Don't compete on "more novel hypotheses" (Google/Sakana/FutureHouse win on scale). Win on **"hypotheses *you* can actually run, ranked by information-gain-per-unit-effort *on your bench*."** It's the only axis above that no funded lab occupies, it's domain-agnostic, it directly leverages the local-vs-web data-plane split, and it reframes the whole tool from "idea generator" to "personalized research-strategist" — a category of one.

Sources: [DeepMind co-scientist](https://deepmind.google/blog/co-scientist-a-multi-agent-ai-partner-to-accelerate-research/), [Sakana v2](https://arxiv.org/abs/2504.08066), [Robin/FutureHouse](https://www.futurehouse.org/research-announcements/demonstrating-end-to-end-scientific-discovery-with-robin-a-multi-agent-system), [SciAgents](https://arxiv.org/abs/2409.05556), [MOOSE-Chem](https://arxiv.org/abs/2410.07076), [MOOSE-Chem2](https://arxiv.org/abs/2505.19209), [Asta DataVoyager](https://allenai.org/blog/asta-datavoyager), [A-Lab/SDL](https://royalsocietypublishing.org/rsos/article/12/7/250646/235354/), [PiEvo](https://arxiv.org/abs/2602.06448), [Constraint-Guided LLM Agents](https://arxiv.org/html/2501.13299v1)


---

# PiEvo adaptation / information-gain math

# PiEvo → Our CLI: Concrete Closed-Loop Bayesian Design

Adapted for an ultra-agentic, domain-agnostic CLI where "experiments" are **local, runnable, lightweight computations** (simulations, surrogate models, numerical solvers, or literature lookups). Two data planes are respected throughout: the **local plane** (raw data + embeddings, never leaves the machine) and the **web/profiling plane** (field/institution metadata only).

---

## Notation (our adaptation of PiEvo)

| Symbol | Meaning |
|---|---|
| `X` | design/candidate space — the knobs of a runnable experiment (a dict-schema of params) |
| `x ∈ X` | one concrete experiment configuration |
| `h` | a hypothesis: NL proposition + a target region/point `x_h ∈ X` + parent principle |
| `P` | a principle: NL proposition constraining which `h` are plausible |
| `P_t` | active principle set at round `t` |
| `w_t(P) = p_t(P)` | posterior weight of principle `P`, `Σ_P w_t(P)=1` |
| `e_h, e_P` | unit-normalized text embeddings of hypothesis / principle |
| `φ(h,P)` | semantic-bridge feature vector (Eq. 2 below) |
| `GP_P` | per-principle Gaussian-Process expert: `(x, φ) → (μ_P, σ_P²)` |
| `μ_P(h), σ_P²(h)` | GP_P predictive mean / epistemic variance for `h` |
| `μ̄(h) = Σ_P w_t(P) μ_P(h)` | posterior-mixture predictive mean |
| `y_t, σ_obs²` | observation and its noise variance |

---

## 1. Data structures (plain Python)

```python
from dataclasses import dataclass, field
from typing import Optional, Literal
import numpy as np

Vec = np.ndarray  # float32

@dataclass
class Principle:
    id: str
    text: str                      # NL proposition: "Yield saturates with catalyst load above ~X mol%"
    embedding: Vec                 # e_P, unit-normalized, LOCAL plane
    prior_logw: float              # log p_0(P), from lit-review confidence
    post_logw: float               # log p_t(P) (unnormalized); normalize over P_t at read time
    provenance: Literal["literature", "anomaly", "warmup", "user"]
    spawned_round: int
    gp: "GPExpert"                 # its calibrated surrogate (see §2)
    obs_ids: list[str] = field(default_factory=list)   # observations explained by this P

@dataclass
class Hypothesis:
    id: str
    text: str                      # "Increasing temperature 20->40C raises conversion >15%"
    embedding: Vec                 # e_h
    parent_principle_id: str
    x_target: dict                 # concrete point/region in X to probe
    mode: Literal["explore", "exploit"]
    # guidance metadata (user requirement #6):
    difficulty: float              # 0..1, LLM+cost-model estimate
    effort: dict                   # {"compute_s": .., "human_min": .., "$": ..}
    explains: list[str]            # principle_ids this h would discriminate
    info_gain: Optional[float] = None   # I_t(h), filled by IDS
    regret: Optional[float] = None      # Delta_t(h)
    ids_score: Optional[float] = None   # Delta^2 / I

@dataclass
class Observation:
    id: str
    hypothesis_id: str
    x: dict                        # config actually run
    y: float                       # scalar outcome (see §2 "what is y")
    sigma_obs: float               # measurement/sim noise (1 std)
    source: Literal["sim", "compute", "surrogate", "literature", "user_data"]
    round: int

@dataclass
class WorldState:
    P_t: list[Principle]           # the Active Principle set
    candidates: list[Hypothesis]
    history: list[Observation]
    design_space: dict             # schema of X
    round: int
```

- **Active Principle set `P_t`**: just `WorldState.P_t`. It *grows* (§4) — never assume fixed cardinality.
- **Posterior `p_t(P)`**: stored as unnormalized `post_logw` per principle; the live distribution is `softmax([P.post_logw for P in P_t])`. MAP principle = `argmax`. Store in log-space for numerical stability across many Bayes updates.

---

## 2. Semantic-embedding → GP bridge (Eq. 2)

**Embedding model (local plane).** Use a *local* sentence-embedding model so raw domain text never leaves the box: `BAAI/bge-small-en-v1.5` (384-d) or `gte-small` via `sentence-transformers`. Unit-normalize. (The web/profiling plane may use an API embedding — different plane, different model is fine.) Embeddings are deterministic + cheap, so this does **not** burn LLM budget — consistent with the cheap-LLM preference.

**The bridge feature (our Eq. 2).** PiEvo's `φ(h,P) = [e_h·e_P, ‖e_h−e_P‖₂]` connects NL to a numeric kernel. We extend it so the GP sees *both* the semantic relation to the principle **and** the physical knobs:

```
φ(h,P) = [ e_h·e_P ,  ‖e_h − e_P‖₂ ,  ψ(x_h) ]
```

where `ψ(x_h)` is the normalized numeric design vector (standardized continuous params, one-hot categoricals). The first two terms are the PiEvo semantic coordinates; `ψ(x_h)` grounds predictions in actual experiment geometry.

**Kernel.** Per-principle GP with a **sum/product RBF** over the two blocks (separate lengthscales so semantics and physics are weighted independently):

```
k(φ, φ') = σ_f² · exp(−½ (Δsem/ℓ_sem)²) · exp(−½ ‖Δphys/ℓ_phys‖²) + σ_obs²·δ
```

Fit `ℓ_sem, ℓ_phys, σ_f, σ_obs` by marginal-likelihood (or fix lengthscales during the ~5 warm-up rounds, then optimize). Use a tiny GP lib (`GPyTorch`/`scikit-learn GaussianProcessRegressor`) — one GP per active principle (the "GP experts"). Each is cheap (≤ a few hundred points).

**GP mean function = the literature prior.** Crucial for §4: seed each GP's *prior mean* `m_P(x)` from the literature-extracted relationship for that principle (e.g., a fitted curve / reported value), not zero-mean. Then early predictions reflect what papers claim, and deviations are measured against literature.

**What is the outcome `y`?**
- **Simulation/compute experiment**: `y` = the scalar metric the tool returns (yield, RMSE, binding ΔG, stability, classification AUC…). `σ_obs` from sim stochasticity (run-to-run std) or solver tolerance.
- **Surrogate model**: `y` = surrogate prediction; `σ_obs` = surrogate's own predictive std (propagate it).
- **Literature-derived value**: `y` = the number extracted from a paper; `σ_obs` = reported error bar, or, if absent, an LLM-assessed extraction-uncertainty inflated by a fixed floor. Tag `source="literature"` so the soundness caveat (§6) applies.

> The objective must be reduced to a **single scalar** per round (PiEvo assumes scalar `y_t`). For multi-objective domains, scalarize (weighted/Chebyshev) or maintain parallel GP heads and aggregate in §3.

---

## 3. IDS acquisition (Eq. 1) — the "highest quantitative information gain"

**Selection rule (our Eq. 1):**
```
h_t = argmin_{h ∈ candidates}   Δ_t(h)² / I_t(h)
```

### Δ_t(h): expected regret (value gap)
Posterior-mixture mean: `μ̄(h) = Σ_P w_t(P) μ_P(h)`. Let the incumbent target be the best believed attainable value `v* = max_{h'} μ̄(h')` (for maximization). Then
```
Δ_t(h) = v* − μ̄(h)        (clipped at ε>0 so the argmin is well-defined)
```
This is expected suboptimality: small for exploit-y candidates. (For a known target/setpoint domain, use `Δ_t(h)=|target − μ̄(h)|`.)

### I_t(h): mutual information between principle and outcome — `I(P ; Y | h)`
This is the quantity the user means by "quantitative information gain." Each principle predicts `Y|P,h ~ N(μ_P(h), s_P²)` with `s_P² = σ_P²(h) + σ_obs²`. The posterior-weighted **mixture** predictive is `Σ_P w_t(P) N(μ_P, s_P²)`. Mutual information = entropy of the mixture minus the average entropy of components (this is exactly **BALD**, with the "model" being the principle identity):

```
I_t(h) = H[ Σ_P w_t(P) N(μ_P(h), s_P²(h)) ]  −  Σ_P w_t(P) · H[ N(μ_P(h), s_P²(h)) ]
```

- Component (Gaussian) entropy is analytic: `H[N(μ,s²)] = ½ log(2πe s²)`.
- Mixture entropy `H[mixture]` has no closed form → **moment-match** to a single Gaussian (fast, upper-bounds true entropy) or use a handful of MC samples:
  - `μ_mix = Σ w_P μ_P`, `s²_mix = Σ w_P (s_P² + μ_P²) − μ_mix²`, then `H ≈ ½ log(2πe s²_mix)`.

Interpretation: `I_t(h)` is **large when the active principles disagree about the outcome of `h`** (running it discriminates between them) — pure principle-discriminating information. If `|P_t|=1` (single surviving principle), this term collapses; add the **GP epistemic** info so we still reduce surrogate uncertainty:
```
I_t(h) += ½ log(1 + σ_P²(h)/σ_obs²)        # GP information gain, per MAP principle
```

```python
def ids_score(h, P_t, w, sigma_obs):
    mus  = np.array([P.gp.mean(h) for P in P_t])
    s2   = np.array([P.gp.var(h) + sigma_obs**2 for P in P_t])
    H_comp = 0.5*np.log(2*np.pi*np.e*s2)
    mu_mix = np.sum(w*mus)
    s2_mix = np.sum(w*(s2 + mus**2)) - mu_mix**2
    H_mix  = 0.5*np.log(2*np.pi*np.e*s2_mix)
    I = H_mix - np.sum(w*H_comp)                      # I(P;Y|h)  (BALD)
    I += 0.5*np.log1p(P_map.gp.var(h)/sigma_obs**2)   # + GP epistemic
    v_star = max(np.sum(w*[Pi.gp.mean(hp) for Pi in P_t]) for hp in candidates)
    Delta = max(v_star - mu_mix, 1e-6)
    return Delta**2 / max(I, 1e-9)                     # minimize
```

**Explore/exploit knob** (Hypothesis Agent modes): exponentiate info, `Δ²/I^β`. `β>1` → exploration-heavy (info-greedy); `β<1` → exploitation. Use this to satisfy "diversity" (APD) vs "efficiency" (AUOC) trade-off explicitly.

---

## 4. Anomaly-driven augmentation (Eq. 3) — *vs literature priors* (our key novelty)

Because GP means are **seeded from the literature** (§2), the anomaly score measures *the user's real local data contradicting the published consensus* — not just a surrogate residual. That is the differentiator.

For each new local observation `s` under hypothesis `h_s`, evaluate against the principle that generated it (and against the full mixture):
```
z_s   = (y_s − μ(h_s)) / sqrt( σ²(h_s) + σ_obs² )           # calibrated residual
S_s   = 1 − exp( −sqrt( z_s² ) ) = 1 − exp(−|z_s|)           # PiEvo Eq.3, ∈[0,1)
```
Trigger when `S_s > θ_t`. Use an **adaptive threshold**: `θ_t` from a per-round false-positive budget (e.g., `θ_t` mapped from a Bonferroni-corrected z, `|z| > Φ⁻¹(1 − α/2/n_tests)`), so more tests ⇒ stricter, avoiding spurious principle spawns.

**On trigger** → the **Principle Agent** (strong, *non-reasoning* model, §6) is prompted with: the anomalous `(x_s, y_s)`, the violated principle text, and nearby history, and asked to draft a **new principle** `P_new` that reconciles literature + the surprising local datum. Embed it, attach a fresh `GP_{P_new}` whose prior mean is fit to the anomalous neighborhood, add to `P_t`.

**Posterior recompute (Eq. 4), in log-space over the now-larger `P_t`:**
```
log p_{t+1}(P) = log p_0(P) + Σ_s log N( y_s ; μ_P(h_s), σ_P²(h_s)+σ_obs² )
```
then normalize via `softmax`. A principle that explains the anomaly gains weight; literature-only principles that mispredict it decay. Optionally prune principles whose `w_t(P) < w_min` (keep them archived for re-activation, since the space is *evolving* — don't hard-delete).

This is the loop's creativity engine: **surprise relative to the published prior is what manufactures novel, testable propositions**, which then generate the next hypotheses.

---

## 5. The round loop + stopping criteria

```
WARM-UP  (~5 rounds — PiEvo lesson):
  • Lit-review + user-data inspection → seed initial principles P_0 (literature provenance).
  • Fit each GP_P prior mean to literature relationship; sample a few cheap probes to anchor GP priors.

REPEAT each round t:
  1. PRINCIPLE AGENT: propose/augment P_t (only meaningfully active outside anomalies if surprise occurred).
  2. HYPOTHESIS AGENT: under MAP principle P* = argmax w_t(P), generate K candidate h's
     (mix of explore & exploit), each with x_target, difficulty, effort, "explains".
  3. DEBATE: Principle vs Hypothesis agent exchange N rounds (critique feasibility/novelty/testability)
     -> prune/refine candidates. (User requirement: agents discuss back-and-forth.)
  4. IDS SELECT: h_t = argmin Δ_t(h)²/I_t(h)  over surviving candidates (§3).
  5. EXPERIMENT AGENT: run the pluggable tool for x_{h_t}  -> (y_t, σ_obs).   [LOCAL plane]
  6. UPDATE: append Observation; refit GP_{P} on its explained points; recompute posterior (Eq.4).
  7. ANOMALY CHECK (§4): if S_s>θ_t -> spawn principle, recompute posterior, expand P_t.
  8. LOG guidance row: chosen h, info_gain, regret, what-it-explains, difficulty, effort, new μ̄.

STOP when ANY:
  • budget exhausted (rounds / compute-$ / wall-clock);
  • max_h I_t(h) < ε_info  for all candidates  (nothing left to learn);
  • posterior entropy H[p_t(P)] < ε_H AND stable for r rounds (one principle dominates → converged);
  • best regret Δ_t < ε_reg  (good-enough solution found, AUOC plateaued);
  • no anomalies for r rounds AND APD (diversity) below floor (exploration saturated).
```

Expose `--max_turn`, `--budget`, and these ε's as CLI flags (PiEvo's `--max_turn 20` analog). Persist `WorldState` to disk each round so the REPL can resume — Claude-Code-style.

---

## 6. PiEvo lessons we MUST honor

**(a) Non-reasoning crisp models on the strategic layers (the −26% lesson).** Wire the **per-agent model router** (locked decision #5) so:
- *Strategy layers → non-reasoning/crisp models* (low temp): IDS scoring rationale, principle **selection**, explore/exploit decisions, anomaly *trigger* judgments. "Diversity of reasoning conflicts with rigorous utility." Use e.g. a fast non-thinking OpenRouter model / DeepSeek-chat (NOT a reasoning variant).
- *Comprehension/generation layers → reasoning models*: literature reading + gap extraction, principle **drafting** content, simulation-code synthesis, anomaly **explanation**. These benefit from depth.
- Config mirrors PiEvo's `config/model.yaml`: `{agent: {model, temp, reasoning: on/off, tools}}`, provider-swappable.

**(b) Lightweight models degrade principle generation.** Route **Principle Agent generation** to one of the strongest available backends (still cheap-first per preference, but the *best* of the cheap tier), never the smallest. Cheap small models are fine for embeddings, extraction, formatting.

**(c) Embedding-likelihood is a *proxy* for physical likelihood (soundness risk).** Our posterior (Eq.4) uses GP likelihoods built on **embedding-derived features**. Mitigations, surfaced in the CLI:
- Prefer **real numeric `y`** (sim/data) over embedding-only signals whenever a runnable experiment exists; literature-only `y` carries inflated `σ_obs`.
- **Calibrate** `σ` (check residual z-scores are ~N(0,1); widen if over-confident).
- Print a standing caveat on any conclusion driven primarily by `source="literature"` likelihoods: *"ranking influenced by semantic proxy, not measured outcomes — verify experimentally."*

**(d) ~5 warm-up rounds** to seed GP priors — hard-coded default, flag-overridable.

**(e) Surrogate-only validity.** Like PiEvo, we never claim wet-lab truth; outputs are hypotheses + *info-gain-ranked experiment plans*. The institution-profiler (decision #2) feeds **feasibility**: difficulty/effort in §1 are scored against the user's *inferred equipment/capabilities*, so "testable for THIS user" is concrete.

---

## 7. Fallback: literature/data-only mode (no runnable experiment)

When no executable tool maps to `X` (or the user declines to run anything), the loop degenerates to **one-shot information-gain ranking** — still principled:

1. Seed `P_t` and the GP **prior** means from literature (§2). No observations are taken.
2. For every candidate `h`, compute the **prior-predictive** `I_t(h) = I(P;Y|h)` exactly as §3 (BALD over the literature-seeded mixture) — this needs only priors, no data. It answers *"if you could measure this, how much would it resolve between competing principles?"*
3. Rank by a **cost-aware EVPI proxy**:
   ```
   rank(h) = I_t(h) / cost(h)         cost = effort/difficulty from the profiler-aware model
   ```
   (Equivalently, sort by `Δ_t(h)²/I_t(h)` if a value target exists.) This is value-of-information per unit effort — the static analog of IDS.
4. Emit a **ranked, static hypothesis list**, each row carrying the user's required guidance:
   - **info_gain** `I_t(h)` (bits/nats — the quantitative number),
   - **what it would explain** = the principle pair it discriminates (`h.explains`),
   - **difficulty** + **effort** (profiler-aware),
   - which **literature gap** it targets.

This guarantees the tool produces value even with zero compute, and the *same* `I_t` machinery powers both the closed loop and the fallback — only the data source for the posterior update differs. When the user later runs an experiment, the identical objects (§1) flow into the full loop (§5) with no rework.

---

### One-paragraph summary for the orchestrator
Represent **principles** as NL+embedding+GP-expert with literature-seeded prior means and a log-space posterior weight; **hypotheses** as NL+embedding+target point in a design space `X`+guidance metadata; **observations** as scalar `y` (sim/compute/surrogate/literature) with calibrated `σ_obs`. Bridge text→numbers with `φ(h,P)=[e_h·e_P, ‖e_h−e_P‖, ψ(x_h)]` and a two-block RBF GP per principle. Select experiments by IDS `argmin Δ²/I`, where `I=I(P;Y|h)` is BALD (mixture entropy − mean component entropy) plus GP epistemic info — this *is* the user's quantitative info-gain. Detect anomalies as calibrated residuals **against the literature prior** (`S=1−e^{−|z|}>θ_t`), spawning reconciling principles and Bayes-updating an **evolving** `P_t`. Run ~5 warm-up rounds; route strategic layers to non-reasoning models and generation to strong reasoning models; flag the embedding-likelihood proxy caveat; and fall back to one-shot `I_t/cost` ranking when nothing is runnable.


---

# Multimodal ingestion

I have a complete picture of the prototype. Here is the ingestion architecture design.

---

# Multimodal Ingestion Architecture — HypoForge CLI

Design for how the ultra-agentic CLI ingests diverse sources, mapping everything into one `Evidence` abstraction that feeds the PiEvo-style closed loop. Honors the two-data-plane rule (raw data stays **local**; only field/institution metadata goes to the **web** plane).

## 0. Salvage assessment (what carries over from the prototype)

| Existing file | Verdict | Role in new design |
|---|---|---|
| `/Users/abdollahegazy/bnl/aijam/parsers/registry.py` | **Keep, extend** | Becomes the deterministic fast-path of the **Opener Router** (`open_source()`). Its magic-byte sniffing (HDF5 `\x89HDF`, PDF `%PDF-`, text/CSV heuristics) is exactly right. |
| `/Users/abdollahegazy/bnl/aijam/parsers/tabular.py` | **Keep wholesale** | `_load` (CSV/TSV/Excel/Parquet/Feather/JSON/NumPy/HDF5/NetCDF) + `_profile_dataframe` (stats, `top_correlations`, sample rows, `_safe` JSON-coercion) become the `structured_profile` + numeric-quantity extractor for tabular/array/sim Evidence. |
| `/Users/abdollahegazy/bnl/aijam/parsers/document.py` | **Keep, upgrade** | Text/section/term extraction stays. Swap `pypdf` → **PyMuPDF (`fitz`)** to also pull embedded figures + render pages for the vision path. |
| `/Users/abdollahegazy/bnl/aijam/parsers/image.py` | **Replace pixel-stats with vision** | Keep Pillow metadata (dims/mode/format); the RGB-mean "understanding" is too shallow — route pixels to a vision model (§3). |
| `/Users/abdollahegazy/bnl/aijam/parsers/generic.py` | **Keep** | Last-resort fallback; feeds the agentic escalation path. |
| `/Users/abdollahegazy/bnl/aijam/tools/lit_apis.py` | **Keep wholesale** | Semantic Scholar + arXiv + OpenAlex + DuckDuckGo, parallel fan-out, dedupe, `_deinvert`. This is the literature ingestion plane and the seed for principle priors (§5). |
| `/Users/abdollahegazy/bnl/aijam/agents/llm.py` | **Keep core, generalize** | `call_json`/`_extract_json` robustness + mock backend are gold. Generalize `get_llm()` from one global provider to a **per-role router** (`get_llm(role=...)`) and add a vision call path (§3, §6). |
| The `ParseResult` dict (registry.py docstring) | **Evolve into `Evidence`** | Its `{kind, summary, profile, text, notes}` shape is the direct ancestor of the unified abstraction below. |

New deps to add: `pymupdf` (PDF figures/render), `filetype` or `python-magic` (robust sniffing), `xarray` (NetCDF/labelled sim fields), `sentence-transformers` or an embeddings API (semantic bridge, §5). Drop nothing; `streamlit`/`plotly` become optional (CLI renders text/sparklines, can still emit Plotly HTML on request).

---

## 1. The unified `Evidence` abstraction

Every source — a PDF, a CSV, an HDF5 sim dump, a microscopy TIFF, a retrieved abstract — normalizes into one `Evidence` record. This is the single currency the discovery engine consumes.

```python
# core/evidence.py
from dataclasses import dataclass, field
from typing import Any, Literal

Modality = Literal["literature", "tabular", "array", "simulation", "visual", "document", "unknown"]
Plane    = Literal["local", "web"]   # locality firewall — never crosses

@dataclass
class Quantity:
    """One numeric fact extracted from any modality -> a warm-up observation candidate."""
    name: str                       # "Re_critical", "slope(dPsi/dT)", "peak_wavelength_nm"
    value: float | None
    unit: str | None = None
    uncertainty: float | None = None   # sigma if reported / inferable (error bars, CI, std)
    conditions: dict = field(default_factory=dict)  # {"T":300,"pH":7} -> GP input x
    source_locator: str = ""        # "fig3.b axis-y" | "df.corr[A,B]" | "abstract sent 4"

@dataclass
class Claim:
    """One natural-language proposition -> candidate principle / prior."""
    text: str                       # "turbulence onset scales with Re^0.5"
    polarity: Literal["asserts","contradicts","open_question"] = "asserts"
    confidence: float = 0.5         # extractor's calibrated-ish confidence
    support: list[str] = field(default_factory=list)  # locators / citations

@dataclass
class Evidence:
    id: str                         # stable hash of (path, locator)
    modality: Modality
    plane: Plane                    # LOCAL raw data vs WEB metadata  <-- the firewall flag
    summary: str                    # short text the strategy LLMs read
    structured_profile: dict        # modality-specific stats (the prototype's `profile`)
    quantities: list[Quantity] = field(default_factory=list)
    claims: list[Claim]     = field(default_factory=list)
    provenance: dict        = field(default_factory=dict)   # see below
    raw_ref: str | None = None      # path or in-memory handle; NOT the bytes (local stays local)
    notes: list[str]    = field(default_factory=list)       # opener decisions / fallbacks
    embedding: list[float] | None = None                    # for the semantic bridge (§5)
```

**`provenance`** (audit trail, also drives trust-weighting of priors):
```python
{"opener": "tabular/_load_hdf5", "uri": "/abs/path/sim_run42.h5",
 "sniffed_as": "hdf5", "bytes": 5_120_334, "ingested_at": "...",
 "extractor_model": "qwen2.5-vl (vision)", "checksum": "sha256:..."}
```

**Field-by-field rationale**

- **`modality`** — routes downstream handling and which extractor ran.
- **`plane`** — *the institution-profiling firewall.* `local` Evidence (datasets, sims, your own PDFs/images) may be read by local tools and summarized to the LLM, but its **raw bytes never leave the machine**. `web` Evidence (retrieved abstracts, the crawled institution page → inferred equipment) is public-by-construction. The Experiment Agent's tools assert `plane=="local"` before touching data files; the literature/profiling agents only emit `plane=="web"`.
- **`structured_profile`** — the prototype's `profile` dict, verbatim for tabular; modality-specific otherwise.
- **`quantities`** — the bridge to Bayesian modeling: each becomes a `(x → y, σ)` warm-up point (§5).
- **`claims`** — the bridge to principles: literature/figure claims seed `P_0` (§5).
- **`embedding`** — precomputed normalized text embedding of `summary`+`claims`, so Evidence plugs straight into PiEvo's semantic kernel `φ(h,P)` (Eq. 2).

A whole ingest run produces an **`EvidenceStore`** (list + index by modality/plane + a duplicate filter reusing `lit_apis._dedupe`'s title-key idea generalized to checksums).

---

## 2. Pointing the tool at "a PDF, a file, or a folder" + the Opener decision

The user supplies paths in the REPL or via flags, Claude-Code-style:

```
hypoforge> /ingest ~/proj/turbulence/            # recurse a folder
hypoforge> /ingest run42.h5 paper.pdf notes.md   # explicit list
hypoforge  --data ./local_data --paper ./refs/   # one-shot flags
> "look in ./sims for the latest field dumps and read the PDF I dropped in refs"
```

Free-form mentions ("the PDF I dropped in refs") are resolved by the agent loop using a `glob`/`find` tool, then handed to the same opener. Folders are walked, `.gitignore`/size caps respected, and each file dispatched.

### The Opener Router — three-tier with graceful fallback

```
open_source(path) ->
  Tier 0  Locality tag:   inside --data tree => plane=local; else default per source type
  Tier 1  Sniff:          extension map  (registry._TABULAR/_DOCUMENT/_IMAGE)
                          ↓ if unknown/missing
                          magic-byte + `filetype` lib  (registry._sniff, extended)
  Tier 2  Specialized parser: tabular | document | visual | array/sim | generic
                          (try/except -> NEVER crash; fall to generic.parse with error note)
  Tier 3  Agentic escalation (only if Tier 2 yields modality="unknown"/low-info):
                          the Ingestion Agent gets {head bytes hex, size, failed-parser note}
                          and a toolbox (hexdump, `file`, try-as-X) to decide an opener,
                          or label it "uninterpretable" with a reason.
```

Tiers 0–2 are the prototype's `registry.parse_file` essentially unchanged — keep the exception wrapper that routes any parser crash to `generic.parse(path, ext, error=...)`. Two extensions needed:

- **Sniffing robustness:** add `filetype`/`python-magic` after the extension map and before the bespoke `_sniff`, so renamed/extensionless files (common for sim dumps) still route. Add magic numbers for NetCDF (`CDF\x01`/`\x89HDF` already covered), NumPy (`\x93NUMPY`), Parquet (`PAR1`), PNG/JPEG/TIFF.
- **Large-array / simulation specialization (new):** HDF5/NetCDF/`.npy` over a size threshold are **simulation** modality, not generic tabular. Instead of flattening to a DataFrame (prototype's current `_load_numpy` behavior), profile them out-of-core: shape, dtype, dim names (via `xarray` for NetCDF), per-field summary stats (min/max/mean/percentiles via chunked reduction), NaN/mask fraction, and **field-level features** (spatial gradients, spectral peaks, monotonic trends along an axis, detected fronts/regime boundaries). Logs (`.log`/`.out`) get regex-extracted scalars (residuals, iteration counts, convergence flags) → `Quantity` series. This keeps memory bounded and turns a 5 GB field into a handful of `Quantity` warm-up points + `Claim`s ("field develops a shock at x≈0.7").

**Graceful fallback guarantee** (inherited): a file can fail every specialized parser and still return a valid `Evidence` (modality `unknown`, a `generic` profile, notes explaining what was tried) — the pipeline never dies on a bad file.

---

## 3. Visual understanding (figures, plots, microscopy, instrument images)

The prototype's `image.py` only computes RGB means — replace with a **vision-LLM extraction** pass that turns pixels into structured `quantities` + `claims`.

### Model choice (per-role router, OpenRouter-first, cheap)

A dedicated `"vision"` role in the model router (§6):

- **Primary:** `qwen/qwen2.5-vl-72b-instruct` (or the free `:free` tier) on OpenRouter — best-in-class cheap chart/plot/OCR/document understanding; reads axis labels, tick values, legends.
- **Fallback:** `google/gemini-2.0-flash` (already the prototype default, has a free tier and strong vision) → then DeepSeek-VL if available → then the prototype's pixel-stats as an offline last resort.
- This is a **non-reasoning** extraction job (transcribe what's in the figure), so per PiEvo lesson (c) it's fine to use a fast crisp model; reserve "think-mode" models away from this and from the strategy layers.

### Inputs to the vision pass
1. Standalone image files (PNG/JPG/TIFF/microscopy).
2. **Figures embedded in PDFs** — PyMuPDF extracts embedded raster/vector images *and* renders each page to PNG; figure-captioned regions are cropped and sent. (This is the key upgrade to `document.py`.)
3. Optionally, plots HypoForge itself generates from tabular data (closing the loop visually).

### Extraction schema (vision → structured Evidence)
The vision model is prompted for strict JSON (reuse `call_json`'s robust parser):

```json
{
  "figure_type": "scatter|line|heatmap|histogram|micrograph|spectrum|schematic|photo",
  "caption_text": "verbatim caption / title if present",
  "axes": [{"name":"Reynolds number","unit":"-","scale":"log","range":[1e2,1e6]},
           {"name":"drag coefficient","unit":"-","scale":"linear","range":[0.1,1.4]}],
  "series": [{"label":"smooth wall","trend":"decreasing","slope_sign":"-",
              "fit":"power-law","fit_params":{"exponent":-0.25,"R2":0.97}}],
  "regimes": [{"region":"Re<3e5","behavior":"laminar"},
              {"region":"Re>3e5","behavior":"turbulent — drop in Cd (drag crisis)"}],
  "breakpoints": [{"x":3e5,"description":"abrupt transition"}],
  "anomalies": ["one outlier at Re≈5e4 far above trend"],
  "quantities": [{"name":"transition_Re","value":3e5,"unit":"-","uncertainty":5e4}],
  "claims": [{"text":"Cd collapses by ~5x across the drag-crisis transition","confidence":0.7}],
  "readability": 0.9
}
```

Mapping to `Evidence`: `figure_type/axes/regimes` → `structured_profile`; `quantities` → `Quantity[]` (axis values, fitted slopes, transition points become **warm-up observations**); `regimes`/`breakpoints`/`anomalies` → `Claim[]` that can **seed or contradict principles** (an anomaly directly feeds PiEvo's Eq. 3 augmentation). `readability` gates how much we trust the extraction (low → flag, don't fabricate numbers).

Microscopy/instrument photos with no axes still yield qualitative `claims` ("dendritic grain structure", "phase separation visible") + morphometric `quantities` if computable locally (object count, area fraction via a cheap CV pass) — all `plane=local`.

---

## 4. Pluggable Experiment Tool interface (the closed loop)

Mirrors PiEvo's `pievo/tools/` decorator registry. The **Experiment Agent** selects a hypothesis via IDS (Eq. 1), then calls a registered tool to get an observation `y_t`.

```python
# tools/experiment_registry.py
EXPERIMENT_TOOLS: dict[str, ExperimentTool] = {}

def experiment_tool(name, *, cost: float, deterministic: bool,
                    touches=("compute",), supports_dry_run=True, domain="generic"):
    """Register a runnable experiment. `touches` ⊆ {compute, local_data, network}."""
    def deco(fn):
        EXPERIMENT_TOOLS[name] = ExperimentTool(
            name=name, fn=fn, cost=cost, deterministic=deterministic,
            touches=set(touches), supports_dry_run=supports_dry_run, domain=domain,
            schema=infer_schema(fn))           # param names/types/bounds from signature+annotations
        return fn
    return deco

@dataclass
class Observation:
    y: float                      # scalar objective the GP models
    sigma_obs: float = 0.0        # measurement noise (-> Eq.3 anomaly score denominator)
    aux: dict = field(default_factory=dict)   # extra fields, plots, arrays
    cost_spent: float = 0.0
    dry_run: bool = False
```

**Example registered tools** (domain-agnostic core + hero-domain plug-ins):
```python
@experiment_tool("fit_surrogate", cost=0.1, deterministic=True, touches=("compute","local_data"))
def fit_surrogate(x: dict, target: str) -> Observation:
    """Train a cheap GP/RF surrogate on LOCAL data, predict y at proposed conditions x."""

@experiment_tool("run_simulation", cost=5.0, deterministic=False, touches=("compute",))
def run_simulation(params: dict) -> Observation:
    """Invoke a user-supplied solver binary in the sandbox; parse stdout -> y."""

@experiment_tool("recompute_statistic", cost=0.05, deterministic=True, touches=("local_data",))
def recompute_statistic(expr: str, subset: dict) -> Observation:
    """Evaluate a statistic (correlation, regression slope, effect size) on the local dataset."""
```

### Sandbox / safety
- **Locality firewall:** a tool whose `touches` includes `network` is **refused** if any input Evidence is `plane=local` — raw data can never be exfiltrated through an experiment. `local_data` tools run with **network disabled**.
- **Isolation:** each call runs in a **subprocess** confined to a per-run workspace dir (no writes outside it), with **wall-clock timeout**, **memory cap (rlimit)**, and CPU niceness. User-supplied solver binaries / arbitrary code default to a container (`docker run --network=none --read-only -v workspace`) when available, else the rlimit'd subprocess. No `eval` of LLM output; tools are pre-registered Python, the LLM only chooses *which* tool and *what params* (params validated against `schema` bounds before dispatch — same spirit as the prototype's "LLM never emits executable code" viz design).
- **Determinism & seeds:** `deterministic` tools fix seeds for reproducible warm-up; stochastic ones report `sigma_obs`.

### Dry-run / simulated mode (demo-critical)
Every tool supporting it exposes a **`dry_run`** path that returns a *plausible* `Observation` without doing real work — drawn from the current GP posterior mean ± its variance (so the loop still "learns"), or from a cached surrogate. Enabled globally via `--dry-run` (mirrors the prototype's `_MockLLM` fallback and PiEvo's "evaluate on high-fidelity **surrogates**, never wet-lab" lesson). This makes the closed loop fully runnable on a laptop with no solver and no API keys — essential for the live demo.

---

## 5. From Evidence → warm-up observations + literature-seeded principle priors

This is the join between ingestion and the discovery engine. PiEvo needs two things to start: ~5 warm-up rounds to seed the GP priors, and an initial Active Principles set `P_0`. Ingestion supplies both.

### (a) Warm-up observations (seed the per-principle GP experts)
- Each `Quantity` with a `value` and `conditions` becomes a warm-up datapoint `(x = conditions-vector, y = value, σ = uncertainty)`.
- Sources, in priority order: **local tabular/array** (`top_correlations`, regression slopes, group means from `_profile_dataframe`), **simulation field features** (transition points, spectral peaks, residual convergence), **figure extractions** (digitized axis points, fitted slopes, regime boundaries from §3), and **literature** (reported effect sizes/constants in abstracts).
- We aim for **≥5 calibrated points** before the loop starts (PiEvo lesson a). If local data is thin, the Experiment Agent runs ~5 `fit_surrogate`/`recompute_statistic` calls (or dry-run draws) to reach quorum.
- Heterogeneous-unit quantities are bucketed by `(target, conditions-schema)` so each GP expert sees a coherent input space; `provenance.plane` weights trust (local measurement > web-reported number).

### (b) Literature-seeded principle priors (`P_0`)
- The literature plane (`lit_apis.search_all` → `literature.review`'s `knowledge_gaps`/`established_findings`/`open_questions`) and figure/sim `claims` are converted into **principle candidates**: each `Claim` with `polarity="asserts"` and high confidence → a candidate principle proposition; `open_question`/gap claims → *low-prior* exploratory principles the Hypothesis Agent can target.
- The **Principle Agent** dedupes/merges these into `P_0`, and the prior `p_0(P)` is set from claim `confidence` × source trust (peer-reviewed citation count from `lit_apis`, local-data corroboration boosts it).
- **Semantic bridge wiring (Eq. 2):** every Evidence and every principle carries an `embedding`. When a hypothesis `h` is proposed, `φ(h,P)=[e_h·e_P, ‖e_h−e_P‖]` is computed against these embeddings to drive the RBF kernel — so the same embedding we compute at ingest time is reused, no recompute.
- **Anomaly hook (Eq. 3):** any ingested `Quantity` whose `value` deviates from the seeded GP mean beyond `θ_t` (e.g. a figure outlier, a sim that contradicts a literature claim) is fed straight into anomaly-driven augmentation, prompting the Principle Agent to propose a reconciling principle on round 0 — ingestion can *itself* surprise the model before any experiment runs.

### Model-routing note for the strategy layers
Per PiEvo lesson (c), the **Principle Agent and IDS/strategy selection use crisp non-reasoning models** (e.g., a fast DeepSeek-chat or a small OpenRouter model), while **reasoning-heavy models** are reserved for hypothesis *drafting*, the debate/critic panel (salvaged `validation.py`), and figure interpretation. The `get_llm(role=...)` router (generalized from `agents/llm.py`) makes this a one-line config per role — satisfying the "modular per-agent model" lock.

---

## 6. Putting it together (ingest flow)

```
paths / free-form prompt
        │
        ▼
 Opener Router  ── Tier0 locality ─ Tier1 sniff ─ Tier2 parser ─ Tier3 agentic escalate
        │                                   (registry.py + filetype + new sim/array path)
        ├── tabular/array ─► tabular.py profile ──┐
        ├── document(PDF) ─► fitz: text + figures ─┤
        ├── simulation ───► out-of-core field profile + log scalars ─┤
        ├── visual ───────► vision LLM (Qwen2.5-VL/Gemini) extract ───┤
        └── literature ───► lit_apis fan-out (web plane) ─────────────┤
                                                                      ▼
                                                          Evidence  (modality, plane,
                                                          profile, quantities, claims,
                                                          provenance, embedding)
                                                                      │
                                   ┌──────────────────────────────────┴───────────┐
                                   ▼                                               ▼
                       Quantities → warm-up GP points (≥5)              Claims → P_0 principle priors
                                   │                                               │
                                   └──────────────► PiEvo loop ◄───────────────────┘
                                        (Principle / Hypothesis / Experiment agents,
                                         IDS Eq.1, semantic bridge Eq.2, anomaly Eq.3)
```

**Net:** the prototype's parsers, `lit_apis`, and `llm.call_json` are reused almost verbatim; the new work is (1) the `Evidence` schema with the `plane` firewall and `quantities`/`claims` extraction, (2) the sim/large-array specialization, (3) the vision extraction pass replacing pixel-stats, (4) the sandboxed experiment-tool registry with dry-run, and (5) the Evidence→warm-up/principle-prior bridge that connects ingestion to the Bayesian discovery engine.

Key file paths referenced: `/Users/abdollahegazy/bnl/aijam/parsers/registry.py`, `/Users/abdollahegazy/bnl/aijam/parsers/tabular.py`, `/Users/abdollahegazy/bnl/aijam/parsers/document.py`, `/Users/abdollahegazy/bnl/aijam/parsers/image.py`, `/Users/abdollahegazy/bnl/aijam/parsers/generic.py`, `/Users/abdollahegazy/bnl/aijam/tools/lit_apis.py`, `/Users/abdollahegazy/bnl/aijam/agents/llm.py`, `/Users/abdollahegazy/bnl/aijam/agents/validation.py`.


---

# Institution capability profiling

I explored the existing repo and grounded the design in it. Here is the deliverable.

---

# Capability Profiling Subsystem — Design

*The institution/equipment "can THIS user actually do it?" wedge for the hypothesis CLI.*

This is our differentiator. Every other hackathon team will wire up agents that emit a static hypothesis list. We additionally answer: **"...and here's exactly which of these YOU can run, how hard, and what it'd cost you."** That requires modeling the user's real lab.

> Worked example throughout: your cwd is `/Users/abdollahegazy/bnl/aijam` — I'll treat **BNL (Brookhaven National Lab)** as the hero user. It's a perfect stress test: huge shared facilities (NSLS-II synchrotron, CFN nanocenter, SDCC HPC) that a naive field-prior would never guess, plus real access-mode nuance (beamtime proposals, not "in a drawer").

---

## 0. Where it sits & how it reuses the existing code

The Streamlit prototype is being replaced by a Claude-Code-style CLI, but four pieces salvage almost verbatim:

| Existing file | Reused for |
|---|---|
| `agents/llm.py` (`get_llm`, `call_json`, `active_provider`, mock fallback) | The per-role **model router** — extend, don't rewrite. |
| `tools/lit_apis.py` (`requests` + `ThreadPoolExecutor` fan-out, `_HEADERS`, 429 backoff, `_dedupe`, `_err`) | The **polite crawler + scholarly clients** copy this etiquette pattern exactly. |
| `tools/lit_apis.py:openalex()` / `web()` | Identity discovery (OpenAlex authors + ROR + DDG). |
| `parsers/registry.py` (`ParseResult`) | The **LOCAL data plane** — already isolated from the web. |

Proposed new layout (mirrors PiEvo's `tools/` decorator + `config/*.yaml` style):

```
capability/
  discovery.py     # prompt -> identity candidates -> user-confirmed identity
  crawl.py         # robots/rate-limit/cache crawler (reuses lit_apis etiquette)
  extract.py       # html|pdf -> raw capabilities (structured-JSON LLM)
  normalize.py     # alias tables + ontology mapping (free-text -> taxonomy)
  priors.py        # field -> typical-capability prior  (FALLBACK)
  graph.py         # Capability Graph build + coverage queries
  feasibility.py   # hypothesis -> required caps -> score, difficulty, work
  debate.py        # optimist / skeptic / judge before committing a verdict
  schema.py        # CapabilityProfile dataclasses + JSON Schema
  cache/           # on-disk html + profile cache (gitignored, TTL, deletable)
tools/
  web_tools.py     # search()/fetch() wrappers (WebSearch/WebFetch in-harness; ddgs+requests in prod)
  scholarly.py     # OpenAlex authors + ROR + Semantic Scholar author clients
config/
  models.yaml      # per-role model router
  field_priors.yaml
  ontology.yaml    # instrument/technique taxonomy + aliases
```

The CLI agent loop registers `capability/*` functions as **tools** (PiEvo `@tool` decorator pattern) so the agent can call `discover_identity`, `profile_capabilities`, `score_feasibility` autonomously inside its REPL.

---

## 1. Discovery — find their lab from a free-form prompt

### 1a. Extract identity entities (cheap LLM, structured)
First call (role `discovery-extract`, a fast non-reasoning model via `call_json`) pulls an `IdentityHints` object from the prompt:

```json
{ "person": "Jane Doe", "group": "Soft Matter Group", "institution": "Brookhaven National Lab",
  "department": "CMPMS", "field": "X-ray scattering of polymers", "location": "Upton, NY",
  "orcid": null, "pasted_urls": [], "named_instruments": ["GISAXS"], "role": "staff scientist" }
```

### 1b. Resolution ladder (cheapest → strongest, short-circuit on a confident hit)
1. **Pasted URL** → skip search entirely, go straight to crawl.
2. **ORCID** (if given) → `pub.orcid.org/v3.0/{id}` → employment affiliation + works (authoritative).
3. **OpenAlex Authors** — `api.openalex.org/authors?search={person}` (no key, already a dependency). Returns `last_known_institution` (+ **ROR id**), `works_count`, and **`x_concepts`** — a weighted field vector *for free*. ROR id → `api.ror.org/organizations/{ror}` → official homepage, institution **type** (Education / Facility / Government / Company) and country.
4. **Semantic Scholar author** → affiliations + recent papers (cross-check).
5. **Web search** (`tools/lit_apis.py:web` / harness `WebSearch`) over query templates:
   - `"{group}" {institution}`
   - `{person} {institution} lab|group research`
   - `{institution} {department} {field} faculty {person}`

### 1c. Disambiguation & candidate scoring
Each candidate URL scored 0–1 on additive signals:

```
+0.30 domain TLD/host matches institution (.edu/.ac/.gov/national-lab domain or ROR homepage host)
+0.25 person name appears on page
+0.20 path/anchor contains lab|group|research|people|facilities
+0.15 field terms co-occur with person
+0.10 OpenAlex/ROR corroborate the same institution
-0.40 aggregator/spam (researchgate, linkedin, academia.edu) — demote, don't seed crawl
```

### 1d. User-confirmation step (REPL — the Claude-Code feel)
Never silently trust web identity. Present the top 1–3 and require confirmation:

```
I think you're: Jane Doe — Soft Matter Group, CMPMS @ Brookhaven National Lab
  homepage: https://www.bnl.gov/cmpms/soft-matter   (confidence 0.86)
  field (OpenAlex): X-ray scattering · polymer physics · GISAXS
[Enter] confirm  ·  [e] edit  ·  [s] pick a different result  ·  [n] no website (use field prior)
```

The confirmed `Identity` is cached (`capability/cache/identity/{hash}.json`) so re-runs skip the network.

---

## 2. Crawl & extract → structured capability profile

### 2a. Polite crawler (`crawl.py`)
Seeds from the confirmed homepage. Reuses the `lit_apis` etiquette and adds crawl-specific guards:

- **robots.txt**: `urllib.robotparser` per host; obey `Disallow` + crawl-delay.
- **Same registrable domain only**, `depth ≤ 2`, `≤ 25 pages`, `≤ 2 MB/page`.
- **Rate-limit** ~1 req / 1.5 s per host; identifying `User-Agent` (extends existing `_HEADERS`).
- **Priority frontier** — only follow links whose URL/anchor matches a lexicon:
  `people|team|members|research|projects|facilities|instruments|equipment|infrastructure|capabilities|methods|resources|cleanroom|microscopy|beamline|computing|cluster|publications`.
- **On-disk cache** with TTL (raw HTML kept for provenance + audit + offline demo).
- Main-text extraction via `trafilatura`/readability; PDFs (annual reports, facility brochures) routed through the **existing `parsers/document.py`** — the data-plane parser is reused read-only.

### 2b. Extraction (`extract.py`, role `cap-extract` — cheapest high-volume model)
Per page-section, a schema-constrained `call_json` pulls typed candidates with **provenance**:

```json
{ "instruments": [{"name":"Titan Krios G3i","raw":"...as written...","model":"G3i"}],
  "techniques": ["GISAXS","SAXS","AFM"], "compute": ["SDCC Institutional Cluster, ~1 PF"],
  "materials": ["block copolymers","thin films"], "software": ["SasView"],
  "expertise": ["self-assembly","grazing-incidence scattering"],
  "people": [{"role":"PI"},{"role":"postdoc","n":3},{"role":"phd","n":5}],
  "collaborators": ["NSLS-II CMS beamline 11-BM"],
  "_provenance": {"url":"...","snippet":"...","section":"Facilities"} }
```

### 2c. Normalize to ontology (`normalize.py`)
Free-text → controlled vocabulary via an **alias table** (`config/ontology.yaml`), LLM fallback for misses:
`"Titan Krios" → cryo-EM`; `"Bruker Avance 600" → NMR@600MHz`; `"11-BM CMS" → synchrotron GISAXS/SAXS`.
Each capability gets a **category** + canonical id, and `ENABLES`/`REQUIRES` links (instrument↔technique).

### 2d. Confidence + the publications backstop
Per-capability confidence by source:

| Source | Confidence | Note |
|---|---|---|
| Explicit "Facilities/Instruments" page | **0.9** | listed hardware |
| Methods section of the group's own recent papers | **0.75** | *actively used* — often more reliable than the website |
| Mentioned in prose / news | 0.5 | |
| Field prior only (no evidence) | **0.25** | flagged "assumed — confirm?" |

Messy sites (Wix/Google Sites/dead pages) degrade gracefully: when the crawl is thin, pull the group's last ~20 works via OpenAlex/S2 author id and mine **methods/abstracts** for instruments & techniques. This doubles as proof the capability is real and current.

---

## 3. Fallback — infer capability from FIELD alone

When there's no site or it's barren:

1. **Curated prior** `config/field_priors.yaml` — subfield → typical {instruments, techniques, compute} with prior weights. Hand-seed a dozen fields (good enough for the demo; extensible).
2. **Institution-tier scaling** from ROR `type`/size: *national lab* (BNL) → unlocks synchrotron/HPC/cleanroom priors; *PUI/small college* → benchtop-only; *company* → applied/scale-up. This single signal is what makes the prior realistic instead of generic.
3. **OpenAlex `x_concepts`** gives the field vector automatically, so even a name-only prompt yields a plausible prior.
4. **LLM prior** (role `cap-prior`) conditioned on `field + tier` fills gaps.

All fallback capabilities are stamped `source:"field_prior"`, `confidence ≤ 0.3`, so feasibility scoring discounts them and the agent surfaces them as assumptions to confirm: *"I'm assuming you have access to a benchtop rheometer — correct?"*

---

## 4. Capability Graph + Profile schema

### 4a. Graph model (drives feasibility)
- **Nodes:** `Institution`, `Group`, `Person`, `Instrument`, `Technique`, `ComputeResource`, `Material`, `Software`, `ExpertiseArea`, `Collaborator`, `SharedFacility`.
- **Edges:** `HAS_INSTRUMENT`, `HAS_EXPERTISE`, `OPERATED_BY`, `LOCATED_AT`, `COLLABORATES_WITH`, `ACCESS_VIA(SharedFacility|Collaborator)`, and the two load-bearing ones — `ENABLES` (instrument→technique) and `REQUIRES` (technique→instrument).

Feasibility = does the **set of techniques a hypothesis' `test_plan` demands** have a covering path to instruments the user can reach? Missing nodes = the gap list + acquisition cost.

### 4b. `CapabilityProfile` JSON schema (persisted/cached centerpiece)

```jsonc
{
  "schema_version": "1.0",
  "identity": {
    "person": "Jane Doe", "group": "Soft Matter Group",
    "institution": "Brookhaven National Laboratory",
    "ror": "https://ror.org/02ex6cf31", "institution_type": "Government/Facility",
    "field": "X-ray scattering of soft matter",
    "field_vector": [["polymer physics",0.4],["GISAXS",0.3],["self-assembly",0.3]],
    "homepage": "https://www.bnl.gov/cmpms/soft-matter",
    "confidence": 0.86, "confirmed_by_user": true
  },
  "tier": { "class": "national_lab", "scale_multiplier": 1.0,
            "unlocks": ["synchrotron","hpc","cleanroom"] },
  "capabilities": [
    {
      "id": "tech:gisaxs", "label": "GISAXS", "category": "technique",
      "access": "shared_facility",            // in_house | shared_facility | collaborator | acquirable | infeasible
      "via": "NSLS-II 11-BM (CMS)",
      "requires_instruments": ["instr:synchrotron_beamline"],
      "confidence": 0.9, "source": "facilities_page",
      "provenance": [{"url":"https://www.bnl.gov/nsls2/beamlines/11bm","snippet":"...CMS, GISAXS/SAXS...","retrieved":"2026-06-29"}],
      "cost": { "money_usd": 0, "access_effort": "beamtime_proposal",
                "lead_time_weeks": 12, "expertise_on_hand": true }
    },
    {
      "id": "instr:rheometer", "label": "Benchtop rheometer", "category": "instrument",
      "access": "in_house", "confidence": 0.75, "source": "publication_methods",
      "cost": { "money_usd": 0, "access_effort": "scheduling", "lead_time_weeks": 0 }
    },
    {
      "id": "instr:cryo_em", "label": "Cryo-EM (Titan Krios)", "category": "instrument",
      "access": "infeasible", "confidence": 0.3, "source": "field_prior",
      "cost": { "money_usd": 5000000, "access_effort": "external_partner", "lead_time_weeks": 26 }
    }
  ],
  "people": { "pi": 1, "postdoc": 3, "phd": 5, "skills": ["scattering","AFM","simulation"] },
  "compute": [{ "label": "SDCC Institutional Cluster", "scale": "~1 PF", "access":"shared_facility" }],
  "materials": ["block copolymers","thin films"],
  "expertise_embedding": "vec:db://profiles/jane-doe",   // for the PiEvo semantic bridge (§7)
  "coverage_index": { "techniques_present": 18, "instruments_present": 11 },
  "provenance_audit": { "pages_crawled": 9, "robots_respected": true,
                        "sources": ["bnl.gov","openalex.org","ror.org"],
                        "cache": "capability/cache/jane-doe/" },
  "generated_at": "2026-06-29T15:00:00Z", "ttl_days": 30
}
```

---

## 5. Profile → "difficulty" + "work-required" guidance

### 5a. Map hypothesis → required capabilities
For each hypothesis from `agents/hypothesis.py` (which already emits `test_plan` + `required_data`), a `feasibility-extract` call lifts the **required capability set**. Resolve each against the graph:

```
status = have(in_house) | shared(facility, needs booking) | collaborator | acquirable($) | infeasible
```

### 5b. Scores
```
feasibility   = Σ_c  w(status_c) · confidence_c   / N      # 0..1
difficulty(1-5) = f( #missing, max acquisition difficulty, technique complexity,
                     sample/measurement count parsed from test_plan )
work_weeks    = Σ_steps  effort_step · access_multiplier(status)
                 # in_house ×1, shared ×1.5+lead_time, collaborator ×3, acquirable ×6
```

Each hypothesis is annotated with a guidance block the user asked for:

```json
{ "feasibility": 0.78, "difficulty": 3, "work_estimate_weeks": 6,
  "what_it_explains": "Quantifies the unmodeled GISAXS–rheology coupling (lit gap G2).",
  "you_already_have": ["GISAXS via 11-BM","rheometer"],
  "missing": [{ "cap":"cryo-EM","cheapest_path":"CFN user proposal","cost_usd":0,"lead_weeks":10 }],
  "cheapest_path": "Run on existing NSLS-II beamtime; no purchase needed.",
  "confidence": 0.82 }
```

### 5c. Agents debate before committing (`debate.py`)
Three roles produce the final numbers (the "discuss back-and-forth" requirement):
- **Capability Optimist** — argues access via shared facility / collaborator / creative substitution.
- **Capability Skeptic** — hidden costs: calibration, sample prep, expertise gaps, beamtime queues.
- **Feasibility Judge** — commits the final `difficulty`/`work`/`confidence` with a one-line rationale.

This rides directly on the existing adversarial-critic pattern in `agents/validation.py`.

---

## 6. Privacy / ethics boundary (make it defensible to judges)

**Two physically separated data planes, enforced in code, not just convention:**

| | LOCAL plane | WEB plane |
|---|---|---|
| Contents | raw experimental files (your `parsers/` output) | identity/field **metadata** only (name, lab, field, public URLs) |
| Network | **never** leaves the machine | search/crawl public pages only |
| To the LLM | only derived profiles, opt-in; never raw rows by default | metadata + fetched public text |

Enforcement: discovery/crawl functions accept **only** the `IdentityHints`/`Identity` type — they are structurally incapable of receiving the `ParseResult` data object. An outbound **allowlist guard** sits in `tools/web_tools.py`: any string heading to the network is checked against the data-plane object and refused if it overlaps (redaction tripwire).

Crawl etiquette (all already half-present in `lit_apis`): robots.txt compliance, identifying User-Agent, rate-limit + 429 backoff, depth/page caps, **public pages only — never auth/login/paywall**, TTL'd on-disk cache to avoid re-hitting hosts, full provenance per capability (auditable), and a `--forget` command that wipes `capability/cache/`.

**Judge one-liner:** *"We profile the **lab**, never the user's **data**. Public scholarly metadata only (OpenAlex/ROR/the lab's own site), robots-respecting, rate-limited, cached, user-confirmed, and deletable. Raw experiments stay on your disk."*

---

## 7. Tie-in: per-role model router + cost-aware IDS (the PiEvo bridge)

### Model router (`config/models.yaml`, extends `agents/llm.py`)
`get_llm(role=...)` reads a per-role map. Apply PiEvo lesson (c) — **crisp non-reasoning models on the strategic/utility layer, reasoning models only for explanation**:

```yaml
discovery-extract:  { provider: openrouter, model: "google/gemini-2.0-flash", temp: 0.0 }
cap-extract:        { provider: deepseek,   model: "deepseek-chat",            temp: 0.0 }  # cheapest, high-volume
normalize:          { provider: openrouter, model: "google/gemini-2.0-flash", temp: 0.0 }
feasibility-judge:  { provider: deepseek,   model: "deepseek-chat",            temp: 0.2 }  # NON-reasoning (utility layer)
debate:             { provider: openrouter, model: "<mid>",                    temp: 0.7 }
explain:            { provider: openrouter, model: "<reasoning model>",        temp: 0.5 }  # prose only
```

### Cost-aware Information-Directed Selection
The profile plugs straight into PiEvo Eq.1. Instead of pure `h_t = argmin Δ²/I`, we make the loop pick the experiment with the most **information gain per unit of THIS user's effort**:

```
h_t = argmin_h  [Δ_t(h)]² / ( I_t(h) · feasibility(h | profile) )
                 # ≡ maximize  info_gain · feasibility  per  cost(h|profile)
```

A hypothesis with huge `I_t(h)` that needs a $5M cryo-EM Jane doesn't have is automatically demoted beneath one she can run on next month's NSLS-II beamtime. The `expertise_embedding` field also feeds PiEvo's semantic bridge (Eq.2) so the profile participates in the GP kernel, not just as a post-hoc filter.

---

## TL;DR build order for the hackathon
1. `tools/scholarly.py` (OpenAlex authors + ROR) + `discovery.py` + REPL confirm — **identity in, confirmed lab out.** (Biggest wow-per-hour; mostly free APIs you already depend on.)
2. `crawl.py` + `extract.py` + `normalize.py` → first `CapabilityProfile` JSON.
3. `priors.py` fallback + institution-tier scaling (lets the demo work even with a bare prompt).
4. `feasibility.py` + `debate.py` → attach the difficulty/work/what-it-explains block to existing hypotheses.
5. Wire cost-aware IDS into the PiEvo loop last.

**Answer to the framing question:** yes — and the capability layer is what turns a generic "synthesize literature + data → hypotheses" tool (which everyone will build) into one that knows *who is asking* and *what they can actually do about it*.


---

# CLI runtime

I have enough grounding. Here is the design.

---

# HypoForge CLI Runtime — The Ultra-Agentic Shell

*The Claude-Code-style runtime that ties every subsystem (ingestion, capability profiling, PiEvo loop) into one interactive, resumable, tool-driven agent loop.*

This subsystem owns **nothing scientific** and **everything operational**: the REPL, the agent loop, the tool registry, session/filesystem state, planning, streaming, human-in-the-loop checkpoints, and persistence. Other teams plug their functions in as **tools**; the runtime is what makes it *feel* like Claude Code.

---

## 0. Salvage & reuse from the prototype

| Existing | Runtime reuses it as |
|---|---|
| `agents/llm.py` `call_json`/`_extract_json`/`_MockLLM` | The model-call substrate. Generalize `get_llm()` → `get_llm(role=...)`. The runtime never crashes without keys (mock fallback = offline demo). |
| `agents/orchestrator.py` `run_pipeline` + `progress(key,label,frac)` callback | Becomes the body of **one** tool (`run_oneshot_pipeline`) AND the template for the streaming event bus. The progress-callback pattern is promoted to the runtime-wide `EventBus`. |
| `parsers/registry.parse_file` | Wrapped by the `ingest` tool; runtime adds the locality firewall + session indexing. |
| `tools/lit_apis.py` ThreadPool fan-out | Called by lit/profile tools; runtime adds checkpointing around network calls. |

Nothing is thrown away. The Streamlit `app.py` is retired; its orchestration logic survives as a tool.

---

## 1. Top-level package layout

```
hypoforge/
  __main__.py            # `python -m hypoforge` entrypoint
  cli.py                 # Typer/argparse command surface: run/profile/ingest/resume/replay/forget
  repl.py                # interactive prompt loop (prompt_toolkit): slash-commands, streaming render
  runtime/
    loop.py              # THE agent loop: model -> tool_calls -> observe -> repeat
    router.py            # get_llm(role=...) per-role model router (extends agents/llm.py)
    bus.py               # EventBus: typed streaming events -> renderer(s) + transcript
    registry.py          # @tool decorator + ToolSpec + JSON-schema dispatch + locality guard
    planner.py           # todo/plan object the agent reads & rewrites (TodoList)
    checkpoint.py        # human-in-the-loop gates (approve experiment / confirm lab site)
    session.py           # Session model, project dirs, WorldState handle, autosave
    state.py             # serialize/deserialize: transcript, plan, EvidenceStore, WorldState
    render.py            # terminal rendering (rich): spinners, panels, diffs, tables
    errors.py            # graceful tool-failure -> observation, never crash the loop
  tools/                 # the registered tool surface (thin wrappers over subsystems)
    fs_tools.py          # glob/find/read_head/list_dir/resolve_path  (filesystem access)
    ingest_tools.py      # wraps parsers/* -> Evidence  (LOCAL plane)
    lit_tools.py         # wraps tools/lit_apis.py        (WEB plane)
    profile_tools.py     # wraps capability/*            (WEB plane, identity only)
    loop_tools.py        # wraps PiEvo engine: warmup/round/select/run_experiment (LOCAL plane)
    report_tools.py      # emit_hypotheses / write_report / export_json
  config/
    models.yaml          # per-role model map (PiEvo config/model.yaml analog)
    runtime.yaml         # budgets, caps, autosave interval, default flags
  prompts/
    system_shell.md      # the agentic system prompt (loop persona + tool-use contract)
.forge/                  # PER-PROJECT state dir (created in user's cwd, gitignored)
    sessions/<id>/
       transcript.jsonl  # append-only event log (resumable)
       plan.json         # current TodoList
       world.json        # PiEvo WorldState (principles, GPs-as-params, history)
       evidence/         # EvidenceStore index (refs, not raw bytes)
       checkpoints/      # pending + answered HITL prompts
       config.lock.json  # resolved flags + model routing for this run (reproducibility)
    cache/               # crawl/lit cache (TTL, --forget wipes)
```

**Design rule:** `runtime/` is domain-agnostic and depends on no subsystem; `tools/` is the only place that imports `parsers/`, `capability/`, `pievo/`. Swapping a subsystem touches one wrapper file.

---

## 2. The command surface

```
forge run        "<free-form prompt>"  [paths...]   # main: ingest + closed-loop discovery
forge profile    [--prompt "..."] [--url URL]       # just the institution capability profile
forge ingest     <paths...>                         # just index data/PDFs/folders into a session
forge resume     [<session-id>]                     # reattach to the latest/given session REPL
forge replay     <session-id> [--speed 2x]          # re-stream a past transcript (demo gold)
forge forget     [--cache|--session <id>|--all]     # wipe caches / sessions (privacy)
forge tools                                         # list registered tools + schemas
```

Common flags (resolved once, frozen into `config.lock.json`):

```
--data <dir>        roots that are tagged plane=local (raw data firewall)
--paper <path/dir>  PDFs/refs to ingest
--dry-run           experiments return surrogate draws (no solver/API needed) — demo mode
--auto              auto-approve low-risk checkpoints (still gates network + experiments)
--yes               approve ALL checkpoints (unattended; prints what it would have asked)
--max-turn 20       hard cap on agent-loop iterations (PiEvo's --max_turn analog)
--max-rounds 15     closed-loop scientific rounds
--budget-usd 0.50   LLM spend ceiling; loop stops & checkpoints when hit
--warmup 5          PiEvo warm-up rounds
--model-config config/models.yaml   provider-swappable per-role routing
--offline           force mock LLM + cached web only
--no-net            disable all network tools (pure local)
```

A single invocation:

```
forge run "I study GISAXS of block copolymers at BNL. Look in ./sims for field dumps \
           and read the PDF in ./refs. What can I test next?" --data ./sims --paper ./refs --dry-run
```

This drops into the REPL after the first autonomous burst, leaving the user at a prompt.

---

## 3. The agent loop (`runtime/loop.py`)

The heart. A standard tool-calling loop, model-agnostic, driven by the per-role router.

```python
# runtime/loop.py
def agent_loop(session: Session, user_msg: str, *, role="orchestrator",
               max_turn: int) -> None:
    bus = session.bus
    session.transcript.append(Event("user", text=user_msg))
    msgs = session.build_context()            # system + plan + recent transcript + tool results

    for turn in range(max_turn):
        # 1. MODEL STEP (streamed) ----------------------------------------
        reply = router.call(role, msgs, tools=registry.schemas(),
                            stream=bus.token_sink)        # streams tokens live
        session.transcript.append(Event("assistant", reply))

        if not reply.tool_calls:                # model chose to talk, not act
            if session.plan.all_done() or reply.signals_stop():
                break
            msgs = session.refresh()            # nudge: "continue or call a tool"
            continue

        # 2. TOOL STEP ----------------------------------------------------
        for call in reply.tool_calls:
            bus.emit(ToolStart(call.name, call.args))
            try:
                gate = checkpoint.guard(call, session)    # HITL? (see §7)
                if gate.deferred:                          # paused for human
                    session.park(call); return             # loop resumes on answer
                obs = registry.dispatch(call, session)     # locality-checked dispatch
            except ToolError as e:
                obs = Observation.failure(str(e))          # never crash the loop
            bus.emit(ToolEnd(call.name, obs.preview()))
            session.transcript.append(Event("tool", call.name, obs))
            msgs = session.append_tool_result(call, obs)

        session.autosave()                      # persist every turn (resumable)
```

Key properties:
- **Turn-bounded** (`--max-turn`) so it can't run forever; the *scientific* round budget is separate (`--max-rounds`) and lives inside the PiEvo `loop_tools`.
- **Stateless model, stateful session**: the model gets reconstructed context each turn from durable session state, so a crash + `forge resume` is lossless.
- **Park/resume on checkpoints**: when a tool needs human approval, the loop *returns* (parks the pending call); answering it re-enters the loop exactly where it left off.
- **Role switch**: the orchestrator role drives the shell; it can invoke the PiEvo sub-loop, which internally uses `principle`/`hypothesis`/`experiment` roles (crisp non-reasoning for strategy per PiEvo lesson c).

---

## 4. The tool registry (`runtime/registry.py`)

A decorator registry mirroring PiEvo's `pievo/tools/`, with **JSON-schema dispatch** and the **locality firewall** baked in.

```python
# runtime/registry.py
TOOLS: dict[str, ToolSpec] = {}

def tool(name, *, plane: Plane, touches=("compute",), checkpoint=False,
         cost=0.0, summary=""):
    """Register a callable as an agent tool.
       plane     : 'local' | 'web'  -> firewall class of the tool
       touches   : subset of {compute, local_data, network}
       checkpoint: require human approval before running
    """
    def deco(fn):
        TOOLS[name] = ToolSpec(
            name=name, fn=fn, plane=plane, touches=set(touches),
            checkpoint=checkpoint, cost=cost, summary=summary,
            schema=schema_from_signature(fn),   # introspect type hints -> JSON schema
        )
        return fn
    return deco

def dispatch(call, session) -> Observation:
    spec = TOOLS[call.name]
    args = spec.schema.validate(call.args)               # reject malformed args
    _firewall(spec, args, session)                       # <-- the data-plane guard
    session.budget.charge(spec.cost)
    return spec.fn(session=session, **args)

def _firewall(spec, args, session):
    # A tool that touches the network may not receive any local-plane handle.
    if "network" in spec.touches:
        for v in args.values():
            if session.evidence.is_local_ref(v):
                raise ToolError(f"firewall: '{spec.name}' is networked; "
                                f"cannot receive local-plane data {v!r}")
    # A local_data tool runs with network disabled (enforced in subprocess sandbox).
```

**Registered tools (the agent's verbs):**

| Tool | plane | touches | checkpoint | Wraps |
|---|---|---|---|---|
| `list_dir`, `glob`, `read_head` | local | local_data | – | `fs_tools` |
| `ingest(paths)` → Evidence ids | local | local_data | – | `parsers/registry` |
| `lit_search(queries)` | web | network | – | `tools/lit_apis` |
| `discover_lab(hints)` | web | network | **yes** | `capability/discovery` |
| `crawl_profile(url)` → CapabilityProfile | web | network | **yes** | `capability/crawl+extract` |
| `warmup_loop(n)` | local | compute,local_data | – | `pievo` engine |
| `propose_round()` → candidates+guidance | local | compute | – | `pievo` |
| `run_experiment(h_id)` → Observation | local | compute,local_data | **yes** | `pievo/tools` |
| `emit_hypotheses()`, `write_report()` | local | compute | – | `report_tools` |

The model only ever picks a tool name + params; it **never emits executable code** — same safety stance as the prototype's viz design. Tool schemas are produced from Python type hints so adding a subsystem function = one decorator.

---

## 5. Filesystem access & the session/project model (`runtime/session.py`)

```python
@dataclass
class Session:
    id: str                       # ulid; dir = ./.forge/sessions/<id>/
    root: Path                    # user cwd at launch
    data_roots: list[Path]        # --data dirs -> everything under = plane=local
    bus: EventBus
    transcript: Transcript        # append-only JSONL
    plan: TodoList
    evidence: EvidenceStore       # ingested Evidence index (refs only)
    world: WorldState | None      # PiEvo state (None until warmup)
    budget: Budget                # usd + turns + wallclock ledger
    pending: ParkedCall | None    # set when a checkpoint is open
    config: ResolvedConfig        # frozen flags + model routing
```

- **Project = a `.forge/` dir** in the user's cwd (like `.git/`). Multiple sessions coexist; `forge resume` lists them with one-line summaries.
- **Filesystem tools are sandboxed by `data_roots`**: `glob`/`read_head` resolve only inside `root` and `data_roots`; paths outside require an explicit `--data` add or a checkpoint. Free-form mentions ("the PDF I dropped in refs") are resolved by the model calling `glob("**/*.pdf")` then `ingest`.
- **Locality tagging happens at ingest**: any path under a `data_root` → `Evidence.plane="local"`; lit/profile results → `plane="web"`. The firewall (§4) then physically prevents local handles from reaching networked tools.

---

## 6. Planning / todo mechanism (`runtime/planner.py`)

A first-class object the agent **reads and rewrites** each turn — what gives the Claude-Code "I can see it thinking in steps" feel.

```python
@dataclass
class TodoItem:
    id: str
    text: str                                  # "Confirm BNL Soft-Matter homepage"
    status: Literal["pending","in_progress","done","blocked"]
    blocked_on: str | None = None              # e.g. "checkpoint:lab_confirm"

class TodoList:
    items: list[TodoItem]
    def render(self) -> str: ...               # checkbox list shown in REPL + transcript
    def all_done(self) -> bool: ...
```

- Exposed to the model as two tools: `set_plan(items)` and `update_todo(id, status)`. The system prompt instructs: *propose a plan before acting on multi-step work; mark exactly one item in_progress.*
- Rendered live as a checkbox panel (`render.py`). On `forge resume`, the plan is restored verbatim, so the loop knows what's left.
- For the closed loop, the planner seeds a canonical skeleton: `ingest → profile lab → warmup(5) → [round×N: propose→debate→select→run→update] → report`. Each scientific round appends a `done` line with the IDS guidance row (info_gain, regret, difficulty, effort).

---

## 7. Human-in-the-loop checkpoints (`runtime/checkpoint.py`)

Two checkpoints matter for the demo and for trust; both ride the same mechanism.

```python
@dataclass
class Checkpoint:
    kind: Literal["confirm_lab","approve_experiment","approve_network","budget_exceeded"]
    prompt: str
    options: list[str]               # ["confirm","edit","reject","skip"]
    payload: dict                    # what would run / what was discovered
    default: str                     # used under --auto for low-risk kinds

def guard(call, session) -> Gate:
    spec = TOOLS[call.name]
    if not spec.checkpoint:                       return Gate.allow()
    if session.config.yes:                         return Gate.allow()
    if session.config.auto and spec.risk=="low":   return Gate.allow()
    cp = build_checkpoint(call, session)
    session.open_checkpoint(cp); bus.emit(CheckpointOpen(cp))
    return Gate.deferred()                          # loop parks; REPL prompts user
```

Two flagship gates:

**(a) Confirm the discovered lab** (the differentiator's trust moment):
```
I think you're: Jane Doe — Soft Matter Group, CMPMS @ Brookhaven National Lab
  homepage  https://www.bnl.gov/cmpms/soft-matter   (confidence 0.86)
  field     X-ray scattering · polymer physics · GISAXS
[Enter] confirm  ·  [e] edit  ·  [s] pick another  ·  [n] no site (use field prior)
forge>
```

**(b) Approve an experiment before it runs** (closed-loop safety + the "you're in control" feel):
```
▶ Experiment proposed (round 6, IDS-selected)
  hypothesis  h-id 42: "Raising anneal T 180→210°C shifts GISAXS d-spacing >8%"
  tool        run_simulation(params={T:210, t:600})   cost≈$0.00 (dry-run)
  why this one  info_gain 1.74 nats · regret 0.21 · feasibility 0.78 (you have 11-BM)
  difficulty 3/5 · est. effort 6 wks real / 4s compute
[Enter] run  ·  [p] params  ·  [s] skip (pick next-best)  ·  [a] auto-approve rest
```

- Checkpoints are **persisted** under `checkpoints/`, so `forge resume` re-presents an open gate.
- `--auto` clears low-risk gates (e.g. reading a public page) but **never** auto-runs experiments or first network egress without at least a logged notice; `--yes` clears everything for unattended/CI runs and prints what it skipped.
- A **budget checkpoint** fires when `--budget-usd` is hit: pause, show spend, offer continue/stop.

---

## 8. Streaming output & the event bus (`runtime/bus.py`, `render.py`)

A typed event stream is the single source of truth for *both* the live terminal render *and* the durable transcript — generalizing the prototype's `progress(key,label,frac)` callback.

```python
Event = Union[Token, AssistantMsg, ToolStart, ToolEnd, CheckpointOpen,
              Plan, RoundResult, Warning, Error]

class EventBus:
    def emit(self, ev: Event):
        for sink in self.sinks: sink(ev)     # sinks: TerminalRenderer, TranscriptWriter
    def token_sink(self, tok: str):          # passed to router.call(stream=...)
        self.emit(Token(tok))
```

- **TerminalRenderer** (`rich`): streams model tokens live; shows a spinner + elapsed for each `ToolStart`; collapses long tool output into a one-line preview with `[+]` expand; renders the plan checkbox panel and per-round IDS guidance tables.
- **TranscriptWriter**: appends every event to `transcript.jsonl`. This *is* the persistence layer (§9) and powers `forge replay`.
- Mock/offline mode still streams (deterministic) so the demo never shows a dead terminal.

---

## 9. Transcript & state persistence (`runtime/state.py`)

Designed so a multi-hour closed loop survives crashes, `Ctrl-C`, and machine sleeps.

```
.forge/sessions/<id>/
  transcript.jsonl   # append-only Event log  -> replay + audit + context rebuild
  plan.json          # TodoList snapshot
  world.json         # WorldState: principles (text+embedding+post_logw+gp_params),
                     #             candidates, history(observations), design_space, round
  evidence/index.json# Evidence records (modality, plane, summary, quantities, claims,
                     #   raw_ref=PATH only — never bytes)  + checksum dedupe
  checkpoints/*.json # open & answered HITL gates
  config.lock.json   # resolved flags + per-role model map (reproducibility)
```

- **Autosave every turn** (`session.autosave()`); `world.json` written every scientific round. GPs are serialized as their fitted hyperparams + the (x,y,σ) history, so they refit deterministically on resume — small, portable, no pickle of heavy objects.
- **Context reconstruction**: `session.build_context()` assembles system prompt + plan + last-K transcript turns + a rolling summary of older turns (cheap-model summarization to stay in budget). The model is fully stateless; the session is the brain.
- **`forge replay`** re-emits `transcript.jsonl` to the renderer at adjustable speed — a zero-risk, deterministic demo that needs no keys or network.
- **Privacy**: only `raw_ref` paths live in state, never raw rows/bytes (local-plane firewall extends to disk state). `forge forget` wipes sessions/caches.

---

## 10. Per-role model router (`runtime/router.py`, `config/models.yaml`)

Generalizes the prototype's single `get_llm()` into PiEvo's per-agent config, honoring lesson (c): **crisp non-reasoning models on strategy, reasoning models on comprehension/generation.**

```yaml
# config/models.yaml  — provider-swappable; falls back to mock if key missing
orchestrator:   { provider: openrouter, model: "google/gemini-2.0-flash", temp: 0.3, reasoning: off }
principle:      { provider: deepseek,   model: "deepseek-chat",          temp: 0.2, reasoning: off }  # strategy
hypothesis:     { provider: openrouter, model: "<reasoning model>",      temp: 0.6, reasoning: on  }  # generation
ids_select:     { provider: deepseek,   model: "deepseek-chat",          temp: 0.0, reasoning: off }  # utility layer
debate:         { provider: openrouter, model: "<mid>",                  temp: 0.7, reasoning: on  }
vision:         { provider: openrouter, model: "qwen/qwen2.5-vl-72b-instruct", temp: 0.0 }
cap_extract:    { provider: deepseek,   model: "deepseek-chat",          temp: 0.0 }
summarize:      { provider: openrouter, model: "<cheap small>",          temp: 0.0 }  # context compaction
```

```python
# runtime/router.py  (thin extension of agents/llm.py)
def call(role: str, msgs, *, tools=None, stream=None):
    cfg = MODELS[role]
    llm = get_llm(provider=cfg.provider, model=cfg.model, temperature=cfg.temp)
    return _invoke(llm, msgs, tools=tools, stream=stream)   # reuses call_json robustness
```

One line per role to re-route; missing keys → mock backend → demo still runs.

---

## 11. How it all ties together (one `forge run`)

```
forge run "<prompt>" --data ./sims --paper ./refs --dry-run
   │
   ├─(repl.py) parse flags → ResolvedConfig → new Session in ./.forge/sessions/<id>/
   │
   ├─(loop.py) orchestrator role gets system_shell.md + prompt
   │     turn1: set_plan([ingest, profile, warmup, rounds…])         ▸ plan panel streams
   │     turn2: glob("**/*.{h5,pdf}") → ingest(...)                  ▸ Evidence (LOCAL)
   │     turn3: lit_search(queries)                                  ▸ papers (WEB)
   │     turn4: discover_lab(hints) ──► CHECKPOINT "confirm BNL?"    ▸ loop PARKS
   │           └─ user hits Enter ──► loop RESUMES
   │     turn5: crawl_profile(url) → CapabilityProfile (WEB)
   │     turn6: warmup_loop(5)  → seed principles + GP priors (LOCAL)
   │   ┌─ round t (loop_tools drives principle/hypothesis/ids roles):
   │   │   propose_round() → candidates + guidance(difficulty,effort,explains,info_gain)
   │   │   debate (optimist/skeptic/judge)  ▸ streamed back-and-forth
   │   │   IDS select  h_t = argmin Δ²/(I·feasibility)   ◄ capability profile plugs in
   │   │   run_experiment(h_t) ──► CHECKPOINT "approve experiment?" ──► run (dry-run draw)
   │   │   update posterior + anomaly check; append RoundResult to plan & transcript
   │   └─ repeat until stop-criterion / --max-rounds / --budget
   │
   ├─ emit_hypotheses() + write_report()  → ranked list w/ info-gain-per-effort
   └─ drop to REPL prompt  (user can ask follow-ups; state persisted; resumable)
```

Every box above is a registered tool; the runtime is the glue, the firewall, the streamer, and the memory. Other teams' subsystems are pure functions behind decorators — the **runtime is what makes them an agent.**

---

### TL;DR build order (hackathon)
1. `runtime/registry.py` (`@tool` + schema-from-hints + firewall) and `runtime/router.py` (extend `agents/llm.py`). *Half a day; unlocks everyone.*
2. `runtime/loop.py` + `runtime/bus.py` + `repl.py` with 3 trivial tools (`glob`, `read_head`, `ingest`) → a working Claude-Code-style REPL.
3. `runtime/session.py` + `state.py` (transcript JSONL + autosave + `forge resume`).
4. `checkpoint.py` (the two gates) + `planner.py` (todo panel) — the "wow" interactions.
5. Wrap PiEvo loop as `loop_tools`; wire `forge replay` last (bulletproof demo).

**Key files referenced:** `/Users/abdollahegazy/bnl/aijam/agents/llm.py` (router substrate + mock fallback), `/Users/abdollahegazy/bnl/aijam/agents/orchestrator.py` (progress-callback → EventBus pattern, becomes the `run_oneshot_pipeline` tool), `/Users/abdollahegazy/bnl/aijam/parsers/registry.py` (behind `ingest`), `/Users/abdollahegazy/bnl/aijam/tools/lit_apis.py` (behind `lit_search`).


---

# Modular model router

Grounded. The prototype already has the salvageable spine: `active_provider()`, `call_json()`/`_extract_json()` (robust parsing), and `_MockLLM`. The router generalizes the single global `get_llm(temperature)` into `get_llm(role=...)` driven by YAML, adds provider adapters for OpenRouter/DeepSeek/local, and wraps everything in retries + JSON-mode + cost/latency accounting. Here is the design.

---

# Subsystem: Modular Multi-Model Router (`router/`)

The single seam every agent talks through. No agent imports a provider SDK; they import one function and pass a **role string**. Swapping a model = editing one YAML line. Honors PiEvo lesson (c): **crisp non-reasoning models on strategic/utility layers, reasoning models on analysis/critique.**

## 0. What we salvage vs build

| From `agents/llm.py` | Verdict | New home |
|---|---|---|
| `call_json` + `_extract_json` (balanced-brace JSON recovery, re-ask loop) | **Keep verbatim** | `router/parse.py` |
| `_MockLLM` (deterministic keyword responses) | **Keep, extend** | `router/providers/mock.py` |
| `active_provider()` key-presence → mock fallback | **Keep the idea**, make per-role | `router/providers/__init__.py` |
| `get_llm(temperature)` global factory | **Replace** with `get_llm(role=...)` | `router/client.py` |
| env-only model selection | **Replace** with `config/models.yaml` (+ env overrides) | `router/config.py` |

## 1. File layout

```
config/
  models.yaml          # role -> model assignment (the heart)
  pricing.yaml         # model -> $/Mtok in,out + latency hint (cost engine)
router/
  __init__.py          # public API: complete(), complete_json(), get_spec(), Budget
  roles.py             # the canonical Role registry (string constants + defaults)
  config.py            # load+validate models.yaml, apply env overrides, resolve fallbacks
  client.py            # the one thin client: retries, JSON-mode, timeout, cost logging
  budget.py            # per-run + per-role cost/latency budget guard + downgrade ladder
  ledger.py            # append-only usage records -> .hypoforge/usage.jsonl + summary
  parse.py             # salvaged _extract_json + JSON re-ask
  providers/
    __init__.py        # registry: name -> Provider adapter; key detection
    base.py            # Provider protocol (one method: chat())
    openai_compat.py   # OpenRouter + DeepSeek (both are OpenAI-compatible)
    local.py           # Ollama / llama.cpp (OpenAI-compatible localhost)
    mock.py            # offline deterministic backend (salvaged _MockLLM)
```

OpenRouter, DeepSeek, Ollama, and llama.cpp all speak the **OpenAI chat-completions** wire format, so one `openai_compat.py` adapter covers three of four providers — only `base_url`/`api_key`/headers differ.

## 2. The role registry (`router/roles.py`)

Roles are coarse *functions*, not agents, so several agents can share one role. The PiEvo split is baked into the default `reasoning` flag.

```python
# router/roles.py
from enum import StrEnum

class Role(StrEnum):
    # --- STRATEGIC / UTILITY LAYER -> non-reasoning, low temp (PiEvo lesson c) ---
    PRINCIPLE     = "principle"      # Principle Agent: propose/augment principles
    STRATEGY      = "strategy"       # IDS selection rationale, explore/exploit, anomaly trigger
    FEASIBILITY   = "feasibility"    # capability judge: difficulty/work numbers
    EXTRACT       = "extract"        # high-volume cheap structured extraction (lit, capability)
    NORMALIZE     = "normalize"      # free-text -> ontology mapping
    DISCOVERY     = "discovery"      # identity-hint extraction from prompt

    # --- ANALYSIS / GENERATION LAYER -> reasoning models, higher temp ---
    HYPOTHESIS    = "hypothesis"     # creative hypothesis drafting
    CRITIC        = "critic"         # adversarial validation / debate panel
    LITERATURE    = "literature"     # read papers, extract gaps/limitations
    VISION        = "vision"         # figure/plot/microscopy extraction (multimodal)
    EXPLAIN       = "explain"        # prose: "what it explains", final guidance text
    CODE          = "code"           # simulation/surrogate code synthesis

ALIASES = {                          # back-compat for salvaged agents
    "validation": Role.CRITIC, "understanding": Role.EXTRACT,
}
```

`Role` is a `StrEnum`, so `complete(Role.CRITIC, ...)` and `complete("critic", ...)` are identical — callers can pass plain strings, keeping the migration from the prototype trivial.

## 3. The config schema (`config/models.yaml`)

```yaml
# config/models.yaml — role -> model assignment. Edit one line to swap a model.
version: 1

defaults:                      # applied to every role unless overridden
  provider: openrouter
  temperature: 0.3
  max_tokens: 2048
  reasoning: false             # default OFF — most roles are strategic/extraction
  timeout_s: 60
  retries: 2
  json_mode: true              # ask provider for response_format=json_object when supported

# Ordered providers tried when the primary key is missing / a call hard-fails.
# 'mock' is always the terminal fallback so the tool NEVER crashes (salvaged behavior).
fallback_chain: [openrouter, deepseek, local, mock]

roles:
  # ----- STRATEGIC / UTILITY: crisp NON-reasoning, low temp -----
  principle:                   # PiEvo lesson (b): use the BEST of the cheap tier here
    provider: deepseek
    model: deepseek-chat       # strong, non-reasoning. NOT deepseek-reasoner.
    temperature: 0.2
    reasoning: false
  strategy:
    model: openai/gpt-4o-mini  # fast crisp, no think-mode
    temperature: 0.0
    max_tokens: 512
    reasoning: false
  feasibility:
    provider: deepseek
    model: deepseek-chat
    temperature: 0.2
    reasoning: false
  extract:                     # cheapest high-volume; a free OpenRouter tier is ideal
    model: "meta-llama/llama-3.3-70b-instruct:free"
    temperature: 0.0
    max_tokens: 1024
  normalize:   { model: "google/gemini-2.0-flash-001", temperature: 0.0 }
  discovery:   { model: "google/gemini-2.0-flash-001", temperature: 0.0, max_tokens: 512 }

  # ----- ANALYSIS / GENERATION: reasoning models, more headroom -----
  hypothesis:
    model: deepseek/deepseek-r1     # reasoning ON for creative drafting
    temperature: 0.8
    reasoning: true
    max_tokens: 4096
  critic:
    model: deepseek/deepseek-r1
    temperature: 0.6
    reasoning: true
  literature:
    model: "google/gemini-2.0-flash-thinking-exp"
    temperature: 0.3
    reasoning: true
    max_tokens: 8192
  vision:
    model: "qwen/qwen2.5-vl-72b-instruct"   # cheap best-in-class chart/plot OCR
    temperature: 0.0
    reasoning: false                         # transcription, not reasoning
    modality: image
  explain:     { model: "deepseek/deepseek-r1", temperature: 0.5, reasoning: true }
  code:        { model: "deepseek/deepseek-chat", temperature: 0.1, max_tokens: 6000 }

budget:                        # see §6
  run_usd_cap: 1.50            # whole session
  per_call_usd_cap: 0.15
  run_latency_s_cap: 1200
  on_exceed: downgrade         # downgrade | block | warn
  downgrade_to: extract        # role whose (cheap) model we fall back to
```

**Override precedence** (highest wins), resolved in `config.py`:
`env var` → `models.yaml roles.<role>` → `models.yaml defaults`.
Env overrides let the demo machine swap everything without touching files:
`HYPOFORGE_ROLE_HYPOTHESIS_MODEL=deepseek/deepseek-chat`, `HYPOFORGE_FORCE_PROVIDER=mock`, `HYPOFORGE_OFFLINE=1`.

## 4. Resolved spec + provider protocol

```python
# router/config.py
from dataclasses import dataclass

@dataclass(frozen=True)
class ModelSpec:
    role: str
    provider: str          # openrouter | deepseek | local | mock
    model: str
    temperature: float
    max_tokens: int
    reasoning: bool        # maps to provider-specific knob (DeepSeek model id / OpenRouter `reasoning`)
    json_mode: bool
    timeout_s: int
    retries: int
    modality: str = "text" # "image" enables the vision content path

def get_spec(role: str) -> ModelSpec: ...      # merges env > role > defaults, validates
def all_specs() -> dict[str, ModelSpec]: ...    # for `hypoforge models` REPL command
```

```python
# router/providers/base.py
from typing import Protocol
from dataclasses import dataclass

@dataclass
class LLMResult:
    text: str
    prompt_tokens: int
    completion_tokens: int
    model: str
    provider: str
    latency_s: float
    raw_usage: dict | None = None   # provider-reported usage if present

class Provider(Protocol):
    name: str
    def available(self) -> bool: ...                       # key/host present?
    def chat(self, spec: ModelSpec, messages: list[dict],
             images: list[bytes] | None = None) -> LLMResult: ...
```

`openai_compat.py` implements `chat()` once for both OpenRouter and DeepSeek (differ only by `base_url`/`api_key`/headers + the `reasoning` knob). `reasoning=True` resolves to the right lever per provider: a reasoning **model id** (DeepSeek `deepseek-reasoner`), or OpenRouter's `reasoning: {effort}` body field — abstracted so YAML just says `reasoning: true`.

## 5. The one client (`router/client.py`) — public API

```python
# router/__init__.py  (the entire surface agents use)
def complete(role: str, prompt: str, *, system: str = "",
             images: list[bytes] | None = None,
             temperature: float | None = None,   # per-call override
             budget: "Budget | None" = None) -> str: ...

def complete_json(role: str, prompt: str, *, system: str = "",
                  schema: dict | None = None,     # optional JSON-Schema validation
                  images: list[bytes] | None = None,
                  budget: "Budget | None" = None): ...
```

Migration is mechanical — the salvaged agents change `call_json(prompt, sys)` → `complete_json(Role.CRITIC, prompt, system=sys)`.

`complete()` control flow:

```
spec = get_spec(role)                       # resolve YAML+env
budget.precheck(spec)                       # may downgrade spec or raise BudgetExceeded
for attempt in range(spec.retries + 1):
    provider = resolve_provider(spec)       # primary, else next in fallback_chain that .available()
    try:
        res = provider.chat(spec, messages, images)   # json_mode -> response_format if supported
        ledger.record(role, res, cost=price(res))     # §6 cost logging
        budget.charge(res)                             # subtract from run caps
        return res.text
    except (Timeout, RateLimit, ProviderError) as e:
        backoff(attempt)                    # reuse lit_apis 429 backoff style
        spec = next_fallback(spec)          # walk fallback_chain; terminal = mock
# JSON path additionally runs salvaged _extract_json + one re-ask before mock
```

Key behaviors:
- **JSON-mode** sends `response_format={"type":"json_object"}` to providers that support it; for those that don't, the salvaged `_extract_json` + re-ask loop in `parse.py` is the safety net. `schema` (if given) is validated with a 1-line `jsonschema.validate`; failure triggers one targeted re-ask.
- **Fallback never crashes**: if every real provider is down/keyless, the terminal `mock` provider returns deterministic JSON — the whole pipeline still runs offline (salvaged guarantee).
- **Vision**: when `spec.modality=="image"` and `images` given, `openai_compat` packs `image_url` content blocks; a non-vision fallback degrades to text-only with a `notes` flag rather than erroring.

## 6. Cost/latency budget + logging (`budget.py`, `ledger.py`, `pricing.yaml`)

```yaml
# config/pricing.yaml — $ per 1M tokens (in,out) + rough latency for the budget planner
"deepseek-chat":                 { in: 0.27, out: 1.10, latency_s: 4 }
"deepseek/deepseek-r1":          { in: 0.55, out: 2.19, latency_s: 18 }
"openai/gpt-4o-mini":            { in: 0.15, out: 0.60, latency_s: 3 }
"qwen/qwen2.5-vl-72b-instruct":  { in: 0.20, out: 0.60, latency_s: 6 }
"*:free":                        { in: 0.0,  out: 0.0,  latency_s: 8 }   # glob: any :free model
"mock-llm":                      { in: 0.0,  out: 0.0,  latency_s: 0 }
```

```python
# router/budget.py
class Budget:
    def __init__(self, usd_cap, per_call_cap, latency_cap, on_exceed="downgrade"):
        self.spent_usd = 0.0; self.elapsed_s = 0.0; ...
    def precheck(self, spec) -> ModelSpec:
        est = estimate_cost(spec)                  # prompt_tokens*price.in + max_tokens*price.out
        if self.spent_usd + est > self.usd_cap or est > self.per_call_cap:
            if self.on_exceed == "block": raise BudgetExceeded(spec.role)
            if self.on_exceed == "downgrade": return downgrade(spec)   # swap to budget.downgrade_to model
            warn(...)                              # 'warn' just logs and proceeds
        return spec
    def charge(self, res): self.spent_usd += price(res); self.elapsed_s += res.latency_s
    def report(self) -> dict: ...                  # per-role + total $/tokens/latency
```

**`ledger.record()`** appends one line per call to `.hypoforge/usage.jsonl`:

```json
{"ts":"2026-06-29T15:02Z","role":"hypothesis","provider":"openrouter",
 "model":"deepseek/deepseek-r1","prompt_tok":1840,"completion_tok":712,
 "usd":0.0026,"latency_s":17.4,"attempt":0,"fallback":false}
```

A REPL command `hypoforge cost` prints the rolled-up table (per-role spend, total $, p50/p95 latency, fallback count) so the team can watch the budget live during the demo. The **downgrade ladder** (`on_exceed: downgrade`) means a runaway closed loop silently drops expensive reasoning roles to the cheap `extract` model and keeps running rather than dying mid-demo.

## 7. Offline / mock mode

Three independent triggers, all converging on `mock`:
1. `HYPOFORGE_OFFLINE=1` or `--offline` → `resolve_provider` returns `mock` for **every** role.
2. A role's provider key absent **and** no fallback key present → that role uses `mock` (per-role, salvaged `active_provider` logic — other roles keep their real models).
3. Any hard failure exhausts `fallback_chain` → terminal `mock`.

`providers/mock.py` extends the prototype `_MockLLM` keyword router with role-aware responses (e.g. `Role.PRINCIPLE` returns a syntactically valid principle JSON, `Role.VISION` returns the figure-extraction schema from the ingestion design). It also returns fake but plausible token counts so `ledger`/`budget` exercise their full code path offline — meaning the cost dashboard is demoable with zero API keys.

## 8. How the rest of the system plugs in

- **PiEvo loop**: `principle`/`strategy` roles (non-reasoning) drive IDS selection & anomaly triggers; `hypothesis`/`critic` (reasoning) drive drafting & debate — the −26% think-mode pitfall is avoided by construction in YAML.
- **Capability subsystem**: `discovery`/`extract`/`normalize`/`feasibility` roles map 1:1 to that design's `config/models.yaml` rows — this IS that file.
- **Ingestion**: the `vision` role is the figure/plot extractor; `literature` reads gaps.

---

### TL;DR
One YAML (`config/models.yaml`) maps **role → {provider, model, temperature, max_tokens, reasoning}**, with env overrides and an ordered `fallback_chain` ending in `mock`. One client (`router/client.py`) exposes `complete()` / `complete_json()`, handling retries, OpenAI-compatible OpenRouter+DeepSeek+local adapters, JSON-mode (+ salvaged `_extract_json` recovery), per-call cost logging to `usage.jsonl`, and a `Budget` guard that downgrades expensive reasoning roles when caps are hit. PiEvo's lesson is encoded as defaults: strategic/utility roles ship `reasoning: false`, analysis/critique roles ship `reasoning: true`. Salvage `call_json`, `_extract_json`, and `_MockLLM` from `/Users/abdollahegazy/bnl/aijam/agents/llm.py`.

Relevant existing file to refactor: `/Users/abdollahegazy/bnl/aijam/agents/llm.py` (provider detection, `call_json`, `_MockLLM` move into `router/`).


---

# Principle-evolvable discovery engine

# Principle-Evolvable Discovery Engine — Concrete Hackathon Design

The closed loop. The heart. This subsystem takes warm-up `Evidence` (from ingestion) + literature-seeded principle candidates (from the literature subsystem) + a feasibility scorer (from the capability subsystem), and runs the adapted PiEvo Bayesian-optimization-over-principles loop until a stopping criterion fires.

It reuses the prototype almost verbatim where it can: `agents/llm.py:call_json` (robust JSON + mock fallback) becomes the agent transport; `agents/validation.py`'s adversarial-panel pattern becomes the debate stage; `agents/hypothesis.py`'s multi-framing generation becomes the Hypothesis Agent's candidate pool. Everything new is numeric: the GP experts, the IDS acquisition, the posterior, the anomaly score.

---

## 0. Module layout

All new code lives under a new `engine/` package, parallel to `agents/`, `parsers/`, `tools/`. Nothing here imports Streamlit.

```
engine/
  __init__.py
  state.py          # WorldState, Principle, Hypothesis, Observation, DesignSpace (dataclasses)
  embed.py          # local sentence-embedding wrapper (bge-small) + caching; the LOCAL plane
  bridge.py         # phi(h,P) semantic feature + ParamCodec (dict<->numeric vector psi(x))
  gp.py             # GPExpert: per-principle Gaussian-Process surrogate (sklearn)
  posterior.py      # log-space Bayes update (Eq.4), softmax weights, MAP, entropy, pruning
  infogain.py       # ids_score (Eq.1), mutual_information BALD (Eq.3), regret Delta
  anomaly.py        # calibrated residual S_s (Eq.3) vs surrogate AND literature prior + adaptive theta
  agents/
    __init__.py
    principle.py    # Principle Agent: seed P_0, augment on anomaly  (crisp non-reasoning model)
    hypothesis.py   # Hypothesis Agent: generate candidates under MAP principle (reasoning model)
    experiment.py   # Experiment Agent: pick tool, run x_target -> Observation  (local plane)
    debate.py       # optimist/skeptic/judge panel before IDS commit  (reuses validation.py pattern)
  experiments/
    __init__.py
    registry.py     # @experiment_tool decorator + EXPERIMENT_TOOLS dict + dry_run
    builtins.py     # fit_surrogate, recompute_statistic, run_simulation, literature_lookup
  loop.py           # DiscoveryEngine: warm-up + per-round state machine + stopping criteria
  config/
    engine.yaml     # warm-up rounds, max_turn, epsilons, beta, theta budget, per-role models
  router.py         # get_llm(role=...) — generalizes agents/llm.py to per-role model map
```

Dependencies to add (all small, laptop-friendly): `scikit-learn` (GP), `sentence-transformers` (local embeddings), `numpy`/`scipy` (already present via pandas). No GPyTorch needed for the hackathon — `sklearn.gaussian_process.GaussianProcessRegressor` is enough at ≤ few-hundred points per principle.

---

## 1. Core state (`engine/state.py`)

These are the single currency the loop manipulates. They are deliberately **domain-agnostic**: a `Principle`/`Hypothesis` is just text + an embedding + a target point in an abstract numeric design space `X`. Nothing knows about chemistry vs. turbulence vs. genomics.

```python
# engine/state.py
from dataclasses import dataclass, field
from typing import Literal, Optional
import numpy as np

Vec = np.ndarray
Provenance = Literal["literature", "anomaly", "warmup", "user"]
Mode = Literal["explore", "exploit"]
Source = Literal["sim", "compute", "surrogate", "literature", "user_data"]

@dataclass
class DesignSpace:
    """Schema of X — the abstract knobs. Domain-agnostic: continuous + categorical."""
    continuous: dict[str, tuple[float, float]]   # name -> (lo, hi)
    categorical: dict[str, list[str]]            # name -> levels
    target_name: str = "y"                       # the scalar objective being modeled
    maximize: bool = True

@dataclass
class Principle:
    id: str
    text: str                      # NL proposition constraining plausible hypotheses
    embedding: Vec                 # e_P, unit-normalized (LOCAL plane)
    prior_logw: float              # log p_0(P) from literature confidence x source trust
    post_logw: float               # log p_t(P), unnormalized; softmax over P_t at read time
    provenance: Provenance
    spawned_round: int
    gp: "GPExpert"                 # its calibrated surrogate expert
    obs_ids: list[str] = field(default_factory=list)

@dataclass
class Hypothesis:
    id: str
    text: str
    embedding: Vec                 # e_h
    parent_principle_id: str
    x_target: dict                 # concrete point in X to probe
    mode: Mode
    # guidance metadata (user requirement #6) — filled progressively:
    difficulty: float = 0.5        # 0..1 (set by capability subsystem)
    effort: dict = field(default_factory=dict)   # {"compute_s":..,"human_min":..,"$":..}
    feasibility: float = 1.0       # from capability profile; 1.0 if profiling disabled
    explains: list[str] = field(default_factory=list)  # principle ids it discriminates
    info_gain: Optional[float] = None   # I_t(h)
    regret: Optional[float] = None      # Delta_t(h)
    ids_score: Optional[float] = None   # the committed Delta^2/(I*feasibility)

@dataclass
class Observation:
    id: str
    hypothesis_id: str
    x: dict
    y: float
    sigma_obs: float
    source: Source
    round: int

@dataclass
class WorldState:
    space: DesignSpace
    P_t: list[Principle]           # the Active Principle set — GROWS, never fixed-card
    candidates: list[Hypothesis]
    history: list[Observation]
    round: int = 0
    # bookkeeping for stopping criteria:
    entropy_trace: list[float] = field(default_factory=list)
    best_regret_trace: list[float] = field(default_factory=list)
    rounds_since_anomaly: int = 0

    def weights(self) -> np.ndarray:
        """Live posterior softmax([post_logw]) over the current P_t."""
        lw = np.array([p.post_logw for p in self.P_t])
        lw -= lw.max()
        w = np.exp(lw); return w / w.sum()

    def map_principle(self) -> Principle:
        return self.P_t[int(np.argmax([p.post_logw for p in self.P_t]))]
```

`WorldState` is pickled to `runs/<id>/state.pkl` each round so the REPL can `/resume` — the Claude-Code feel.

---

## 2. Semantic bridge: text → numeric features (`engine/bridge.py`)

This is how natural-language propositions get a numeric Bayesian treatment (PiEvo Eq. 2), **extended** so the GP also sees the physical knobs. The `ParamCodec` is the only place that touches domain-specific param names — it standardizes continuous values and one-hot-encodes categoricals, so everything downstream is a plain vector. Domain-agnosticism lives here.

```python
# engine/bridge.py
import numpy as np

class ParamCodec:
    """Maps a domain x-dict <-> normalized numeric vector psi(x). Domain-agnostic."""
    def __init__(self, space):
        self.cont = list(space.continuous.items())     # [(name,(lo,hi)),...]
        self.cat  = list(space.categorical.items())

    def psi(self, x: dict) -> np.ndarray:
        v = []
        for name, (lo, hi) in self.cont:
            val = float(x.get(name, (lo + hi) / 2))
            v.append((val - lo) / (hi - lo + 1e-12))    # -> ~[0,1]
        for name, levels in self.cat:
            onehot = [1.0 if x.get(name) == lvl else 0.0 for lvl in levels]
            v.extend(onehot)
        return np.asarray(v, dtype=np.float32)

def phi(e_h: np.ndarray, e_P: np.ndarray, psi_x: np.ndarray) -> np.ndarray:
    """Eq.2 extended: [e_h . e_P, ||e_h - e_P||, psi(x_h)].
    First two are PiEvo's semantic coordinates; psi grounds it in experiment geometry."""
    dot = float(np.dot(e_h, e_P))
    dist = float(np.linalg.norm(e_h - e_P))
    return np.concatenate([[dot, dist], psi_x]).astype(np.float32)
```

Embeddings are produced by `engine/embed.py`, a thin cached wrapper over `sentence-transformers` `BAAI/bge-small-en-v1.5` (384-d, unit-normalized). This is the **local plane** — raw domain text never leaves the box, and embeddings are deterministic + cheap so they burn zero LLM budget (honors the cheap-LLM preference). `embed.py` exposes one function `embed(texts: list[str]) -> np.ndarray` with an `lru_cache` on text hash.

---

## 3. Per-principle GP expert (`engine/gp.py`)

One calibrated Gaussian-Process surrogate per active principle. The critical trick: **its prior mean is seeded from the literature relationship**, so early predictions reflect what papers claim, and the anomaly score (§6) measures the *user's local data contradicting published consensus*.

```python
# engine/gp.py
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel

class GPExpert:
    """Surrogate for one principle. Feature = phi(h,P); two RBF blocks
    (semantic block dims 0:2, physics block dims 2:) with separate lengthscales."""
    def __init__(self, n_phys: int, prior_mean_fn=None, sigma_obs=0.1):
        # separable kernel: semantic RBF * physics RBF (anisotropic), + noise
        k_sem  = ConstantKernel(1.0) * RBF(length_scale=[1.0, 1.0])
        k_phys = RBF(length_scale=np.ones(max(n_phys, 1)))
        self.kernel = k_sem * k_phys + WhiteKernel(noise_level=sigma_obs**2)
        self.gp = GaussianProcessRegressor(kernel=self.kernel, normalize_y=False,
                                           n_restarts_optimizer=1, alpha=1e-6)
        self.m = prior_mean_fn or (lambda phi: 0.0)   # literature prior mean m_P(x)
        self.X, self.r = [], []                       # phi rows, RESIDUALS y - m(phi)
        self.fitted = False

    def add(self, phi_row: np.ndarray, y: float):
        self.X.append(phi_row); self.r.append(y - self.m(phi_row))

    def fit(self):
        if len(self.X) >= 2:
            self.gp.fit(np.vstack(self.X), np.asarray(self.r)); self.fitted = True

    def predict(self, phi_row: np.ndarray):
        """Return (mu, sigma2) = literature prior mean + GP residual correction."""
        base = self.m(phi_row)
        if not self.fitted:
            return base, 1.0          # prior-only: mean=literature, unit epistemic var
        mu_r, std_r = self.gp.predict(phi_row[None, :], return_std=True)
        return float(base + mu_r[0]), float(std_r[0] ** 2)

    def mean(self, phi_row): return self.predict(phi_row)[0]
    def var(self,  phi_row): return self.predict(phi_row)[1]
```

`prior_mean_fn` is built by the literature seeder: if a paper reports "yield ≈ f(catalyst)", we fit a cheap 1-D curve and pass it; otherwise a constant equal to the reported value. Before warm-up data exists, `predict` returns the literature mean with unit epistemic variance — exactly the prior-predictive state needed for the fallback ranking (§9).

---

## 4. Information gain + IDS acquisition (`engine/infogain.py`)

This is the quantitative "information gain" the user asked for. `I_t(h)` is **BALD** with the "model" being the principle identity: mixture entropy minus mean component entropy. Selection is PiEvo Eq. 1, with the capability subsystem's `feasibility(h)` folded in so the loop maximizes *info-gain per unit of THIS user's effort*.

```python
# engine/infogain.py
import numpy as np

def _phi_of(h, P, codec, embed_cache):
    from .bridge import phi
    return phi(h.embedding, P.embedding, codec.psi(h.x_target))

def predictive_components(h, P_t, codec):
    """Per-principle Gaussian predictive N(mu_P, s_P^2) for hypothesis h."""
    mus, s2 = [], []
    for P in P_t:
        ph = _phi_of(h, P, codec, None)
        mu, var = P.gp.predict(ph)
        mus.append(mu); s2.append(var + P.gp.gp.kernel_.k2.noise_level if P.gp.fitted else var + 0.01)
    return np.asarray(mus), np.asarray(s2)

def mutual_information(mus, s2, w):
    """I(P ; Y | h) = H[mixture] - sum_P w_P H[component_P]   (BALD).
    Mixture entropy via moment-matching to a single Gaussian (fast upper bound)."""
    H_comp = 0.5 * np.log(2 * np.pi * np.e * s2)
    mu_mix = float(np.sum(w * mus))
    s2_mix = float(np.sum(w * (s2 + mus**2)) - mu_mix**2)
    H_mix  = 0.5 * np.log(2 * np.pi * np.e * max(s2_mix, 1e-12))
    I = H_mix - float(np.sum(w * H_comp))
    return max(I, 0.0), mu_mix

def ids_score(h, P_t, w, codec, sigma_obs, beta=1.0):
    """Eq.1 (cost-aware): argmin Delta^2 / (I^beta * feasibility).
    Returns (score, info_gain, regret, mu_mix); lower score is better."""
    mus, s2 = predictive_components(h, P_t, codec)
    I, mu_mix = mutual_information(mus, s2, w)

    # If principles agree (|P_t|=1 or collapsed I), still reduce GP epistemic uncertainty:
    P_map = P_t[int(np.argmax([p.post_logw for p in P_t]))]
    sig2 = P_map.gp.var(_phi_of(h, P_map, codec, None))
    I += 0.5 * np.log1p(sig2 / (sigma_obs**2 + 1e-12))      # + GP epistemic info (nats)

    return I, mu_mix, s2, mus    # regret computed by caller (needs v* over all candidates)

def select_ids(candidates, P_t, w, codec, sigma_obs, beta=1.0, maximize=True):
    """Full IDS over the candidate pool. Computes v* once, then argmin."""
    rows = []
    for h in candidates:
        I, mu_mix, *_ = ids_score(h, P_t, w, codec, sigma_obs, beta)
        rows.append((h, I, mu_mix))
    mu_all = np.array([mu for _, _, mu in rows])
    v_star = mu_all.max() if maximize else mu_all.min()
    best, best_score = None, np.inf
    for (h, I, mu_mix) in rows:
        Delta = max(abs(v_star - mu_mix), 1e-6)            # expected regret
        score = Delta**2 / (max(I, 1e-9)**beta * max(h.feasibility, 1e-3))
        h.info_gain, h.regret, h.ids_score = I, Delta, score
        if score < best_score:
            best, best_score = h, score
    return best
```

`beta>1` → exploration-heavy (info-greedy, raises diversity/APD); `beta<1` → exploitation (raises AUOC). The CLI exposes `--beta`. `feasibility` defaults to 1.0 so the engine works standalone if the capability subsystem is absent — a clean interface seam.

---

## 5. Posterior update over principles (`engine/posterior.py`)

Log-space Bayes (PiEvo Eq. 4) for numerical stability across many rounds. A principle that predicts observations well gains weight; literature-only principles that mispredict the user's data decay.

```python
# engine/posterior.py
import numpy as np

def gauss_loglik(y, mu, s2):
    return -0.5 * (np.log(2 * np.pi * s2) + (y - mu)**2 / s2)

def recompute_posterior(state, codec, sigma_obs):
    """Eq.4: log p_{t+1}(P) = log p_0(P) + sum_s log N(y_s; mu_P(h_s), sigma_P^2 + sigma_obs^2).
    Each principle is scored against the FULL observation history."""
    from .infogain import _phi_of
    hyp_by_id = {h.id: h for h in state.candidates}
    obs = state.history
    for P in state.P_t:
        ll = 0.0
        for o in obs:
            h = hyp_by_id.get(o.hypothesis_id)
            if h is None:
                continue
            mu, var = P.gp.predict(_phi_of(h, P, codec, None))
            ll += gauss_loglik(o.y, mu, var + max(o.sigma_obs, sigma_obs)**2)
        P.post_logw = P.prior_logw + ll
    return state.weights()

def posterior_entropy(state):
    w = state.weights()
    return float(-np.sum(w * np.log(w + 1e-12)))

def prune(state, w_min=1e-3):
    """Archive (don't hard-delete) principles below the weight floor — the space EVOLVES."""
    w = state.weights()
    keep = [P for P, wi in zip(state.P_t, w) if wi >= w_min or len(state.P_t) <= 2]
    state.P_t = keep
```

---

## 6. Anomaly detection vs surrogate AND literature prior (`engine/anomaly.py`)

The differentiator. Because GP means are literature-seeded (§3), the calibrated residual `S_s` measures published-consensus violation, **not** just a surrogate miss. We compute it against both the generating principle (surrogate) and the literature prior mean explicitly, and take the max so either kind of surprise fires augmentation. The threshold is adaptive (per-round false-positive budget, Bonferroni-style) so more tests ⇒ stricter ⇒ no spurious principle spawns.

```python
# engine/anomaly.py
import numpy as np
from scipy.stats import norm

def calibrated_residual(y, mu, sigma2, sigma_obs):
    z = (y - mu) / np.sqrt(sigma2 + sigma_obs**2 + 1e-12)
    return 1.0 - np.exp(-abs(z)), z                  # S_s in [0,1), Eq.3

def adaptive_theta(n_tests, alpha=0.05):
    z_crit = norm.ppf(1 - alpha / (2 * max(n_tests, 1)))   # Bonferroni
    return 1.0 - np.exp(-z_crit)

def detect(obs, h, P_gen, codec, sigma_obs, n_tests):
    """Score against BOTH the generating principle's surrogate AND its literature prior."""
    from .infogain import _phi_of
    ph = _phi_of(h, P_gen, codec, None)
    mu_surr, var_surr = P_gen.gp.predict(ph)            # surrogate (data-corrected)
    mu_lit = P_gen.gp.m(ph)                             # raw literature prior mean
    S_surr, z_s = calibrated_residual(obs.y, mu_surr, var_surr, sigma_obs)
    S_lit,  z_l = calibrated_residual(obs.y, mu_lit, 1.0, sigma_obs)
    S = max(S_surr, S_lit)
    theta = adaptive_theta(n_tests)
    return {"triggered": S > theta, "S": S, "theta": theta,
            "z_surrogate": z_s, "z_literature": z_l,
            "kind": "literature" if S_lit >= S_surr else "surrogate"}
```

On trigger the Principle Agent (§7) drafts a reconciling principle, it gets a fresh `GPExpert` whose prior mean is fit to the anomalous neighborhood, it's appended to `P_t`, and `recompute_posterior` runs over the enlarged set. **Ingestion itself can trigger this on round 0** — a figure outlier or a sim contradicting a literature claim spawns a novel principle before any experiment runs.

---

## 7. The three agents (`engine/agents/`)

Each agent is a thin LLM call through `engine/router.py:get_llm(role=...)`, which generalizes `agents/llm.py` to a per-role model map (PiEvo lesson c). Strategy layers get **crisp non-reasoning** models; generation/explanation get reasoning models.

| Agent | File | Role / model class | Job |
|---|---|---|---|
| Principle | `principle.py` | `principle` — strongest *cheap* non-reasoning | Seed `P_0` from literature `claims`; draft reconciling principle on anomaly |
| Hypothesis | `hypothesis.py` | `hypothesis` — reasoning | Under MAP principle, emit K candidates (explore+exploit) with `x_target` |
| Experiment | `experiment.py` | `experiment` — non-reasoning + tools | Map chosen `h` → registered tool, run it, return `Observation` |
| Debate | `debate.py` | `debate` — mid + judge non-reasoning | Optimist/skeptic/judge prune candidates before IDS commit |

**Principle Agent** (augmentation) — the only place "creativity" enters the numeric loop:

```python
# engine/agents/principle.py
from ..router import get_llm_json   # call_json bound to a role

def augment(anomaly, violated_principle, neighborhood_obs, round_t) -> dict:
    prompt = f"""A local observation contradicts the current principle.
VIOLATED PRINCIPLE: {violated_principle.text}
ANOMALY: x={anomaly['x']} y={anomaly['y']} (z_vs_literature={anomaly['z_literature']:.2f},
         z_vs_surrogate={anomaly['z_surrogate']:.2f}, kind={anomaly['kind']})
NEARBY HISTORY: {neighborhood_obs}
Draft ONE new principle (NL proposition) that reconciles the published prior with this
surprising local datum. Return JSON: {{"text": "...", "prior_confidence": 0.0-1.0}}"""
    return get_llm_json("principle", prompt,
        system="You write crisp, falsifiable scientific principles. No hedging.")
```

**Hypothesis Agent** reuses the prototype's multi-framing trick (`agents/hypothesis.py`) but now conditions on the MAP principle text and emits `x_target` in the design space, tagging each candidate `explore` or `exploit`.

**Debate** rides directly on `agents/validation.py`'s optimist/skeptic/judge panel — it prunes candidates on feasibility/novelty/testability *before* IDS spends a GP evaluation, satisfying the "agents discuss back-and-forth" requirement.

---

## 8. Experiment tools (`engine/experiments/`)

PiEvo's `pievo/tools/` decorator registry. The Experiment Agent only chooses *which* tool and *what params* — the LLM never emits executable code (params validated against the inferred schema). The locality firewall lives here: any tool whose `touches` includes `network` is refused if input Evidence is `plane="local"`.

```python
# engine/experiments/registry.py
EXPERIMENT_TOOLS = {}
def experiment_tool(name, *, cost, deterministic, touches=("compute",), supports_dry_run=True):
    def deco(fn):
        EXPERIMENT_TOOLS[name] = dict(fn=fn, cost=cost, deterministic=deterministic,
                                      touches=set(touches), dry_run=supports_dry_run)
        return fn
    return deco
```

`builtins.py` ships three domain-agnostic tools — `fit_surrogate` (train cheap RF/GP on local data, predict y at proposed x), `recompute_statistic` (correlation/slope/effect-size on the dataset), `run_simulation` (sandboxed user solver) — plus a `--dry-run` path that draws `y ~ N(GP mean, GP var)` so the loop is fully runnable on a laptop with no solver and no API keys. **Demo-critical.**

---

## 9. The round loop + stopping criteria (`engine/loop.py`)

```python
# engine/loop.py (orchestration sketch)
class DiscoveryEngine:
    def __init__(self, state, codec, cfg):
        self.s, self.codec, self.cfg = state, codec, cfg

    def warmup(self, evidence_quantities):
        # 1. Seed P_0 from literature claims (Principle Agent) -> GPExperts w/ literature mean fns.
        # 2. Convert each ingested Quantity -> warm-up Observation (x=conditions, y=value, sigma).
        # 3. If <5 calibrated points, run fit_surrogate/recompute (or dry-run draws) to quorum.
        # 4. Fit every GP; recompute_posterior; round-0 anomaly check on ingested data.
        ...

    def step(self):
        s = self.s; s.round += 1
        principle.maybe_augment(s)                                 # 1. Principle Agent
        cands = hypothesis.generate(s, k=self.cfg.K)               # 2. Hypothesis Agent
        cands = debate.prune(cands, s)                             # 3. DEBATE
        s.candidates = cands
        h = select_ids(cands, s.P_t, s.weights(), self.codec,      # 4. IDS Eq.1
                        self.cfg.sigma_obs, self.cfg.beta, s.space.maximize)
        obs = experiment.run(h, dry_run=self.cfg.dry_run)          # 5. EXPERIMENT (local plane)
        s.history.append(obs)
        h.parent_principle().gp.add(...); h.parent_principle().gp.fit()
        recompute_posterior(s, self.codec, self.cfg.sigma_obs)     # 6. UPDATE (Eq.4)
        a = anomaly.detect(obs, h, h.parent_principle(), self.codec,# 7. ANOMALY (Eq.3)
                           self.cfg.sigma_obs, n_tests=len(s.history))
        if a["triggered"]:
            principle.spawn(s, a, h); recompute_posterior(...)     #    augment P_t
            s.rounds_since_anomaly = 0
        else:
            s.rounds_since_anomaly += 1
        prune(s)
        self._log_guidance_row(h, obs, a)                          # 8. guidance + persist
        return self._stop()

    def _stop(self):
        s, c = self.s, self.cfg
        max_I = max((h.info_gain or 0) for h in s.candidates)
        H = posterior_entropy(s); s.entropy_trace.append(H)
        return any([
            s.round >= c.max_turn,                                  # budget
            max_I < c.eps_info,                                     # nothing left to learn
            (H < c.eps_H and _stable(s.entropy_trace, c.r)),        # one principle dominates
            (min(s.best_regret_trace[-1:] or [9e9]) < c.eps_reg),   # good-enough found
            (s.rounds_since_anomaly >= c.r and _apd(s) < c.apd_floor)  # exploration saturated
        ])
```

Warm-up defaults to ~5 rounds (PiEvo lesson a), flag-overridable. All `eps_*`, `beta`, `max_turn`, `--dry-run` are CLI flags mirroring PiEvo's `--max_turn 20`. Each round appends a **guidance row** (chosen `h`, `info_gain` in nats, `regret`, what-it-explains = the principle pair it discriminates, difficulty, effort, new posterior-mixture mean) and pickles `WorldState`.

**Fallback mode (no runnable experiment):** the *same* `mutual_information` machinery runs on the literature-seeded priors only — rank `h` by `I_t(h) / cost(h)` (value-of-information per unit effort), emit a static ranked list with identical guidance metadata. When the user later runs an experiment, the same objects flow into the full loop with no rework. This guarantees value with zero compute.

---

## 10. How it stays domain-agnostic

- **No domain logic in the engine.** Principles/hypotheses are text + embedding; the only structured numeric object is `DesignSpace` (continuous + categorical knobs) and `ParamCodec` normalizes it generically. Swap turbulence for genomics by changing only the `DesignSpace` and which experiment tools are registered.
- **Scalar objective contract.** Everything reduces to one scalar `y` per round (PiEvo assumption). Multi-objective domains scalarize upstream (weighted/Chebyshev) before reaching the engine.
- **Embedding bridge** is what lets *any* NL proposition get a GP/Bayesian treatment without hand-built features — the domain enters only through the words the literature/ingestion subsystems already produce.
- **Tools are pluggable** via the decorator; the three builtins (`fit_surrogate`, `recompute_statistic`, `run_simulation`) cover most domains generically, and a hero domain just adds one more registered function.

---

## 11. Interfaces to the other subsystems (the seams)

| Provides | From | Into engine |
|---|---|---|
| `Quantity[]` (x, y, σ) | Ingestion (`Evidence.quantities`) | `warmup()` → warm-up `Observation`s + GP fit |
| `Claim[]` + `knowledge_gaps` | Literature subsystem | Principle Agent → `P_0` + `prior_logw` |
| literature relationship curves | Literature subsystem | `GPExpert.prior_mean_fn` (the literature-seeded mean) |
| `feasibility(h)`, `difficulty`, `effort` | Capability subsystem | folds into `ids_score` denominator + guidance row |
| `get_llm(role=...)` | `engine/router.py` (generalizes `agents/llm.py`) | all four agents |
| `embed()` | `engine/embed.py` (local plane) | every Principle/Hypothesis embedding |

**Build order for the days we have:** (1) `state.py` + `bridge.py` + `embed.py` + `gp.py` — the numeric core, unit-testable with synthetic data; (2) `infogain.py` + `posterior.py` + `anomaly.py` — the math, validated on a toy 1-D function; (3) `experiments/builtins.py` with `--dry-run` so the loop closes on a laptop; (4) wrap the three agents over `router.py`; (5) `loop.py` state machine + stopping; (6) wire feasibility from the capability subsystem last. Each stage is independently demoable, and stage 3 already gives a runnable closed loop.

Key existing files reused: `/Users/abdollahegazy/bnl/aijam/agents/llm.py` (→ `engine/router.py`), `/Users/abdollahegazy/bnl/aijam/agents/validation.py` (→ `engine/agents/debate.py`), `/Users/abdollahegazy/bnl/aijam/agents/hypothesis.py` (→ `engine/agents/hypothesis.py` multi-framing generation).


---

# Hypothesis eval / ranking / debate

# Subsystem Design — Hypothesis Evaluation, Ranking & Multi-Agent Debate

**Module home:** `evaluation/` (new package, sibling to `agents/`, `capability/`, `core/`). It consumes the engine's `Hypothesis`/`info_gain` (from the PiEvo loop, §3 of the math spec), the `CapabilityProfile` (capability subsystem), and the literature `Evidence`/`Claim` store. It produces a single ranked, debated, guidance-annotated `ScoredHypothesis` stream that the REPL prints and that feeds **cost-aware IDS** back into the loop.

It is the salvage-and-upgrade of `agents/validation.py` (the parallel critic panel) — same `call_json` + `ThreadPoolExecutor` pattern, generalized from a flat 4-critic average into a **calibrated 7-axis composite + structured debate**.

```
evaluation/
  score.py        # the 7 sub-scorers + composite combiner + reweighting
  rubrics.py      # frozen rubric text (anchors) for each axis -> prompt + parse
  debate.py       # proponent / skeptic / referee structured dialogue
  record.py       # ScoredHypothesis dataclass + JSON (de)serialization
  present.py      # CLI rendering (ranked table, expand card, debate transcript)
  weights.py      # WeightProfile presets + `/weights` REPL command handler
config/
  scoring.yaml    # default weights, axis on/off, debate budget, model roles
```

---

## 1. The composite score

Every candidate hypothesis `h` gets **seven sub-scores in `[0,1]`**, then a single scalar `V(h)` ("research value per unit effort") that drives both the user-facing ranking and the engine's experiment selection.

| # | Axis | Symbol | Source of truth | Who computes it |
|---|------|--------|-----------------|-----------------|
| i | Expected Information Gain | `I` | engine: `Hypothesis.info_gain` (BALD nats, §3) | numeric, from loop — *not* an LLM |
| ii | Feasibility (equipment-grounded) | `F` | `CapabilityProfile` feasibility block | capability subsystem |
| iii | Difficulty | `D` | profile + test_plan complexity | LLM `eval-difficulty` + cost model |
| iv | Work / Effort | `W` | profile cost rollup (weeks/$/samples) | deterministic rollup |
| v | Explanatory scope | `E` | how many principles `h` discriminates | engine + LLM `eval-explain` |
| vi | Novelty vs literature | `N` | embedding distance + LLM judge | numeric + LLM `eval-novelty` |
| vii | Testability | `T` | falsifiability of test_plan | LLM `eval-testability` |

Two of these (`I`, `W`) are **numbers the system already has** — they are read, not re-judged, which keeps them cheap and trustworthy. Three (`D`, `N`, `E`) are **hybrid**: a numeric prior is computed deterministically, then an LLM nudges it within a clamped band so a hallucinating model can't override hard evidence. Two (`T`, plus the LLM half of `N`) are pure LLM judgments against frozen rubrics.

### 1.1 Sub-score rubrics

Each LLM-scored axis is graded **1–5 against fixed verbal anchors** (anchored rating scales beat free-form 0–1 — far better inter-call consistency), then mapped to `[0,1]` via `(s-1)/4`. Anchors live in `rubrics.py` and are injected verbatim into the prompt.

**(i) Information Gain `I`** — *not graded by an LLM.* Taken directly from `Hypothesis.info_gain` (the IDS `I_t(h)` = mixture entropy − mean component entropy + GP epistemic term, in nats). Normalized across the current candidate set with a robust min-max:
```
I = (info_gain - p05) / (p95 - p05)   clipped to [0,1]   # p05/p95 over live candidates
```
In literature-only fallback mode it's the prior-predictive BALD value (§7 of the math spec). This is the load-bearing "quantitative information gain" number the user asked for; everything else is feasibility/quality shaping around it.

**(ii) Feasibility `F`** — read from the capability subsystem's `feasibility` field (already `0..1`, computed as `Σ_c w(status_c)·confidence_c / N`). Pass-through. If the profile is missing (no institution found), `F = 0.5` (neutral) and the record is flagged `feasibility_assumed`.

**(iii) Difficulty `D`** (we store and rank by **ease = 1 − difficulty**, so higher is better everywhere):

| Anchor | Difficulty | Meaning |
|---|---|---|
| 1 | very easy | one in-house instrument, standard protocol, <1 day setup |
| 2 | easy | in-house but multi-step or needs mild calibration |
| 3 | moderate | shared facility booking OR new analysis pipeline |
| 4 | hard | beamtime/queue + nontrivial sample prep + expertise stretch |
| 5 | very hard | needs acquisition, external partner, or capability the lab lacks |

Numeric prior from the profile (`#missing caps`, `max access_effort`, `sample/measurement count` parsed from `test_plan`); LLM may adjust ±1 anchor with justification. `D_score = 1 − (difficulty−1)/4`.

**(iv) Work/Effort `W`** — deterministic rollup from the capability `cost` blocks (no LLM): `work_weeks = Σ_steps effort_step · access_multiplier(status)` (in_house ×1, shared ×1.5+lead, collaborator ×3, acquirable ×6). Plus `samples` and `money_usd`. Mapped to a score with a saturating curve so "2 weeks vs 3 weeks" matters but "40 vs 41 weeks" doesn't:
```
W = exp(-work_weeks / TAU)            # TAU default 8 weeks, configurable
```

**(v) Explanatory scope `E`** — "what would this actually explain?" Two signals combined: (a) **numeric** — how many active principles in `P_t` the experiment discriminates, i.e. the count/weight of principles whose predicted `y|h` disagree (directly from the IDS mixture); (b) **LLM** breadth judgment:

| Anchor | Scope | Meaning |
|---|---|---|
| 1 | trivial | confirms one already-believed point; explains nothing new |
| 2 | local | resolves a single narrow parameter |
| 3 | mechanistic | discriminates between two competing principles |
| 4 | unifying | reconciles a literature claim with local-data anomaly |
| 5 | foundational | would force a new principle / overturn a consensus |

`E = 0.5·(num_term) + 0.5·(anchor_term)`. The LLM is also asked to emit a one-sentence `what_it_explains` string (surfaced to the user) and the list of `discriminated_principle_ids`.

**(vi) Novelty `N`** — hybrid, to defuse the LLM's tendency to call everything novel:
```
N_embed = min over retrieved literature of  ‖e_h − e_paper‖   (cosine distance, reuse ingest embeddings)
```
mapped so "far from all prior work" → high. LLM `eval-novelty` grades 1–5 against:

| Anchor | Novelty | Meaning |
|---|---|---|
| 1 | known | directly answered by a retrieved paper |
| 2 | incremental | obvious extension of cited work |
| 3 | gap-filling | targets a stated literature gap |
| 4 | contrarian | predicts against the established finding |
| 5 | unexplored | no adjacent prior work; opens a direction |

`N = clamp(0.5·N_embed + 0.5·anchor, N_embed−0.2, N_embed+0.2)` — the embedding number is the spine; the LLM may only flex it ±0.2.

**(vii) Testability `T`** — pure rubric judgment of the `test_plan` + `predicted_outcome`:

| Anchor | Testability | Meaning |
|---|---|---|
| 1 | unfalsifiable | no measurable outcome, vague variables |
| 2 | weak | outcome stated but no concrete method |
| 3 | adequate | falsifiable claim + a runnable method |
| 4 | strong | operationalized variables, specified Δ/threshold, controls |
| 5 | decisive | pre-registerable, clear pass/fail, power/noise considered |

### 1.2 How they combine

The composite is a **weighted geometric-ish blend** with a hard gate. We use a multiplicative gate on the two "veto" axes (feasibility and testability) and a weighted sum on the rest — so a beautiful, high-info hypothesis you physically cannot run, or cannot falsify, is correctly killed rather than averaged into the middle:

```
quality   = w_I·I + w_E·E + w_N·N + w_D·D_score + w_W·W      # research-merit block
gate      = F^γ_F · T^γ_T                                     # feasibility & testability veto
V(h)      = gate · quality                                    # composite, 0..1
```

Defaults (`config/scoring.yaml`):
```yaml
weights:   { I: 0.34, E: 0.18, N: 0.18, D: 0.15, W: 0.15 }   # sum to 1.0 over the merit block
gates:     { F: 1.0,  T: 0.7 }                                # exponents γ; F is a hard veto, T softer
explore_beta: 1.0      # >1 info-greedy (diversity/APD), <1 exploit (efficiency/AUOC)
```
The `I` term is additionally raised to `explore_beta` *before* the sum (`I**explore_beta`) so the same explore/exploit knob from the engine's IDS is honored here — exploration mode upweights info, exploitation mode flattens it.

**Tie-break / ranking key:** sort by `V(h)` desc; ties broken by raw `info_gain` desc, then by `W` (cheaper first).

### 1.3 The bridge back to the engine (cost-aware IDS)

The user-facing ranking and the engine's *next-experiment* choice are the **same objective**, expressed two ways. The engine selects via the math spec's cost-aware IDS:
```
h_t = argmin_h  Δ_t(h)² / ( I_t(h) · F(h) )
```
We expose a single function so both live in one place:

```python
# evaluation/score.py
def selection_score(rec: "ScoredHypothesis", *, mode="ids") -> float:
    """mode='ids' -> engine's argmin Δ²/(I·F); mode='value' -> user-facing V(h) (higher=better)."""
    if mode == "ids":
        I = max(rec.subscores["I_raw"], 1e-9)
        return (rec.regret ** 2) / (I * max(rec.subscores["F"], 1e-3))
    return rec.composite   # V(h)
```
Same inputs, no divergence between "what the loop runs" and "what the user is told is best."

### 1.4 User reweighting

`weights.py` ships named presets and a live REPL command:

```
hypoforge> /weights show
hypoforge> /weights set I=0.5 N=0.1            # renormalizes the merit block, re-ranks instantly
hypoforge> /weights preset cheap_wins          # high W + F, low I  → "what can I knock out fast?"
hypoforge> /weights preset moonshot            # high I + N, low W   → "what's most informative, cost be damned"
hypoforge> /weights gate F=2.0                 # make feasibility an even harder veto
```

Presets in `config/scoring.yaml`:
```yaml
presets:
  balanced:   { I: 0.34, E: 0.18, N: 0.18, D: 0.15, W: 0.15 }
  cheap_wins: { I: 0.15, E: 0.10, N: 0.10, D: 0.30, W: 0.35 }
  moonshot:   { I: 0.45, E: 0.20, N: 0.25, D: 0.05, W: 0.05 }
  novelty:    { I: 0.25, E: 0.15, N: 0.40, D: 0.10, W: 0.10 }
```
Reweighting **never re-calls the LLM** — sub-scores are cached on the record, so `/weights` re-ranks in microseconds. This is what makes the CLI feel live.

---

## 2. The debate mechanism

Ranking by score is necessary but not sufficient — the user explicitly wants agents to **argue back and forth before committing**. Debate runs on the **top-K** candidates (default K=3, the ones about to be committed to the loop or shown as "recommended"), *not* every hypothesis (cost control). It's the upgrade of `validation.py`'s static critic panel into a real adversarial dialogue with a deciding referee.

### 2.1 Roles (three agents, PiEvo model-routing aware)

| Role | Model role (router) | Mandate |
|---|---|---|
| **Proponent** (blue) | `debate-proponent` — reasoning model, temp 0.7 | Argue the hypothesis is worth running: maximize `I·E·N`, defend testability, name the cheapest viable path from the profile. |
| **Skeptic** (red) | `debate-skeptic` — reasoning model, temp 0.7 | Attack: hidden confounds, the test won't falsify, novelty is illusory (cite the near-neighbor paper), feasibility blockers (calibration, beamtime queue, expertise gap). |
| **Referee** | `debate-referee` — **crisp non-reasoning** model, temp 0.2 | Adjudicate per turn, decide when settled, emit the committed sub-score *adjustments* + a one-line rationale. |

The split is the PiEvo lesson (c) in action: **divergent reasoning models generate the arguments; a crisp non-reasoning model makes the strategic call** ("think-mode hurts the utility layer −26%"). The referee is the only agent allowed to move a score.

### 2.2 Turn structure (what each turn argues)

A debate is a bounded transcript of typed turns. Each turn targets **specific axes** so the argument is grounded, not vibes:

```
Round 1  PROPONENT  : opening case  -> claims on (I, E, N, T) with evidence locators
Round 1  SKEPTIC    : rebuttal      -> attacks the weakest 2 axes + a feasibility blocker (F/D/W)
Round 1  REFEREE    : interim ruling -> per-axis "leaning" + flags unresolved cruxes
Round 2  PROPONENT  : answers the cruxes only (concede or defend, no new scope)
Round 2  SKEPTIC    : final objections / concedes
Round 2  REFEREE    : verdict + score deltas
```

Each non-referee turn is a `call_json` returning:
```json
{ "axis_claims": [{"axis":"N","direction":"up","argument":"...","evidence":"paper:S2#abc / df.corr / fig3.b"}],
  "concedes": ["T"],                       // axes this side gives up
  "crux": "Does the proposed control actually remove the temperature confound?",
  "feasibility_note": "11-BM beamtime lead 12wk pushes work_weeks to 14" }
```
The referee turn returns score deltas clamped to ±1 anchor per axis so a single rhetorical flourish can't swing a score wildly:
```json
{ "deltas": {"N": -0.15, "T": +0.10}, "unresolved": ["confound"],
  "ruling": "Novelty overstated (near-neighbor S2#abc exists); testability improved by added control.",
  "settled": false }
```

### 2.3 Termination rule

Debate stops at the **first** of:
1. **Referee declares settled** — `settled: true` AND no `unresolved` cruxes.
2. **Score convergence** — the candidate's composite `V(h)` changed `< ε_debate` (default 0.02) between consecutive referee rulings.
3. **Max rounds** — `debate_max_rounds` (default 2) reached; referee forced to commit.
4. **Concession** — either side concedes all contested axes.

This guarantees ≤ `2·(2+1) = 6` LLM calls per debated hypothesis, ≤ ~18 for the default top-3 — cheap enough to run every loop iteration.

```python
# evaluation/debate.py  (skeleton, reuses agents/llm.call_json)
def debate(rec, ctx, max_rounds=2, eps=0.02) -> DebateResult:
    transcript, prev_V = [], rec.composite
    for r in range(1, max_rounds + 1):
        pro  = _turn("proponent", rec, ctx, transcript)
        skep = _turn("skeptic",   rec, ctx, transcript)
        rule = _referee(rec, ctx, transcript + [pro, skep])
        transcript += [pro, skep, rule]
        rec = apply_deltas(rec, rule["deltas"])      # re-runs §1.2 combiner -> new composite
        if rule["settled"] and not rule["unresolved"]:        break
        if abs(rec.composite - prev_V) < eps:                 break
        prev_V = rec.composite
    return DebateResult(final=rec, transcript=transcript,
                        confidence=_referee_confidence(transcript),
                        unresolved=rule.get("unresolved", []))
```

### 2.4 How the transcript reaches the user

Debate output is stored on the record (§3) and surfaced three ways, escalating in verbosity:

- **Inline badge** in the ranked table: `⚖ committed` / `⚖ contested` / `⚖ split` + a `Δ` showing how much debate moved the score.
- **`/why H3`** prints the referee's `ruling` lines (the executive summary) + the single unresolved crux, if any.
- **`/debate H3`** prints the full color-coded transcript (proponent blue, skeptic red, referee bold) so the user can audit the reasoning — the "discuss back-and-forth" made visible.

---

## 3. The hypothesis record schema

`evaluation/record.py`. This is the superset object — it extends the prototype's hypothesis dict (`agents/hypothesis.py`) and the engine's `Hypothesis` dataclass, carrying everything the loop, the ranker, and the CLI need. JSON-serializable for the on-disk `WorldState` so the REPL can resume.

```python
# evaluation/record.py
from dataclasses import dataclass, field

@dataclass
class SubScores:
    I: float; F: float; D_score: float; W: float; E: float; N: float; T: float
    I_raw: float            # nats, pre-normalization (for IDS bridge)
    difficulty_1_5: int     # raw anchor, for display
    work_weeks: float; samples: int; money_usd: float
    novelty_embed: float    # the embedding-distance spine

@dataclass
class DebateTurn:
    role: str               # proponent | skeptic | referee
    round: int
    content: dict           # the JSON payload from §2.2

@dataclass
class ScoredHypothesis:
    # ---- identity & content (from agents/hypothesis.py, verbatim keys) ----
    id: str                                  # "H3"
    title: str; statement: str; rationale: str
    knowledge_gap_addressed: str; data_grounding: str
    test_plan: str; required_data: str
    predicted_outcome: str; novelty_basis: str
    framing: str                             # mechanistic | predictive | ...
    # ---- engine linkage (PiEvo loop) ----
    parent_principle_id: str
    x_target: dict                           # point in design space X
    mode: str                                # explore | exploit
    info_gain: float                         # I_t(h), nats
    regret: float                            # Δ_t(h)
    discriminated_principle_ids: list[str]   # what it would explain (numeric side of E)
    # ---- evaluation outputs ----
    subscores: SubScores
    composite: float                         # V(h), 0..1  (the rank key)
    rank: int | None = None
    # ---- guidance block (the user's explicit ask) ----
    what_it_explains: str = ""               # one-sentence, LLM (E axis)
    you_already_have: list[str] = field(default_factory=list)   # from profile
    missing: list[dict] = field(default_factory=list)           # [{cap, cheapest_path, cost_usd, lead_weeks}]
    cheapest_path: str = ""
    caveats: list[str] = field(default_factory=list)            # e.g. "ranking influenced by semantic proxy"
    # ---- debate ----
    debate_transcript: list[DebateTurn] = field(default_factory=list)
    debate_verdict: str = "undebated"        # committed | contested | split | undebated
    debate_confidence: float = 0.0
    unresolved_cruxes: list[str] = field(default_factory=list)
    # ---- provenance / flags ----
    flags: list[str] = field(default_factory=list)   # feasibility_assumed, literature_proxy, ...
    scored_by: dict = field(default_factory=dict)    # {axis: model_id}  (router audit)
```

The `caveats`/`flags` lists carry the math-spec's soundness warnings automatically — e.g. any hypothesis whose `info_gain` was driven by `source="literature"` likelihoods gets `flags += ["literature_proxy"]` and a standing caveat string, so the CLI can print *"ranking influenced by semantic proxy, not measured outcomes — verify experimentally."*

---

## 4. CLI presentation

Claude-Code-style: a dense ranked table by default, drill-down on demand, live re-rank on `/weights`.

### 4.1 The ranked board (`/rank`, auto-printed each loop round)

```
HypoForge · round 7 · profile: Soft Matter Group @ BNL (national_lab) · weights: balanced

  #  ID   HYPOTHESIS                              V    info  feas  diff  work    novel  ⚖
 ─────────────────────────────────────────────────────────────────────────────────────
  1  H3   GISAXS–rheology coupling sets domain   0.81  1.9n  0.92  ●●○   6wk    ●●●●○  committed  ▲0.06
            spacing in BCP thin films
  2  H7   Shear rate shifts order-disorder       0.74  2.4n  0.78  ●●●   9wk    ●●●○○  contested  ▼0.04
            transition T_odt by >5K
  3  H1   Solvent-anneal time saturates grain    0.69  0.8n  0.95  ●○○   2wk    ●●○○○  committed  ─
            size above ~30 min
  4  H9   Substrate stiffness controls defect    0.41  3.1n  0.30  ●●●●  26wk*  ●●●●● split      ▼0.18
            density  ⚠ needs cryo-EM (infeasible here)
 ─────────────────────────────────────────────────────────────────────────────────────
  ★ NEXT EXPERIMENT (cost-aware IDS): H3  — highest info-gain-per-effort you can run on your bench.
  H9 has the most raw info (3.1n) but is demoted: requires cryo-EM (not in your profile, ~$5M / 26wk).

  /why H3 · /debate H7 · /card H3 · /weights preset moonshot · /run H3 · /forget
```

`info` is the literal nats (the quantitative info-gain the user wanted); `diff`/`novel` are 3- and 5-dot glyphs; `work` shows weeks (`*` = needs acquisition); `⚖` is the debate verdict with the score delta debate produced.

### 4.2 The guidance card (`/card H3`)

```
H3 · GISAXS–rheology coupling sets domain spacing in BCP thin films        V = 0.81  (rank 1)
 ────────────────────────────────────────────────────────────────────────────────────────
 STATEMENT   Increasing shear rate 0.1→10 s⁻¹ during casting shifts equilibrium domain
             spacing d₀ by >8%, measurable by in-situ GISAXS.
 EXPLAINS    Quantifies the unmodeled GISAXS–rheology coupling (literature gap G2); would
             discriminate principle P2 (flow-aligned) vs P5 (thermodynamic-only).         [E ●●●●○]
 INFO GAIN   1.9 nats  — principles P2 and P5 disagree sharply on the outcome here.        [I ●●●●○]
 ────────────────────────────────────────────────────────────────────────────────────────
 FEASIBILITY 0.92 — you can run this.                                                      [F ●●●●●]
   you have    GISAXS via NSLS-II 11-BM (CMS) · benchtop rheometer (in-house)
   missing     none
   path        Run on existing NSLS-II beamtime; no purchase needed.
 DIFFICULTY  2 / 5 (easy)   ·   WORK  ~6 weeks  (12wk beamtime lead, ×1.5 shared-facility)  [D ●●○]
   samples ~12 films · cost $0 · expertise on hand
 NOVELTY     gap-filling (4/5); nearest prior work is 0.34 away (Chen 2024, no shear).     [N ●●●●○]
 TESTABILITY decisive (5/5): pre-registerable, clear >8% threshold, controls specified.    [T ●●●●●]
 ────────────────────────────────────────────────────────────────────────────────────────
 ⚖ DEBATE  committed (confidence 0.86, moved V +0.06)
   referee: "Novelty held up — shear-coupled GISAXS unreported; skeptic's confound (thermal
             drift) addressed by proponent's isothermal-stage control. Feasibility uncontested."
   unresolved: none                                                       (/debate H3 for full)
 ────────────────────────────────────────────────────────────────────────────────────────
 ⚐ no caveats.        /run H3  to execute · /weights to re-rank · /skip H3
```

### 4.3 Debate transcript (`/debate H7`)

```
⚖ H7 · "Shear rate shifts T_odt by >5K"   —  CONTESTED  (V 0.74, debate moved ▼0.04)

 R1 ▌PROPONENT   N↑ "no paper couples shear to T_odt directly" (gap G4) · T↑ "DSC + rheo-SAXS gives
                 clean >5K threshold" · crux: none
 R1 ▌SKEPTIC     N↓ "Lopez 2023 reports shear-thinning near T_odt — partial overlap (S2#9f2)"
                 F↓ "rheo-SAXS cell needs recommission, +3wk" · crux: "Is >5K resolvable above DSC noise?"
 R1 ▌REFEREE     deltas N −0.12, W −0.05 · ruling: "Novelty partial, not unexplored. Resolution crux
                 stands." · settled: false · unresolved: [DSC-noise]
 R2 ▌PROPONENT   concedes N · T↑ "use modulated-DSC, σ≈1.5K ≪ 5K → resolvable"
 R2 ▌SKEPTIC     concedes DSC-noise · "fine, but 9wk total"
 R2 ▌REFEREE     deltas T +0.08 · ruling: "Crux resolved; novelty incremental-to-gap-filling.
                 Commit." · settled: true

 NET: novelty downgraded (overlap with Lopez 2023), testability upgraded. Worth running but
      H3 dominates on feasibility-adjusted info-gain.
```

---

## 5. Build order (hackathon, days)

1. **`record.py` + `score.py` numeric core** — read `info_gain`, `F`, `work_weeks` straight from the engine + profile; compute `V(h)`; sort. Wire into the existing `validation.py` call site. *(Half a day — gives a real ranked board immediately, even before LLM axes.)*
2. **`rubrics.py` + the 3 hybrid/LLM axes** (`D`, `N`, `T`, `E`) — parallel `call_json` exactly like `validate_all`'s `ThreadPoolExecutor`. Reuse `_extract_json` robustness + the `_MockLLM` so it runs keyless for the demo.
3. **`present.py`** — the ranked board + `/card` (text glyphs, no deps). Biggest demo wow-per-hour.
4. **`weights.py` + `/weights`** — instant re-rank from cached sub-scores. Cheap, very impressive live.
5. **`debate.py`** — proponent/skeptic/referee on top-3, `/debate` + `/why`. Last, because the board is already compelling; debate is the credibility upgrade.

**Answer to the framing question:** yes — and this subsystem is where "a pile of hypotheses" becomes *"here is the single experiment you should run next, why it's worth more than the flashier one, exactly what it costs *you*, and the argument our own agents had before recommending it."* The composite score makes the ranking defensible; the debate makes it trustworthy; the same objective that ranks for the user also drives the closed loop's next move — no gap between what the tool says and what it does.


---

# Experiment executor + privacy planes

I've grounded enough in the existing code (`tools/lit_apis.py` etiquette, `agents/llm.py` mock-fallback pattern, `parsers/registry.py` `ParseResult`). Here is the subsystem design.

---

# Subsystem: Experiment Executor + Data/Privacy Planes

**Owns two things that the rest of HypoForge depends on:**
1. **The Experiment Executor** — the pluggable tool registry the *Experiment Agent* calls to actually *run* a hypothesis (surrogate fit, numeric sim, scripted stat, optional external binary) and get back a structured `Observation(y, σ)` that feeds the GP update + IDS loop (research Eq.1/Eq.3).
2. **The two-data-plane firewall** — raw local experimental data *never* leaves the machine; only field/institution metadata goes out for profiling. Enforced in code, surfaced in the REPL.

These two are deliberately the *same* subsystem: the executor is exactly where exfiltration could happen (a tool could `requests.post` your CSV), so the plane guard lives at the tool dispatch boundary.

Proposed new layout (mirrors PiEvo's `tools/` decorator style; reuses prototype files noted inline):

```
experiment/
  registry.py      # @experiment_tool decorator, EXPERIMENT_TOOLS, ExperimentTool
  observation.py   # Observation dataclass + scalarize() helpers
  schema.py        # infer_schema(): signature/annotations -> ParamSpec + bounds validation
  runner.py        # Experiment Agent entrypoint: validate -> guard -> sandbox -> Observation
  sandbox.py       # subprocess + rlimit + timeout (+ docker --network=none if present)
  dryrun.py        # posterior-draw fallback so the loop always demos
  tools/
    __init__.py    # importing this registers all builtins (decorator side-effects)
    generic.py     # fit_surrogate, recompute_statistic, eval_model   (domain-agnostic)
    softmatter.py  # HERO domain: scft_domain_spacing, cahn_hilliard_coarsening, saxs_peak
planes/
  guard.py         # PlaneGuard: the locality firewall + outbound allowlist tripwire
  manifest.py      # PlaneManifest: per-run audit of what stayed local vs hit the network
  fingerprint.py   # cheap local-data fingerprints for the redaction tripwire
config/
  experiment.yaml  # per-tool cost/timeout caps, sandbox backend, dry_run default
```

---

## 1. The Observation schema (`experiment/observation.py`)

Every tool returns exactly this. It is the single currency the Bayesian engine consumes — `y` + `sigma_obs` map straight onto the GP update and the anomaly denominator `σ²(h)+σ_obs²` (research §2/§4).

```python
# experiment/observation.py
from dataclasses import dataclass, field
from typing import Any, Literal

Source = Literal["surrogate", "sim", "compute", "external_bin", "dry_run", "literature"]

@dataclass
class Observation:
    y: float                      # the scalar objective the GP models (REQUIRED)
    sigma_obs: float = 0.0        # 1-std measurement/sim noise -> Eq.3 denominator
    source: Source = "compute"
    aux: dict = field(default_factory=dict)   # extra scalars, arrays, plot paths
    cost_spent: float = 0.0       # actual compute-$ / seconds, for cost-aware IDS
    dry_run: bool = False
    seed: int | None = None       # set for deterministic tools (reproducible warm-up)
    plane: Literal["local", "web"] = "local"   # provenance of the data it touched
    notes: list[str] = field(default_factory=list)
    error: str | None = None      # set instead of raising -> loop never dies (registry.py ethos)
```

**Scalarization helper** (research §2: "objective must reduce to a single scalar"). Multi-output tools call this so they still return one `y`:

```python
def scalarize(outputs: dict, weights: dict | None = None,
              method: Literal["weighted", "chebyshev"] = "weighted") -> tuple[float, float]:
    """dict of {metric: (value, sigma)} -> (y, sigma_obs). Default: equal-weighted sum."""
```

**Why `error` instead of raising:** the prototype's `registry.parse_file` wraps every parser so a bad file never crashes the pipeline. The executor inherits that contract — a tool that blows up returns `Observation(y=nan, error=...)`, the runner logs it, the loop skips that round. Robustness over purity for a hackathon.

---

## 2. The tool-registration interface (`experiment/registry.py`)

A decorator, exactly mirroring PiEvo's `pievo/tools/` registry pattern. The LLM **never emits executable code** — it only chooses *which* registered tool and *what params*, and params are validated against an inferred schema before dispatch (same principle as the prototype's "LLM never writes code" viz design).

```python
# experiment/registry.py
from dataclasses import dataclass, field
from typing import Callable, Literal
from .schema import infer_schema, ParamSpec

Touch = Literal["compute", "local_data", "network"]

@dataclass
class ExperimentTool:
    name: str
    fn: Callable                  # (params: dict) -> Observation
    cost: float                   # nominal cost unit (drives cost-aware IDS denominator)
    deterministic: bool           # True -> seed fixed, reproducible warm-up points
    touches: set[Touch]           # what data planes it may read  <-- firewall input
    supports_dry_run: bool
    domain: str
    timeout_s: float
    schema: dict[str, ParamSpec]  # param name -> {type, bounds, default}, inferred from signature

EXPERIMENT_TOOLS: dict[str, ExperimentTool] = {}

def experiment_tool(name, *, cost, deterministic, touches=("compute",),
                    supports_dry_run=True, domain="generic", timeout_s=30.0):
    def deco(fn):
        EXPERIMENT_TOOLS[name] = ExperimentTool(
            name=name, fn=fn, cost=cost, deterministic=deterministic,
            touches=set(touches), supports_dry_run=supports_dry_run,
            domain=domain, timeout_s=timeout_s, schema=infer_schema(fn))
        return fn
    return deco
```

`infer_schema` (`experiment/schema.py`) reads the function signature + type annotations + a small convention (`Annotated[float, Bounds(0, 1)]`) to build a `ParamSpec` per argument. The runner validates the LLM-proposed `x_target` dict against these bounds and **rejects out-of-range params** before any code runs — no `eval`, no surprise inputs.

**What the Experiment Agent sees:** a compact catalog (`name`, one-line doc, `schema`, `cost`, `touches`, `domain`) injected into its prompt. It returns `{"tool": "...", "params": {...}}`; the runner does the rest.

---

## 3. The runner — dispatch path with the firewall inline (`experiment/runner.py`)

This is the single chokepoint. **Every** experiment goes through here, so the plane guard is unavoidable.

```python
# experiment/runner.py
def run_experiment(tool_name: str, params: dict, *, evidence_planes: set[str],
                   dry_run: bool, manifest: "PlaneManifest") -> Observation:
    tool = EXPERIMENT_TOOLS[tool_name]

    # 1. validate params against inferred schema bounds (no eval, no injection)
    ok, fixed, errs = validate_params(params, tool.schema)
    if not ok:
        return Observation(y=float("nan"), error=f"bad params: {errs}")

    # 2. THE FIREWALL (planes/guard.py) — refuse exfiltration BEFORE running
    PlaneGuard.check(tool, evidence_planes, manifest)   # raises PlaneViolation -> caught below

    # 3. global dry-run OR no real backend -> simulated observation
    if dry_run or not tool_runnable(tool):
        return dryrun.draw(tool, params)                # source="dry_run"

    # 4. sandboxed execution (subprocess/rlimit/timeout/container)
    try:
        obs = sandbox.run(tool, fixed, timeout_s=tool.timeout_s)
    except SandboxTimeout as e:
        return Observation(y=float("nan"), error=f"timeout {tool.timeout_s}s")
    obs.cost_spent = obs.cost_spent or tool.cost
    manifest.record(tool, obs)
    return obs
```

---

## 4. The two-data-plane firewall (`planes/`)

This is the *defensible* part for the judges. Two planes, separated **structurally**, not by convention.

| | LOCAL plane | WEB plane |
|---|---|---|
| Contents | raw experimental files (prototype `parsers/` output, `Evidence.plane=="local"`) | identity/field metadata only (name, lab, field, public URLs) |
| Network | **never** | search/crawl public pages (reuses `lit_apis` etiquette) |
| To the LLM | only *derived* scalars/summaries, opt-in; never raw rows | metadata + fetched public text |

### 4a. `PlaneGuard.check` — the rule, enforced at dispatch

```python
# planes/guard.py
class PlaneViolation(Exception): ...

class PlaneGuard:
    @staticmethod
    def check(tool: ExperimentTool, evidence_planes: set[str], manifest):
        # RULE 1: a tool that touches local_data may NOT also touch network.
        if "network" in tool.touches and "local_data" in tool.touches:
            raise PlaneViolation(f"{tool.name} mixes local_data + network")
        # RULE 2: if ANY input evidence is local, refuse a network-touching tool outright.
        if "network" in tool.touches and "local" in evidence_planes:
            raise PlaneViolation(
                f"{tool.name} wants network while local data is in scope — refused")
        # RULE 3: local_data tools run with network HARD-disabled in the sandbox.
        if "local_data" in tool.touches:
            manifest.require_network_off(tool.name)
```

Enforcement has **three layers** so a single bug can't leak data:
1. **Type-structural:** discovery/crawl functions (`capability/*`, the WEB plane) accept only `IdentityHints`/`Identity` dataclasses — they are *structurally incapable* of receiving a `ParseResult`/local `Evidence` object. The function signatures make exfiltration a type error.
2. **Dispatch guard:** `PlaneGuard.check` above, rules 1–3.
3. **Sandbox network kill:** `local_data` tools execute with network actually removed (`docker run --network=none`, or in the bare-subprocess fallback, env scrubbed + a `socket` guard that raises on connect). Belt and suspenders: even a malicious registered tool *cannot* open a socket.

### 4b. Redaction tripwire (`planes/fingerprint.py`)

For the outbound WEB plane (profiling queries), a final guard scans any string heading to the network against cheap fingerprints of the local data (column names, a few sampled cell values, file checksums). Overlap → the request is refused and flagged. This catches the subtle case where the LLM tries to paste a local value into a search query.

```python
def scan_outbound(payload: str, fp: LocalFingerprint) -> list[str]:
    """Return list of leaked tokens (column names / sampled values) found in payload."""
```

### 4c. What the user sees (the Claude-Code feel) — `planes/manifest.py`

Every run accumulates a `PlaneManifest`, printed in the REPL so the boundary is *visible*, not just claimed:

```
hypoforge> /run h_07
  experiment: scft_domain_spacing  (touches: compute, local_data)
  plane:      LOCAL  ·  network: OFF (hard-disabled in sandbox)
  data read:  ./local_data/anneal_sweep.csv  (stayed on disk, 0 bytes sent)
  → y = 38.4 nm   σ_obs = 1.2   cost = 0.1   [sim, seed=42]

hypoforge> /planes
  LOCAL  : 3 files read, 0 bytes left the machine
  WEB    : 9 pages fetched (bnl.gov, openalex.org, ror.org) — metadata only
  audit  : planes/cache/run_<id>/manifest.json   ·   /forget wipes it
```

`/forget` wipes `planes/cache/` and `capability/cache/`. The manifest JSON is the auditable proof for the "judge one-liner": *we profile the lab, never the data.*

---

## 5. The sandbox (`experiment/sandbox.py`)

Tiered, degrades gracefully (same philosophy as the LLM mock fallback in `agents/llm.py` — always runs):

```
Tier A (preferred): docker run --network=none --read-only \
                      -v <workspace>:/work:rw --memory=512m --cpus=1 \
                      --pids-limit=64  <runner-image>   # full isolation
Tier B (no docker): subprocess in a per-run workspace dir with:
                      - resource.setrlimit(RLIMIT_AS, mem_cap)   # memory
                      - resource.setrlimit(RLIMIT_CPU, cpu_cap)
                      - wall-clock timeout via SIGALRM / proc.kill()
                      - cwd pinned to workspace; no writes outside
                      - env scrubbed; socket guard raises on connect (network kill)
Tier C (pure-python builtins): run in-process but ONLY for trusted registered
                      tools with no file/network touch (e.g. eval_model on a fitted GP)
```

Key invariants:
- **No `eval` of LLM output.** Tools are pre-registered Python. The LLM picks the tool + params; params are bounds-checked. External *binaries* (a user's solver) run only in Tier A/B with network off and a workspace jail.
- **Determinism:** `deterministic=True` tools get a fixed `seed` injected → reproducible warm-up points (research §2/§5a, the ~5 warm-up rounds).
- **Cost caps** from `config/experiment.yaml` (`timeout_s`, `mem_mb`, `max_cost`) so a runaway sim can't hang the demo.

---

## 6. Dry-run / simulated fallback (`experiment/dryrun.py`) — demo-critical

Mirrors PiEvo's "evaluate on high-fidelity **surrogates**, never wet-lab" lesson and the prototype's `_MockLLM`. With `--dry-run` (or when no solver/key is present) the loop is **fully runnable on a laptop with zero setup** — essential for the live demo.

A dry-run observation is *not* random noise; it's drawn from the **current GP posterior** so the loop still "learns" and the IDS curve still bends:

```python
# experiment/dryrun.py
def draw(tool, params, world_state=None) -> Observation:
    """Plausible Observation without real compute.
       Priority: (1) sample current posterior-mixture at x_target (loop keeps learning),
                 (2) else a cached surrogate prediction,
                 (3) else the tool's analytic toy-model (each hero tool ships one)."""
    mu, sigma = posterior_predict(world_state, params) if world_state else tool_toy(tool, params)
    y = mu + np.random.default_rng(_seed(params)).normal(0, sigma)
    return Observation(y=float(y), sigma_obs=float(sigma), source="dry_run",
                       dry_run=True, notes=["DRY RUN — no real experiment executed"])
```

The REPL clearly banners dry-run rows so nobody mistakes them for real data (parallel to the prototype's mock-LLM UI banner).

---

## 7. Concrete hero-domain tools (`experiment/tools/softmatter.py`)

Hero domain = **soft-matter / block-copolymer thin films** (the BNL Soft Matter / GISAXS user from the capability-profiling design). All three are pure-Python, run in seconds on a laptop, and return real numeric `y`. Domain-agnostic generics live in `generic.py`; these are the *polished* demo tools.

```python
# experiment/tools/softmatter.py
import numpy as np
from typing import Annotated
from ..registry import experiment_tool
from ..observation import Observation
from ..schema import Bounds

@experiment_tool("scft_domain_spacing", cost=0.2, deterministic=True,
                 touches=("compute",), domain="soft_matter", timeout_s=20)
def scft_domain_spacing(
    chi_N: Annotated[float, Bounds(10, 60)],      # Flory–Huggins χN (segregation strength)
    f_A:   Annotated[float, Bounds(0.2, 0.8)],    # block fraction
    T_anneal_C: Annotated[float, Bounds(100, 280)],
) -> Observation:
    """Surrogate strong-segregation scaling for lamellar domain spacing L0 (nm).
    L0 ~ a * N^(2/3) * chi^(1/6), with a mild thermal-expansion term.
    y = predicted L0 (nm). Cheap closed-form 'simulation' — the GP's physical anchor."""
    a = 0.55                                       # statistical segment length proxy (nm)
    N = chi_N / 0.18                               # back out N from a nominal chi
    L0 = a * N**(2/3) * (chi_N/N)**(1/6) * (1 + 2.1e-4*(T_anneal_C - 150))
    sigma = 0.03 * L0                              # 3% model/run noise
    return Observation(y=float(L0), sigma_obs=float(sigma), source="sim",
                       aux={"N": N, "regime": "strong_segregation"})

@experiment_tool("cahn_hilliard_coarsening", cost=2.0, deterministic=False,
                 touches=("compute",), domain="soft_matter", timeout_s=60)
def cahn_hilliard_coarsening(
    mobility:  Annotated[float, Bounds(0.1, 5.0)],
    chi:       Annotated[float, Bounds(0.5, 3.0)],
    steps:     Annotated[int,   Bounds(200, 4000)] = 1500,
    grid:      int = 96,
) -> Observation:
    """Tiny 2D Cahn–Hilliard solver (phase separation). Returns the coarsening
    exponent n from L(t) ~ t^n (expected ~1/3, Lifshitz–Slyozov).
    y = fitted exponent n; sigma from the fit residual. A REAL numeric experiment."""
    n_exp, resid = _run_ch_2d(mobility, chi, steps, grid)   # FFT semi-implicit, ~1s
    return Observation(y=float(n_exp), sigma_obs=float(resid), source="sim",
                       aux={"expected": 1/3})

@experiment_tool("saxs_peak_from_data", cost=0.05, deterministic=True,
                 touches=("compute", "local_data"), domain="soft_matter", timeout_s=15)
def saxs_peak_from_data(
    data_path: str,
    q_col: str = "q", I_col: str = "I",
) -> Observation:
    """Read a LOCAL 1D SAXS/GISAXS profile (reuses parsers/tabular._load),
    find the primary structure peak q*, return domain spacing d = 2π/q* (nm).
    touches=local_data -> sandbox runs with network HARD-OFF (firewall RULE 3).
    Raw scattering curve NEVER leaves the machine; only the scalar d is returned."""
    from parsers import tabular
    df = tabular._load(data_path, _ext(data_path), notes=[])   # salvaged loader
    q, I = df[q_col].to_numpy(), df[I_col].to_numpy()
    qstar = float(q[np.argmax(I)])
    d = 2*np.pi / qstar
    sigma = d * (q[1]-q[0]) / qstar                 # q-resolution-limited uncertainty
    return Observation(y=float(d), sigma_obs=float(sigma), source="compute",
                       plane="local", aux={"q_star": qstar})
```

Note `saxs_peak_from_data` is the firewall showcase: `touches=("compute","local_data")` → the runner forces network off, the manifest logs *"0 bytes sent"*, and only the derived scalar `d` (nm) is handed back to the GP — the raw curve stays in `./local_data`.

**Domain-agnostic generics (`generic.py`)** so the tool works outside soft matter:
- `fit_surrogate(x: dict, target: str, data_path: str)` → GP/RF on **local** data, predict `y` at `x` (`touches=("compute","local_data")`).
- `recompute_statistic(expr: str, subset: dict, data_path: str)` → correlation/slope/effect-size on the local dataset (`local_data`).
- `eval_model(model_id: str, x: dict)` → evaluate an already-fitted in-memory surrogate (Tier-C in-process, no file/network).

---

## 8. How it plugs into the loop (interfaces the other subsystems rely on)

- **Experiment Agent → runner:** the agent emits `{"tool", "params"}`; calls `run_experiment(...)` → `Observation`. That's the whole contract.
- **Observation → Bayesian engine:** `obs.y`, `obs.sigma_obs` go straight into the GP refit + posterior update (research Eq.4) and the anomaly score `S = 1 − exp(−|z|)` with `z = (y − μ(h))/√(σ²(h)+σ_obs²)` (Eq.3).
- **`tool.cost` + profiler feasibility → cost-aware IDS:** the executor exposes `cost`/`cost_spent`; the IDS layer divides by `I_t(h)·feasibility(h|profile)` (research §7) so an experiment the user can't run is demoted.
- **`touches` → feasibility hints:** a tool tagged `domain="soft_matter"` + needed instruments lets the capability subsystem map "can THIS user run it?".

---

## 9. Build order (hackathon, hours not days)

1. `observation.py` + `registry.py` + `schema.py` — the decorator + Observation + bounds validation. *(skeleton the whole team codes against)*
2. `tools/generic.py` (`fit_surrogate`, `recompute_statistic`) + `tools/softmatter.py` (`scft_domain_spacing`, `saxs_peak_from_data`). *(real `y` values flowing)*
3. `dryrun.py` + `--dry-run` flag — **loop demos with zero setup.** *(do this early; it de-risks the live demo)*
4. `planes/guard.py` + `manifest.py` + the `/planes` REPL view — the differentiator judges can see.
5. `sandbox.py` Tier B (rlimit subprocess), then `cahn_hilliard_coarsening` as the "we run a *real* numeric experiment live" wow moment. Tier A (docker) only if time permits.

**Salvaged verbatim:** `parsers/tabular._load` (local data loading inside `saxs_peak_from_data`/`fit_surrogate`), the `agents/llm.py` mock-fallback *pattern* (reused as the dry-run philosophy), the `tools/lit_apis.py` etiquette (reused on the WEB plane, never the LOCAL plane). New code is the registry/decorator, Observation, sandbox, dry-run, and the plane guard + manifest.

**One-line answer to the framing question:** yes — and this subsystem is what makes the "closed loop" real and *safe*: hypotheses get tested by actual lightweight experiments returning calibrated `(y, σ)`, a dry-run path guarantees the loop always runs for the demo, and a code-enforced firewall means your raw data is provably never the thing that goes on the wire.


---

# Critique: feasibility/build

# Feasibility Review — HypoForge CLI (brutal hackathon lead read)

I read the design and the existing prototype (`agents/llm.py`, `agents/orchestrator.py`, `tools/lit_apis.py`, `parsers/*`). The salvage claims are real and accurate: `call_json`/`_extract_json`/`_MockLLM`, the `progress(key,label,frac)` callback in `run_pipeline`, the `ThreadPoolExecutor` lit fan-out, and `scikit-learn`/`scipy` are already in `requirements.txt`. That's a genuine head start. Good.

Now the bad news.

## Verdict

**The design is a 3-month research product specced as a 2-day hackathon build.** It defines **6 new packages** (`router/`, `engine/`, `evaluation/`, `experiment/`, `planes/`, `hypoforge/runtime/`) and ~40 files, several of which are individually risky research artifacts (per-principle GP experts, BALD mutual information, Bayesian posterior over an evolving principle set, anomaly-driven augmentation, a structured 3-agent debate with score deltas, a docker/rlimit sandbox, a cost-ledger router with downgrade ladder). A small team that tries to build the whole thing will have 40% of everything half-working and **nothing demoable**. You can absolutely ship something that *feels* like the vision in 2 days — but only by being ruthless about what is real vs. what is theater, and by pre-deciding the fallback for every live piece.

The single biggest trap is not the math. **It is the assumption that a free/cheap LLM will reliably drive a free-form, multi-turn, tool-calling agent loop** (`runtime/loop.py`). Free OpenRouter models and `deepseek-chat` have flaky-to-absent function-calling and fall apart over 5+ sequential tool decisions. If your core demo path depends on the model autonomously choosing `glob → ingest → discover_lab → crawl → warmup → round×N`, it *will* stall or hallucinate a tool name live in front of judges. Build the "agentic feel" on rails, not on faith.

## Riskiest / over-scoped parts (ranked)

| # | Component | Risk | Why it bites |
|---|---|---|---|
| 1 | **Free-form tool-calling agent loop** (`runtime/loop.py`, park/resume, checkpoints, event bus) | 🔴 Critical | Cheap models won't reliably emit valid multi-step tool calls; debugging this eats a day; it's the spine everything hangs off. |
| 2 | **Full PiEvo GP/IDS closed loop** (`engine/gp.py`, `infogain.py`, `posterior.py`, `anomaly.py`, `bridge.py`) | 🔴 Critical | 5 interlocking numeric modules. BALD MI + per-principle GP + log-Bayes posterior + Bonferroni anomaly is easy to get *subtly wrong* and impossible to verify under time pressure. Numbers that look plausible but are nonsense are worse than no numbers. |
| 3 | **Live institution crawl + capability extraction** (`capability/*`, `discover_lab`, `crawl_profile`) | 🔴 Critical | Network-dependent, site-structure-dependent, LLM-extraction-dependent. Will fail or return garbage on a random lab live. This is your *differentiator* so it must appear to work flawlessly. |
| 4 | **sentence-transformers local embeddings** (`engine/embed.py`) | 🟠 High | Not in `requirements.txt`. First-run downloads a model (~100MB+) — dead air or failure on conference wifi. The entire semantic bridge depends on it. |
| 5 | **Per-role router w/ budget ledger, pricing.yaml, downgrade ladder** (`router/budget.py`, `ledger.py`) | 🟠 High | Lots of code for near-zero demo value. A dict `{role: model}` does 95% of it. |
| 6 | **Structured 3-agent debate w/ clamped score deltas** (`evaluation/debate.py`) | 🟡 Med | High wow-per-pixel but ≥6 LLM calls/hypothesis, brittle JSON, cuttable. Can be faked as a 2-pass critic. |
| 7 | **Sandbox: docker/rlimit/socket-guard** (`experiment/sandbox.py`) | 🟡 Med | Real isolation engineering. Unnecessary — your builtin tools are trusted pure-Python. In-process is fine for a demo. |
| 8 | **Plane firewall as 3-layer structural enforcement** (`planes/guard.py`, fingerprint tripwire) | 🟢 Low-Med | Conceptually your best judge-story, but the *full* enforcement (type-structural + dispatch + sandbox socket kill + outbound fingerprint scan) is overkill. A single dispatch-time guard + a `/planes` manifest print gets you 100% of the demo credibility. |

## The Minimal Viable Spine (this MUST work end-to-end before anything else)

A single command runs and *looks* like Claude Code, on rails, with mock fallback everywhere:

```
forge run "I study GISAXS of block copolymers at BNL" --data ./sims --dry-run
```

1. **REPL + streaming renderer** (`rich`) that prints a live plan checklist + streams text. *Feel only — no autonomous tool-calling required.*
2. **Fixed orchestrator pipeline** (salvage `run_pipeline`, promote `progress()` → event stream): `ingest → profile → seed → loop → rank → report`. Each step is a normal function call you control, rendered as if the agent chose it.
3. **Ingest** local data via existing `parsers/registry.parse_file` → a few `(x, y, σ)` quantities.
4. **Institution profile** → a `CapabilityProfile` (equipment list + feasibility scorer). *Live crawl attempted, canned fallback guaranteed.*
5. **A loop that visibly runs N rounds** and updates *something* numeric each round (even if it's a simplified surrogate, not full GP/IDS).
6. **Ranked hypotheses with the 4 guidance fields** the user explicitly asked for: difficulty, effort, what-it-explains, info-gain — rendered as the board + `/card`.
7. **`--dry-run` + mock LLM** so the whole thing runs offline with zero keys.

If those 7 work, you have a winning demo. Everything else is upside.

## Staged build order — cut from the bottom up

**Stage 0 (spine, non-negotiable):** REPL + rich renderer + rails orchestrator + ingest + mock router (plain dict) + `--dry-run`. → *A fake-agentic CLI that ingests and prints a hardcoded ranked board.*

**Stage 1 (the numbers, simplified):** Replace hardcoded board with a **single-GP / closed-form surrogate** ranking. Compute a *defensible* info-gain proxy (GP posterior variance reduction at `x_target` — one `GaussianProcessRegressor`, no per-principle experts, no BALD mixture). Compute feasibility from the profile. This gives real, explainable numbers without the 5-module math stack.

**Stage 2 (the wedge):** Institution profiling. Live `WebSearch`/fetch + LLM extract, **with a cached/canned hero-domain profile that always loads.** The confirm-lab checkpoint (the trust moment) works against either.

**Stage 3 (the loop made real):** Wire the surrogate into an actual multi-round loop: propose candidates → score → "run" experiment (dry-run posterior draw) → update GP → re-rank. The optimization curve visibly bends. This is your "closed-loop" proof.

**Stage 4 (polish, only if ahead):** Add per-principle GPs + true IDS, OR the structured debate, OR `forge replay`. **Pick ONE.**

**Cut order when behind (delete in this sequence):** budget ledger/pricing → docker sandbox → fingerprint tripwire → structured debate (→ 2-pass critic) → anomaly-driven principle augmentation → per-principle GP experts (→ single GP) → free-form tool-calling (→ rails) → live crawl (→ canned). Note: the last two cuts still leave a fully demoable product.

## Guaranteed demo fallback for every risky piece

Pre-build these *now*, not at 2am:

| Risky piece | Fallback that ALWAYS works |
|---|---|
| Free-form tool-calling loop | **Rails orchestrator** rendered to look agentic. The model only fills content, never drives control flow. |
| Full GP/IDS math | **Single sklearn GP**, info-gain = variance-reduction proxy; if even that breaks, **precomputed numbers** rendered live. |
| Live institution crawl | **Canned `CapabilityProfile` for the BNL Soft-Matter hero user** loaded from `fixtures/`. Live attempt with 4s timeout → silent fall back to canned. |
| sentence-transformers download | **Vendor the model into the repo** ahead of time, OR fall back to **hashing-vectorizer / TF-IDF embeddings** (sklearn, already a dep). Never download live. |
| Any LLM call (no keys / rate-limited / offline wifi) | Existing **`_MockLLM`**, extended to return valid JSON per role. Demo runs fully offline. |
| Experiment execution | **`--dry-run` posterior draw** (already in design) — the loop "learns" with zero compute. |
| Whole live demo collapses | **`forge replay <session-id>`** re-streams a known-good recorded transcript at 2x. Build this *early* as the bulletproof escape hatch — it's deterministic, needs no keys, no network. This single feature de-risks the entire presentation. |

Rule: **conference wifi does not exist.** Every path must complete with `--offline`.

## ~2-Day hour-by-hour plan (2 builders; "A" = runtime/CLI, "B" = engine/numbers)

**Day 1**
- **0:00–1:00 — Both:** Repo scaffolding, venv, pin deps. **Decide hero domain = soft-matter NOW.** Write the canned `CapabilityProfile` fixture + a sample local dataset. Add `sentence-transformers` *or* commit to TF-IDF embeddings (recommend TF-IDF to kill the download risk).
- **1:00–3:00 — A:** `router.py` as a thin `get_llm(role)` dict over salvaged `llm.py` (no ledger/pricing). REPL skeleton with `rich` streaming + a static plan checklist panel.
- **1:00–3:00 — B:** `engine/state.py` dataclasses + a **single** `GPExpert` (sklearn) + a toy 1-D objective. Unit-test that GP fit/predict returns sane `(μ, σ)`. No bridge, no posterior yet.
- **3:00–5:00 — A:** Rails orchestrator: promote `run_pipeline`’s `progress()` into an event stream; wrap `parsers/registry.parse_file` as `ingest`. CLI ingests `--data` and prints evidence.
- **3:00–5:00 — B:** Info-gain = variance-reduction proxy + a feasibility-weighted ranking score `V(h)`. Produce a **real ranked board from synthetic candidates.**
- **5:00–7:00 — Both: INTEGRATION GATE 1.** `forge run --dry-run --offline` ingests data and prints a ranked board with the 4 guidance fields. *If this isn't working by end of Day 1, cancel Stages 3–4.*
- **7:00–8:00:** Start `transcript.jsonl` writing → stub `forge replay`. **Record one good run tonight** as the fallback asset.

**Day 2**
- **0:00–2:00 — A:** Institution profiling: confirm-lab checkpoint UI + live fetch attempt with timeout → canned fallback. Make the trust moment land.
- **0:00–2:00 — B:** Close the loop: multi-round propose→score→dry-run-draw→refit→re-rank. Render the optimization curve / per-round guidance row.
- **2:00–4:00 — Both: INTEGRATION GATE 2.** Full path: `run → ingest → confirm lab → loop rounds → final ranked report`, offline, deterministic. **Freeze the spine here.**
- **4:00–6:00 — Pick exactly ONE upside:** structured debate **or** per-principle IDS **or** the `/weights` live re-rank (cheap, high wow, recommended). Time-box hard; revert if not clean by 6:00.
- **6:00–7:00:** `--budget` notice, `/planes` manifest print (the firewall story — single guard + manifest, skip the 3-layer fortress).
- **7:00–8:00:** **Demo hardening.** Re-record the golden transcript. Rehearse `forge replay` as plan B. Write the 3 judge one-liners. Stop coding.

## Go/no-go gates (enforce these)
- **End of Day 1:** ranked board prints offline, or you cut the closed loop entirely and ship "ingest + profile + ranked hypotheses." Still a fine demo.
- **Day 2 noon:** full offline path works end-to-end → freeze. After freeze, only additive, revertible features on a branch.
- **Golden transcript recorded by Day 1 night and re-recorded after freeze.** This is the thing you actually present if live breaks.

## Bottom line
Yes, a small team can ship a *credibly-working* version in 2 days — but only the **spine + one differentiator demoed on rails with canned fallbacks**, not the full closed-loop research engine. Build the "agentic feel" as scripted orchestration, fake the autonomy, make the numbers real-but-simple (one GP, variance-reduction info-gain), guarantee the institution-profiling wedge with a canned hero profile, and treat `forge replay` of a pre-recorded run as the load-bearing demo safety net. The PiEvo math is the part to *gesture at* with a working simplification, not the part to fully implement.


---

# Critique: differentiation/pitch

# Skeptical Judge Verdict: Is HypoForge Actually Differentiated?

I've seen 20 of these. Let me tell you what I'm thinking by minute 1 of your demo, and what would actually change my vote.

---

## The brutal baseline: what every other team is shipping

By the time you present, I've already seen:
- "Multi-agent system that reads papers and proposes hypotheses" (×8)
- "RAG over my PDFs + GPT-4 brainstorms experiments" (×5)
- "Agent loop with tools that searches literature and writes a report" (×4)
- At least 2 that name-drop a Bayesian/active-learning paper they didn't implement.

So my default prior on you is: **"same thing with extra steps."** Your job in 3 minutes is to kill that prior, fast, with something I *cannot* say about the other 20. Most of your architecture does NOT do that — it's beautifully engineered table stakes. Two things *might*.

---

## Pressure-testing wedge #1: Institution-profiling

**Is it differentiated?** Yes — this is the only thing in your whole deck I haven't seen another team do. Nobody else is asking "can *this specific lab* actually run this?" That's a genuinely novel framing and it's *demoable in 15 seconds* (the "H9 needs cryo-EM you don't have → demoted" moment). Lead with this.

**But here's where I call BS, and you must preempt all three:**

1. **"You're just doing a web search and vibe-guessing my equipment."**
   - This is the fatal objection. Crawling a lab homepage gives you a stale, marketing-flavored, incomplete list. The BNL Soft Matter page won't say "our rheometer's bearing is shot and beamtime is booked through Q3." Your feasibility score is **confidently wrong**, and a confidently-wrong feasibility number is *worse* than no number — it demotes a great hypothesis for a bad reason.
   - **Preempt:** Show the confirm-lab checkpoint as a *first-class feature, not a fallback.* "We infer, then we let you correct in one keystroke — and the correction persists." Frame profiling as a *fast-draft the human ratifies*, not an oracle. Also: let the user point at a CV / grant abstract / equipment page locally as ground truth. That converts "creepy guess" into "smart prefill."

2. **"This is a privacy theater / a liability."** Auto-discovering "I think you're Jane Doe at BNL" from a prompt feels invasive on stage. A judge from industry will flinch.
   - **Preempt:** Your two-plane firewall is the answer, but *only if you make it concrete.* The "0 bytes left the machine" manifest line is your single best trust artifact. Show it. (More below — this is actually your real weapon.)

3. **"Feasibility is a soft re-ranking, not a capability."** If profiling only nudges a score, it's a garnish. Make it *change the answer.* The demo must show a hypothesis that is #1 by raw info-gain getting **demoted below** a runnable one, with the dollar figure. That's the only version of this that lands.

**Verdict on wedge #1:** Differentiated and demo-friendly, but currently resting on a shaky inference. The fix is to reframe profiling as *human-ratified prefill + a hard feasibility veto*, not an autonomous oracle.

---

## Pressure-testing wedge #2: EIG / uncertainty-minimization (the PiEvo angle)

**Is it differentiated?** On paper, yes — almost no hackathon team actually closes the loop with a calibrated acquisition function. "1.9 nats" on screen is a flex none of the others can match.

**But this is where the *sharpest* judges will eat you alive:**

1. **"Your information gain is information about a GP fit to *embeddings of your own sentences*, not about nature."** This is the soundness landmine, and it's in *your own grounding notes* (PiEvo lesson d: "embedding-likelihood is a PROXY for physical likelihood"). The whole numeric edifice — IDS, BALD, posterior, anomaly — sits on a semantic-similarity kernel. A physics PhD judge will ask: "What does 1.9 nats *mean* physically?" and if your answer is hand-wavy, the entire quantitative wedge collapses into "fancy-looking numbers."
   - **Preempt, do not hide:** Put the `literature_proxy` caveat *on the slide*. Own it: "These nats rank *which experiment most separates our competing hypotheses*, not a physical entropy. It's a decision-ranking signal, validated by whether the loop converges faster than random/greedy — here's that ablation." Then **show the curve**: HypoForge's IDS selection vs. random selection vs. greedy-exploit on your Cahn–Hilliard toy, AUOC gap. *That* converts "fancy number" into "measurably better search." Without that ablation plot, drop the nats from the headline.

2. **"You demo'd on a closed-form surrogate. So you built an optimizer for a function you already wrote down."** The dry-run/surrogate path that saves your demo is *also* the thing that makes the loop look circular — if the experiment is `scft_domain_spacing`, a one-line scaling law, then "discovering" its behavior is theater.
   - **Preempt:** Use `cahn_hilliard_coarsening` (a *real* PDE solver where the coarsening exponent is genuinely unknown to the agent a priori) as your live "real experiment" moment, and explicitly say "this is a real numerical experiment, not a lookup." The contrast between dry-run (banner'd) and a real solver run is your credibility.

3. **"~5 warm-up rounds + GPs on a handful of points = you're fitting noise."** Calibration of a GP on <10 points is a fair attack.
   - **Preempt:** Don't over-claim calibration. Claim *direction*, not precision: "We don't promise the right answer in 5 rounds; we promise we ask better questions than brainstorming." Lower the bar to one you can defend.

**Verdict on wedge #2:** Genuinely differentiated *if and only if* you show a convergence/AUOC ablation vs. random. Without that plot, it reads as mathematical cosplay and a skeptic will treat your nats as decoration.

---

## The thing you're underselling that should actually be front-and-center

**The two-data-plane firewall + the `/planes` manifest.** "3 files read, 0 bytes left the machine. Audit: manifest.json."

Here's why this beats both your named wedges as the *pitch centerpiece*:
- It's **structurally enforced and visible** — code, not a promise. Judges can't say BS to a manifest that says 0 bytes.
- It answers the #1 unspoken question every PI and every industry judge has about "upload your data to my agent": *where does my data go?* Every other team quietly POSTs your CSV to OpenAI. You can say, on stage, "we provably don't." Nobody else can.
- It *unifies* your two wedges into one story: **"We profile the institution on the public web; your raw data never leaves the laptop — and here's the receipt."** That single sentence is your differentiator. It makes the creepy-profiling objection (wedge #1's weakness) into a *strength*: profiling is safe *because* it's structurally separated from your data.

This is the one thing I literally cannot say about the other 20 demos.

---

## The single thing for the 3-minute pitch

Open cold with the **demoted-hypothesis moment**, narrated through the firewall:

> "Here's the most informative hypothesis we found — 3.1 nats, top of the list. We're throwing it away. It needs cryo-EM your lab doesn't have, ~$5M, 26 weeks. Instead, run *this* one: less flashy, but it's the most you can learn *on the bench you actually own this week*. And while we figured that out — we crawled your institution's public page for capabilities, but watch this: your raw scattering data never left this machine. Zero bytes. Here's the audit log."

That 30 seconds contains all three claims that are uniquely yours: feasibility-as-veto, info-gain-per-effort, and the provable firewall. Everything else (ingestion, lit review, debate, the REPL) is *supporting cast* — mention it exists, don't spend time on it, because every other team has it too.

---

## The claims judges will call BS on — preempt table

| Claim you'll make | The BS-call | Your one-line preempt |
|---|---|---|
| "Infers your equipment" | "Stale web guess, confidently wrong" | "Inferred draft, **you ratify in one keystroke**; or point it at your CV — feasibility is a *hard veto*, shown demoting a top hypothesis" |
| "1.9 nats of info gain" | "Info about your embeddings, not physics" | Caveat on-slide + **AUOC-vs-random ablation plot**; "ranks which experiment best separates rival hypotheses, validated by faster convergence" |
| "Closed-loop discovery" | "You optimized a formula you wrote" | Run the **real Cahn–Hilliard solver** live, banner the dry-run rows as not-real |
| "Agents debate before committing" | "Two LLMs role-play, prove it matters" | Show debate **moving a score** (H7 novelty downgraded after skeptic cites a real near-neighbor paper) — the delta is the proof |
| "Novel hypotheses" | "How do you know it's novel, not just unsearched?" | Embedding-distance spine + nearest-paper shown ("0.34 from Chen 2024"); novelty is *measured distance*, LLM only flexes ±0.2 |
| "Privacy-safe" | "Prove the data didn't leak" | The `/planes` manifest: "0 bytes sent," structural type-firewall, `/forget` wipes it |

---

## What to CUT from the pitch (it's table stakes, it dilutes you)

- The REPL/Claude-Code-feel, resume/replay, model router, planner panel, budget ledger. All excellent engineering, all *expected*. Thirty seconds total, as "yes, it's a real tool, not a notebook."
- The full 7-axis scoring rubric. Judges will assume you can score things. Show the *ranking outcome*, not the rubric.
- Debate as a *centerpiece*. It's a credibility upgrade, not a differentiator — everyone has "critic agents." Use it as the answer to "but can I trust the ranking," not as a headline.

---

## Bottom line

**Differentiated? Partially — and not via the parts you've invested the most architecture in.** Your closed loop and multi-agent stack are *excellent table stakes* that win you a passing grade, not the room. Your two genuinely novel ideas are (1) **feasibility-as-a-hard-veto grounded in institution profiling** and (2) **a structurally-enforced, visible data firewall** — and #2 is stronger, safer, and more demoable than you're currently treating it.

Fuse them into one sentence — *"we profile the lab on the public web to tell you what's worth running on the bench you actually own, and your raw data provably never leaves this machine"* — open on the demoted-hypothesis moment, back the nats with one ablation plot, and you've beaten the 20 demos that were all just "agents, but for science."

The risk that sinks you: leading with the EIG math without the convergence-vs-random plot. A skeptic will smell proxy-likelihood and write you off as mathematical decoration. **No ablation → drop the nats from the headline and lead entirely with feasibility + firewall.**


---

# Critique: Bayesian soundness

# Soundness Audit: GP/IDS Information-Gain over LLM Hypotheses with Embedding Likelihoods

Verdict up front: the architecture is internally coherent and the engineering is careful, but the **scientific claims rest on a chain of proxies that are presented to the user with more authority than they have earned**. The single most dangerous phrase in the whole design is "1.9 nats of quantitative information gain" rendered as a clean number next to a real experiment. Below are the specific failure modes, ranked by how badly they can mislead a real scientist, each with a concrete guardrail.

---

## 1. The embedding likelihood is the load-bearing wall, and it ignores sign, magnitude, and negation

`φ(h,P) = [e_h·e_P, ‖e_h−e_P‖]` plus a GP over those features is the mechanism by which natural-language propositions get a "Bayesian" treatment. The problem is structural, not tunable:

- **Sentence embeddings encode topical/lexical similarity, not physical compatibility.** "Annealing raises d-spacing >8%" and "Annealing *lowers* d-spacing >8%" have near-identical embeddings (cosine typically >0.9). The GP kernel will treat two physically *opposite* hypotheses as nearly the same point in X and smooth their `y` values together. A surrogate built on this cannot represent the very contrasts the loop exists to resolve.
- **Numeric thresholds ("> 8%", "T_odt > 5 K") are nearly invisible** to general-purpose embeddings. The discriminating content of most testable hypotheses lives precisely in the magnitudes the kernel can't see.
- **Consequence for the posterior.** Eq. 4 updates `p(P)` by how well each principle's embedding-feature GP fits `y`. The discriminative signal between principles comes almost entirely from *which principle's wording is more semantically similar to the winning hypothesis's wording*. That is a linguistic similarity contest wearing the clothes of Bayesian model selection. The PiEvo authors flag this as "a soundness risk"; in your adaptation it is *the* mechanism, so the risk is not peripheral — it is the engine.

**Guardrails (do all three):**
1. **Extract structured claim features and put them in `ψ(x)`, not in the embedding.** Parse each hypothesis into (signed direction, magnitude, threshold, variable) with a cheap deterministic/LLM pass and feed those as numeric kernel dimensions. The embedding should be a *weak auxiliary* feature, never the spine.
2. **A negation/antonym hard-separator.** Detect direction-of-effect; force opposite-sign hypotheses to be far in kernel space regardless of cosine similarity. Without this the GP is actively wrong, not merely noisy.
3. **A "proxy soundness score," computed and displayed.** On warm-up data, measure rank correlation between embedding-kernel similarity and actual `|y_i − y_j|` similarity. If it's low (it often will be), **automatically disable the semantic kernel block** and fall back to physics-only features, and tell the user the semantic bridge was untrustworthy here. Make the proxy earn its place every run.

---

## 2. "Quantitative information gain" is information about *your principle list*, under an assumption that is always false

The BALD term `I(P;Y|h) = H[mixture] − Σ w_P H[component]` quantifies how much an observation would tell you about *which element of `P_t` is correct* — **conditional on one of them being correct (M-closed)**. Real discovery is M-open: the true mechanism is essentially never in your current finite list. So the reported nats measure resolution of a discrete latent that is itself misspecified. Reducing entropy over a wrong hypothesis set can look like "learning" while you converge confidently on the least-wrong wording.

Additional precision problems with the number itself:
- **The mixture entropy is moment-matched to a single Gaussian — an explicit upper bound.** You are reporting a biased-high estimate as a point value. "1.9 nats" is really "≤ ~1.9 nats."
- **The `+ 0.5·log(1+σ²/σ_obs²)` term is a different quantity** (GP epistemic variance reduction) summed into the same "nats" scalar. Information-about-principle and information-about-the-residual-surface are not additive in any coherent sense; this is an ad-hoc acquisition heuristic, not an information measure.
- **Cross-round nats are not comparable.** `P_t` changes cardinality and identity every time a principle spawns/prunes, so an "info-gain trace" plots a quantity defined on a moving latent space. Trend lines over it are meaningless.

**Guardrails:**
- **Rename it in every surface.** Not "quantitative information gain" — "**expected model-discrimination (proxy, nats)**." One honest label kills most of the over-claim.
- **Add an explicit "none of the above" principle** carrying real prior mass, so the posterior can represent "our principle set is inadequate." Watch its weight; if it grows, the headline MI numbers should be *greyed out*, not trusted.
- **Compute MI by Monte Carlo** (sample the mixture, numerically estimate entropies) and report a standard error, instead of the upper-bound moment-match. If you keep the closed form, label it `≤`.
- **Report the two info terms separately** (principle-discrimination vs. surrogate-uncertainty reduction). Never sum-then-display.

---

## 3. The GP uncertainties — which everything depends on — are least reliable exactly when you use them most

The anomaly score, the MI, the posterior likelihood, and the stopping rule **all consume the GP's σ**. Yet:
- **Warm-up is ~5 points** into a product kernel (2 semantic dims × anisotropic physics RBF × one-hot categoricals = easily 10+ effective dimensions) with `n_restarts_optimizer=1`. Marginal-likelihood hyperparameter fitting on 5 points in 10 dims is **unidentified**; lengthscales and noise will be arbitrary. The σ you propagate into z-scores in the first several rounds is essentially fabricated.
- **`normalize_y=False` with residuals about a literature mean** is fine only if the literature mean is right; if it's biased, the residuals have nonzero mean and a zero-mean GP prior fights it, inflating apparent structure.
- A product of an MLE-fit semantic RBF and an MLE-fit anisotropic physics RBF on tiny data is a **textbook overfitting/degeneracy setup**.

**Guardrails:**
- **Gate the whole inferential layer behind a calibration check.** Before any anomaly or "converged" claim, run **leave-one-out predictive coverage / PIT** on the available points: do ~90% of held-out `y` land in 90% predictive intervals? Report Expected Calibration Error. If coverage fails, **down-rank to a "ranking only, uncertainty unreliable" mode** and say so.
- **Replace GP σ with conformal predictive intervals** (split/LOO conformal on residuals) for anything user-facing. Conformal gives finite-sample coverage guarantees that a 5-point MLE GP cannot.
- **Use heavier tails / fix the noise floor.** Bound the lengthscales, set a sane `alpha`/WhiteKernel floor from domain knowledge, and prefer Student-t residuals so a couple of outliers don't collapse σ.
- **Refuse to optimize hyperparameters below a minimum n** (e.g., < ~15 calibrated points); use fixed, domain-reasonable priors until then and **display "priors only — σ not data-identified."**

---

## 4. Anomaly-vs-literature is a confounded noise amplifier with a hard-coded scale

`S = 1 − exp(−|z|)`, `z = (y−μ)/√(σ²+σ_obs²)`, thresholded by Bonferroni θ. Three independent soundness failures:

1. **It assumes z is a valid Gaussian z-score.** It isn't — misspecified embedding-feature GP, non-Gaussian residuals, tiny-n σ. **Bonferroni correction on a miscalibrated statistic is false rigor**: it dresses an uncalibrated residual in the language of multiple-testing control.
2. **The "z vs literature" uses σ = 1.0 hard-coded.** Whether a datum is "anomalous vs published consensus" is then decided entirely by an arbitrary unit scale. Change that 1.0 and anomalies appear/vanish. Not defensible.
3. **Confounding.** A local-vs-literature mismatch can be (a) real new physics, (b) the literature curve mis-fit/extrapolated out of range, (c) **units/normalization mismatch** between the user's data and the digitized literature, or (d) the embedding proxy mismapping `x`. The design attributes *all four* to "spawn a new principle." Most real "anomalies" in practice are (b)/(c) — instrument calibration and unit errors, not discoveries. An auto-spawning loop will **inflate `P_t` with principles that reconcile your own normalization bugs**, and the posterior degrades accordingly.

**Guardrails:**
- **A human gate on principle birth.** You already gate experiments and lab-confirmation — add an "**approve new principle**" checkpoint. Before spawning, show: raw residual, the *assumed* σ, the literature points and user points **on one plot in shared units**, and an explicit "is this physics, or calibration/units?" prompt.
- **Require replication and a practical-significance floor.** Don't spawn from a single point; require ≥k independent observations exceeding *both* statistical significance *and* a domain-meaningful effect size (`> noise` AND `> what a scientist would care about`).
- **Derive the literature σ from the literature**, not 1.0 — propagate the reported error bars / digitization uncertainty / extrapolation distance. If the literature point is an extrapolation beyond its support, inflate σ accordingly so out-of-range "anomalies" don't fire.
- **Run a units/normalization sanity pass first** (range, dimensional consistency) and route those failures to a "data issue," not a "discovery."

---

## 5. Two loop mechanics manufacture certainty from nothing — fix before demo

These are the ones that can actively embarrass you in front of a domain judge:

- **Dry-run draws update the posterior.** §9's `step()` appends the dry-run `Observation` and refits the GP / recomputes the posterior like any other. But the dry-run `y` is *sampled from the current posterior itself*. Feeding a model's own prediction back as evidence is a **self-fulfilling loop**: entropy contracts, `best_regret` improves, stopping criteria fire — all with **zero real information**. The tool will confidently announce convergence on a laptop with no data. **Fix:** dry-run observations must either set effective `σ_obs = ∞` (exercise the pipeline, update nothing), or be tagged and **excluded from every confidence/entropy/stopping computation**. Banner all numbers in dry-run as "PIPELINE TEST — NOT EVIDENCE."
- **`fit_surrogate` returns interpolation as "Observation."** Training an RF/GP on local data and then "predicting y at x" yields a *model extrapolation*, not a new measurement. Feeding it into the posterior **double-counts the data the surrogate was trained on** and biases σ downward. **Fix:** give it a distinct `source="model_extrapolation"`, exclude it from the principle likelihood (or down-weight massively), and never let it trigger anomalies.

---

## 6. IDS regret and the feasibility divide are heuristics, not the theory they cite

- `Δ_t(h) = |v* − μ_mix|` with `v* = max over the current candidate pool`. That is regret against **the LLM's current guesses' predicted best**, not a true optimum. Candidates churn each round, so `v*` — and therefore every "regret 0.21" you print — is self-referential and unstable.
- Dividing `Δ²/I` by feasibility folds an economic quantity into an information-theoretic acquisition. Reasonable as a *heuristic*, but it is then **no longer IDS** and shouldn't be presented as "argmin Δ²/(I·F)" with the authority of the cited equation.

**Guardrail:** label the acquisition "**feasibility-weighted acquisition heuristic**," and show the un-weighted info and the feasibility factor *separately* (your `/card` already does — keep them visually un-merged so the user sees the value judgment as a value judgment).

---

## 7. Statistical-multiplicity / double-use-of-data hygiene

The same observations (a) update the posterior that selects the MAP principle, (b) condition the LLM that generates candidates, and (c) fit the surrogate that scores them — then the "best" is tested against that surrogate. This is **the garden of forking paths**: optimistic bias is structural.

**Guardrails:**
- **Pre-register the predicted outcome + threshold** (you already capture `predicted_outcome`) *before* running, persist it, and evaluate the real result against the frozen prediction. Surface "pre-registered: d > 8%; observed: 6% → not supported."
- **Hold out** at least some warm-up points from GP fitting purely for the calibration check in §3.
- Track and display **how many genuinely independent real observations** underlie each principle's weight; a principle "supported" by surrogate draws and dry-runs should be visibly distinguished from one supported by measurements.

---

## 8. Prior sensitivity

`prior_logw = literature_confidence × source_trust` are subjective, uncalibrated scalars, and the posterior inherits them. With few real likelihood updates (the common case), **the prior dominates the ranking**.

**Guardrail:** ship a one-line **prior-sensitivity / robustness panel**: re-rank with σ inflated 2×, with the semantic kernel dropped, and with prior weights halved. If the top experiment is stable across these, say so (earns trust). If it flips, the headline recommendation should carry a "**fragile to assumptions**" flag. This is cheap (no new LLM calls — it's a recompute over cached sub-scores) and is the single most credibility-building addition you can make.

---

## Honest-uncertainty UX: the minimum bar to be "defensible, not hand-wavy"

Every nats/score/anomaly number needs a **provenance tag**, rendered inline:

- `n_real` — count of genuine measurements behind it (vs surrogate/dry-run draws).
- `proxy?` — was the value embedding-mediated? (yes ⇒ caption "semantic proxy, not physical likelihood — verify experimentally," which your `flags` already supports — make it *non-dismissible*, not a footnote).
- `calibrated?` — did this run pass the LOO coverage check? If no, grey the uncertainty and the MI.
- **Show intervals, not points.** Predictive interval + observed coverage, not a bare μ.
- **State the breakers.** One line per headline number: "this assumes your principle list contains the truth, the embedding kernel tracks physics here, and the GP σ is calibrated — currently [pass/fail/fail]."
- **Stopping safety:** never emit "converged / good enough" without (i) ≥ N_min real observations and (ii) a passed calibration check. Entropy-based stopping over a proxy/dry-run-contaminated posterior is exactly how you'd confidently stop having learned nothing.

---

## Triage for the hackathon

**Must-fix before any live demo (these produce confidently-wrong output):**
1. Dry-run and `fit_surrogate` observations must not update beliefs / confidence (§5).
2. Negation/sign separator in the kernel, or the surrogate is actively wrong (§1.2).
3. Rename "quantitative information gain" → "expected model-discrimination (proxy, nats)" everywhere (§2).
4. Human gate on principle birth (§4).

**Cheap, high-credibility additions:**
5. LOO calibration/coverage check gating the inference layer (§3).
6. Prior/assumption sensitivity panel (§8).
7. Provenance tags + "assumption breakers" line on every headline number (UX).

**Honest framing for judges:** what you have is a **defensible decision-support and exploration-prioritization heuristic** that is transparent about its proxies — *not* a calibrated measurement of information about nature. Say that out loud. A tool that shows its own calibration failing and greys out its nats is far more credible to a real scientist than one that always prints a confident 1.9.


---

# Critique: demo

# HypoForge — 3-Minute Live Demo Director's Cut

## The one-sentence pitch (say this first, while terminal is still blank)
> "Every other team built an agent that spits out a list of hypotheses. Ours profiles *your specific lab's equipment* from the web, then runs a closed Bayesian loop that tests hypotheses with real micro-experiments and tells you the single next experiment **you can actually run** — and watches its own uncertainty drop in real time."

---

## Hero assets (lock these before demo day)

| Asset | Exact thing | Why this one |
|---|---|---|
| **Hero domain** | Soft-matter / block-copolymer thin films (GISAXS) | All three `experiment/tools/softmatter.py` tools already designed; runs in seconds, pure-Python, no solver/GPU |
| **Hero lab** | "Soft Matter Group, CMPMS @ Brookhaven National Lab" + NSLS-II 11-BM/CMS beamline | Real, crawlable public pages; gives a believable equipment profile (GISAXS beamtime + benchtop rheometer) |
| **Hero data (LOCAL plane)** | `./sims/anneal_sweep.csv` (a χN / f_A / T_anneal → domain-spacing sweep) **+** `./sims/saxs_profile.csv` (a 1-D q vs I curve with a clean primary peak) | Feeds `saxs_peak_from_data` + warm-up Observations; the curve is the "0 bytes left your machine" showcase |
| **Hero PDF (the planted anomaly)** | One real-ish open-access paper claiming domain spacing is *thermodynamic-only* (no shear/flow dependence) | This is the consensus the local data will **contradict** → triggers anomaly-driven new-principle spawn. The whole "wow" hinges on this |
| **Replacement for current sample** | Current `sample_data/ocean_samples.csv` is the WRONG domain — build the soft-matter fixtures instead | |

> **Build the data so the story is guaranteed:** the local `anneal_sweep.csv` must contain a shear/flow-rate column whose effect the planted PDF denies. The anomaly *must* fire. Tune the numbers offline until `S_s > theta` reliably on `--dry-run`.

---

## The script — beat by beat (180 seconds)

### Beat 0 (0:00–0:15) — One command, then it comes alive
User types ONE line (have it in clipboard / shell history, do not type live):
```
forge run "I study GISAXS of block copolymer thin films at BNL. Data's in ./sims, \
           read the paper in ./refs. What should I test next?" --data ./sims --paper ./refs --dry-run
```
**On screen:** the plan panel streams in as checkboxes (`set_plan`): ingest → profile lab → warmup(5) → rounds → report. *This is the Claude-Code "I can see it thinking" feel.* Narrate: "It just wrote its own plan."

### Beat 1 (0:15–0:40) — Ingestion + the firewall, made visible
Streams: `glob("**/*.{csv,pdf}")` → `ingest(...)` → Evidence tagged `plane=local`. A `/planes`-style line scrolls:
```
LOCAL : sims/anneal_sweep.csv, sims/saxs_profile.csv  → indexed on disk, 0 bytes sent
```
Narrate: "Raw data is tagged LOCAL and physically firewalled — it can never reach a network tool. Watch."

### Beat 2 (0:40–1:05) — THE DIFFERENTIATOR: lab profiling + the trust checkpoint
`discover_lab` → `crawl_profile` runs (WEB plane). Loop **parks** at the confirm-lab checkpoint:
```
I think you're: Soft Matter Group, CMPMS @ Brookhaven National Lab
  homepage  https://www.bnl.gov/cmpms/soft-matter   (confidence 0.86)
  capabilities  GISAXS via NSLS-II 11-BM · benchtop rheometer (in-house) · NO cryo-EM
[Enter] confirm · [e] edit · [s] another · [n] field prior
```
User hits **Enter**. Narrate: "It read our *public* lab page and inferred what instruments we have. That's the wedge — it now judges feasibility for *this* lab." (This is also a natural human-in-the-loop "you're in control" beat.)

### Beat 3 (1:05–1:30) — Warm-up: the GP priors get seeded from the literature
`warmup_loop(5)` streams: principles seeded from the PDF's claims (P5 = "thermodynamic-only"), local sweep rows become warm-up Observations, GPs fit. A round-0 anomaly check runs on the ingested data. Narrate: "It's building a Bayesian model where the *prior* is what the paper claims, and the *data* is yours."

### Beat 4 (1:30–2:10) — THE WOW: anomaly fires → new principle → uncertainty drops
The local shear-dependent data contradicts the paper's thermodynamic-only principle. Anomaly score crosses threshold and streams:
```
⚠ ANOMALY  S=0.91 > θ=0.74  (kind=literature)  local data contradicts Chen-2024
→ Principle Agent spawns P7: "flow/shear during casting shifts equilibrium d-spacing"
   posterior recomputed over {P5,P7}
```
Then a **debate** streams (proponent blue / skeptic red / referee) on the top candidates — back-and-forth visible. Then IDS selects, the experiment-approval checkpoint shows, user approves, `scft_domain_spacing` / `saxs_peak_from_data` runs, posterior updates.

**The visible "uncertainty drops" moment** — print a tiny live entropy/AUOC sparkline that bends after the experiment:
```
posterior entropy  H:  1.38 → 1.05 → 0.61  ▇▆▃   (one principle is winning)
```

### Beat 5 (2:10–2:45) — The payoff: the ranked board + the demoted moonshot
`emit_hypotheses()` renders the ranked table. **The killer contrast row:**
```
 1  H3  Shear rate shifts domain spacing >8%   V=0.81  info 1.9n  feas 0.92  6wk   committed
 4  H9  Substrate stiffness controls defects   V=0.41  info 3.1n  feas 0.30  26wk* split
 ★ NEXT EXPERIMENT (cost-aware IDS): H3 — highest info-gain-per-effort YOU can run.
   H9 has the most raw info (3.1n) but is demoted: needs cryo-EM (not in your profile, ~$5M/26wk).
```
Narrate the single most important sentence of the whole demo: **"The flashiest hypothesis has the most information — but our tool knows *you can't run it*, so it recommends the one you can. That's the difference between a brainstorm and a research plan."**

### Beat 6 (2:45–3:00) — Live re-rank, then drop to prompt
Type `/weights preset moonshot` → board re-sorts in microseconds (cached sub-scores, no LLM). Narrate: "Re-ranks instantly because the scores are cached — and it's still a live REPL; ask it anything next." Leave it at the `forge>` prompt. Done.

---

## The single screenshot that sells it
**Beat 5: the ranked board with H3 recommended and H9 visibly demoted, plus the `★ NEXT EXPERIMENT` line and the bent entropy sparkline in the same frame.** That one image encodes the entire thesis: quantitative info-gain (nats) + equipment-grounded feasibility + a concrete *next action*, with the system visibly having reduced its own uncertainty. If you capture only one still for the slide deck / devpost, it's this. Second choice: the **confirm-lab checkpoint** (Beat 2) — it's the most "wait, it figured out our equipment from the web?" moment.

---

## What can break live, and how to de-risk each

### Tier 1 — will-kill-the-demo risks (eliminate entirely)
| Risk | De-risk |
|---|---|
| **No/expired API keys, rate limits, OpenRouter/DeepSeek down** | Run the whole thing on `--offline` + mock router as the *default demo mode*. The router's terminal `mock` provider returns deterministic, role-aware JSON (per architecture §7). Real keys are a bonus, never a dependency. |
| **Network flakiness on the conference WiFi** (lab crawl / lit search) | **Pre-warm the cache** the morning of: run `forge profile --url <bnl page>` and `lit_search` once on good WiFi so `.forge/cache/` has the crawl + papers. Then run demo with `--no-net` so it reads cache only. Never crawl live. |
| **The anomaly doesn't fire** (the entire wow beat depends on it) | Tune the fixture data offline until `S_s > theta` is deterministic with a fixed seed. Add a demo-mode assertion/test that runs the warm-up and confirms the anomaly triggers before you walk on stage. |
| **Experiments are slow / hang** | `--dry-run` everywhere: observations are drawn from the GP posterior (fast, deterministic via seed). `cahn_hilliard_coarsening` is the only "real numeric" tool — keep it OUT of the critical path or pre-warm it; the closed-form `scft_domain_spacing` is instant. |
| **Whole live run flakes** | **Record `forge replay <session-id>` as the bulletproof fallback.** It re-streams a known-good transcript.jsonl at adjustable speed with zero keys/network. Have it one keystroke away. Honestly: consider running the *replay* as the primary and only going live if WiFi is solid. |

### Tier 2 — annoyance risks (smooth them out)
| Risk | De-risk |
|---|---|
| Typos while typing the long prompt live | Prefill in shell history (`↑`) or clipboard; never type the command live. |
| Token-by-token streaming feels slow on stage | Cap warm-up to 5 rounds, max-rounds ~6 for the demo; set replay `--speed 1.5x`; trim verbose tool output to one-line previews. |
| LLM picks an unexpected tool / goes off-script | Mock/offline mode is deterministic by design — same path every run. Rehearse the *exact* seed. |
| Checkpoints stall waiting for input you forget to give | Know the two gates (confirm-lab = Enter, approve-experiment = Enter). Or pre-set `--auto` so only those two flagship gates stop, and rehearse them. |
| Terminal too small / font unreadable | Big font, wide terminal, dark theme tested on the actual projector resolution. The `rich` tables wrap ugly when narrow — size for the room. |
| Budget/cost panel shows scary numbers | In mock mode cost is $0.00 — leave `/cost` visible as a flex: "entire run, zero dollars." |

### Tier 3 — credibility risks (judges may poke)
| Risk | De-risk |
|---|---|
| "Is the info-gain real or hand-waved?" | Show it's a literal number in nats read from BALD/IDS, not an LLM vibe. The `/card H3` view shows `INFO GAIN 1.9 nats — principles P2 and P5 disagree sharply here.` |
| "Is the dry-run faking results?" | Be upfront: dry-run rows are banner-flagged `DRY RUN — no real experiment executed`; explain they're posterior draws so the loop still learns. Offer to run `cahn_hilliard_coarsening` once for real if asked — "here's an actual numeric experiment." |
| "Did it really not upload my data?" | Run `/planes` → `LOCAL: 2 files read, 0 bytes left the machine`. The firewall is code-enforced (type-structural + dispatch guard + sandbox network kill). This is your defensible moat — rehearse saying it. |

---

## Pre-flight checklist (tape to the laptop)
1. Build hero fixtures: `./sims/anneal_sweep.csv` (with shear column), `./sims/saxs_profile.csv` (clean peak), `./refs/<thermodynamic-only paper>.pdf`. Verify the anomaly fires.
2. Pre-warm caches on good WiFi: lab crawl + lit search → confirm `.forge/cache/` populated.
3. Record a golden session and verify `forge replay <id>` looks perfect — this is the safety net.
4. Set demo defaults: `--dry-run --offline` (or `--no-net`), `--warmup 5 --max-rounds 6`, fixed seed.
5. Prefill the `forge run` command in clipboard + shell history.
6. Rehearse the two checkpoints (lab-confirm, experiment-approve) and the `/weights preset moonshot` re-rank.
7. Big font, wide dark terminal, tested on the projector.
8. Decide go/no-go rule: **WiFi solid → live; any doubt → run `forge replay` and narrate over it.**

**Relevant files:** salvage spine at `/Users/abdollahegazy/bnl/aijam/agents/llm.py` (mock fallback = the offline guarantee), `/Users/abdollahegazy/bnl/aijam/parsers/tabular.py` (loads the local SAXS curve), `/Users/abdollahegazy/bnl/aijam/tools/lit_apis.py` (pre-warm target). Note `/Users/abdollahegazy/bnl/aijam/sample_data/ocean_samples.csv` is the wrong domain — replace with the soft-matter fixtures above before the demo.
