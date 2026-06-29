"""
Session persistence + transcript.

Every emitted event is appended to .forge/sessions/<id>/transcript.jsonl. This IS
the persistence layer and it powers `forge replay` — the deterministic, no-keys,
no-network demo safety net.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(".forge") / "sessions"


class Transcript:
    def __init__(self, session_id: str, record: bool = True):
        self.session_id = session_id
        self.record = record
        self.events: list[dict] = []
        self.dir = ROOT / session_id
        if record:
            self.dir.mkdir(parents=True, exist_ok=True)
            self.path = self.dir / "transcript.jsonl"
            self._fh = open(self.path, "w")
        else:
            self._fh = None

    def emit(self, etype: str, **payload):
        ev = {"type": etype, "payload": payload}
        self.events.append(ev)
        if self._fh:
            self._fh.write(json.dumps(ev, default=str) + "\n")
            self._fh.flush()
        return ev

    def write_manifest(self, manifest: dict):
        if self.record:
            (self.dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

    def close(self):
        if self._fh:
            self._fh.close()


def load_transcript(session_id: str) -> list[dict]:
    path = ROOT / session_id / "transcript.jsonl"
    if not path.exists():
        # allow passing a direct path
        path = Path(session_id)
    events = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def latest_session() -> str | None:
    if not ROOT.exists():
        return None
    sessions = sorted(ROOT.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
    return sessions[0].name if sessions else None
