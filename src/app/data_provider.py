"""Market data provider abstractions."""

from __future__ import annotations

import os
import random
from dataclasses import dataclass
from typing import Any


@dataclass
class DataProvider:
    """Simple mockable OHLCV data provider."""

    mock: bool = True

    def get_candles(self, symbol: str, limit: int = 20) -> list[list[Any]]:
        if not symbol:
            raise ValueError("symbol must be non-empty")
        if limit <= 0:
            return []

        if self.mock:
            candles = self._generate_mock_ohlcv(limit=limit)
            print(f"DataProvider: generated {len(candles)} mock candles for {symbol}")
            return candles

        # Placeholder for real provider integration
        print(f"DataProvider: no live provider configured for {symbol}")
        return []

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
