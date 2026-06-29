"""
Parser registry: given an uploaded file, figure out how to open it and return a
normalized ParseResult dict the rest of the system understands.

ParseResult = {
    "kind":      "tabular" | "document" | "image" | "array" | "generic",
    "filename":  str,
    "summary":   str,            # short text the LLM reads to understand the data
    "profile":   dict,           # structured stats / metadata (JSON-safe)
    "dataframe": pandas.DataFrame | None,   # for tabular -> visualization
    "text":      str | None,     # for documents
    "preview":   Any,            # small object the UI can render directly
    "notes":     list[str],      # parser decisions ("opened as HDF5", fallbacks...)
}
"""
from __future__ import annotations

import os

from . import tabular, document, image as image_parser, generic

# extension -> handler
_TABULAR = {".csv", ".tsv", ".xlsx", ".xls", ".parquet", ".json", ".jsonl",
            ".h5", ".hdf5", ".nc", ".npy", ".npz", ".feather"}
_DOCUMENT = {".pdf", ".docx", ".txt", ".md", ".rst", ".tex"}
_IMAGE = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".tiff", ".webp"}


def parse_file(path: str) -> dict:
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext in _TABULAR:
            return tabular.parse(path, ext)
        if ext in _DOCUMENT:
            return document.parse(path, ext)
        if ext in _IMAGE:
            return image_parser.parse(path, ext)
        # Unknown: sniff content.
        return _sniff(path, ext)
    except Exception as e:  # never let a parser crash the pipeline
        return generic.parse(path, ext, error=str(e))


def _sniff(path: str, ext: str) -> dict:
    """No known extension — peek at the bytes and route intelligently."""
    with open(path, "rb") as f:
        head = f.read(4096)
    # HDF5 magic
    if head[:8] == b"\x89HDF\r\n\x1a\n":
        return tabular.parse(path, ".h5")
    # PDF magic
    if head[:5] == b"%PDF-":
        return document.parse(path, ".pdf")
    # Looks like text?
    try:
        head.decode("utf-8")
        text_like = True
    except UnicodeDecodeError:
        text_like = False
    if text_like:
        sample = head.decode("utf-8", "ignore")
        # crude CSV detection
        if sample.count(",") > sample.count("\n") and "\n" in sample:
            return tabular.parse(path, ".csv")
        return document.parse(path, ".txt")
    return generic.parse(path, ext)
