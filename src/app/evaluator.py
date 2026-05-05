"""Signal evaluation and output formatting."""

from __future__ import annotations

from typing import Any

from app.config.config_loader import load_config

reject_stats = {
    "no_momentum": 0,
    "no_volume_trend": 0,
    "no_follow_through": 0,
    "weak_candle": 0,
    "low_volatility": 0,
}


def _reject(reason: str) -> dict[str, Any]:
    if reason in reject_stats:
        reject_stats[reason] += 1
    return {
        "confidence": 0.0,
        "decision": "REJECT",
        "reason": reason,
    }


def evaluate_signal(signal: dict[str, Any] | None) -> dict[str, Any] | str:
    if signal is None:
        return "No signal"

    strategy = load_config()["strategy"]
    print("STRATEGY CONFIG:", strategy)

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
    if candle_strength is None or float(candle_strength) < strategy["min_candle_strength"]:
        return _reject("weak_candle")

    # 5) volatility
    volatility = metrics.get("volatility")
    if volatility is None or float(volatility) < strategy["min_volatility"]:
        return _reject("low_volatility")

    return {
        "confidence": 1.0,
        "decision": "ACCEPT",
        "reason": signal.get("reason", "validated"),
        "signal": f"{signal['symbol']}: {signal['action']}",
    }
