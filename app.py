"""
HypoForge — upload any data, get novel testable hypotheses.

Run:  streamlit run app.py
"""
from __future__ import annotations

import os
import tempfile

import pandas as pd
import streamlit as st

from agents.llm import provider_status
from agents.orchestrator import run_pipeline

st.set_page_config(page_title="HypoForge", page_icon="🔬", layout="wide")

# --------------------------------------------------------------------------- #
#  Header
# --------------------------------------------------------------------------- #
st.title("🔬 HypoForge")
st.caption("Upload any data → an agent team parses it, reviews the literature, "
           "and proposes **novel, testable hypotheses** grounded in real knowledge gaps.")

status = provider_status()
if status["is_mock"]:
    st.warning(
        f"⚠️ **Running in MOCK mode** — no LLM key found (requested "
        f"`{status['requested']}`). The pipeline runs end-to-end with placeholder "
        f"reasoning. Add a key to `.env` (e.g. `GOOGLE_API_KEY=...` from "
        f"[aistudio.google.com/apikey](https://aistudio.google.com/apikey)) and "
        f"restart for real analysis.", icon="⚠️")
else:
    st.success(f"LLM backend: **{status['active']}** ({status['model']})", icon="✅")

# --------------------------------------------------------------------------- #
#  Sidebar
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.header("Pipeline")
    st.markdown(
        "1. **Ingest** — open & profile the file\n"
        "2. **Understand** — infer domain & variables\n"
        "3. **Visualize** ‖ **Literature review**\n"
        "4. **Hypothesize** — multi-framing generation\n"
        "5. **Validate** — adversarial critic panel")
    st.divider()
    st.subheader("Literature sources")
    src_map = {
        "Semantic Scholar": "semantic_scholar",
        "arXiv": "arxiv",
        "OpenAlex": "openalex",
        "Web (DuckDuckGo)": "web",
    }
    chosen = [v for k, v in src_map.items()
              if st.checkbox(k, value=True, key=f"src_{v}")]
    st.divider()
    st.caption("Supports CSV, Excel, Parquet, JSON, HDF5, NumPy, PDF, DOCX, "
               "text, images — and falls back gracefully on anything else.")

# --------------------------------------------------------------------------- #
#  Upload
# --------------------------------------------------------------------------- #
uploaded = st.file_uploader(
    "Upload your data",
    type=["csv", "tsv", "xlsx", "xls", "parquet", "json", "jsonl", "h5", "hdf5",
          "npy", "npz", "pdf", "docx", "txt", "md", "png", "jpg", "jpeg", "tif"],
    help="Anything from a scientific simulation dump to a PDF paper.")

run = st.button("🚀 Forge hypotheses", type="primary", disabled=uploaded is None)

# --------------------------------------------------------------------------- #
#  Run pipeline
# --------------------------------------------------------------------------- #
if run and uploaded is not None:
    suffix = os.path.splitext(uploaded.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded.getbuffer())
        tmp_path = tmp.name
    # preserve original name for nicer summaries
    nice_path = os.path.join(os.path.dirname(tmp_path), uploaded.name)
    try:
        os.replace(tmp_path, nice_path)
    except Exception:
        nice_path = tmp_path

    bar = st.progress(0.0, text="Starting…")

    def _progress(key, label, frac):
        bar.progress(frac, text=f"{label}…")

    with st.spinner("Agents working…"):
        try:
            result = run_pipeline(nice_path, progress=_progress, sources=chosen or None)
            st.session_state["result"] = result
        except Exception as e:
            st.error(f"Pipeline failed: {e}")
            st.exception(e)
    bar.empty()

# --------------------------------------------------------------------------- #
#  Render results
# --------------------------------------------------------------------------- #
result = st.session_state.get("result")
if result:
    s = result["stats"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Papers reviewed", s["n_papers"])
    c2.metric("Knowledge gaps", s["n_gaps"])
    c3.metric("Hypotheses", s["n_hypotheses"])
    c4.metric("Strong / promising", s["n_strong"])

    tabs = st.tabs(["🧠 Hypotheses", "🔭 Data understanding", "📊 Visualizations",
                    "📚 Literature & gaps", "🗂 Raw profile"])

    # --- Hypotheses --------------------------------------------------------
    with tabs[0]:
        st.subheader("Ranked hypotheses")
        st.caption("Scored by an adversarial panel (novelty · testability · "
                   "grounding · plausibility).")
        for h in result["hypotheses"]:
            v = h["validation"]
            emoji = {"strong": "🟢", "promising": "🟡",
                     "weak": "🟠", "rejected": "🔴"}.get(v["verdict"], "⚪")
            with st.expander(
                    f"{emoji} **{h.get('title', h.get('id'))}** — "
                    f"score {v['overall_score']}/10 · *{v['verdict']}* · "
                    f"[{h.get('framing', '')}]"):
                st.markdown(f"**Hypothesis.** {h.get('statement', '')}")
                cols = st.columns(4)
                for col, key in zip(cols, ["novelty", "testability",
                                           "grounding", "plausibility"]):
                    col.metric(key.title(), f"{v['scores'].get(key, '–')}/10")

                st.markdown(f"**Rationale.** {h.get('rationale', '')}")
                st.markdown(f"**Knowledge gap addressed.** "
                            f"{h.get('knowledge_gap_addressed', '')}")
                st.markdown(f"**Grounded in data.** {h.get('data_grounding', '')}")
                st.markdown(f"**How to test it.** {h.get('test_plan', '')}")
                if h.get("required_data"):
                    st.markdown(f"**Data needed.** {h['required_data']}")
                st.markdown(f"**Predicted outcome.** {h.get('predicted_outcome', '')}")
                st.markdown(f"**Why it's novel.** {h.get('novelty_basis', '')}")

                ref = v.get("refined_hypothesis")
                if ref and isinstance(ref, dict) and ref.get("statement"):
                    st.info(f"**Sharpened by the panel:** {ref.get('statement')}\n\n"
                            f"*Improved test:* {ref.get('test_plan', '')}")

                with st.popover("See critic reviews"):
                    for name, r in v["reviews"].items():
                        st.markdown(f"**{name.title()} ({r.get('score')}/10).** "
                                    f"{r.get('critique', '')}")
                        if r.get("red_flags"):
                            st.markdown("- ⚠️ " + "\n- ⚠️ ".join(r["red_flags"]))

    # --- Understanding -----------------------------------------------------
    with tabs[1]:
        u = result["understanding"]
        st.subheader(u.get("domain", "—"))
        st.markdown(f"**What this data is.** {u.get('data_nature', '')}")
        st.markdown(u.get("description", ""))
        cc = st.columns(2)
        with cc[0]:
            st.markdown("**Key variables**")
            for kv in u.get("key_variables", []):
                st.markdown(f"- {kv}")
            st.markdown("**Observed patterns**")
            for p in u.get("observed_patterns", []):
                st.markdown(f"- {p}")
        with cc[1]:
            st.markdown("**Questions this data could answer**")
            for q in u.get("likely_questions", []):
                st.markdown(f"- {q}")
            st.markdown("**Literature queries used**")
            for q in u.get("search_queries", []):
                st.markdown(f"- `{q}`")

    # --- Visualizations ----------------------------------------------------
    with tabs[2]:
        figs = result["figures"]
        parsed = result["parsed"]
        if parsed["kind"] == "image":
            st.image(parsed["preview"], caption=parsed["filename"], width=400)
        if not figs:
            st.info("No automatic visualizations for this data type.")
        for f in figs:
            st.markdown(f"**{f['title']}**")
            if f.get("description"):
                st.caption(f["description"])
            st.plotly_chart(f["figure"], use_container_width=True)

    # --- Literature --------------------------------------------------------
    with tabs[3]:
        lit = result["literature"]
        st.markdown(f"**State of the field.** {lit.get('field_summary', '')}")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🔍 Knowledge gaps")
            for g in lit.get("knowledge_gaps", []):
                st.markdown(f"- {g}")
            st.markdown("### ❓ Open questions")
            for q in lit.get("open_questions", []):
                st.markdown(f"- {q}")
        with c2:
            st.markdown("### ✅ Established findings")
            for fnd in lit.get("established_findings", []):
                st.markdown(f"- {fnd}")
        st.divider()
        st.markdown(f"### 📄 Papers retrieved ({lit.get('n_papers', 0)})")
        for p in lit.get("papers", [])[:30]:
            title = p.get("title", "")
            url = p.get("url", "")
            head = f"[{title}]({url})" if url else title
            meta = f"{p.get('source')} · {p.get('year') or 'n.d.'}"
            if p.get("citations"):
                meta += f" · {p['citations']} citations"
            st.markdown(f"- {head}  \n  <small>{meta}</small>",
                        unsafe_allow_html=True)
        if lit.get("source_errors"):
            with st.expander("Source warnings"):
                for e in lit["source_errors"]:
                    st.caption(f"{e.get('source')}: {e.get('abstract')}")

    # --- Raw profile -------------------------------------------------------
    with tabs[4]:
        parsed = result["parsed"]
        st.markdown(f"**Parser decisions:** {', '.join(parsed.get('notes', []))}")
        st.code(parsed["summary"])
        if isinstance(parsed.get("preview"), pd.DataFrame):
            st.dataframe(parsed["preview"], use_container_width=True)
        st.json(parsed.get("profile", {}), expanded=False)

else:
    st.info("⬆️ Upload a file and click **Forge hypotheses** to begin.")
