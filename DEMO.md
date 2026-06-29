# HypoForge — Demo Runbook

**One-liner:** *"Not what's novel, but what's worth running on the bench you actually own."*

Everything below runs **fully offline, no API keys, deterministic** (mock LLM +
canned lab profile + fixed-seed data). Nothing can break from wifi or rate limits.

## Setup (once)
```bash
cd /Users/abdollahegazy/bnl/aijam
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
chmod +x forge
```

## The three commands

```bash
# 1. THE DEMO — full agentic run (paced, looks live, but is offline+scripted)
./forge run

# 2. THE SAFETY NET — re-stream a pre-recorded golden run, identical output
./forge replay              # replays the latest session
./forge replay run-6cf6e468 # or a specific one ; add --speed 1.5

# 3. THE WEDGE, standalone — the inferred lab capability profile
./forge profile
```
`python -m hypoforge run` works too if you don't want the wrapper.
Useful flags: `--fast` (no typewriter pacing, for testing), `--no-debate`,
`--rounds N`, `--live-experiments`.

## What the judges see (≈3 min, the beats)

1. **Plan panel streams** — "it wrote its own plan" (ingest → profile → warm-up → loop → debate → report).
2. **Ingest (LOCAL plane)** — reads `anneal_sweep.csv`, `saxs_profile.csv`, the preprint → `✓ LOCAL plane sealed — 0 sent`.
3. **THE WEDGE** — discovers the lab on the public web (OpenAlex/ROR/BNL), prints the inferred instrument list, confirm-lab checkpoint.
4. **Warm-up** — seeds principle **P0 "spacing is temperature-only"** from the preprint; fits the GP; entropy `H = 0.59`.
5. **THE WOW** — the closed loop runs; the very first shear measurement **fires the anomaly** (`S=0.99 > θ=0.70`): *your data contradicts the published consensus*. A new principle **P1 "shear-dependent"** is spawned (approve checkpoint), and the **entropy sparkline bends `0.59 → 0.15 → 0.06 → 0.00`** as belief collapses onto P1.
6. **Debate** — proponent/skeptic/referee on the top hypotheses; the **referee visibly moves a score** (H7 novelty `0.82 → 0.34` after the skeptic cites a real near-neighbor paper) and it re-ranks.
7. **THE PAYOFF (one screenshot)** — the ranked board:
   - **★ #1 "Steady shear raises equilibrium domain spacing"** — recommended; *directly tests the anomaly we just found*, runnable in-house (~3 wks).
   - **✗ #7 "Cryo-tomography…"** — **2.15 nats, the most raw information of all** — but **struck through and demoted**: needs cryo-EM the lab doesn't have (~27 wks). *"A brainstorm, not a research plan."*
   - **`★ NEXT EXPERIMENT`** line states exactly what to run and why.
8. **`/planes` firewall** — `LOCAL: 3 files read, 0 bytes left the machine`. The receipt.

## The three sentences that win the room
1. *"The flashiest hypothesis has the most information — but our tool knows you can't run it, so it recommends the one you can."*
2. *"Your local data contradicted the published consensus, and the tool caught it — that's the anomaly that spawned a new principle."*
3. *"We profiled your lab from the public web, but your raw scattering data never left this machine. Here's the audit log: zero bytes."*

## If anything feels risky live
Run `./forge replay` instead of `./forge run` — byte-for-byte identical output,
zero dependencies. Decide by a wifi/laptop check before you walk up.
