"""
Modular per-role model router.

Every agent asks for a ROLE ("principle", "hypothesis", "skeptic", ...); the YAML
config maps roles -> {provider, model, temperature, reasoning}. Providers are all
OpenAI-compatible (openrouter, deepseek). When no key is present we fall back to
"mock" and return the provided `fixture` text, so the whole tool runs fully
offline and deterministically — which is exactly how we demo it.

This is the one place that knows about providers; no agent imports an SDK.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import yaml

_CFG = Path(__file__).parent / "config" / "models.yaml"

_KEY_ENV = {
    "openrouter": "OPENROUTER_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
}
_BASE_URL = {
    "openrouter": "https://openrouter.ai/api/v1",
    "deepseek": "https://api.deepseek.com",
}


@lru_cache(maxsize=1)
def _config() -> dict:
    try:
        return yaml.safe_load(_CFG.read_text())
    except Exception:
        return {"defaults": {"provider": "openrouter"}, "roles": {}, "fallback_chain": ["mock"]}


def role_spec(role: str) -> dict:
    cfg = _config()
    spec = dict(cfg.get("defaults", {}))
    spec.update(cfg.get("roles", {}).get(role, {}))
    spec["role"] = role
    return spec


def _has_key(provider: str) -> bool:
    env = _KEY_ENV.get(provider)
    return bool(env and os.getenv(env))


def resolve_provider(role: str) -> str:
    """Return the provider actually usable for this role (walks the fallback chain)."""
    cfg = _config()
    want = role_spec(role).get("provider", "openrouter")
    chain = [want] + [p for p in cfg.get("fallback_chain", []) if p != want]
    for p in chain:
        if p == "mock" or _has_key(p):
            return p
    return "mock"


def is_offline() -> bool:
    """True when no provider key is available (the default demo state)."""
    return not any(_has_key(p) for p in _KEY_ENV)


def generate(role: str, prompt: str, system: str = "", fixture: str | None = None) -> str:
    """Generate text for a role. Offline/mock -> return the deterministic fixture."""
    provider = resolve_provider(role)
    if provider == "mock":
        return fixture if fixture is not None else f"[mock:{role}]"
    spec = role_spec(role)
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage

        llm = ChatOpenAI(
            model=spec.get("model", "deepseek/deepseek-chat"),
            temperature=spec.get("temperature", 0.3),
            api_key=os.getenv(_KEY_ENV[provider]),
            base_url=_BASE_URL[provider],
            timeout=40,
        )
        msgs = []
        if system:
            msgs.append(SystemMessage(content=system))
        msgs.append(HumanMessage(content=prompt))
        return llm.invoke(msgs).content
    except Exception:
        return fixture if fixture is not None else f"[mock:{role}]"


def model_label(role: str) -> str:
    p = resolve_provider(role)
    if p == "mock":
        return "mock (offline)"
    return f"{p}:{role_spec(role).get('model', '?')}"
