from __future__ import annotations

import argparse
import asyncio

import pandas as pd

from graph import ResearchGraph
from services.market_data import NIFTY50


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=50)
    args = p.parse_args()
    g = ResearchGraph()
    rows = []
    for t in NIFTY50[: args.limit]:
        s = asyncio.run(g.run_for_ticker(t))
        rows.append({"ticker": t, "signal": s.final_verdict.signal, "confidence": s.final_verdict.confidence_score, "entry": s.risk_report.entry, "entry_date": s.risk_report.estimated_entry_date, "target_1": s.risk_report.targets[0], "target_2": s.risk_report.targets[1], "target_3": s.risk_report.targets[2], "stop": s.risk_report.stop_loss})
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
