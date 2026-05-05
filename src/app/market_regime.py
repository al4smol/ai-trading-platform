"""Market regime detection helpers."""

from __future__ import annotations

from typing import Any


OHLCV_CLOSE = 4

LOW_VOL_THRESHOLD_PCT = 0.2
RANGE_OSCILLATION_THRESHOLD_PCT = 0.5
CONSISTENT_DIRECTION_WINDOW = 4


def _safe_close(candle: list[Any] | tuple[Any, ...]) -> float | None:
    if len(candle) <= OHLCV_CLOSE:
        return None
    try:
        return float(candle[OHLCV_CLOSE])
    except (TypeError, ValueError):
        return None


def _is_consistent_direction(closes: list[float]) -> bool:
    if len(closes) < CONSISTENT_DIRECTION_WINDOW:
        return False
    window = closes[-CONSISTENT_DIRECTION_WINDOW:]
    increasing = all(window[i] < window[i + 1] for i in range(len(window) - 1))
    decreasing = all(window[i] > window[i + 1] for i in range(len(window) - 1))
    return increasing or decreasing


def detect_market_regime(candles: list[list[Any]] | None) -> str:
    """Detect market regime using volatility, oscillation and directional momentum."""
    if candles is None or len(candles) < 5:
        return "RANGE"

    closes = [_safe_close(c) for c in candles[-5:]]
    if any(close is None for close in closes):
        return "RANGE"

    numeric_closes = [float(c) for c in closes if c is not None]
    min_close = min(numeric_closes)
    max_close = max(numeric_closes)
    last_close = numeric_closes[-1]

    if last_close == 0:
        return "RANGE"

    volatility_pct = ((max_close - min_close) / last_close) * 100
    oscillation_pct = ((max_close - min_close) / min_close) * 100 if min_close else 0.0
    momentum = numeric_closes[-1] > numeric_closes[-2] > numeric_closes[-3]
    consistent_direction = _is_consistent_direction(numeric_closes)

    if volatility_pct < LOW_VOL_THRESHOLD_PCT:
        return "LOW_VOL"

    if not momentum and oscillation_pct < RANGE_OSCILLATION_THRESHOLD_PCT:
        return "RANGE"

    if momentum and consistent_direction:
        return "TREND"

    return "RANGE"
