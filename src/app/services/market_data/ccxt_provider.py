"""Live market data provider powered by ccxt."""

from __future__ import annotations

import time
import importlib
import importlib.util
from typing import Any

from app.config.config_loader import load_config


CCXT_AVAILABLE = importlib.util.find_spec("ccxt") is not None
ccxt = importlib.import_module("ccxt") if CCXT_AVAILABLE else None


class CcxtProvider:
    """Fetch OHLCV data from configurable ccxt exchange."""

    def __init__(self) -> None:
        self.config = load_config()

    def _build_exchange(self) -> tuple[str, Any]:
        if not CCXT_AVAILABLE or ccxt is None:
            raise RuntimeError("ccxt_not_installed")
        exchange_name = self.config.get("default_exchange", "binance")
        exchanges_cfg = self.config.get("exchanges", {})
        params = exchanges_cfg.get(exchange_name, {})
        exchange_class = getattr(ccxt, exchange_name)
        exchange = exchange_class(params)
        return exchange_name, exchange

    def fetch_ohlcv(self, symbol: str, timeframe: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
        strategy_cfg = self.config.get("strategy", {})
        fetch_timeframe = timeframe if timeframe is not None else strategy_cfg.get("timeframe", "1m")
        fetch_limit = limit if limit is not None else strategy_cfg.get("candle_limit", 50)

        try:
            exchange_name, exchange = self._build_exchange()
            print(">>> CCXT FETCH START")
            print("EXCHANGE:", exchange_name)
            print("SYMBOL:", symbol)

            for attempt in range(1, 4):
                try:
                    raw = exchange.fetch_ohlcv(symbol, timeframe=fetch_timeframe, limit=fetch_limit)
                    return [
                        {
                            "timestamp": row[0],
                            "open": row[1],
                            "high": row[2],
                            "low": row[3],
                            "close": row[4],
                            "volume": row[5],
                        }
                        for row in raw
                    ]
                except (ccxt.RequestTimeout, ccxt.NetworkError, ccxt.ExchangeNotAvailable) as e:
                    print(f"CCXT RETRY {attempt}/3:", e)
                    time.sleep(1)
                except ccxt.RateLimitExceeded as e:
                    print("CCXT RATE LIMIT:", e)
                    time.sleep(1)

            return []
        except Exception as e:
            print("CCXT ERROR:", e)
            return []
