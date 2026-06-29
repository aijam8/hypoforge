"""Image parser: basic metadata + pixel statistics (light understanding)."""
from __future__ import annotations

import os


def parse(path: str, ext: str) -> dict:
    notes: list[str] = []
    from PIL import Image
    import numpy as np

    img = Image.open(path)
    img.load()
    arr = np.asarray(img.convert("RGB"))
    notes.append(f"Opened image via Pillow ({img.format}, mode {img.mode}).")

    profile = {
        "width": img.width,
        "height": img.height,
        "mode": img.mode,
        "format": img.format,
        "aspect_ratio": round(img.width / max(img.height, 1), 3),
        "mean_rgb": [round(float(arr[..., c].mean()), 1) for c in range(3)],
        "std_rgb": [round(float(arr[..., c].std()), 1) for c in range(3)],
        "brightness": round(float(arr.mean()), 1),
    }
    summary = (f"Image '{os.path.basename(path)}' {img.width}x{img.height} "
               f"({img.mode}). Mean RGB {profile['mean_rgb']}, "
               f"overall brightness {profile['brightness']}/255.")
    return {
        "kind": "image",
        "filename": os.path.basename(path),
        "summary": summary,
        "profile": profile,
        "dataframe": None,
        "text": None,
        "preview": path,  # the UI st.image()'s the path directly
        "notes": notes,
    }
