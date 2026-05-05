"""Range-bound mean-reversion strategy."""

from __future__ import annotations

from typing import Any

from app.config.config_loader import load_config
from app.core.signals.signal_engine import add_signal_metrics


OHLCV_OPEN = 1
OHLCV_HIGH = 2
OHLCV_LOW = 3
OHLCV_CLOSE = 4


def _get_field(candle: Any, index: int, key: str) -> float | None:
    if isinstance(candle, dict):
        value = candle.get(key)
    elif isinstance(candle, (list, tuple)) and len(candle) > index:
        value = candle[index]
    else:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _load_range_config() -> dict[str, float]:
    config = load_config()
    strategy_cfg = config.get("range_strategy", {})
    return {
        "range_window": int(strategy_cfg.get("range_window", 20)),
        "entry_zone_low": float(strategy_cfg.get("entry_zone_low", 0.25)),
        "entry_zone_high": float(strategy_cfg.get("entry_zone_high", 0.75)),
        "breakout_buffer": float(strategy_cfg.get("breakout_buffer", 0.002)),
        "min_volatility": float(strategy_cfg.get("min_volatility", 0.2)),
        "min_candle_strength": float(strategy_cfg.get("min_candle_strength", 0.2)),
    }


def run_range_strategy(candles: list[dict[str, Any]] | list[list[Any]], symbol: str) -> dict[str, Any] | None:
    cfg = _load_range_config()

    if not candles:
        print("STRATEGY: RANGE")
        print("RANGE: no valid setup")
        return None

    window = candles[-cfg["range_window"] :]
    highs = [_get_field(candle, OHLCV_HIGH, "high") for candle in window]
    lows = [_get_field(candle, OHLCV_LOW, "low") for candle in window]
    closes = [_get_field(candle, OHLCV_CLOSE, "close") for candle in window]

    if any(v is None for v in highs) or any(v is None for v in lows) or closes[-1] is None:
        print("STRATEGY: RANGE")
        print("RANGE: no valid setup")
        return None

    range_high = max(highs)
    range_low = min(lows)
    range_width = range_high - range_low
    if range_width <= 0:
        print("STRATEGY: RANGE")
        print("RANGE: no valid setup")
        return None

    last_price = closes[-1]
    range_mid = (range_high + range_low) / 2.0
    pos = (last_price - range_low) / range_width

    print("STRATEGY: RANGE")
    print("RANGE HIGH:", range_high)
    print("RANGE LOW:", range_low)
    print("POSITION IN RANGE:", pos)

    breakout_up = last_price > range_high * (1 + cfg["breakout_buffer"])
    breakout_down = last_price < range_low * (1 - cfg["breakout_buffer"])

    signal_base = {"symbol": symbol, "action": "BUY", "reason": "RANGE_MEAN_REVERSION", "metrics": {}}
    signal_with_metrics = add_signal_metrics(signal_base, candles)
    metrics = signal_with_metrics.get("metrics", {})

    momentum = metrics.get("momentum")
    candle_strength = metrics.get("candle_strength")
    volatility = metrics.get("volatility")

    if breakout_up or breakout_down:
        print("RANGE: no valid setup")
        return None

    if volatility is None or volatility < cfg["min_volatility"]:
        print("RANGE: no valid setup")
        return None

    if candle_strength is None or candle_strength < cfg["min_candle_strength"]:
        print("RANGE: no valid setup")
        return None

    action: str | None = None

    if pos < cfg["entry_zone_low"]:
        if momentum is True:
            print("RANGE: no valid setup")
            return None
        action = "BUY"
    elif pos > cfg["entry_zone_high"]:
        if momentum is False:
            print("RANGE: no valid setup")
            return None
        action = "SELL"

    if action is None:
        print("RANGE: no valid setup")
        return None

    distance_from_mid = min(1.0, abs(pos - 0.5) * 2)
    volatility_factor = min(1.0, volatility / max(cfg["min_volatility"], 1e-9))
    confidence = round(distance_from_mid * candle_strength * volatility_factor, 4)

    result = {
        "symbol": symbol,
        "action": action,
        "reason": "RANGE_MEAN_REVERSION",
        "confidence": confidence,
        "metrics": {
            **metrics,
            "range_high": range_high,
            "range_low": range_low,
            "range_mid": range_mid,
            "position_in_range": pos,
            "distance_from_mid": distance_from_mid,
        },
    }
    print("RANGE SIGNAL:", result)
    return result
