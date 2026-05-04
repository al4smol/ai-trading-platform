"""Execution layer for turning accepted signals into trades."""

from __future__ import annotations

from typing import Any


def build_trade(signal: dict[str, Any], candles: list[list[Any]]) -> dict[str, Any]:
    last_close = float(candles[-1][4])
    action = signal["action"]

    if action == "BUY":
        stop_loss = last_close * 0.995
        take_profit = last_close * 1.01
    else:
        stop_loss = last_close * 1.005
        take_profit = last_close * 0.99

    return {
        "symbol": signal.get("symbol"),
        "action": action,
        "entry": last_close,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "risk": abs(last_close - stop_loss),
    }
