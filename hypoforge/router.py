"""
Modular per-role model router (real).

Every agent asks for a ROLE (intake / extract / literature / hypothesis / ranking /
critique / synthesis / ...); config/models.yaml maps each role to a concrete model.
Providers are OpenAI-compatible (OpenRouter, DeepSeek). This is the ONLY place that
talks to a model API — swap a role's model in YAML and nothing else changes.

Honesty: every call's prompt/completion size is accounted into router.USAGE so the
privacy manifest can report exactly how much *derived* text was sent to the model
provider (raw user files are never sent as bytes — only derived summaries/extracts).

Modes:
  * normal  -> calls the hosted model
  * FORCE_MOCK (set by --no-internet/--offline) -> returns the provided `fixture`
    (or a stub) and makes ZERO network calls.
"""
from __future__ import annotations

import json
import os
import re
import time
from functools import lru_cache
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=str(Path(__file__).resolve().parent.parent / ".env"))

_CFG = Path(__file__).parent / "config" / "models.yaml"

_BASE_URL = {
    "openrouter": "https://openrouter.ai/api/v1/chat/completions",
    "deepseek": "https://api.deepseek.com/chat/completions",
}
_KEY_ENV = {"openrouter": "OPENROUTER_API_KEY", "deepseek": "DEEPSEEK_API_KEY"}

# Set True by the CLI for --no-internet / --offline: no model egress at all.
FORCE_MOCK = False

# Running tally for the privacy manifest.
USAGE = {"calls": 0, "prompt_chars": 0, "completion_chars": 0, "by_role": {}}


@lru_cache(maxsize=1)
def _config() -> dict:
    import yaml
    try:
        return yaml.safe_load(_CFG.read_text())
    except Exception:
        return {"defaults": {"provider": "openrouter", "model": "deepseek/deepseek-chat"},
                "roles": {}, "fallback_chain": ["openrouter", "mock"]}


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
    if FORCE_MOCK:
        return "mock"
    cfg = _config()
    want = role_spec(role).get("provider", "openrouter")
    chain = [want] + [p for p in cfg.get("fallback_chain", []) if p != want]
    for p in chain:
        if p == "mock" or _has_key(p):
            return p
    return "mock"


def is_offline() -> bool:
    return FORCE_MOCK or not any(_has_key(p) for p in _KEY_ENV)


def model_label(role: str) -> str:
    p = resolve_provider(role)
    return "mock (no egress)" if p == "mock" else f"{role_spec(role).get('model', '?')}"


def reset_usage():
    USAGE.update({"calls": 0, "prompt_chars": 0, "completion_chars": 0, "by_role": {}})


# --------------------------------------------------------------------------- #
def generate(role: str, prompt: str, system: str = "", fixture: str | None = None,
             max_tokens: int = 1400, temperature: float | None = None,
             json_mode: bool = False) -> str:
    provider = resolve_provider(role)
    if provider == "mock":
        return fixture if fixture is not None else f"[mock:{role}]"

    spec = role_spec(role)
    model = spec.get("model", "deepseek/deepseek-chat")
    temp = spec.get("temperature", 0.3) if temperature is None else temperature
    messages = ([{"role": "system", "content": system}] if system else []) + \
               [{"role": "user", "content": prompt}]
    body = {"model": model, "messages": messages, "max_tokens": max_tokens,
            "temperature": temp}
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    headers = {"Authorization": f"Bearer {os.getenv(_KEY_ENV[provider])}",
               "Content-Type": "application/json",
               "HTTP-Referer": "https://github.com/aijam8/hypoforge",
               "X-Title": "HypoForge"}

    text = ""
    for attempt in range(3):
        try:
            r = requests.post(_BASE_URL[provider], headers=headers, json=body, timeout=90)
            if r.status_code == 429:
                time.sleep(2 + attempt * 2)
                continue
            r.raise_for_status()
            msg = r.json()["choices"][0]["message"]
            text = msg.get("content") or msg.get("reasoning") or ""
            break
        except Exception:
            if attempt == 2:
                return fixture if fixture is not None else ""
            time.sleep(1 + attempt)

    USAGE["calls"] += 1
    USAGE["prompt_chars"] += len(prompt) + len(system)
    USAGE["completion_chars"] += len(text)
    USAGE["by_role"][role] = USAGE["by_role"].get(role, 0) + 1
    return text


def generate_json(role: str, prompt: str, system: str = "", fixture=None,
                  max_tokens: int = 1600, temperature: float | None = None):
    """Generate and robustly parse a JSON object/array. Returns fixture on hard failure."""
    sys = (system + "\n\nRespond with ONLY valid JSON — no markdown fences, no prose.").strip()
    raw = generate(role, prompt, sys, fixture=None, max_tokens=max_tokens,
                   temperature=temperature, json_mode=True)
    parsed = _extract_json(raw)
    if parsed is not None:
        return parsed
    # one repair attempt
    raw2 = generate(role, "Re-emit STRICTLY valid JSON for the same content:\n" + raw[:3000],
                    sys, max_tokens=max_tokens, temperature=0.0)
    parsed = _extract_json(raw2)
    if parsed is not None:
        return parsed
    return fixture if fixture is not None else {"_parse_error": True, "raw": raw[:500]}


def _extract_json(text: str):
    if not text:
        return None
    t = re.sub(r"^```(?:json)?", "", text.strip()).strip()
    t = re.sub(r"```$", "", t).strip()
    try:
        return json.loads(t)
    except Exception:
        pass
    for op, cl in (("{", "}"), ("[", "]")):
        s = t.find(op)
        if s == -1:
            continue
        depth = 0
        for i in range(s, len(t)):
            if t[i] == op:
                depth += 1
            elif t[i] == cl:
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(t[s:i + 1])
                    except Exception:
                        break
    # salvage a possibly-truncated array: collect complete top-level {...} objects
    s = t.find("[")
    if s != -1:
        objs, i, n = [], s + 1, len(t)
        while i < n:
            while i < n and t[i] in " \n\r\t,":
                i += 1
            if i >= n or t[i] == "]":
                break
            if t[i] == "{":
                depth, start = 0, i
                closed = False
                while i < n:
                    if t[i] == "{":
                        depth += 1
                    elif t[i] == "}":
                        depth -= 1
                        if depth == 0:
                            try:
                                objs.append(json.loads(t[start:i + 1]))
                            except Exception:
                                pass
                            i += 1
                            closed = True
                            break
                    i += 1
                if not closed:
                    break   # truncated mid-object: stop, keep what we have
            else:
                i += 1
        if objs:
            return objs
    return None
