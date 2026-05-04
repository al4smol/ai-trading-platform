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

    candle_strength = metrics.get("candle_strength")
    if not isinstance(candle_strength, (int, float)) or candle_strength < 0.5:
        return {"confidence": 0.0, "decision": "REJECT", "reason": "weak_candle"}

    score = 0
    volatility = metrics.get("volatility")
    if isinstance(volatility, (int, float)) and volatility > 0.8:
        score += 1

    confidence = float(score)
    decision = "ACCEPT" if confidence >= 1 else "REJECT"
    reason = "ok" if decision == "ACCEPT" else "low_volatility"

    return {"confidence": confidence, "decision": decision, "reason": reason}
