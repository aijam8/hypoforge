"""
Visualization agent.

The LLM proposes which charts best reveal the data; this module then *builds*
them deterministically with Plotly (the LLM never emits executable code, so it's
safe). Works for tabular data (the common case), documents (term frequencies),
and images (channel histograms).

Returns a list of {"title", "description", "figure"} where figure is a Plotly
Figure object the Streamlit UI renders with st.plotly_chart.
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .llm import call_json

_SYSTEM = (
    "You are a data-visualization expert. Given a dataset's columns and stats, "
    "choose the handful of charts that best reveal structure, relationships and "
    "anomalies relevant to forming scientific hypotheses."
)


def visualize(parse_result: dict, understanding: dict) -> list[dict]:
    kind = parse_result["kind"]
    if kind == "tabular" and parse_result.get("dataframe") is not None:
        return _visualize_tabular(parse_result, understanding)
    if kind == "document":
        return _visualize_document(parse_result)
    if kind == "image":
        return _visualize_image(parse_result)
    return []


# --------------------------------------------------------------------------- #
#  Tabular
# --------------------------------------------------------------------------- #
def _visualize_tabular(parse_result: dict, understanding: dict) -> list[dict]:
    df: pd.DataFrame = parse_result["dataframe"]
    profile = parse_result["profile"]
    numeric = [c["name"] for c in profile["columns"]
               if c["name"] in profile["numeric_columns"]]
    categorical = [c["name"] for c in profile["columns"]
                   if c["name"] not in numeric and c["n_unique"] <= 30]

    plan = _ask_plan(profile, numeric, categorical, understanding)
    figs: list[dict] = []
    for spec in plan:
        try:
            fig = _build(df, spec, numeric, categorical)
            if fig is not None:
                figs.append({"title": spec.get("title", spec.get("type", "chart")),
                             "description": spec.get("reason", ""),
                             "figure": fig})
        except Exception:
            continue
        if len(figs) >= 6:
            break

    if not figs:  # guarantee at least something useful
        figs = _default_tabular(df, numeric)
    return figs


def _ask_plan(profile, numeric, categorical, understanding) -> list[dict]:
    prompt = f"""Dataset understanding: {understanding.get('description', '')}

Numeric columns: {numeric}
Categorical columns (low-cardinality): {categorical}
Strongest correlations: {profile.get('top_correlations', [])[:6]}

Propose 4-6 charts. Return JSON:
{{"charts": [
  {{"type": "histogram|scatter|correlation_heatmap|box|bar|line|scatter_matrix",
    "x": "column or null", "y": "column or null", "color": "column or null",
    "title": "short title", "reason": "why this helps form hypotheses"}}
]}}
Only reference columns that exist. Prefer charts that expose relationships and outliers."""
    res = call_json(prompt, _SYSTEM, temperature=0.4)
    charts = res.get("charts") if isinstance(res, dict) else None
    if not charts:
        charts = [
            {"type": "correlation_heatmap", "title": "Correlation heatmap"},
            {"type": "histogram", "x": numeric[0] if numeric else None,
             "title": "Distribution"},
        ]
    return charts


def _build(df, spec, numeric, categorical):
    t = (spec.get("type") or "").lower()
    x, y, color = spec.get("x"), spec.get("y"), spec.get("color")
    x = x if x in df.columns else (numeric[0] if numeric else None)
    if color not in df.columns:
        color = None

    if t == "correlation_heatmap":
        corr = df[numeric].corr(numeric_only=True)
        if corr.empty:
            return None
        return px.imshow(corr, text_auto=".2f", aspect="auto",
                         color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
                         title=spec.get("title", "Correlation heatmap"))
    if t == "histogram":
        if x is None:
            return None
        return px.histogram(df, x=x, color=color, marginal="box",
                            title=spec.get("title", f"Distribution of {x}"))
    if t == "scatter":
        y = y if y in df.columns else (numeric[1] if len(numeric) > 1 else None)
        if x is None or y is None:
            return None
        return px.scatter(df, x=x, y=y, color=color, trendline="ols",
                          opacity=0.7, title=spec.get("title", f"{y} vs {x}"))
    if t == "box":
        y = y if y in df.columns else (numeric[0] if numeric else None)
        cat = x if x in categorical else (categorical[0] if categorical else None)
        if y is None:
            return None
        return px.box(df, x=cat, y=y, color=color,
                      title=spec.get("title", f"{y} by group"))
    if t == "bar":
        cat = x if x in categorical else (categorical[0] if categorical else None)
        if cat is None:
            return None
        agg = df[cat].value_counts().nlargest(20)
        return px.bar(x=agg.index.astype(str), y=agg.values,
                      title=spec.get("title", f"Counts of {cat}"),
                      labels={"x": cat, "y": "count"})
    if t == "line":
        y = y if y in df.columns else (numeric[0] if numeric else None)
        if y is None:
            return None
        return px.line(df, x=x, y=y, title=spec.get("title", f"{y} over {x}"))
    if t == "scatter_matrix":
        dims = numeric[:5]
        if len(dims) < 2:
            return None
        return px.scatter_matrix(df, dimensions=dims, color=color,
                                 title=spec.get("title", "Scatter matrix"))
    return None


def _default_tabular(df, numeric):
    figs = []
    if len(numeric) >= 2:
        corr = df[numeric].corr(numeric_only=True)
        figs.append({"title": "Correlation heatmap",
                     "description": "Pairwise correlations across numeric columns.",
                     "figure": px.imshow(corr, text_auto=".2f", aspect="auto",
                                         color_continuous_scale="RdBu_r",
                                         zmin=-1, zmax=1)})
    if numeric:
        figs.append({"title": f"Distribution of {numeric[0]}",
                     "description": "Histogram of the first numeric variable.",
                     "figure": px.histogram(df, x=numeric[0], marginal="box")})
    return figs


# --------------------------------------------------------------------------- #
#  Document / Image
# --------------------------------------------------------------------------- #
def _visualize_document(parse_result):
    terms = parse_result["profile"].get("top_terms", [])[:20]
    if not terms:
        return []
    fig = px.bar(x=[t["count"] for t in terms][::-1],
                 y=[t["term"] for t in terms][::-1], orientation="h",
                 labels={"x": "frequency", "y": "term"},
                 title="Most frequent terms")
    return [{"title": "Term frequency",
             "description": "Dominant vocabulary — a proxy for the document's themes.",
             "figure": fig}]


def _visualize_image(parse_result):
    p = parse_result["profile"]
    fig = go.Figure()
    for i, ch in enumerate(["R", "G", "B"]):
        fig.add_trace(go.Bar(name=ch, x=[ch], y=[p["mean_rgb"][i]],
                             error_y=dict(type="data", array=[p["std_rgb"][i]])))
    fig.update_layout(title="Mean channel intensity (±std)", yaxis_title="0-255")
    return [{"title": "Color channel statistics",
             "description": "Per-channel brightness — basic image composition.",
             "figure": fig}]
