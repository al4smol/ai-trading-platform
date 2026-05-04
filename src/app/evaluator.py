"""Signal evaluation and output formatting."""

from __future__ import annotations

from typing import Any


def evaluate_signal(signal: dict[str, Any] | None) -> str:
    if signal is None:
        return "No signal"
    return f"{signal['symbol']}: {signal['action']} ({signal['reason']})"
