"""
Literature-review agent.

Fans the understanding agent's search queries out across Semantic Scholar, arXiv,
OpenAlex and the web (in parallel), then asks the LLM to synthesize the corpus
into: a state-of-the-field summary, the dominant findings, and — most important —
explicit *knowledge gaps* the data could help fill.
"""
from __future__ import annotations

import os

from tools import lit_apis
from .llm import call_json

_SYSTEM = (
    "You are a meticulous research librarian and domain scientist. You read paper "
    "abstracts and identify what is well-established versus what remains unknown, "
    "contested, or unstudied. You never invent citations."
)


def review(understanding: dict, sources: list[str] | None = None,
           per_source: int | None = None) -> dict:
    queries = understanding.get("search_queries") or []
    queries = [q for q in queries if isinstance(q, str) and q.strip()][:6]
    if not queries:
        queries = [understanding.get("domain", "scientific data analysis")]

    per_source = per_source or int(os.getenv("MAX_PAPERS_PER_SOURCE", "8"))
    papers = lit_apis.search_all(queries, sources=sources, per_source=per_source)
    real_papers = [p for p in papers if not p.get("_error")]
    errors = [p for p in papers if p.get("_error")]

    synthesis = _synthesize(understanding, real_papers)
    return {
        "queries": queries,
        "papers": real_papers,
        "source_errors": errors,
        "n_papers": len(real_papers),
        "field_summary": synthesis.get("field_summary", ""),
        "established_findings": synthesis.get("established_findings", []),
        "knowledge_gaps": synthesis.get("knowledge_gaps", []),
        "open_questions": synthesis.get("open_questions", []),
    }


def _synthesize(understanding: dict, papers: list[dict]) -> dict:
    corpus = _format_corpus(papers)
    prompt = f"""We are studying data described as: {understanding.get('description', '')}
Domain: {understanding.get('domain', 'unknown')}
Key variables: {understanding.get('key_variables', [])}

Below are abstracts retrieved from the literature ({len(papers)} papers).
Read them and characterize the state of knowledge.

LITERATURE CORPUS:
{corpus}

Return JSON:
{{
  "field_summary": "3-5 sentence synthesis of what this field currently knows",
  "established_findings": ["well-supported facts relevant to our data (max 6)"],
  "knowledge_gaps": ["specific, concrete gaps / unanswered questions / contradictions the literature reveals (max 8). Each should be something our data could plausibly help address."],
  "open_questions": ["broader open questions in the field (max 5)"]
}}"""
    res = call_json(prompt, _SYSTEM, temperature=0.4)
    if not isinstance(res, dict) or res.get("_parse_error"):
        return {"field_summary": "", "established_findings": [],
                "knowledge_gaps": [], "open_questions": []}
    return res


def _format_corpus(papers: list[dict], limit: int = 28) -> str:
    rows = []
    for i, p in enumerate(papers[:limit], 1):
        abstract = (p.get("abstract") or "").strip().replace("\n", " ")
        if len(abstract) > 600:
            abstract = abstract[:600] + "…"
        cite = f", cited {p['citations']}x" if p.get("citations") else ""
        yr = p.get("year") or "n.d."
        rows.append(f"[{i}] ({p.get('source')}, {yr}{cite}) {p.get('title')}\n"
                    f"    {abstract or '(no abstract available)'}")
    return "\n\n".join(rows) if rows else "(no papers retrieved)"
