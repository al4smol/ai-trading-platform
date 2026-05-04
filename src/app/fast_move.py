"""Event detection logic."""

from __future__ import annotations

from typing import Any


def detect_fast_move(symbol: str, candles: list[list[Any]] | None, threshold_pct: float = 0.5) -> dict[str, Any] | None:
    if candles is None:
        print(f"Event: no candles for {symbol}")
        return None
    if len(candles) < 5:
        print(f"Event: insufficient candles for {symbol}")
        return None

    window = candles[-5:]
    closes = [float(c[4]) for c in window]
    min_price = min(closes)
    max_price = max(closes)

    if min_price == 0:
        print(f"Event: invalid min_price=0 for {symbol}")
        return None

    move_pct = ((max_price - min_price) / min_price) * 100
    if move_pct < threshold_pct:
        print(f"Event: no fast move for {symbol} ({move_pct:.2f}%)")
        return None

    direction = "UP" if closes[-1] > closes[0] else "DOWN"
    event = {
        "type": "FAST_MOVE",
        "symbol": symbol,
        "direction": direction,
        "change_pct": move_pct,
    }
    print(f"Event: detected {event}")
    return event
