"""
Orchestrator — runs the full pipeline and reports progress via a callback.

    parse → understand → (visualize ‖ literature-review) → hypothesize → validate

Visualization and literature review are independent, so they run concurrently.
The `progress` callback receives (step_key, label, fraction) so the Streamlit UI
can render a live status. The final return is one big result dict.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from parsers import registry
from . import understanding as understanding_agent
from . import visualization as viz_agent
from . import literature as lit_agent
from . import hypothesis as hyp_agent
from . import validation as val_agent

_STEPS = [
    ("parse", "Opening & profiling the data"),
    ("understand", "Understanding what the data is"),
    ("explore", "Visualizing data + reviewing literature (parallel)"),
    ("hypothesize", "Generating novel testable hypotheses"),
    ("validate", "Adversarial validation panel"),
    ("done", "Done"),
]


def run_pipeline(file_path: str, progress=None, sources=None) -> dict:
    def report(key, frac):
        if progress:
            label = dict(_STEPS).get(key, key)
            progress(key, label, frac)

    # 1. Parse -------------------------------------------------------------
    report("parse", 0.05)
    parsed = registry.parse_file(file_path)

    # 2. Understand --------------------------------------------------------
    report("understand", 0.2)
    understanding = understanding_agent.understand(parsed)

    # 3. Visualize ‖ Literature review ------------------------------------
    report("explore", 0.35)
    with ThreadPoolExecutor(max_workers=2) as ex:
        f_viz = ex.submit(viz_agent.visualize, parsed, understanding)
        f_lit = ex.submit(lit_agent.review, understanding, sources)
        figures = _safe(f_viz, [])
        literature = _safe(f_lit, _empty_lit())

    # 4. Hypotheses --------------------------------------------------------
    report("hypothesize", 0.6)
    hypotheses = hyp_agent.generate(understanding, literature)

    # 5. Validate ----------------------------------------------------------
    report("validate", 0.8)
    validated = val_agent.validate_all(hypotheses, understanding, literature)

    report("done", 1.0)
    return {
        "parsed": parsed,
        "understanding": understanding,
        "figures": figures,
        "literature": literature,
        "hypotheses": validated,
        "stats": {
            "n_papers": literature.get("n_papers", 0),
            "n_gaps": len(literature.get("knowledge_gaps", [])),
            "n_hypotheses": len(validated),
            "n_strong": sum(1 for h in validated
                            if h["validation"]["verdict"] in ("strong", "promising")),
        },
    }


def _safe(future, default):
    try:
        return future.result()
    except Exception:
        return default


def _empty_lit():
    return {"queries": [], "papers": [], "source_errors": [], "n_papers": 0,
            "field_summary": "", "established_findings": [],
            "knowledge_gaps": [], "open_questions": []}
