from __future__ import annotations

import json

import pandas as pd

from services.llm import estimate_daily_cost
from services.notifications import EmailClient, build_daily_digest
from services.persistence import ResearchStore


if __name__ == "__main__":
    store = ResearchStore()
    df = store.get_recent_runs(100)
    if df.empty:
        print("No runs to digest")
        raise SystemExit(0)
    sdf = pd.DataFrame([json.loads(x) for x in df["summary_json"]])
    sdf = sdf.rename(columns={"confidence_score": "confidence", "stop_loss": "stop_loss", "entry": "entry", "ticker": "ticker", "signal": "signal"})
    body = build_daily_digest(sdf, regime="Neutral", llm_cost=estimate_daily_cost(2, 50))
    sent = EmailClient().send("Daily Nifty Digest", body)
    print("Sent" if sent else "Skipped (email not configured)")
