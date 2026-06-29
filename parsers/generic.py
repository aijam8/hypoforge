"""Last-resort parser for unknown / binary files."""
from __future__ import annotations

import os


def parse(path: str, ext: str = "", error: str | None = None) -> dict:
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        head = f.read(2048)
    try:
        text = head.decode("utf-8")
        is_text = True
    except UnicodeDecodeError:
        text = head[:256].hex(" ")
        is_text = False

    notes = ["Fell back to generic parser."]
    if error:
        notes.append(f"Specialized parser failed: {error}")

    profile = {
        "size_bytes": size,
        "extension": ext,
        "is_text": is_text,
        "head_hex": head[:64].hex(" ") if not is_text else None,
    }
    summary = (f"Unrecognized file '{os.path.basename(path)}' ({size} bytes, "
               f"ext '{ext or 'none'}'). "
               + ("Appears to be text; first bytes shown."
                  if is_text else "Appears binary; hex header captured."))
    return {
        "kind": "generic",
        "filename": os.path.basename(path),
        "summary": summary,
        "profile": profile,
        "dataframe": None,
        "text": text if is_text else None,
        "preview": text,
        "notes": notes,
    }
