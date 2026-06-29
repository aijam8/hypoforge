"""
Data-Understanding agent.

Takes the parser's structured summary and produces a light semantic read of the
data: what domain it's from, the key variables/entities, what questions it could
answer, and — crucially — the search queries the literature agent should run.
"""
from __future__ import annotations

from .llm import call_json

_SYSTEM = (
    "You are a senior research data scientist. You are handed an automated "
    "profile of an unknown dataset or document. Infer what it is and what it is "
    "about, soberly and without overclaiming. Be concrete."
)


def understand(parse_result: dict) -> dict:
    kind = parse_result["kind"]
    prompt = f"""Here is an automated profile of an uploaded {kind} file named \
"{parse_result['filename']}".

PROFILE / SUMMARY:
{parse_result['summary']}

STRUCTURED DETAILS (truncated):
{_trim(parse_result.get('profile'))}

Analyze it and return JSON with EXACTLY these keys:
{{
  "domain": "the scientific/technical field this most likely belongs to",
  "data_nature": "what this data physically represents (1-2 sentences)",
  "description": "a clear 3-4 sentence description of what the data contains and shows",
  "key_variables": ["the most important variables / entities / concepts (max 8)"],
  "likely_questions": ["research questions this data could help answer (max 5)"],
  "observed_patterns": ["concrete patterns visible in the profile, e.g. strong correlations, skew, recurring terms (max 5)"],
  "search_queries": ["3-6 focused literature-search queries to find related work and knowledge gaps for this data"]
}}"""
    result = call_json(prompt, _SYSTEM, temperature=0.3)
    if not isinstance(result, dict) or result.get("_parse_error"):
        result = _fallback(parse_result)
    result.setdefault("search_queries", [parse_result["filename"]])
    return result


def _trim(obj, limit: int = 2500) -> str:
    import json

    try:
        s = json.dumps(obj, default=str, indent=1)
    except Exception:
        s = str(obj)
    return s[:limit]


def _fallback(parse_result: dict) -> dict:
    return {
        "domain": "unspecified",
        "data_nature": parse_result["summary"][:200],
        "description": parse_result["summary"][:400],
        "key_variables": [c["name"] for c in
                          parse_result.get("profile", {}).get("columns", [])[:8]],
        "likely_questions": [],
        "observed_patterns": [],
        "search_queries": [parse_result["filename"]],
    }
