import asyncio

import pandas as pd

from graph.pipeline import ResearchGraph


def test_pipeline_e2e_mocked(monkeypatch):
    g = ResearchGraph()

    def fake_ohlcv(*args, **kwargs):
        idx = pd.date_range("2025-01-01", periods=250, freq="D")
        return pd.DataFrame({"Open": 100, "High": 102, "Low": 99, "Close": range(1, 251), "Volume": 1000}, index=idx)

    monkeypatch.setattr(g.market, "load_ohlcv", fake_ohlcv)
    monkeypatch.setattr(g.market, "get_info", lambda t: {"shortName": "MockCo", "sector": "IT", "trailingPE": 20, "returnOnEquity": 0.2})
    monkeypatch.setattr(g.market, "get_news", lambda t: [])
    monkeypatch.setattr(g.market, "load_macro_snapshot", lambda: {"usdinr_ret1d": 0.001, "brent_ret1d": 0.0, "vix_ret1d": -0.02, "spx_ret1d": 0.01, "nasdaq_ret1d": 0.01})

    state = asyncio.run(g.run_for_ticker("MOCK.NS"))
    assert state.final_verdict.signal in {"BUY", "SELL", "HOLD"}
    assert state.json_summary["ticker"] == "MOCK.NS"
