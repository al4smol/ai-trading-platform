"""JSON config loader for market data providers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_CONFIG_CACHE: dict[str, Any] | None = None


def load_config() -> dict[str, Any]:
    """Load and cache application config from JSON file."""
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE

    config_path = Path(__file__).with_name("config.json")
    try:
        with config_path.open("r", encoding="utf-8") as f:
            _CONFIG_CACHE = json.load(f)
    except Exception as e:
        print("CONFIG LOAD ERROR:", e)
        raise Exception(f"failed_to_load_config: {config_path}") from e

    return _CONFIG_CACHE


def get_strategy_config() -> dict[str, Any]:
    """Return strategy-specific config section."""
    config = load_config()
    return config["strategy"]
