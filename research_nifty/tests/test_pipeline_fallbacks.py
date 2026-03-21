import asyncio

from graph.pipeline import ResearchGraph


def test_market_data_loader_uses_fallback(monkeypatch):
    g = ResearchGraph()

    def boom(*args, **kwargs):
        raise ValueError("no data")

    monkeypatch.setattr(g.market, "load_ohlcv", boom)
    monkeypatch.setattr(g.market, "get_info", lambda t: {"currentPrice": 123.0, "shortName": "Mock", "sector": "IT"})
    monkeypatch.setattr(g.market, "get_news", lambda t: [])
    monkeypatch.setattr(g.market, "load_macro_snapshot", lambda: {"usdinr_ret1d": 0.0, "brent_ret1d": 0.0, "vix_ret1d": 0.0, "spx_ret1d": 0.0, "nasdaq_ret1d": 0.0})

    state = asyncio.run(g.run_for_ticker("MOCK.NS"))
    assert state.json_summary["ticker"] == "MOCK.NS"
    assert any("fallback used" in e for e in state.errors)
