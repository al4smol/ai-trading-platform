"""Market data provider abstractions."""

from __future__ import annotations

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
            candles: list[list[Any]] = []
            price = 100.0
            for i in range(limit):
                open_price = price
                close_price = price + (1.0 if i % 2 == 0 else -0.3)
                high = max(open_price, close_price) + 0.2
                low = min(open_price, close_price) - 0.2
                volume = 1000 + i * 50
                candles.append([i, open_price, high, low, close_price, volume])
                price = close_price
            print(f"DataProvider: generated {len(candles)} mock candles for {symbol}")
            return candles

        # Placeholder for real provider integration
        print(f"DataProvider: no live provider configured for {symbol}")
        return []
