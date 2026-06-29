"""
Honest data-flow accounting — three planes, reported transparently.

  LOCAL : raw user files. Read on-machine. Raw BYTES are never transmitted —
          only derived summaries/extracts are. `bytes_left_machine` stays 0.
  MODEL : derived text sent to the hosted LLM (OpenRouter/DeepSeek). In
          --no-internet/offline mode this is 0 (true zero egress).
  WEB   : public pages fetched for literature / institution profiling.

This replaces the earlier "0 bytes left the machine" overclaim: when a hosted
model is used, derived text DOES leave, and we say so, with counts.
"""
from __future__ import annotations

from dataclasses import dataclass, field


class PlaneViolation(RuntimeError):
    pass


@dataclass
class PlaneLedger:
    local_files: int = 0
    local_bytes_read: int = 0
    local_bytes_sent: int = 0            # raw bytes transmitted — must stay 0
    model_calls: int = 0
    model_chars_sent: int = 0            # derived text sent to the LLM
    web_pages: int = 0
    web_domains: set = field(default_factory=set)
    no_internet: bool = False

    def record_local(self, n_files: int, n_bytes: int):
        self.local_files += n_files
        self.local_bytes_read += n_bytes

    def record_web(self, url: str):
        if not url:
            return
        self.web_pages += 1
        try:
            dom = url.split("/")[2] if "://" in url else url.split("/")[0]
        except Exception:
            dom = url
        self.web_domains.add(dom)

    def sync_model(self, usage: dict):
        self.model_calls = usage.get("calls", 0)
        self.model_chars_sent = usage.get("prompt_chars", 0)

    def manifest(self) -> dict:
        return {
            "mode": "no-internet (zero egress)" if self.no_internet else "hosted-model",
            "local": {"files_read": self.local_files,
                      "bytes_read": self.local_bytes_read,
                      "raw_bytes_transmitted": self.local_bytes_sent},
            "model": {"llm_calls": self.model_calls,
                      "derived_chars_sent": self.model_chars_sent},
            "web": {"pages_fetched": self.web_pages,
                    "domains": sorted(self.web_domains)},
        }
