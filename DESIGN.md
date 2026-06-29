# HypoForge — Final Architecture & Build Plan

*An ultra-agentic CLI that reads your data and your lab, then tells you the single most informative experiment **you can actually run** — and proves your raw data never left the machine.*

Lead architect's note: this document resolves the architects-vs-critics tension by **making calls**. Where the architects specced a 3-month research engine, I've cut it to a hackathon spine with the full design preserved as labeled upside. Every soundness guardrail the statistician demanded that prevents *confidently-wrong output* is promoted to **must-fix**. The product name is **HypoForge**; the CLI binary is `forge`.

> **LOCKED DECISIONS (user, 2026-06-29):**
> 1. **Hero domain = soft-matter @ BNL** (BCP thin films / GISAXS, NSLS-II 11-BM). Engine stays domain-agnostic; only fixtures are domain-specific.
> 2. **Demo = replay-primary** (`forge replay` of a golden transcript), go live only after a venue wifi check.
> 3. **Stage-4 upside (first to build if time) = structured debate that visibly moves a score.** (`/weights` live re-rank and per-principle IDS are the fallbacks if debate slips.)
> 4. **Pitch = balanced** — firewall, feasibility-veto, and info-gain math get roughly equal weight in the 3-minute story.
> 5. LLM backends = OpenRouter + DeepSeek (already chosen); default-offline-mock for the demo, real keys are a bonus.

---

## 1. THE WEDGE

Every other team will wire up agents that read papers and emit a ranked list of hypotheses — that is now table stakes (Google co-scientist, FutureHouse, SciAgents, Sakana all do it at scale we can't match). **HypoForge wins on the one axis no funded lab occupies: it profiles *your specific lab's* equipment and expertise from public web sources, then ranks hypotheses by information-gain-*per-unit-effort-on-your-bench*, with a hard feasibility veto — and it does this behind a code-enforced firewall where your raw experimental data provably never touches the network.** The differentiator is not "more novel ideas," it's the reframing from *idea generator* to *personalized research strategist*: the flashiest hypothesis (3.1 nats, needs a $5M cryo-EM you don't have) gets **demoted below** the one you can run on next month's beamtime — and the `/planes` manifest shows "0 bytes left the machine" as the receipt. That fusion — feasibility-as-veto + a visible data firewall — is the single sentence none of the other 20 demos can say.

---

## 2. REFINED PROBLEM FRAMING

**Submit this framing:**

> Scientific discovery is bottlenecked not by a shortage of hypotheses but by a shortage of *the right hypothesis for the lab that has to test it*. HypoForge is a command-line research strategist that synthesizes a scientist's local data, the published literature, and an automatically-inferred profile of their institution's real instruments and expertise, then runs a closed Bayesian loop that proposes, debates, and self-tests hypotheses — ranking them by quantitative information-gain weighted by what *this* lab can actually execute, while guaranteeing the raw data never leaves the machine.

**Tagline:**

> **HypoForge — not what's novel, but what's worth running on the bench you actually own.**

(Backup tagline if leading with privacy: *"We profile the lab on the public web; your data stays on your disk — here's the receipt."*)

---

## 3. SYSTEM OVERVIEW

```
                            $ forge run "I study GISAXS of block copolymers at BNL.
                              Data in ./sims, read ./refs. What should I test next?"
                                    --data ./sims --paper ./refs --dry-run --offline
                                                │
                  ┌─────────────────────────────▼──────────────────────────────┐
                  │  CLI RUNTIME  (repl.py · rich streaming · plan panel)        │
                  │  RAILS ORCHESTRATOR  — scripted control flow rendered as if  │
                  │  the agent chose each step (LLM fills CONTENT, not control)  │
                  └──┬───────────────┬───────────────┬───────────────┬──────────┘
                     │               │               │               │
        ┌────────────▼───┐  ┌────────▼────────┐  ┌───▼──────────┐  ┌─▼──────────────┐
        │  INGEST        │  │  CAPABILITY      │  │  DISCOVERY    │  │  EVAL / RANK   │
        │  (LOCAL plane) │  │  PROFILING       │  │  ENGINE       │  │  + DEBATE      │
        │  parsers/* →   │  │  (WEB plane)     │  │  (LOCAL plane)│  │                │
        │  Evidence      │  │  discover→crawl→ │  │  principles + │  │  V(h) score,   │
        │  quantities[]  │  │  extract→profile │  │  single/multi │  │  guidance card,│
        │  claims[]      │  │  → feasibility   │  │  GP + IDS     │  │  proponent/    │
        │  vision(figs)  │  │  → CapProfile    │  │  + anomaly    │  │  skeptic/ref   │
        └───────┬────────┘  └────────┬─────────┘  └──────┬───────┘  └───────┬────────┘
                │                    │                    │                  │
   warm-up      │ Quantity[]→(x,y,σ) │ feasibility(h),    │ candidates+      │
   observations │ Claim[]→P_0 priors │ difficulty, effort │ info_gain,regret │
                └────────────────────┴──────────┬─────────┴──────────────────┘
                                                 ▼
                ┌────────────────────────────────────────────────────────────┐
                │  MODEL ROUTER  get_llm(role=…)  · OpenRouter/DeepSeek/mock   │
                │  strategy roles → NON-reasoning crisp;  gen roles → reasoning│
                └────────────────────────────────┬───────────────────────────┘
                                                 ▼
                ┌────────────────────────────────────────────────────────────┐
                │  EXPERIMENT EXECUTOR  (@experiment_tool registry)            │
                │  scft_domain_spacing · cahn_hilliard · saxs_peak_from_data   │
                │  --dry-run posterior draw (banner'd, NON-evidential)         │
                │           ── PLANE GUARD: local_data ⇒ network HARD-OFF ──   │
                └────────────────────────────────┬───────────────────────────┘
                                                 ▼
            RANKED BOARD  +  ★NEXT EXPERIMENT (cost-aware IDS)  +  bent entropy sparkline
            +  /planes manifest ("0 bytes left the machine")  →  drop to forge> REPL
                                                 │
                        persisted every step → .forge/sessions/<id>/  → forge resume / forge replay
```

**Control/data flow, one `forge run`:**

1. **Parse flags → Session** in `./.forge/sessions/<id>/`; everything under `--data` is tagged `plane=local`.
2. **Plan panel** streams a checklist (`ingest → profile → warmup → rounds → report`). *This is the "I can see it thinking" feel — but the steps are a deterministic state machine, not model-chosen.*
3. **Ingest** (LOCAL): `parsers/registry.parse_file` → `Evidence` records → numeric `Quantity[]` + textual `Claim[]`.
4. **Discover + profile lab** (WEB): identity hints → OpenAlex/ROR → crawl homepage → `CapabilityProfile`. **Parks at the confirm-lab checkpoint** (human ratifies in one keystroke).
5. **Warm-up** (~5 rounds): seed principles `P_0` from literature claims; convert `Quantity[]` to warm-up observations; fit GP(s). Round-0 anomaly check on ingested data.
6. **Closed loop** ×N: propose candidates → debate → IDS-select the highest info-gain-per-effort the user *can run* → approve-experiment checkpoint → run (dry-run draw) → update posterior → anomaly check (gated principle birth).
7. **Rank + report**: ranked board with the four guidance fields + `★ NEXT EXPERIMENT` + the demoted-moonshot contrast + entropy sparkline. Drop to REPL. State persisted for `resume`/`replay`.

---

## 4. SUBSYSTEMS

### 4.1 CLI Runtime — *the agentic feel, on rails*

**The single most important architectural call in this document:** we do **not** bet the demo on a cheap LLM autonomously driving a free-form multi-step tool-calling loop. Free OpenRouter models and `deepseek-chat` have flaky function-calling and fall apart over 5+ sequential tool decisions; it will hallucinate a tool name live in front of judges. Instead:

- **Control flow is a scripted state machine** (`runtime/orchestrator.py`, promoted from the prototype's `run_pipeline`). The pipeline `ingest → profile → warmup → round×N → report` is normal Python you control.
- **The LLM fills *content*, never control flow** — it drafts principles, hypotheses, debate turns, explanations. The runtime renders each scripted step *as if* the agent chose it (streaming text, plan checkboxes, tool-start spinners).
- **The REPL is real** (`prompt_toolkit`/`rich`): slash-commands (`/card`, `/why`, `/debate`, `/weights`, `/planes`, `/run`, `/forget`), live token streaming, checkpoint prompts, and `forge resume`/`forge replay`. This delivers the locked "Claude-Code feel" without the brittleness.

**Salvaged:** `agents/orchestrator.py`'s `progress(key,label,frac)` callback → promoted to a typed `EventBus` feeding two sinks: a `rich` `TerminalRenderer` and a `transcript.jsonl` `TranscriptWriter` (which *is* the persistence layer and powers `forge replay`).

**Command surface:**
```
forge run "<prompt>" [paths...]   # main: ingest + closed-loop discovery
forge profile  [--url URL]        # just the capability profile (the wedge, standalone)
forge ingest   <paths...>         # index data into a session
forge resume   [<id>]             # reattach to a session
forge replay   <id> [--speed 2x]  # re-stream a transcript — THE demo safety net
forge forget   [--cache|--all]    # privacy wipe
```
Key flags frozen into `config.lock.json`: `--data` (local roots), `--paper`, `--dry-run`, `--offline`/`--no-net`, `--warmup 5`, `--max-rounds 6`, `--auto` (clears low-risk gates, never experiments/first-egress), `--seed`.

**Free-form tool-calling loop = post-MVP upside on a branch**, only if a strong model + time exist. The rails version ships first and is what we demo.

**Two human-in-the-loop checkpoints** (the trust + control moments, both on the same park/resume mechanism):
- **(a) Confirm lab** — present top-1 inferred identity + capabilities; `[Enter] confirm · [e] edit · [s] another · [n] field-prior`.
- **(b) Approve experiment** — show the IDS-selected hypothesis, the tool+params, and *why this one* (info-gain, regret, feasibility); `[Enter] run · [p] params · [s] skip`.
- **(c) Approve new principle** (added per soundness audit) — before an anomaly spawns a principle, show the residual, the assumed σ, and a "physics or calibration/units?" prompt.

### 4.2 Modular Model Router — `get_llm(role=…)`

Generalizes the prototype's single global `get_llm(temperature)` into a per-role map driven by YAML, over the salvaged `active_provider()`/`call_json`/`_extract_json`/`_MockLLM`. **No agent imports a provider SDK; they pass a role string.** OpenRouter, DeepSeek, and local (Ollama/llama.cpp) all speak the OpenAI chat-completions wire format, so one `openai_compat` adapter covers them; `mock` is the always-present terminal fallback so the tool **never crashes without keys** (salvaged guarantee).

**The PiEvo lesson (c) is encoded as the default `reasoning` flag** — "think-mode hurts the strategic/utility layer −26%; diversity of reasoning conflicts with rigorous utility":

| Role | Layer | Provider · Model | temp | reasoning |
|---|---|---|---|---|
| `orchestrator` | runtime | openrouter · `google/gemini-2.0-flash` | 0.3 | **off** |
| `principle` | **strategy** | deepseek · `deepseek-chat` *(best of cheap tier — lesson b)* | 0.2 | **off** |
| `strategy` / `ids_select` | **strategy/utility** | deepseek · `deepseek-chat` | 0.0 | **off** |
| `feasibility` | **utility** | deepseek · `deepseek-chat` | 0.2 | **off** |
| `extract` | high-volume | openrouter · `meta-llama/llama-3.3-70b-instruct:free` | 0.0 | **off** |
| `discovery` / `normalize` | extraction | openrouter · `google/gemini-2.0-flash` | 0.0 | **off** |
| `hypothesis` | **generation** | openrouter · `deepseek/deepseek-r1` | 0.7 | **on** |
| `critic` / `debate` | **generation** | openrouter · `deepseek/deepseek-r1` | 0.6 | **on** |
| `literature` | comprehension | openrouter · `google/gemini-2.0-flash-thinking-exp` | 0.3 | **on** |
| `referee` | **utility** | deepseek · `deepseek-chat` *(crisp adjudication)* | 0.2 | **off** |
| `vision` | extraction | openrouter · `qwen/qwen2.5-vl-72b-instruct` | 0.0 | off |
| `explain` | generation | openrouter · `deepseek/deepseek-r1` | 0.5 | on |
| `summarize` | compaction | openrouter · `<cheap small>` | 0.0 | off |

**Resolution precedence:** env var → `roles.<role>` → `defaults`. `fallback_chain: [openrouter, deepseek, local, mock]`. **Critic's call honored:** *no* pricing.yaml / budget downgrade-ladder for the hackathon — that's a lot of code for near-zero demo value. We ship one thin extra: `ledger.record()` appends `{role, model, tokens, usd, latency}` to `usage.jsonl`, so `forge cost` can flex "$0.00 — entire run, zero dollars" in mock mode. Pricing/downgrade is post-MVP.

### 4.3 Multimodal Ingestion + the `Evidence` model

Everything — PDF, CSV, HDF5 sim dump, microscopy TIFF, retrieved abstract — normalizes into **one `Evidence` record**, the single currency the engine consumes.

```python
@dataclass
class Quantity:    # → a warm-up observation candidate (x→y,σ)
    name: str; value: float|None; unit: str|None=None
    uncertainty: float|None=None; conditions: dict=…   # {"T":300,"shear":2.0} → GP input x
    source_locator: str = ""
@dataclass
class Claim:        # → a candidate principle / prior
    text: str; polarity: Literal["asserts","contradicts","open_question"]="asserts"
    confidence: float=0.5; support: list[str]=…
@dataclass
class Evidence:
    id: str; modality: Modality; plane: Literal["local","web"]   # ← the firewall flag
    summary: str; structured_profile: dict
    quantities: list[Quantity]=…; claims: list[Claim]=…
    provenance: dict=…; raw_ref: str|None=None      # PATH only, never bytes
    embedding: list[float]|None=None
```

**Salvaged near-verbatim:** `parsers/registry.parse_file` (+ `_sniff` magic bytes) becomes the Opener Router's deterministic fast-path; `parsers/tabular._load`/`_profile_dataframe`/`_top_correlations` become the structured-profile + `Quantity` extractor; `parsers/document.py` text/section extraction; `parsers/generic.py` is the graceful last-resort fallback (a bad file *never* crashes the pipeline — inherited contract).

**New, MVP-scoped:**
- **Tabular/array → `Quantity[]`**: `top_correlations`, regression slopes, group means become `(x,y,σ)` warm-up points. This is the MVP path.
- **`plane` tagging at ingest**: under a `--data` root → `local`; lit/profile results → `web`.

**New, post-MVP upside (cut first when behind):**
- **Vision pass** replacing `image.py`'s RGB-mean stats: `qwen2.5-vl` → strict-JSON figure extraction (axes, regimes, breakpoints, `quantities`, `claims`). Reuses `call_json`'s robust parser. Swap `pypdf`→PyMuPDF for embedded figures. *Not in the critical demo path.*
- **Large-array/simulation specialization** (out-of-core HDF5/NetCDF field profiling). *Nice-to-have.*

### 4.4 Institution Capability Profiling — **the wedge**

The differentiator, and per the skeptical-judge critique it must be reframed: **not an autonomous oracle, but a fast inferred draft the human ratifies, backing a hard feasibility veto.**

**Discovery ladder** (cheapest→strongest, short-circuit on confident hit), reusing `tools/lit_apis.py` etiquette (`_HEADERS`, 429 backoff, ThreadPool):
1. Pasted URL → skip to crawl. 2. ORCID → employment. 3. **OpenAlex Authors** → `last_known_institution` + **ROR id** + `x_concepts` (a free field-vector). 4. ROR → official homepage + institution **type** (Education/Facility/Government/Company). 5. Web search templates.

**Crawl + extract → `CapabilityProfile`:** polite crawler (robots.txt, same-domain, depth≤2, ≤25 pages, ~1 req/1.5s, on-disk TTL cache); per-section `call_json` (role `cap-extract`) pulls instruments/techniques/compute/expertise with provenance; `normalize.py` maps free-text → ontology (`"11-BM CMS"→synchrotron GISAXS/SAXS`). **Publications backstop:** when a site is thin, mine the group's last ~20 OpenAlex/S2 works' methods for *actively-used* instruments (often more reliable than the marketing page).

**Confidence by source:** facilities page 0.9 · paper methods 0.75 · prose 0.5 · field-prior 0.25 (flagged "assumed — confirm?"). **Institution-tier scaling** (national_lab unlocks synchrotron/HPC/cleanroom; PUI→benchtop) makes the field-prior fallback realistic instead of generic.

**Feasibility output per hypothesis** (the user's four guidance fields):
```
feasibility = Σ_c w(status_c)·confidence_c / N        # status: in_house|shared|collaborator|acquirable|infeasible
difficulty(1–5) = f(#missing, max access_effort, technique complexity, sample count from test_plan)
work_weeks = Σ_steps effort·access_mult     # in_house×1, shared×1.5+lead, collaborator×3, acquirable×6
what_it_explains = the principle pair it discriminates
```

**Critic's hard call honored — feasibility is a VETO, not a garnish:** the demo must show a hypothesis that is #1 by raw info-gain getting demoted below a runnable one, with the dollar figure. If profiling is missing, `feasibility=0.5` (neutral) + flag `feasibility_assumed`.

**Demo guarantee (feasibility critic):** the **canned BNL Soft-Matter `CapabilityProfile` always loads from `fixtures/`.** Live crawl is attempted with a 4s timeout, silent fall back to canned. Pre-warm the cache on good wifi the morning of; run the demo `--no-net`.

### 4.5 Principle-Evolvable Closed-Loop Discovery Engine

The PiEvo adaptation: Bayesian optimization over an **evolving set of natural-language principles**, where "experiments" are local lightweight computations. **Staged hard** per the feasibility critic — the full 5-module math stack (per-principle GP experts + BALD mixture MI + log-Bayes posterior + anomaly augmentation) is easy to get *subtly wrong and impossible to verify under time pressure*, and "numbers that look plausible but are nonsense are worse than no numbers."

**MVP (Stage 1–3):** **a single `sklearn` `GaussianProcessRegressor`**, info-gain = **variance-reduction proxy** `½·log(1+σ²(h)/σ_obs²)`. One GP, no per-principle experts, no mixture BALD. Real, explainable, defensible numbers without the degeneracy risk. The loop visibly runs N rounds, "runs" a dry-run experiment, refits the GP, re-ranks — the optimization curve bends. That is a complete, honest closed-loop proof.

**Upside (Stage 4, pick ONE):** per-principle GP experts + true mixture IDS, *or* anomaly-driven principle augmentation, *or* structured debate. Full math in §5.

**Three agents** (thin `get_llm(role=…)` calls):
- **Principle Agent** (`principle`, crisp non-reasoning, best-of-cheap): seed `P_0` from literature claims; on a *gated, approved* anomaly, draft the reconciling principle.
- **Hypothesis Agent** (`hypothesis`, reasoning): salvages `agents/hypothesis.py`'s multi-framing; under the MAP principle emits K candidates with `x_target`, tagged explore/exploit.
- **Experiment Agent** (`experiment`, non-reasoning + tools): maps chosen `h` → registered tool → `Observation(y,σ)`.

**The semantic bridge — corrected per soundness §1.** Naïve `φ(h,P)=[e_h·e_P, ‖e_h−e_P‖]` is the *load-bearing wall and it's cracked*: sentence embeddings encode topical similarity, not physical compatibility — "annealing *raises* d-spacing >8%" and "annealing *lowers* it >8%" embed at cosine >0.9, so the kernel smooths physically-opposite hypotheses together, and numeric thresholds ("> 8%") are nearly invisible. **Fix (must-do):** parse each hypothesis into **structured claim features — (signed direction, magnitude, threshold, variable)** — and put *those* in the numeric block `ψ(x)` as the **spine**; the embedding terms are a **weak auxiliary** with a **negation/sign hard-separator** that forces opposite-sign hypotheses far apart regardless of cosine.

**Embedding backend — feasibility critic's call:** **TF-IDF / hashing vectorizer (sklearn, already a dependency) is the DEFAULT**, killing the ~100MB `sentence-transformers` live-download risk on conference wifi. `bge-small` is optional and only if vendored into the repo ahead of time. Since the embedding is now demoted to auxiliary, the weaker vectorizer is acceptable. Embeddings are deterministic and cheap → zero LLM budget (honors the cheap-LLM preference).

**Anomaly-vs-literature** (the creativity engine): GP prior means are seeded from the literature relationship, so the calibrated residual `S_s = 1−exp(−|z|)` measures *your local data contradicting published consensus*. **Guardrails (must-fix per soundness §4):** principle birth is **human-gated**; require **≥k replicated points** exceeding *both* statistical significance *and* a domain effect-size floor; derive the literature σ **from the literature** (reported error bars / digitization / extrapolation distance), **never the hard-coded 1.0**; run a **units/normalization sanity pass first** and route those to "data issue," not "discovery." For the demo, the planted anomaly fires deterministically and the user approves it at the checkpoint — a clean human-in-the-loop beat.

### 4.6 Hypothesis Evaluation & Ranking

Upgrades `agents/validation.py`'s parallel critic panel into a calibrated composite. Seven sub-scores in [0,1] → one scalar `V(h)` = "research value per unit effort." Two axes (`I`, `W`) are **numbers the system already has** (read, not re-judged); three (`D`,`N`,`E`) are hybrid (numeric prior + LLM nudge clamped to a band); two (`T`, half of `N`) are rubric LLM judgments.

```
quality = w_I·I^β + w_E·E + w_N·N + w_D·D_score + w_W·W      # merit block
gate    = F^γF · T^γT                                         # feasibility & testability VETO
V(h)    = gate · quality
```
Defaults: `{I:0.34, E:0.18, N:0.18, D:0.15, W:0.15}`, `gates {F:1.0, T:0.7}`. The veto correctly *kills* (not averages-down) a high-info hypothesis you can't run or can't falsify. **`/weights preset {cheap_wins|moonshot|novelty}` re-ranks in microseconds from cached sub-scores — no LLM re-call** (the "feels live" moment). Novelty `N` has an **embedding-distance spine** (LLM may only flex ±0.2) so the model can't call everything novel; the nearest paper is shown ("0.34 from Chen 2024").

**The bridge back to the loop:** the user-facing ranking and the engine's next-experiment choice are the **same objective**, expressed two ways (`selection_score(mode="ids"|"value")`) — no gap between what the tool says and what it does.

### 4.7 Multi-Agent Debate

Runs on **top-3 only** (cost control), as the *credibility* upgrade, not the headline (every team has critic agents). Three roles, PiEvo-routed: **Proponent** (reasoning, blue) and **Skeptic** (reasoning, red) generate arguments; the **Referee** (*crisp non-reasoning*) is the only agent allowed to move a score — lesson (c) in action. Bounded ≤2 rounds, terminates on settled/convergence(<0.02)/max-rounds. **The proof it matters:** debate visibly *moves a score* (H7 novelty downgraded after the skeptic cites a real near-neighbor paper). Surfaced via `/why H3` (referee rulings) and `/debate H7` (full color-coded transcript). **Critic's call:** if behind, this degrades to a 2-pass critic over the salvaged `validation.py` — it's Stage-4 upside, not spine.

---

## 5. THE INFORMATION-GAIN MATH

Stated plainly, with the soundness caveats promoted to first-class. **The headline number is renamed everywhere** — per the statistician and the skeptical judge — from "quantitative information gain" to **"expected model-discrimination (proxy, nats)."** That one honest label defuses most of the over-claim.

**Design space & bridge (Eq. 2, corrected):**
```
ψ(x_h) = [ standardized continuous knobs, one-hot categoricals,
           SIGNED direction, magnitude, threshold ]      ← the spine (structured claim features)
φ(h,P) = [ e_h·e_P , ‖e_h−e_P‖ , ψ(x_h) ]                ← embedding terms are WEAK auxiliary
```
with a sign-separator so opposite-effect hypotheses are far apart. Kernel: two-block RBF (semantic block × physics block, separate lengthscales) + white noise.

**Acquisition — cost-aware IDS (Eq. 1):**
```
h_t = argmin_h   Δ_t(h)²  /  ( I_t(h)^β · F(h) )
```
- `Δ_t(h) = |v* − μ̄(h)|`, `μ̄(h)=Σ_P w_t(P)·μ_P(h)`, `v*` = best believed attainable over the candidate pool.
- `F(h)` = feasibility from the capability profile (this is **no longer pure IDS** — label it a *"feasibility-weighted acquisition heuristic"*, and show `I` and `F` **un-merged** on the card so the user sees the value judgment as a value judgment).
- `β>1` exploration (diversity/APD), `β<1` exploitation (efficiency/AUOC) — the `--beta` / `/weights` knob.

**Information term — BALD over principle identity (Eq. 3):**
```
I_t(h) = H[ Σ_P w_P N(μ_P, s_P²) ]  −  Σ_P w_P · H[ N(μ_P, s_P²) ]      (mixture − mean component)
       + ½·log(1 + σ²_MAP(h)/σ_obs²)                                     (GP epistemic, reported SEPARATELY)
```
MVP collapses this to the single-GP epistemic term alone (variance-reduction proxy).

**Posterior over principles (Eq. 4), log-space:**
```
log p_{t+1}(P) = log p_0(P) + Σ_s log N( y_s ; μ_P(h_s), σ_P²(h_s)+σ_obs² )
```

**Anomaly (Eq. 3'):** `z=(y−μ)/√(σ²+σ_obs²)`, `S=1−exp(−|z|)`, adaptive Bonferroni `θ_t`.

### Soundness guardrails — the non-negotiables (fold these into the code, surface them in the UI)

**MUST-FIX before any live demo (these otherwise produce confidently-wrong output):**
1. **Dry-run and `fit_surrogate` observations must NOT update beliefs/confidence.** A dry-run `y` is *sampled from the current posterior* — feeding it back is a self-fulfilling loop that contracts entropy and fires "converged" with zero real information. Set dry-run effective `σ_obs=∞` (exercise the pipeline, update nothing) and **exclude it from every entropy/stopping/confidence computation**; banner every dry-run number "PIPELINE TEST — NOT EVIDENCE." Tag `fit_surrogate` as `source="model_extrapolation"`, exclude from the principle likelihood, never let it trigger anomalies (it double-counts its own training data).
2. **Negation/sign separator in the kernel** (§4.5) — without it the surrogate is *actively wrong*, not merely noisy.
3. **Rename → "expected model-discrimination (proxy, nats)"** on every surface; make the `literature_proxy` caveat **non-dismissible**, not a footnote.
4. **Human gate on principle birth** (§4.5) — most real "anomalies" are units/calibration bugs, not discoveries; auto-spawning inflates `P_t` with principles that reconcile your own normalization errors.

**CHEAP, HIGH-CREDIBILITY additions (do these — they're recomputes over cached scores, no new LLM calls):**
5. **LOO calibration / PIT coverage gate.** Before any "anomaly" or "converged" claim, check ~90% of held-out `y` land in 90% predictive intervals; report ECE. **If coverage fails, drop to "ranking only — uncertainty unreliable" mode and grey out the nats.** A tool that shows its own calibration failing is *more* credible than one that always prints a confident 1.9.
6. **Prior-/assumption-sensitivity panel:** re-rank with σ×2, semantic kernel dropped, prior weights halved. Stable top experiment → say so (earns trust); flips → flag "fragile to assumptions."
7. **Provenance tags on every headline number:** `n_real` (genuine measurements vs surrogate/dry-run draws), `proxy?` (embedding-mediated?), `calibrated?` (passed LOO?). Show **intervals, not points.**

**Structural honesty:**
- **M-open fix:** add an explicit **"none-of-the-above" principle** carrying real prior mass; if its weight grows, grey out the MI numbers.
- **No GP hyperparameter optimization below ~15 calibrated points** — on 5 points in ~10 effective dims the lengthscales/noise are unidentified and the σ you'd propagate is fabricated; use fixed domain-reasonable priors and display "priors only — σ not data-identified." Prefer **conformal predictive intervals** for anything user-facing (finite-sample coverage a 5-point GP can't give).
- **Pre-register** `predicted_outcome` + threshold *before* running; evaluate the real result against the frozen prediction ("pre-registered: d>8%; observed: 6% → not supported").
- **Stopping safety:** never emit "converged/good-enough" without ≥`N_min` *real* observations AND a passed calibration check.

**Honest framing for judges (say it out loud):** *what we have is a defensible decision-support and exploration-prioritization heuristic that is transparent about its proxies — not a calibrated measurement of information about nature.* The credibility move is the **AUOC-vs-random ablation plot** on the real `cahn_hilliard` solver: IDS selection converging faster than random/greedy. **Without that plot, drop the nats from the headline and lead entirely with feasibility + firewall.**

---

## 6. TWO DATA PLANES

The defensible moat, and per the skeptical judge **the actual pitch centerpiece** — stronger and more demoable than either named wedge, because it's *code, not a promise*, and *visible*.

| | **LOCAL plane** | **WEB plane** |
|---|---|---|
| Contents | raw experimental files (`parsers/` output, `Evidence.plane="local"`) | identity/field **metadata** only (name, lab, field, public URLs) |
| Network | **never** | search/crawl public pages only (`lit_apis` etiquette) |
| To the LLM | only *derived* scalars/summaries | metadata + fetched public text |

**Enforcement — lean, per the feasibility critic (single dispatch guard + manifest, NOT the 3-layer fortress):**
1. **Type-structural:** capability/discovery functions accept only `IdentityHints`/`Identity` dataclasses — structurally incapable of receiving a local `Evidence`/`ParseResult`. (Free; just function signatures.)
2. **Dispatch guard** at the one tool chokepoint (`runner.run_experiment`): a tool whose `touches` includes `network` is **refused** if any input Evidence is `plane=local`; `local_data` tools run with **network hard-off**.
3. **`/planes` manifest** printed in the REPL — the trust artifact:
```
hypoforge> /planes
  LOCAL : 2 files read, 0 bytes left the machine
  WEB   : 9 pages fetched (bnl.gov, openalex.org, ror.org) — metadata only
  audit : .forge/sessions/<id>/manifest.json   ·   /forget wipes it
```

**Cut from the architects' design:** the outbound fingerprint/redaction tripwire and the docker socket-kill sandbox — overkill for a hackathon; the single dispatch guard + manifest gets 100% of the demo credibility. (Fingerprint tripwire is a labeled post-MVP hardening.) **Sandbox call:** builtin tools are trusted pure-Python → run in-process (Tier C); only a user-supplied solver binary needs the rlimit subprocess (Tier B); docker (Tier A) only if time permits.

---

## 7. REPO LAYOUT

Leaner than the architects' six-package sprawl (feasibility critic: ~40 files = "40% half-working, nothing demoable"). Salvaged code **stays where it is** and is imported; new code is consolidated.

```
aijam/
├── parsers/                 # SALVAGED in place — registry, tabular, document, image, generic
├── tools/lit_apis.py        # SALVAGED in place — 4 sources, 429 backoff, dedupe
├── agents/llm.py            # SALVAGED — becomes the substrate under hypoforge/router.py
│                            #   (validation.py, hypothesis.py logic migrate into hypoforge/)
├── app.py                   # RETIRED (Streamlit) — orchestration logic survives as a tool
│
├── hypoforge/               # THE NEW PACKAGE
│   ├── __main__.py  cli.py  repl.py
│   ├── runtime/
│   │   ├── orchestrator.py  # RAILS state machine (promoted run_pipeline)
│   │   ├── bus.py render.py # EventBus + rich renderer + transcript writer
│   │   ├── session.py state.py   # .forge/ project dir, autosave, resume/replay
│   │   ├── checkpoint.py planner.py
│   ├── router.py            # get_llm(role=…) over agents/llm.py + mock fallback
│   ├── core/evidence.py     # Evidence, Quantity, Claim
│   ├── ingest/              # opener router (wraps parsers) → Evidence; (vision.py = upside)
│   ├── capability/          # discovery, crawl, extract, normalize, priors, feasibility, schema  ← WEDGE
│   ├── engine/
│   │   ├── state.py bridge.py embed.py      # TF-IDF embed (sklearn); structured-feature spine
│   │   ├── gp.py            # single GP (MVP) → per-principle experts (upside)
│   │   ├── infogain.py posterior.py anomaly.py
│   │   ├── calibration.py   # LOO/PIT gate, conformal intervals, sensitivity panel
│   │   └── loop.py          # warmup + round state machine + stopping
│   ├── evaluation/          # score.py rubrics.py weights.py debate.py present.py record.py
│   ├── experiment/
│   │   ├── registry.py observation.py runner.py dryrun.py schema.py
│   │   └── tools/ generic.py softmatter.py   # scft_domain_spacing, cahn_hilliard, saxs_peak
│   ├── planes/ guard.py manifest.py
│   ├── config/ models.yaml runtime.yaml scoring.yaml field_priors.yaml ontology.yaml
│   ├── prompts/ system_shell.md
│   └── fixtures/            # CANNED BNL profile + hero soft-matter data + planted-anomaly PDF
│
└── .forge/                  # PER-PROJECT state (gitignored): sessions/<id>/{transcript.jsonl,
                             #   plan.json, world.json, evidence/, checkpoints/, manifest.json}, cache/
```

**New deps to pin now:** `typer`, `rich`, `prompt_toolkit`, `pyyaml`. **Deliberately NOT added:** `sentence-transformers` (use sklearn TF-IDF), `pymupdf`/`filetype` (vision/sim ingestion are upside), `gpytorch`, `docker`. `streamlit`/`plotly` become optional.

---

## 8. STAGED BUILD PLAN

**Rule: conference wifi does not exist. Every path completes with `--offline`. Record the golden transcript Night 1.** The cut order when behind, delete in sequence: budget ledger → docker sandbox → fingerprint tripwire → structured debate (→2-pass critic) → anomaly augmentation → per-principle GPs (→single GP) → free-form tool-calling (→rails) → live crawl (→canned). The last two cuts still leave a fully demoable product.

### The Minimal Viable Spine (must work end-to-end before anything else)
`forge run "..." --data ./sims --dry-run --offline` →
1. REPL + `rich` streaming + live plan checklist. 2. Rails orchestrator (`ingest→profile→seed→loop→rank→report`). 3. Ingest local data → a few `(x,y,σ)`. 4. `CapabilityProfile` (canned guaranteed). 5. A loop that visibly runs N rounds updating *something* numeric. 6. Ranked board with the four guidance fields. 7. `--dry-run` + mock LLM → fully offline. **If those 7 work, we have a winning demo. Everything else is upside.**

### Demo fallback for every risky piece (pre-build these, not at 2am)
| Risky piece | Fallback that ALWAYS works |
|---|---|
| Free-form tool-calling | **Rails orchestrator** rendered to look agentic; LLM fills content only |
| Full GP/IDS math | **Single sklearn GP**, variance-reduction info-gain; if it breaks, **precomputed numbers** rendered live |
| Live institution crawl | **Canned BNL `CapabilityProfile`** from `fixtures/`; live attempt 4s timeout → silent canned |
| `sentence-transformers` download | **TF-IDF/hashing vectorizer** (sklearn, already a dep) — never download live |
| Any LLM call (no keys/rate-limit/offline) | Salvaged **`_MockLLM`**, role-aware JSON — runs fully offline |
| Experiment execution | **`--dry-run` posterior draw** (non-evidential, banner'd) |
| Whole live run collapses | **`forge replay <id>`** re-streams a known-good transcript at 2× — deterministic, no keys/net. **The load-bearing safety net; build it early.** |

### ~2-day timeline (2 builders: **A**=runtime/CLI, **B**=engine/numbers)

**Day 1**
- **0:00–1:00 Both:** Scaffold `hypoforge/`, pin deps (`typer rich prompt_toolkit pyyaml`). **Lock hero domain = soft-matter NOW.** Build `fixtures/`: canned BNL profile, `anneal_sweep.csv` (with the shear column the planted PDF denies), `saxs_profile.csv` (clean peak), planted-anomaly PDF. **Commit to TF-IDF embeddings** (kills download risk).
- **1:00–3:00 A:** `router.py` (thin `get_llm(role)` dict over `agents/llm.py`, no ledger) + REPL skeleton with `rich` streaming + static plan panel. **B:** `engine/state.py` + a **single** `GPExpert` (sklearn) on a toy 1-D objective; unit-test sane `(μ,σ)`.
- **3:00–5:00 A:** Rails orchestrator (promote `progress()`→event stream); wrap `parsers/registry.parse_file` as `ingest`; CLI ingests `--data` and prints Evidence. **B:** variance-reduction info-gain + feasibility-weighted `V(h)`; **real ranked board from synthetic candidates.**
- **5:00–7:00 Both — INTEGRATION GATE 1:** `forge run --dry-run --offline` ingests data + prints a ranked board with the four guidance fields. *Not working by EOD1 → cancel Stages 3–4, ship "ingest + profile + ranked hypotheses" (still a fine demo).*
- **7:00–8:00:** `transcript.jsonl` writer → stub `forge replay`. **Record one golden run tonight.**

**Day 2**
- **0:00–2:00 A:** Capability profiling — confirm-lab checkpoint UI + live fetch w/ timeout → canned fallback. **B:** close the loop — multi-round propose→score→dry-run-draw→refit→re-rank; render the bent entropy sparkline. **Apply the dry-run-non-evidential must-fix here.**
- **2:00–4:00 Both — INTEGRATION GATE 2:** full offline path `run→ingest→confirm lab→loop→ranked report`. **Freeze the spine.**
- **4:00–6:00 Build the ONE chosen upside** (time-boxed, revert if not clean): **structured debate that visibly moves a score** (user's pick — best "agents argue" theater; H7 novelty downgraded after the skeptic cites a real near-neighbor paper). If it slips, fall back to `/weights` live re-rank (cheap) or per-principle IDS.
- **6:00–7:00:** `/planes` manifest (firewall story — single guard + manifest). Calibration grey-out + non-dismissible proxy caveat (the cheap credibility wins).
- **7:00–8:00:** Demo hardening — re-record golden transcript, rehearse `forge replay` plan B, write the three judge one-liners. **Stop coding.**

**Go/no-go gates:** EOD1 board prints offline or cut the loop. Day-2 noon full offline path works → freeze; after freeze only additive/revertible features on a branch. Golden transcript recorded Night 1 and re-recorded after freeze.

---

## 9. THE 3-MINUTE DEMO

**Hero assets:** domain = soft-matter/BCP thin films (GISAXS); lab = "Soft Matter Group, CMPMS @ BNL" + NSLS-II 11-BM; local data = `anneal_sweep.csv` (with shear column) + `saxs_profile.csv`; the **planted-anomaly PDF** claims domain spacing is *thermodynamic-only* — the local shear-dependent data contradicts it, firing the anomaly. **Tune the fixtures offline until `S_s>θ` is deterministic under a fixed seed; add a pre-flight assertion that the anomaly triggers before you walk on stage.**

**Open cold, narrate the firewall** (the 30 seconds that contains all three uniquely-ours claims):
> "Here's the most informative hypothesis we found — 3.1 nats, top of the list. We're throwing it away: it needs cryo-EM your lab doesn't have, ~$5M, 26 weeks. Instead, run *this* one — less flashy, but it's the most you can learn on the bench you actually own this week. And while we figured that out, we crawled your institution's public page for capabilities — but watch: your raw scattering data never left this machine. Zero bytes. Here's the audit log."

**Beats:** (0:00) one prefilled command → plan panel streams ("it wrote its own plan"). (0:15) ingest + `LOCAL: 0 bytes sent`. (0:40) **the wedge** — `discover_lab`→`crawl_profile`→ **confirm-lab checkpoint**, hit Enter ("it inferred our instruments from our public page"). (1:05) warm-up — GP priors seeded from the PDF's claim. (1:30) **THE WOW** — anomaly fires (`S=0.91>θ=0.74, kind=literature`), debate streams back-and-forth, IDS selects, approve-experiment checkpoint, experiment runs, and the **entropy sparkline bends**: `H: 1.38→1.05→0.61 ▇▆▃`. (2:10) **the payoff** — ranked board with H3 recommended, **H9 visibly demoted** ("most raw info, but needs cryo-EM you don't have"), and the `★ NEXT EXPERIMENT` line. (2:45) `/weights preset moonshot` → instant re-rank; drop to `forge>`.

**The single 'wow' screenshot** (capture this for the deck): the ranked board with **H3 recommended + H9 demoted + the `★ NEXT EXPERIMENT` line + the bent entropy sparkline in one frame** — it encodes the entire thesis (info-gain + feasibility-veto + concrete next action + visible uncertainty reduction). The one narrated sentence that wins the room: *"The flashiest hypothesis has the most information — but our tool knows you can't run it, so it recommends the one you can. That's the difference between a brainstorm and a research plan."*

**Demo safety:** default to `--offline --no-net --dry-run`, fixed seed, pre-warmed cache. **Strong consideration: run `forge replay` of the golden transcript as the *primary*, going live only if wifi is rock-solid.** Big font, wide dark terminal, tested on the actual projector.

---

## 10. RISKS & OPEN DECISIONS

### Top risks → mitigations
| Risk | Severity | Mitigation (decided) |
|---|---|---|
| Cheap model can't drive a free-form tool loop live | 🔴 | **Rails orchestrator**; LLM fills content only. Free-form loop is post-MVP on a branch. |
| Full GP/IDS math subtly wrong → plausible nonsense numbers | 🔴 | **MVP = single GP + variance-reduction proxy.** Per-principle BALD is one Stage-4 pick, gated by the LOO calibration check. |
| Live institution crawl fails/garbage on stage | 🔴 | **Canned BNL profile always loads**; live attempt 4s timeout → silent canned; pre-warm cache, run `--no-net`. |
| The anomaly doesn't fire (the wow depends on it) | 🔴 | Fixtures tuned offline to deterministic `S_s>θ` under fixed seed + **pre-flight assertion**. |
| "Your nats are about embeddings, not physics" (soundness landmine) | 🔴 | Rename to **"expected model-discrimination (proxy, nats)"**, structured-feature spine + sign-separator, non-dismissible caveat, **AUOC-vs-random ablation plot**; if no plot, **drop nats from the headline**. |
| Dry-run / `fit_surrogate` manufacture false convergence | 🔴 | **Excluded from all belief/entropy/stopping computations**; banner'd non-evidential. (Must-fix.) |
| "Feasibility is a stale web guess, confidently wrong" | 🟠 | Reframe as **human-ratified prefill + hard veto**, not oracle; let the user point at a local CV/grant for ground truth. |
| `sentence-transformers` 100MB live download | 🟠 | **TF-IDF/hashing vectorizer** (sklearn, already a dep); embedding demoted to auxiliary anyway. |
| Whole live demo collapses | 🟠 | **`forge replay`** golden transcript — deterministic, no keys/net. Build early. |
| Over-scope → nothing demoable | 🟠 | Hard go/no-go gates; cut-order list; freeze at Day-2 noon. |

### Decisions — RESOLVED 2026-06-29
1. **Hero domain → soft-matter/BCP-thin-films @ BNL.** Engine domain-agnostic; fixtures domain-specific. Build the fixture set (canned BNL profile, `anneal_sweep.csv` w/ shear column, `saxs_profile.csv`, planted-anomaly PDF) first — anomaly tuned to fire deterministically under a fixed seed.
2. **Demo → replay-primary.** Optimize for a flawless `forge replay` of a golden transcript; go live only after a venue wifi check. Record the golden run Night 1 and after the Day-2 freeze.
3. **Stage-4 upside → structured debate that visibly moves a score** (Proponent/Skeptic/Referee; the Referee — crisp non-reasoning — is the only agent allowed to move a score). Fallbacks if it slips: `/weights` live re-rank, then per-principle IDS.
4. **LLM backends → OpenRouter + DeepSeek.** Default to offline-mock for the demo; real keys are a bonus (live lit-search + crawl pre-warm).
5. **Pitch → balanced:** firewall, feasibility-veto, and info-gain math get roughly equal weight. (Still ship the AUOC-vs-random ablation plot so the nats are defensible when a stats judge probes.)

**Bottom line:** yes — a small team can ship a *credibly-working* HypoForge in two days, but only the **spine + the institution-profiling wedge + the visible data firewall, demoed on rails with canned fallbacks** — not the full closed-loop research engine. Make the agentic feel scripted, make the numbers real-but-simple (one GP, variance-reduction info-gain, renamed and caveated), guarantee the wedge with a canned hero profile, and treat `forge replay` of a pre-recorded run as the load-bearing safety net. The PiEvo math is the part to *gesture at with a working simplification*, not the part to fully implement.