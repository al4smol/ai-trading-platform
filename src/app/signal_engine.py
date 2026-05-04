"""Signal generation from events."""

from __future__ import annotations

from typing import Any

from app.core.signals.signal_engine import add_signal_metrics


def generate_signal(event: dict[str, Any] | None, candles: list[list[Any]] | None) -> dict[str, Any] | None:
    if event is None:
        print("Signal: no event, no signal")
        return None
    if candles is None or not candles:
        print("Signal: no candles, no signal")
        return None

    direction = event.get("direction")
    if direction not in {"UP", "DOWN"}:
        print(f"Signal: unsupported direction={direction}")
        return None

    action = "BUY" if direction == "UP" else "SELL"
    signal = {
        "symbol": event.get("symbol"),
        "action": action,
        "reason": event.get("type"),
        "metrics": {},
    }
    signal = add_signal_metrics(signal, candles, event)
    print(f"Signal: generated {signal}")
    return signal
