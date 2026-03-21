from __future__ import annotations

import asyncio
import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from graph import ResearchGraph
from services.llm import estimate_daily_cost
from services.market_data import MarketDataProvider, NIFTY50
from services.persistence import ResearchStore

st.set_page_config(page_title="Nifty Multi-Agent Research", layout="wide")
st.title("Nifty 50 Multi-Agent Research + Monitoring")

graph = ResearchGraph()
store = ResearchStore()
md = MarketDataProvider()

pages = st.tabs([
    "Single Stock Research", "Batch Scan Dashboard", "Top Ideas", "Live Monitor", "History", "Strategy Performance", "Calibration", "Experiment Comparison", "Self-Improvement Proposals", "Model Usage / Cost", "Policy Promotion Controls"
])

with pages[0]:
    ticker = st.selectbox("Ticker", NIFTY50)
    if st.button("Run Full Research"):
        state = asyncio.run(graph.run_for_ticker(ticker))
        st.subheader("Final Recommendation")
        st.write(state.final_verdict.model_dump())
        st.markdown(state.markdown_report)
        st.json(state.json_summary)

        d1 = md.load_ohlcv(ticker)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=d1.index, y=d1["Close"], name="Close"))
        fig.add_hline(y=state.risk_report.stop_loss, line_dash="dot", annotation_text="Stop")
        for i, t in enumerate(state.risk_report.targets, start=1):
            fig.add_hline(y=t, line_dash="dash", annotation_text=f"T{i}")
        st.plotly_chart(fig, width="stretch")

with pages[1]:
    batch_count = st.slider("Batch universe size", min_value=5, max_value=len(NIFTY50), value=len(NIFTY50))
    if st.button("Run Batch Scan"):
        rows = []
        failures = []
        for t in NIFTY50[:batch_count]:
            try:
                s = asyncio.run(graph.run_for_ticker(t))
                rows.append({
                    "ticker": t,
                    "signal": s.final_verdict.signal,
                    "confidence": s.final_verdict.confidence_score,
                    "setup_quality": s.jury_report.setup_type,
                    "sector": s.sector,
                    "entry": s.risk_report.entry,
                    "stop": s.risk_report.stop_loss,
                    "target_1": s.risk_report.targets[0] if s.risk_report.targets else None,
                    "target_2": s.risk_report.targets[1] if len(s.risk_report.targets) > 1 else None,
                    "target_3": s.risk_report.targets[2] if len(s.risk_report.targets) > 2 else None,
                    "entry_date_est": s.risk_report.estimated_entry_date,
                    "news_brief": " | ".join([n.headline for n in s.sentiment_report.items[:2]]),
                    "errors": " | ".join(s.errors[:2]) if s.errors else "",
                })
            except Exception as exc:
                failures.append(f"{t}: {exc}")
        if failures:
            st.warning(f"{len(failures)} tickers failed in this pass. Showing successful results.")
            st.text("\n".join(failures[:10]))
        st.dataframe(pd.DataFrame(rows), width="stretch")

with pages[2]:
    df = store.get_recent_runs(100)
    if not df.empty:
        sdf = pd.DataFrame([json.loads(x) for x in df["summary_json"]])
        st.dataframe(sdf.sort_values("confidence_score", ascending=False).head(10))

with pages[3]:
    st.info("Use scripts/run_live_monitor.py for scheduled intraday loop (NSE-hours aware).")

with pages[4]:
    st.dataframe(store.get_recent_runs(50))

with pages[5]:
    st.dataframe(store.get_performance_by_regime())

with pages[6]:
    st.info("Calibration table available via evaluation tracker utilities and persisted outcomes.")

with pages[7]:
    st.info("Compare production vs candidate via scripts/promote_candidate.py")

with pages[8]:
    st.info("See reports/improvement_notes for generated proposals.")

with pages[9]:
    st.metric("Estimated daily cost (balanced)", f"${estimate_daily_cost(2, 50, 'balanced'):.2f}")

with pages[10]:
    st.info("Policy promotion gate runs tests + replay metrics before promotion.")
