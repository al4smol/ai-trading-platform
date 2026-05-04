"""Event detection logic."""

from __future__ import annotations

from typing import Any


def detect_fast_move(symbol: str, candles: list[list[Any]] | None, threshold_pct: float = 0.5) -> dict[str, Any] | None:
    if candles is None:
        print(f"Event: no candles for {symbol}")
        return None
    if len(candles) < 2:
        print(f"Event: insufficient candles for {symbol}")
        return None

    prev_close = float(candles[-2][4])
    last_close = float(candles[-1][4])
    if prev_close == 0:
        print(f"Event: invalid prev_close=0 for {symbol}")
        return None

    change_pct = ((last_close - prev_close) / prev_close) * 100
    if abs(change_pct) < threshold_pct:
        print(f"Event: no fast move for {symbol} ({change_pct:.2f}%)")
        return None

    direction = "UP" if change_pct > 0 else "DOWN"
    event = {
        "type": "FAST_MOVE",
        "symbol": symbol,
        "direction": direction,
        "change_pct": change_pct,
    }
    print(f"Event: detected {event}")
    return event
