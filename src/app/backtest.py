"""Simple stochastic backtest runner for pipeline statistics."""

from __future__ import annotations

from app.main import run


def run_backtest(n: int = 100) -> None:
    stats = {
        "runs": 0,
        "signals": 0,
        "accepted": 0,
        "rejected": 0,
        "no_signal": 0,
        "trades": 0,
        "reasons": {},
    }

    for _ in range(n):
        result = run("BTCUSDT", True)

        stats["runs"] += 1

        if result is None or result == "No signal":
            stats["no_signal"] += 1
            continue

        stats["signals"] += 1

        # если это trade (есть entry)
        if isinstance(result, dict) and "entry" in result:
            stats["trades"] += 1
            stats["accepted"] += 1

        # если это evaluation reject
        if isinstance(result, dict) and result.get("decision") == "REJECT":
            stats["rejected"] += 1

            reason = result.get("reason", "unknown")
            stats["reasons"][reason] = stats["reasons"].get(reason, 0) + 1

    print("BACKTEST RESULT:")
    print(stats)


if __name__ == "__main__":
    run_backtest(100)
