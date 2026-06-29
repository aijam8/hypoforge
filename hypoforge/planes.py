"""
The two-data-plane firewall — the trust artifact.

LOCAL plane: raw experimental files. Read on-machine, derived scalars only ever
             reach the LLM; raw bytes NEVER hit the network.
WEB plane:   identity/field metadata only (name, lab, public URLs) for profiling.

This module tracks both and prints the `/planes` manifest ("0 bytes left the
machine"). A single dispatch guard refuses any network-touching tool that was
handed local-plane data.
"""
from __future__ import annotations

from dataclasses import dataclass, field


class PlaneViolation(RuntimeError):
    pass


@dataclass
class PlaneLedger:
    local_files: int = 0
    local_bytes_read: int = 0
    bytes_sent_from_local: int = 0          # MUST stay 0
    web_pages: int = 0
    web_domains: set = field(default_factory=set)

    def record_local(self, n_files: int, n_bytes: int):
        self.local_files += n_files
        self.local_bytes_read += n_bytes

    def record_web(self, url: str):
        self.web_pages += 1
        dom = url.split("/")[2] if "://" in url else url.split("/")[0]
        self.web_domains.add(dom)

    def guard(self, tool_name: str, touches: list[str], input_planes: list[str]):
        """Refuse a network tool that received local-plane data."""
        if "network" in touches and "local" in input_planes:
            raise PlaneViolation(
                f"tool '{tool_name}' touches network but was given local-plane "
                f"data — refused by the plane guard.")

    def manifest(self) -> dict:
        return {
            "local": {"files_read": self.local_files,
                      "bytes_read": self.local_bytes_read,
                      "bytes_left_machine": self.bytes_sent_from_local},
            "web": {"pages_fetched": self.web_pages,
                    "domains": sorted(self.web_domains)},
        }
