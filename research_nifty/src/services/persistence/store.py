from __future__ import annotations

import json
from datetime import datetime

import duckdb
import pandas as pd

from config import get_settings
from models import ResearchState


class ResearchStore:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.conn = duckdb.connect(str(self.settings.db_path))
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        self.conn.execute(
            """
            create table if not exists research_runs (
                run_id varchar,
                ticker varchar,
                created_at timestamp,
                signal varchar,
                confidence double,
                report_md varchar,
                summary_json varchar
            )
            """
        )
        self.conn.execute(
            """
            create table if not exists outcomes (
                run_id varchar,
                ticker varchar,
                ts timestamp,
                result_label varchar,
                mfe double,
                mae double,
                pnl_r double
            )
            """
        )
        self.conn.execute(
            """
            create table if not exists policy_versions (
                version varchar,
                ts timestamp,
                policy_json varchar,
                metrics_json varchar,
                promoted boolean
            )
            """
        )
        self.conn.execute(
            """
            create table if not exists llm_usage (
                ts timestamp,
                provider varchar,
                model varchar,
                input_tokens int,
                output_tokens int,
                estimated_cost double,
                task varchar
            )
            """
        )

    def save_run(self, state: ResearchState) -> str:
        run_id = f"{state.ticker}-{int(state.created_at.timestamp())}"
        self.conn.execute(
            "insert into research_runs values (?, ?, ?, ?, ?, ?, ?)",
            [
                run_id,
                state.ticker,
                state.created_at,
                state.final_verdict.signal,
                state.final_verdict.confidence_score,
                state.markdown_report,
                json.dumps(state.json_summary),
            ],
        )
        return run_id

    def save_outcome(self, run_id: str, ticker: str, result_label: str, mfe: float = 0.0, mae: float = 0.0, pnl_r: float = 0.0) -> None:
        self.conn.execute(
            "insert into outcomes values (?, ?, ?, ?, ?, ?, ?)",
            [run_id, ticker, datetime.utcnow(), result_label, mfe, mae, pnl_r],
        )

    def get_recent_runs(self, limit: int = 50) -> pd.DataFrame:
        return self.conn.execute("select * from research_runs order by created_at desc limit ?", [limit]).df()

    def get_performance_by_regime(self) -> pd.DataFrame:
        return self.conn.execute(
            """
            select r.ticker, o.result_label, avg(o.pnl_r) as avg_r
            from outcomes o join research_runs r on o.run_id = r.run_id
            group by 1,2
            """
        ).df()

    def log_llm_usage(self, provider: str, model: str, input_tokens: int, output_tokens: int, estimated_cost: float, task: str) -> None:
        self.conn.execute(
            "insert into llm_usage values (?, ?, ?, ?, ?, ?, ?)",
            [datetime.utcnow(), provider, model, input_tokens, output_tokens, estimated_cost, task],
        )
