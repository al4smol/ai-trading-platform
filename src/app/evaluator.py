"""Signal evaluation and output formatting."""

from __future__ import annotations

from typing import Any


def _reject(reason: str) -> dict[str, Any]:
    return {
        "confidence": 0.0,
        "decision": "REJECT",
        "reason": reason,
    }


def evaluate_signal(signal: dict[str, Any] | None) -> dict[str, Any] | str:
    if signal is None:
        return "No signal"

    metrics = signal.get("metrics", {})

    # 1) momentum
    if metrics.get("momentum") is not True:
        return _reject("no_momentum")

    # 2) volume_trend
    if metrics.get("volume_trend") is not True:
        return _reject("no_volume_trend")

    # 3) follow_through
    if metrics.get("follow_through") is not True:
        return _reject("no_follow_through")

    # 4) candle_strength
    candle_strength = metrics.get("candle_strength")
    if candle_strength is None or float(candle_strength) < 0.5:
        return _reject("weak_candle")

    # 5) volatility
    volatility = metrics.get("volatility")
    if volatility is None or float(volatility) <= 0:
        return _reject("low_volatility")

    return {
        "confidence": 1.0,
        "decision": "ACCEPT",
        "reason": signal.get("reason", "validated"),
        "signal": f"{signal['symbol']}: {signal['action']}",
    }
