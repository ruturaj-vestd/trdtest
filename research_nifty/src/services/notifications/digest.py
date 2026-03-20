from __future__ import annotations

from datetime import date

import pandas as pd


def build_daily_digest(signals: pd.DataFrame, regime: str, llm_cost: float) -> str:
    top_buy = signals[signals["signal"] == "BUY"].sort_values("confidence", ascending=False).head(5)
    top_sell = signals[signals["signal"] == "SELL"].sort_values("confidence", ascending=False).head(5)
    lines = [
        f"Daily Nifty Digest - {date.today().isoformat()}",
        f"Macro regime: {regime}",
        "",
        "Top BUY ideas:",
    ]
    lines += [f"- {r.ticker}: conf {r.confidence:.2f}, entry {r.entry:.2f}" for _, r in top_buy.iterrows()] or ["- None"]
    lines += ["", "Top SELL/AVOID ideas:"]
    lines += [f"- {r.ticker}: conf {r.confidence:.2f}, stop {r.stop_loss:.2f}" for _, r in top_sell.iterrows()] or ["- None"]
    lines += ["", f"LLM usage estimated today: ${llm_cost:.2f}", "Risk note: Keep gross exposure controlled in high-volatility sessions."]
    return "\n".join(lines)
