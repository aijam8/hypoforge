"""
LLM client factory + JSON helpers.

The whole agent system talks to an LLM only through `get_llm()` and `call_json()`,
so the backend is fully swappable via the LLM_PROVIDER env var:

    gemini      -> langchain-google-genai (free tier; default)
    deepseek    -> langchain-openai pointed at DeepSeek
    openrouter  -> langchain-openai pointed at OpenRouter
    mock        -> offline deterministic responses (no key needed)

If a provider is selected but its key is missing, we transparently fall back to
the mock backend so the app always runs (a banner warns the user in the UI).
"""
from __future__ import annotations

import json
import os
import re
from functools import lru_cache
from typing import Any

from dotenv import load_dotenv

load_dotenv()


# --------------------------------------------------------------------------- #
#  Provider detection
# --------------------------------------------------------------------------- #
def active_provider() -> str:
    """Return the provider we will *actually* use after key checks."""
    provider = os.getenv("LLM_PROVIDER", "gemini").lower().strip()
    keymap = {
        "gemini": os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"),
        "deepseek": os.getenv("DEEPSEEK_API_KEY"),
        "openrouter": os.getenv("OPENROUTER_API_KEY"),
        "mock": "ok",
    }
    if provider not in keymap:
        provider = "gemini"
    if not keymap.get(provider):
        return "mock"
    return provider


def provider_status() -> dict:
    """Human-readable status for the UI banner."""
    requested = os.getenv("LLM_PROVIDER", "gemini").lower().strip()
    active = active_provider()
    return {
        "requested": requested,
        "active": active,
        "is_mock": active == "mock",
        "model": _model_for(active),
    }


def _model_for(provider: str) -> str:
    return {
        "gemini": os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        "deepseek": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        "openrouter": os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat"),
        "mock": "mock-llm",
    }.get(provider, "unknown")


# --------------------------------------------------------------------------- #
#  Factory
# --------------------------------------------------------------------------- #
@lru_cache(maxsize=8)
def get_llm(temperature: float | None = None):
    if temperature is None:
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.5"))
    provider = active_provider()

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=_model_for("gemini"),
            temperature=temperature,
            google_api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"),
            convert_system_message_to_human=True,
        )

    if provider in ("deepseek", "openrouter"):
        from langchain_openai import ChatOpenAI

        if provider == "deepseek":
            return ChatOpenAI(
                model=_model_for("deepseek"),
                temperature=temperature,
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com",
            )
        return ChatOpenAI(
            model=_model_for("openrouter"),
            temperature=temperature,
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )

    return _MockLLM()


# --------------------------------------------------------------------------- #
#  Calling helpers
# --------------------------------------------------------------------------- #
def call_text(prompt: str, system: str = "", temperature: float | None = None) -> str:
    llm = get_llm(temperature)
    if isinstance(llm, _MockLLM):
        return llm.respond(system + "\n" + prompt)
    from langchain_core.messages import HumanMessage, SystemMessage

    messages = []
    if system:
        messages.append(SystemMessage(content=system))
    messages.append(HumanMessage(content=prompt))
    resp = llm.invoke(messages)
    return resp.content if hasattr(resp, "content") else str(resp)


def call_json(prompt: str, system: str = "", temperature: float | None = None,
              retries: int = 2) -> Any:
    """Call the LLM and robustly parse a JSON object/array from the reply."""
    sys = (system + "\n\nReturn ONLY valid JSON. No markdown fences, no prose.").strip()
    last = ""
    for _ in range(retries + 1):
        last = call_text(prompt, sys, temperature)
        parsed = _extract_json(last)
        if parsed is not None:
            return parsed
        prompt = (
            "Your previous reply was not valid JSON. Re-emit the SAME content as "
            "strictly valid JSON only.\n\nPrevious reply:\n" + last[:2000]
        )
    # Last resort: never crash the pipeline.
    return {"_parse_error": True, "raw": last}


def _extract_json(text: str) -> Any:
    if not text:
        return None
    text = text.strip()
    # strip ```json fences
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    # find first balanced {...} or [...]
    for opener, closer in (("{", "}"), ("[", "]")):
        start = text.find(opener)
        if start == -1:
            continue
        depth = 0
        for i in range(start, len(text)):
            if text[i] == opener:
                depth += 1
            elif text[i] == closer:
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start : i + 1])
                    except Exception:
                        break
    return None


# --------------------------------------------------------------------------- #
#  Mock backend — keeps the app fully runnable with no API key.
# --------------------------------------------------------------------------- #
class _MockLLM:
    """Deterministic, keyword-driven stand-in. Returns structured JSON so every
    downstream agent works; clearly labelled as mock in its text."""

    def respond(self, prompt: str) -> str:
        p = prompt.lower()
        # Order matters: use markers unique to each agent's prompt.
        if "critic improvement notes" in p:  # validation editor
            return json.dumps({
                "statement": "[MOCK] Sharpened: A predicts B under condition C, "
                             "controlling for confounders.",
                "test_plan": "[MOCK] Pre-registered regression with n=200, holdout validation.",
                "what_changed": "[MOCK] Added controls and a sample-size target.",
            })
        if "hypothesis under review" in p:  # a critic
            return json.dumps({
                "score": 7,
                "critique": "[MOCK] Reasonable and testable; tighten operational definitions.",
                "red_flags": [],
                "improvement": "[MOCK] Specify sample size and controls.",
            })
        if "framing:" in p:  # hypothesis generation
            return json.dumps([
                {
                    "title": f"[MOCK] Hypothesis {i+1}",
                    "statement": "Variable A is predictive of variable B under condition C.",
                    "rationale": "Grounded in the data profile and an identified knowledge gap.",
                    "knowledge_gap_addressed": "Unquantified A–B interaction.",
                    "data_grounding": "Motivated by a strong correlation in the uploaded data.",
                    "test_plan": "Collect paired A/B samples; fit a regression; test slope != 0.",
                    "required_data": "Paired measurements of A and B with metadata C.",
                    "predicted_outcome": "Significant positive association (p < 0.05).",
                    "novelty_basis": "Not addressed in retrieved literature.",
                } for i in range(2)
            ])
        if "literature corpus" in p:  # literature synthesis
            return json.dumps({
                "field_summary": "[MOCK] The field broadly characterizes these variables "
                                 "but lacks integrative, quantitative links.",
                "established_findings": ["[MOCK] Variable A and B are individually well studied."],
                "knowledge_gaps": [
                    "[MOCK] The interaction between the dataset's main variables is unquantified.",
                    "[MOCK] No published work links the observed distribution to causal drivers.",
                    "[MOCK] Structural/temporal dynamics in this data type are rarely modeled.",
                ],
                "open_questions": ["[MOCK] What mechanism generates the observed correlations?"],
            })
        if "automated profile" in p:  # understanding
            return json.dumps({
                "domain": "[MOCK] unspecified scientific/tabular domain",
                "data_nature": "[MOCK] Measured variables suitable for correlational analysis.",
                "description": "[MOCK] The data contains several measured variables with "
                               "visible correlations, suitable for hypothesis generation.",
                "key_variables": ["var1", "var2", "var3"],
                "likely_questions": ["How do the variables co-vary?"],
                "observed_patterns": ["[MOCK] Notable correlation between two variables."],
                "search_queries": ["relationship between var1 and var2", "var3 mechanism"],
            })
        if "propose 4-6 charts" in p:  # visualization plan
            return json.dumps({
                "charts": [
                    {"type": "correlation_heatmap", "title": "Correlations",
                     "reason": "Expose pairwise relationships."},
                    {"type": "histogram", "x": None, "title": "Distribution",
                     "reason": "Show the spread of a key variable."},
                ]
            })
        return "[MOCK LLM] Set GOOGLE_API_KEY in .env to enable real analysis."
