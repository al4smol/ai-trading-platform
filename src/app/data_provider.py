"""Data provider for OHLCV candles."""

from __future__ import annotations

import random
import time
from typing import Any, List


class DataProvider:
    """Loads OHLCV candles either from mock generator or ccxt exchange."""

    def __init__(self, exchange: Any | None = None, mock: bool = True) -> None:
        self.exchange = exchange
        self.mock = mock

    def _generate_mock_ohlcv(self, limit: int = 50) -> List[List[float]]:
        """Generate synthetic OHLCV candles.

        Candle format: [timestamp, open, high, low, close, volume]
        """
        candles: List[List[float]] = []
        price = 100.0

        start_ts_ms = int(time.time() * 1000) - (limit * 60_000)

        for i in range(limit):
            open_price = price

            # Random movement in ±(0.2%..0.5%) range.
            pct_change = random.uniform(0.002, 0.005)
            direction = random.choice((-1.0, 1.0))
            close_price = open_price * (1 + direction * pct_change)

            # High/low around open/close with small random wick size.
            wick_up = random.uniform(0.0005, 0.003)
            wick_down = random.uniform(0.0005, 0.003)

            base_high = max(open_price, close_price)
            base_low = min(open_price, close_price)
            high_price = base_high * (1 + wick_up)
            low_price = base_low * (1 - wick_down)

            volume = random.uniform(100, 1000)
            timestamp = start_ts_ms + (i * 60_000)

            candles.append(
                [
                    timestamp,
                    round(open_price, 6),
                    round(high_price, 6),
                    round(low_price, 6),
                    round(close_price, 6),
                    round(volume, 6),
                ]
            )

            price = close_price

        return candles

    def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1m",
        limit: int = 50,
    ) -> List[List[float]]:
        """Return OHLCV candles as list (never None)."""
        if self.mock:
            print("Using MOCK data")
            return self._generate_mock_ohlcv(limit)

        if self.exchange is None:
            print("Using MOCK data")
            return self._generate_mock_ohlcv(limit)

        candles = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        return candles or []
