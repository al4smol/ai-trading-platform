"""Entrypoint for ai-trading-platform pipeline."""

from __future__ import annotations

import argparse
from typing import Any

from app.data_provider import DataProvider
from app.evaluator import evaluate_signal
from app.execution import build_trade
from app.fast_move import detect_fast_move
from app.signal_engine import generate_signal


def run(symbol: str, mock: bool) -> dict[str, Any] | None:
    provider = DataProvider(mock=mock)
    candles = provider.get_candles(symbol=symbol, limit=20)
    event = detect_fast_move(symbol=symbol, candles=candles)
    signal = generate_signal(event=event, candles=candles)

    if signal:
        evaluation = evaluate_signal(signal)
        print("Evaluation:", evaluation)

        if isinstance(evaluation, dict) and evaluation.get("decision") == "REJECT":
            print("Signal rejected")
            return evaluation

        trade = build_trade(signal, candles)
        print("TRADE:", trade)
        return trade

    print("No signal → skip evaluation")
    return None


def _parse_bool(raw: str) -> bool:
    return raw.strip().lower() in {"1", "true", "yes", "y"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--mock", default="True")
    args = parser.parse_args()
    run(symbol=args.symbol, mock=_parse_bool(args.mock))


if __name__ == "__main__":
    main()
