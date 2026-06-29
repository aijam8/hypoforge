"""
Local-plane ingestion. Reuses the salvaged parsers/ registry to open whatever the
user points at (CSV, PDF, MD, HDF5, ...) and normalizes each into a compact
Evidence record. Everything ingested here is tagged plane='local' and its bytes
are counted as "read locally / 0 sent".
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field

# make the project root importable so we can reuse parsers/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from parsers import registry  # noqa: E402


@dataclass
class Evidence:
    path: str
    kind: str
    plane: str
    summary: str
    bytes_read: int
    quantities: dict = field(default_factory=dict)   # name -> structured
    claims: list = field(default_factory=list)
    dataframe: object = None
    profile: dict = field(default_factory=dict)


def _expand(paths: list[str]) -> list[str]:
    out = []
    for p in paths:
        if os.path.isdir(p):
            for root, _, files in os.walk(p):
                out.extend(os.path.join(root, f) for f in files
                           if not f.startswith("."))
        elif os.path.isfile(p):
            out.append(p)
    return out


def ingest(paths: list[str], plane: str = "local") -> list[Evidence]:
    evidence: list[Evidence] = []
    for path in _expand(paths):
        try:
            parsed = registry.parse_file(path)
        except Exception as e:
            evidence.append(Evidence(path, "error", plane,
                                     f"could not parse: {e}", _size(path)))
            continue
        ev = Evidence(
            path=path,
            kind=parsed.get("kind", "generic"),
            plane=plane,
            summary=parsed.get("summary", "")[:400],
            bytes_read=_size(path),
            dataframe=parsed.get("dataframe"),
            profile=parsed.get("profile", {}),
        )
        # pull any literature claim from a document (used to seed principles)
        if parsed.get("kind") == "document" and parsed.get("text"):
            ev.claims = [parsed["text"][:600]]
        evidence.append(ev)
    return evidence


def _size(path: str) -> int:
    try:
        return os.path.getsize(path)
    except OSError:
        return 0
