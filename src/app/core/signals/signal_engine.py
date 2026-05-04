"""Signal engine metrics helpers.

This module adds extra analytics metrics into ``signal[\"metrics\"]`` without
modifying signal generation logic or BUY/SELL conditions.
"""

from __future__ import annotations

from typing import Any


OHLCV_OPEN = 1
OHLCV_HIGH = 2
OHLCV_LOW = 3
OHLCV_CLOSE = 4
OHLCV_VOLUME = 5


def _safe_get(candle: list[Any] | tuple[Any, ...], index: int) -> float | None:
    """Return numeric candle field or None when unavailable/invalid."""
    if len(candle) <= index:
        return None
    try:
        return float(candle[index])
    except (TypeError, ValueError):
        return None


def add_signal_metrics(signal: dict[str, Any], candles: list[list[Any] | tuple[Any, ...]]) -> dict[str, Any]:
    """Add extra metrics into ``signal['metrics']`` using OHLCV candle data.

    Added fields:
    - momentum: bool | None
    - volume_trend: bool | None
    - candle_strength: float | None
    - volatility: float | None

    Edge cases:
    - insufficient data -> None for corresponding metric
    - fewer than 5 candles -> volatility is None
    """
    signal.setdefault("metrics", {})

    momentum: bool | None = None
    volume_trend: bool | None = None
    candle_strength: float | None = None
    volatility: float | None = None

    # momentum: close[-1] > close[-2] > close[-3]
    if len(candles) >= 3:
        c1 = _safe_get(candles[-1], OHLCV_CLOSE)
        c2 = _safe_get(candles[-2], OHLCV_CLOSE)
        c3 = _safe_get(candles[-3], OHLCV_CLOSE)
        if c1 is not None and c2 is not None and c3 is not None:
            momentum = c1 > c2 > c3

    # volume_trend: volume[-1] > volume[-2]
    if len(candles) >= 2:
        v1 = _safe_get(candles[-1], OHLCV_VOLUME)
        v2 = _safe_get(candles[-2], OHLCV_VOLUME)
        if v1 is not None and v2 is not None:
            volume_trend = v1 > v2

    # candle_strength for last candle: abs(close-open)/(high-low), range==0 -> 0
    if len(candles) >= 1:
        last = candles[-1]
        o = _safe_get(last, OHLCV_OPEN)
        h = _safe_get(last, OHLCV_HIGH)
        l = _safe_get(last, OHLCV_LOW)
        c = _safe_get(last, OHLCV_CLOSE)
        if None not in (o, h, l, c):
            candle_range = h - l
            if candle_range == 0:
                candle_strength = 0.0
            else:
                body = abs(c - o)
                candle_strength = body / candle_range

    # volatility: average(high-low) over last 5 candles, only if len >= 5
    if len(candles) >= 5:
        ranges: list[float] = []
        for candle in candles[-5:]:
            h = _safe_get(candle, OHLCV_HIGH)
            l = _safe_get(candle, OHLCV_LOW)
            if h is None or l is None:
                ranges = []
                break
            ranges.append(h - l)
        if ranges:
            volatility = sum(ranges) / len(ranges)

    signal["metrics"]["momentum"] = momentum
    signal["metrics"]["volume_trend"] = volume_trend
    signal["metrics"]["candle_strength"] = candle_strength
    signal["metrics"]["volatility"] = volatility

    print(
        "Signal metrics: "
        f"momentum={momentum}, "
        f"volume_trend={volume_trend}, "
        f"candle_strength={candle_strength}, "
        f"volatility={volatility}"
    )

    return signal
