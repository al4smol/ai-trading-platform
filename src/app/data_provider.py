"""Market data provider abstractions."""

from __future__ import annotations

import os
import random
from dataclasses import dataclass, field
from typing import Any

from app.config.config_loader import get_strategy_config
from app.services.market_data.ccxt_provider import CcxtProvider


@dataclass
class DataProvider:
    """Simple mockable OHLCV data provider."""

    mock: bool = True
    ccxt_provider: CcxtProvider = field(default_factory=CcxtProvider)

    def get_candles(self, symbol: str, limit: int | None = None) -> list[list[Any]]:
        if not symbol:
            raise ValueError("symbol must be non-empty")

        strategy_config = get_strategy_config()
        candles_limit = limit if limit is not None else strategy_config["candle_limit"]

        if candles_limit <= 0:
            return []

        if not self.mock:
            print("TRYING REAL DATA")
            candles = self.ccxt_provider.fetch_ohlcv(symbol, limit=candles_limit)
            if not candles:
                print("DataProvider: fallback to mock")
                candles = self._generate_mock(symbol, limit=candles_limit)
                print("DATA SOURCE:", "MOCK")
            else:
                print("DATA SOURCE:", "REAL")
            print("LAST PRICE:", candles[-1]["close"])
            return self._normalize_for_pipeline(candles)

        candles = self._generate_mock(symbol, limit=candles_limit)
        print("DATA SOURCE:", "MOCK")
        print("LAST PRICE:", candles[-1]["close"])
        return self._normalize_for_pipeline(candles)

    def _generate_mock(self, symbol: str, limit: int) -> list[dict[str, Any]]:
        candles = self._generate_mock_ohlcv(limit=limit)
        normalized = [
            {
                "timestamp": row[0],
                "open": row[1],
                "high": row[2],
                "low": row[3],
                "close": row[4],
                "volume": row[5],
            }
            for row in candles
        ]
        print(f"DataProvider: generated {len(normalized)} mock candles for {symbol}")
        return normalized

    def _normalize_for_pipeline(self, candles: list[dict[str, Any]]) -> list[list[Any]]:
        return [[c["timestamp"], c["open"], c["high"], c["low"], c["close"], c["volume"]] for c in candles]

    def _generate_mock_ohlcv(self, limit: int) -> list[list[Any]]:
        mode = os.getenv("MOCK_MARKET_MODE", "mixed").strip().lower()
        candles: list[list[Any]] = []
        price = 100.0

        trend_direction = random.choice([-1, 1])

        for i in range(limit):
            open_price = price
            impulse = False

            if mode == "range":
                move_pct = random.uniform(-0.3, 0.3)
            elif mode == "trend":
                move_pct = trend_direction * random.uniform(0.2, 0.8)
            elif mode == "volatile":
                move_pct = random.uniform(-1.5, 1.5)
            else:
                move_pct = random.uniform(-0.5, 0.5)

            if random.random() < 0.2:
                impulse = True
                move_pct += random.uniform(-2.0, 2.0)

            close_price = open_price * (1 + (move_pct / 100))
            wick_pct = random.uniform(0.05, 0.3)
            high = max(open_price, close_price) * (1 + wick_pct / 100)
            low = min(open_price, close_price) * (1 - wick_pct / 100)

            base_volume = random.uniform(900, 1200)
            if impulse:
                base_volume *= random.uniform(2, 4)
            volume = base_volume + (i * random.uniform(0, 30))

            candles.append([i, open_price, high, low, close_price, volume])
            price = close_price

        return candles
