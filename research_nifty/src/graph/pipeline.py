from __future__ import annotations

from datetime import datetime

import pandas as pd
from langgraph.graph import END, StateGraph

from models import FinalVerdict, ResearchState
from reports.writer import build_json_summary, build_markdown_report, persist_outputs
from services.derivatives import compute_derivatives_report
from services.evaluation import build_consensus
from services.flow import compute_flow_report
from services.fundamentals import compute_fundamental_report
from services.llm import LLMRouter
from services.market_data import MarketDataProvider
from services.market_data.macro import compute_macro_context
from services.notifications import EmailClient
from services.persistence import ResearchStore
from services.policy import PolicyEngine
from services.risk import build_risk_plan
from services.sentiment import compute_sentiment_report
from services.technical import compute_technical_report
from services.valuation import compute_valuation_report


class ResearchGraph:
    def __init__(self) -> None:
        self.market = MarketDataProvider()
        self.store = ResearchStore()
        self.policy_engine = PolicyEngine()
        self.llm = LLMRouter()
        self.email = EmailClient()
        self.graph = self._build()

    def _build(self):
        g = StateGraph(dict)
        g.add_node("universe_loader", self.universe_loader)
        g.add_node("market_data_loader", self.market_data_loader)
        g.add_node("macro", self.macro_analyst)
        g.add_node("technical", self.technical_quant)
        g.add_node("fundamental", self.fundamental_scout)
        g.add_node("valuation", self.valuation_analyst)
        g.add_node("sentiment", self.sentiment_scout)
        g.add_node("derivatives", self.derivatives_analyst)
        g.add_node("flow", self.flow_analyst)
        g.add_node("jury", self.jury_engine)
        g.add_node("risk", self.risk_manager)
        g.add_node("report", self.report_writer)
        g.add_node("persist", self.persistence_notification)

        g.set_entry_point("universe_loader")
        g.add_edge("universe_loader", "market_data_loader")
        g.add_edge("market_data_loader", "macro")
        g.add_edge("macro", "technical")
        g.add_edge("technical", "fundamental")
        g.add_edge("fundamental", "valuation")
        g.add_edge("valuation", "sentiment")
        g.add_edge("sentiment", "derivatives")
        g.add_edge("derivatives", "flow")
        g.add_edge("flow", "jury")
        g.add_edge("jury", "risk")
        g.add_edge("risk", "report")
        g.add_edge("report", "persist")
        g.add_edge("persist", END)
        return g.compile()

    async def run_for_ticker(self, ticker: str) -> ResearchState:
        init = ResearchState(ticker=ticker).model_dump()
        out = await self.graph.ainvoke(init)
        return ResearchState(**out)

    def _fallback_ohlcv(self, start_price: float = 100.0, periods: int = 260, freq: str = "1D") -> pd.DataFrame:
        idx = pd.date_range(end=datetime.utcnow(), periods=periods, freq=freq)
        close = pd.Series(start_price, index=idx).astype(float)
        return pd.DataFrame(
            {
                "Open": close,
                "High": close * 1.002,
                "Low": close * 0.998,
                "Close": close,
                "Volume": 1_000_000.0,
            },
            index=idx,
        )

    async def universe_loader(self, state: dict) -> dict:
        state.setdefault("metadata", {})["universe"] = "Nifty 50"
        state["updated_at"] = datetime.utcnow()
        return state

    async def market_data_loader(self, state: dict) -> dict:
        t = state["ticker"]
        info = self.market.get_info(t)
        px_hint = float(info.get("currentPrice") or info.get("previousClose") or 100.0)

        try:
            d1 = self.market.load_ohlcv(t, "6mo", "1d")
        except Exception as e:
            d1 = self._fallback_ohlcv(px_hint, periods=260, freq="1D")
            state.setdefault("errors", []).append(f"d1 fallback used for {t}: {e}")

        try:
            h1 = self.market.load_ohlcv(t, "1mo", "1h")
        except Exception as e:
            h1 = self._fallback_ohlcv(px_hint, periods=160, freq="1H")
            state.setdefault("errors", []).append(f"h1 fallback used for {t}: {e}")

        state["metadata"]["d1"] = d1
        state["metadata"]["h1"] = h1
        state["metadata"]["info"] = info
        state["metadata"]["news"] = self.market.get_news(t)
        state["company_name"] = info.get("shortName")
        state["sector"] = info.get("sector")
        state["research_freshness_ts"] = datetime.utcnow()
        return state

    async def macro_analyst(self, state: dict) -> dict:
        snapshot = self.market.load_macro_snapshot()
        state["macro_context"] = compute_macro_context(snapshot, state.get("sector")).model_dump()
        return state

    async def technical_quant(self, state: dict) -> dict:
        d1 = state["metadata"]["d1"]
        h1 = state["metadata"]["h1"]
        state["technical_metrics"] = compute_technical_report(d1, h1).model_dump()
        return state

    async def fundamental_scout(self, state: dict) -> dict:
        state["fundamental_score"] = compute_fundamental_report(state["metadata"].get("info", {})).model_dump()
        return state

    async def valuation_analyst(self, state: dict) -> dict:
        pe = state["fundamental_score"].get("pe_ttm")
        state["valuation_report"] = compute_valuation_report(pe).model_dump()
        return state

    async def sentiment_scout(self, state: dict) -> dict:
        report = await compute_sentiment_report(state["ticker"], state["metadata"].get("news", []), self.llm)
        state["sentiment_report"] = report.model_dump()
        return state

    async def derivatives_analyst(self, state: dict) -> dict:
        state["derivatives_report"] = compute_derivatives_report(state["ticker"]).model_dump()
        return state

    async def flow_analyst(self, state: dict) -> dict:
        state["flow_report"] = compute_flow_report(state["ticker"]).model_dump()
        return state

    async def jury_engine(self, state: dict) -> dict:
        rs = ResearchState(**state)
        jury = build_consensus(rs, self.policy_engine.current)
        state["jury_report"] = jury.model_dump()
        state["final_verdict"] = FinalVerdict(
            signal=jury.signal,
            confidence_score=jury.confidence_score,
            conviction_band=jury.conviction_band,
            rationale="; ".join(jury.rationale_tree),
        ).model_dump()
        return state

    async def risk_manager(self, state: dict) -> dict:
        px = float(state["metadata"]["d1"]["Close"].iloc[-1])
        atr = float(state["technical_metrics"].get("atr", 0.0))
        plan = build_risk_plan(px, atr, state["jury_report"]["confidence_score"], state["jury_report"]["signal"], state["macro_context"]["regime_label"], trend=state["technical_metrics"].get("trend", "range"))
        state["risk_report"] = plan.model_dump()
        return state

    async def report_writer(self, state: dict) -> dict:
        rs = ResearchState(**state)
        state["markdown_report"] = build_markdown_report(rs)
        rs = ResearchState(**state)
        state["json_summary"] = build_json_summary(rs)
        return state

    async def persistence_notification(self, state: dict) -> dict:
        rs = ResearchState(**state)
        run_id = self.store.save_run(rs)
        md, js = persist_outputs(rs)
        state["metadata"]["run_id"] = run_id
        state["metadata"]["report_path"] = str(md)
        state["metadata"]["json_path"] = str(js)
        return state
