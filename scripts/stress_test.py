import time

from app.evaluator import reject_stats
from app.main import run


duration_minutes = 30
end_time = time.time() + duration_minutes * 60

stats = {
    "runs": 0,
    "signals": 0,
    "accepted": 0,
    "rejected": 0,
    "no_signal": 0,
}

while time.time() < end_time:
    result = run("BTC/USDT", use_mock=False)

    stats["runs"] += 1

    if result is None:
        stats["no_signal"] += 1
    elif isinstance(result, dict) and result.get("decision") == "REJECT":
        stats["rejected"] += 1
        stats["signals"] += 1
    else:
        stats["accepted"] += 1
        stats["signals"] += 1

    time.sleep(5)

print("FINAL STATS:", stats)
print("REJECT STATS:", reject_stats)
