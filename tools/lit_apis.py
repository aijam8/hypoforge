"""
Literature-search clients. All free, no API keys required.

Each returns a list of normalized Paper dicts:
    {"title", "abstract", "year", "authors", "url", "citations", "source"}

`search_all()` fans the same queries out across every source in parallel.
"""
from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

_TIMEOUT = 20
_HEADERS = {"User-Agent": "HypoForge/1.0 (hackathon research assistant)"}


# --------------------------------------------------------------------------- #
#  Individual sources
# --------------------------------------------------------------------------- #
def semantic_scholar(query: str, limit: int = 8) -> list[dict]:
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {"query": query, "limit": limit,
              "fields": "title,abstract,year,authors,url,citationCount"}
    try:
        r = requests.get(url, params=params, headers=_HEADERS, timeout=_TIMEOUT)
        if r.status_code == 429:
            time.sleep(2)
            r = requests.get(url, params=params, headers=_HEADERS, timeout=_TIMEOUT)
        r.raise_for_status()
        out = []
        for p in r.json().get("data", []) or []:
            out.append({
                "title": p.get("title", ""),
                "abstract": p.get("abstract") or "",
                "year": p.get("year"),
                "authors": [a.get("name", "") for a in (p.get("authors") or [])][:6],
                "url": p.get("url", ""),
                "citations": p.get("citationCount", 0),
                "source": "Semantic Scholar",
            })
        return out
    except Exception as e:
        return [_err("Semantic Scholar", e)]


def arxiv(query: str, limit: int = 8) -> list[dict]:
    try:
        import arxiv as _arxiv

        search = _arxiv.Search(query=query, max_results=limit,
                               sort_by=_arxiv.SortCriterion.Relevance)
        out = []
        for res in _arxiv.Client(page_size=limit, delay_seconds=0, num_retries=2).results(search):
            out.append({
                "title": res.title,
                "abstract": (res.summary or "").replace("\n", " "),
                "year": res.published.year if res.published else None,
                "authors": [a.name for a in res.authors][:6],
                "url": res.entry_id,
                "citations": None,
                "source": "arXiv",
            })
        return out
    except Exception as e:
        return [_err("arXiv", e)]


def openalex(query: str, limit: int = 8) -> list[dict]:
    url = "https://api.openalex.org/works"
    params = {"search": query, "per-page": limit,
              "select": "title,abstract_inverted_index,publication_year,"
                        "authorships,doi,cited_by_count"}
    try:
        r = requests.get(url, params=params, headers=_HEADERS, timeout=_TIMEOUT)
        r.raise_for_status()
        out = []
        for w in r.json().get("results", []) or []:
            out.append({
                "title": w.get("title", "") or "",
                "abstract": _deinvert(w.get("abstract_inverted_index")),
                "year": w.get("publication_year"),
                "authors": [a.get("author", {}).get("display_name", "")
                            for a in (w.get("authorships") or [])][:6],
                "url": w.get("doi") or "",
                "citations": w.get("cited_by_count", 0),
                "source": "OpenAlex",
            })
        return out
    except Exception as e:
        return [_err("OpenAlex", e)]


def web(query: str, limit: int = 6) -> list[dict]:
    """Free web search via DuckDuckGo (no key)."""
    try:
        try:
            from ddgs import DDGS  # package was renamed from duckduckgo_search
        except ImportError:
            from duckduckgo_search import DDGS

        out = []
        with DDGS() as ddgs:
            for hit in ddgs.text(query, max_results=limit):
                out.append({
                    "title": hit.get("title", ""),
                    "abstract": hit.get("body", ""),
                    "year": None,
                    "authors": [],
                    "url": hit.get("href", ""),
                    "citations": None,
                    "source": "Web",
                })
        return out
    except Exception as e:
        return [_err("Web", e)]


# --------------------------------------------------------------------------- #
#  Fan-out
# --------------------------------------------------------------------------- #
_SOURCES = {
    "semantic_scholar": semantic_scholar,
    "arxiv": arxiv,
    "openalex": openalex,
    "web": web,
}


def search_all(queries: list[str], sources: list[str] | None = None,
               per_source: int = 8) -> list[dict]:
    """Run every (source, query) pair in parallel; dedupe by title."""
    sources = sources or list(_SOURCES)
    jobs = [(s, q) for s in sources if s in _SOURCES for q in queries]
    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=min(12, len(jobs) or 1)) as ex:
        futs = {ex.submit(_SOURCES[s], q, per_source): (s, q) for s, q in jobs}
        for fut in as_completed(futs):
            try:
                results.extend(fut.result() or [])
            except Exception:
                pass
    return _dedupe(results)


def _dedupe(papers: list[dict]) -> list[dict]:
    seen, out = set(), []
    for p in papers:
        if p.get("_error"):
            out.append(p)
            continue
        key = (p.get("title") or "").strip().lower()[:120]
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(p)
    # most-cited / most-substantive first; errors sink to the bottom
    out.sort(key=lambda x: (x.get("_error", False),
                            -(x.get("citations") or 0),
                            -len(x.get("abstract") or "")))
    return out


def _deinvert(inv: dict | None) -> str:
    """OpenAlex stores abstracts as an inverted index; rebuild the text."""
    if not inv:
        return ""
    positions: list[tuple[int, str]] = []
    for word, idxs in inv.items():
        for i in idxs:
            positions.append((i, word))
    positions.sort()
    return " ".join(w for _, w in positions)[:2000]


def _err(source: str, e: Exception) -> dict:
    return {"title": f"[{source} unavailable]", "abstract": str(e)[:200],
            "year": None, "authors": [], "url": "", "citations": None,
            "source": source, "_error": True}
