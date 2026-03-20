from __future__ import annotations

from models import FlowReport


def compute_flow_report(ticker: str) -> FlowReport:
    proxy = (sum(ord(c) for c in ticker) % 20) - 10
    fii = proxy * 100.0
    dii = -proxy * 70.0
    score = 0.5 + proxy / 40
    score = max(0.0, min(1.0, score))
    return FlowReport(
        score=score,
        fii_cash=fii,
        dii_cash=dii,
        delivery_pct=45 + proxy,
        block_deal_signal="none",
        note="Flow proxy from local heuristic; pluggable NSE adapters supported.",
    )
