from __future__ import annotations

from services.monitoring import replay_signals


if __name__ == "__main__":
    rows = [
        {"ticker": "RELIANCE.NS", "pnl_r": 1.2},
        {"ticker": "RELIANCE.NS", "pnl_r": -0.8},
        {"ticker": "RELIANCE.NS", "pnl_r": 0.5},
    ]
    print(replay_signals(rows))
