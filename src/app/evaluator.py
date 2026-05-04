"""Signal evaluation and output formatting."""

from __future__ import annotations

from typing import Any


def evaluate_signal(signal: dict[str, Any] | None) -> dict[str, Any]:
    if signal is None:
        return {"confidence": 0.0, "decision": "REJECT", "reason": "no_signal"}

    metrics = signal.get("metrics", {})

    if metrics.get("momentum") is not True:
        return {"confidence": 0.0, "decision": "REJECT", "reason": "no_momentum"}

    if metrics.get("volume_trend") is not True:
        return {"confidence": 0.0, "decision": "REJECT", "reason": "no_volume"}

    score = 0
    candle_strength = metrics.get("candle_strength")
    volatility = metrics.get("volatility")

    if isinstance(candle_strength, (int, float)) and candle_strength > 0.6:
        score += 1

    if isinstance(volatility, (int, float)) and volatility > 0.8:
        score += 1

    confidence = score / 2
    decision = "ACCEPT" if confidence >= 0.5 else "REJECT"

    if score == 2:
        reason = "ok"
    elif score == 1:
        reason = "weak_candle" if not (isinstance(candle_strength, (int, float)) and candle_strength > 0.6) else "low_volatility"
    else:
        reason = "weak_candle"

    return {"confidence": confidence, "decision": decision, "reason": reason}
