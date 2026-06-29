"""Rich rendering helpers: streaming 'agentic' output, panels, sparklines."""
from __future__ import annotations

import time

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console(highlight=False)

# role -> (label, color)
_ROLES = {
    "system": ("forge", "bold cyan"),
    "plan": ("plan", "cyan"),
    "ingest": ("ingest", "green"),
    "profile": ("profile", "magenta"),
    "principle": ("principle-agent", "yellow"),
    "hypothesis": ("hypothesis-agent", "blue"),
    "experiment": ("experiment-agent", "bright_green"),
    "ids": ("strategy", "bright_yellow"),
    "proponent": ("proponent", "blue"),
    "skeptic": ("skeptic", "red"),
    "referee": ("referee", "bright_magenta"),
    "anomaly": ("anomaly", "bold red"),
    "planes": ("planes", "bold green"),
}

_SPARK = "▁▂▃▄▅▆▇█"


class UI:
    """Thin wrapper so animation speed is global and testable (--fast disables sleeps)."""

    def __init__(self, fast: bool = False):
        self.fast = fast

    def _sleep(self, s: float):
        if not self.fast:
            time.sleep(s)

    def rule(self, title: str, style: str = "cyan"):
        console.rule(f"[{style}]{title}", style=style)

    def banner(self, text: str, subtitle: str = ""):
        console.print(Panel.fit(Text(text, style="bold cyan"),
                                subtitle=subtitle, border_style="cyan"))

    def say(self, role: str, text: str, stream: bool = True):
        label, color = _ROLES.get(role, (role, "white"))
        tag = Text(f"  {label} ", style=f"bold {color}")
        console.print(tag, end="")
        if stream and not self.fast:
            self._stream(text, color)
        else:
            console.print(Text(text, style=color))

    def _stream(self, text: str, color: str, cps: float = 0.0):
        # word-wise typewriter
        words = text.split(" ")
        line = Text("", style=color)
        for i, w in enumerate(words):
            console.print(Text(w + (" " if i < len(words) - 1 else ""), style=color), end="")
            self._sleep(0.012)
        console.print("")

    def step(self, label: str, status: str = "•"):
        console.print(f"   [dim]{status}[/dim] {label}")

    def think(self, role: str, n: int = 3):
        label, color = _ROLES.get(role, (role, "white"))
        console.print(Text(f"  {label} ", style=f"bold {color}"), end="")
        for _ in range(n):
            console.print(Text("· ", style="dim"), end="")
            self._sleep(0.18)
        console.print("")

    def panel(self, body: str, title: str = "", style: str = "cyan"):
        console.print(Panel(body, title=title, border_style=style))

    def kv(self, title: str, pairs: list[tuple[str, str]], style: str = "cyan"):
        t = Table(show_header=False, box=None, padding=(0, 2, 0, 0))
        t.add_column(style="bold")
        t.add_column()
        for k, v in pairs:
            t.add_row(k, v)
        console.print(Panel(t, title=title, border_style=style))

    def sparkline(self, values: list[float]) -> str:
        if not values:
            return ""
        lo, hi = min(values), max(values)
        rng = (hi - lo) or 1.0
        return "".join(_SPARK[min(len(_SPARK) - 1, int((v - lo) / rng * (len(_SPARK) - 1)))]
                       for v in values)

    def blank(self):
        console.print("")
