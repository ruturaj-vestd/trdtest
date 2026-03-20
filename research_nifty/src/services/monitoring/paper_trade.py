from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ReplayResult:
    ticker: str
    trades: int
    win_rate: float
    expectancy: float


def replay_signals(rows: list[dict]) -> ReplayResult:
    wins = sum(1 for r in rows if r.get("pnl_r", 0) > 0)
    trades = len(rows)
    exp = sum(r.get("pnl_r", 0.0) for r in rows) / trades if trades else 0.0
    return ReplayResult(ticker=rows[0]["ticker"] if rows else "N/A", trades=trades, win_rate=(wins / trades if trades else 0), expectancy=exp)
