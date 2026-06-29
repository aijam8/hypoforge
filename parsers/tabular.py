"""Tabular / array parsers: CSV, Excel, Parquet, JSON, HDF5, NumPy, NetCDF."""
from __future__ import annotations

import os

import numpy as np
import pandas as pd


def parse(path: str, ext: str) -> dict:
    notes: list[str] = []
    df = _load(path, ext, notes)
    return _profile_dataframe(df, path, notes)


def _load(path: str, ext: str, notes: list[str]) -> pd.DataFrame:
    if ext in (".csv", ".tsv"):
        sep = "\t" if ext == ".tsv" else None
        df = pd.read_csv(path, sep=sep, engine="python", on_bad_lines="skip")
        notes.append(f"Read delimited text ({ext}).")
        return df
    if ext in (".xlsx", ".xls"):
        df = pd.read_excel(path)
        notes.append("Read Excel sheet (first sheet).")
        return df
    if ext == ".parquet" or ext == ".feather":
        df = pd.read_parquet(path) if ext == ".parquet" else pd.read_feather(path)
        notes.append(f"Read columnar {ext} file.")
        return df
    if ext in (".json", ".jsonl"):
        try:
            df = pd.read_json(path, lines=(ext == ".jsonl"))
        except ValueError:
            df = pd.json_normalize(pd.read_json(path, typ="series"))
        notes.append("Parsed JSON into a table.")
        return df
    if ext in (".npy", ".npz"):
        return _load_numpy(path, ext, notes)
    if ext in (".h5", ".hdf5", ".nc"):
        return _load_hdf5(path, notes)
    # fallback
    notes.append("Unknown tabular extension; tried CSV.")
    return pd.read_csv(path, engine="python", on_bad_lines="skip")


def _load_numpy(path: str, ext: str, notes: list[str]) -> pd.DataFrame:
    obj = np.load(path, allow_pickle=True)
    if ext == ".npz":
        # take the largest array
        arr = max(obj.values(), key=lambda a: getattr(a, "size", 0))
        notes.append(f"Loaded .npz; using array '{arr.shape}'.")
    else:
        arr = obj
        notes.append(f"Loaded NumPy array, shape {arr.shape}.")
    arr = np.asarray(arr)
    if arr.ndim == 1:
        return pd.DataFrame({"value": arr})
    if arr.ndim == 2:
        return pd.DataFrame(arr, columns=[f"dim_{i}" for i in range(arr.shape[1])])
    # flatten higher dims down to 2D for inspection
    flat = arr.reshape(arr.shape[0], -1)
    notes.append(f"Flattened {arr.ndim}D array to 2D for inspection.")
    return pd.DataFrame(flat, columns=[f"feat_{i}" for i in range(flat.shape[1])])


def _load_hdf5(path: str, notes: list[str]) -> pd.DataFrame:
    try:
        import h5py
    except ImportError:
        raise RuntimeError("h5py not installed; cannot read HDF5.")
    datasets: dict[str, np.ndarray] = {}

    def _visit(name, obj):
        if isinstance(obj, h5py.Dataset) and obj.ndim <= 2 and obj.size <= 5_000_000:
            try:
                datasets[name] = obj[()]
            except Exception:
                pass

    with h5py.File(path, "r") as f:
        f.visititems(_visit)
    notes.append(f"Opened HDF5; found {len(datasets)} inspectable dataset(s): "
                 f"{', '.join(list(datasets)[:6])}")
    if not datasets:
        return pd.DataFrame({"_empty": []})
    # Build a frame from 1-D datasets of equal length; else use the largest 2-D one.
    one_d = {k: v for k, v in datasets.items() if np.ndim(v) == 1}
    if one_d:
        n = min(len(v) for v in one_d.values())
        return pd.DataFrame({k.split("/")[-1]: v[:n] for k, v in one_d.items()})
    biggest = max(datasets.items(), key=lambda kv: np.size(kv[1]))
    arr = np.atleast_2d(biggest[1])
    return pd.DataFrame(arr, columns=[f"{biggest[0].split('/')[-1]}_{i}"
                                      for i in range(arr.shape[1])])


def _profile_dataframe(df: pd.DataFrame, path: str, notes: list[str]) -> dict:
    df = df.copy()
    # coerce obvious numerics stored as strings
    for c in df.columns:
        if df[c].dtype == object:
            coerced = pd.to_numeric(df[c], errors="coerce")
            if coerced.notna().mean() > 0.8:
                df[c] = coerced

    numeric = df.select_dtypes("number")
    profile = {
        "n_rows": int(df.shape[0]),
        "n_cols": int(df.shape[1]),
        "columns": [{"name": str(c), "dtype": str(df[c].dtype),
                     "missing_pct": round(float(df[c].isna().mean()) * 100, 1),
                     "n_unique": int(df[c].nunique(dropna=True))}
                    for c in df.columns],
        "numeric_columns": [str(c) for c in numeric.columns],
        "describe": _safe(numeric.describe().to_dict()) if not numeric.empty else {},
        "top_correlations": _top_correlations(numeric),
        "sample_rows": _safe(df.head(5).to_dict(orient="records")),
    }
    summary = _summarize(df, profile, os.path.basename(path))
    return {
        "kind": "tabular",
        "filename": os.path.basename(path),
        "summary": summary,
        "profile": profile,
        "dataframe": df,
        "text": None,
        "preview": df.head(20),
        "notes": notes,
    }


def _top_correlations(numeric: pd.DataFrame, k: int = 8) -> list[dict]:
    if numeric.shape[1] < 2:
        return []
    corr = numeric.corr(numeric_only=True)
    pairs = []
    cols = list(corr.columns)
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            v = corr.iloc[i, j]
            if pd.notna(v):
                pairs.append({"a": str(cols[i]), "b": str(cols[j]),
                              "r": round(float(v), 3)})
    pairs.sort(key=lambda d: abs(d["r"]), reverse=True)
    return pairs[:k]


def _summarize(df: pd.DataFrame, profile: dict, fname: str) -> str:
    lines = [f"Tabular dataset '{fname}' with {profile['n_rows']} rows × "
             f"{profile['n_cols']} columns."]
    lines.append("Columns: " + ", ".join(
        f"{c['name']} ({c['dtype']})" for c in profile["columns"][:25]))
    if profile["top_correlations"]:
        tc = profile["top_correlations"][:5]
        lines.append("Strongest numeric correlations: " + "; ".join(
            f"{p['a']}~{p['b']} r={p['r']}" for p in tc))
    return "\n".join(lines)


def _safe(obj):
    """Make numpy/pandas types JSON-serializable."""
    import numpy as _np

    if isinstance(obj, dict):
        return {str(k): _safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_safe(v) for v in obj]
    if isinstance(obj, (_np.integer,)):
        return int(obj)
    if isinstance(obj, (_np.floating,)):
        return None if _np.isnan(obj) else float(obj)
    if isinstance(obj, (_np.ndarray,)):
        return _safe(obj.tolist())
    if pd.isna(obj) if _is_scalar(obj) else False:
        return None
    return obj


def _is_scalar(obj) -> bool:
    return np.isscalar(obj) or obj is None
