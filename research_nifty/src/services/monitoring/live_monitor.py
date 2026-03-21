from __future__ import annotations

import asyncio

from graph.pipeline import ResearchGraph
from services.market_data import NIFTY50
from utils import is_nse_open


async def run_live_monitor(interval_minutes: int = 15, tickers: list[str] | None = None) -> None:
    tickers = tickers or NIFTY50
    graph = ResearchGraph()
    while True:
        if is_nse_open():
            for t in tickers:
                await graph.run_for_ticker(t)
        await asyncio.sleep(interval_minutes * 60)
