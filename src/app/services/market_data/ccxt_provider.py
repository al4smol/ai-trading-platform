"""Live market data provider powered by ccxt."""

from __future__ import annotations

import importlib.util
import time
from pathlib import Path
from typing import Any

import ccxt


def _load_config() -> dict[str, Any]:
    loader_path = Path(__file__).resolve().parents[2] / "config" / "config_loader.py"
    spec = importlib.util.spec_from_file_location("app_config_loader", loader_path)
    if spec is None or spec.loader is None:
        raise Exception(f"failed_to_load_config_loader: {loader_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.load_config()


class CcxtProvider:
    """Fetch OHLCV data from configurable ccxt exchange."""

    def __init__(self) -> None:
        self.config = _load_config()

    def _build_exchange(self) -> tuple[str, Any]:
        exchange_name = self.config.get("default_exchange", "binance")
        exchanges_cfg = self.config.get("exchanges", {})
        params = exchanges_cfg.get(exchange_name, {})
        exchange_class = getattr(ccxt, exchange_name)
        exchange = exchange_class(params)
        return exchange_name, exchange

    def fetch_ohlcv(self, symbol: str, timeframe: str = "1m", limit: int = 50) -> list[dict[str, Any]]:
        try:
            exchange_name, exchange = self._build_exchange()
            print(">>> CCXT FETCH START")
            print("EXCHANGE:", exchange_name)
            print("SYMBOL:", symbol)

            for attempt in range(1, 4):
                try:
                    raw = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
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
