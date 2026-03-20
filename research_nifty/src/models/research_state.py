from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Signal = Literal["BUY", "SELL", "HOLD"]
Conviction = Literal["Low", "Medium", "High"]


class MacroContext(BaseModel):
    macro_score: float = 0.0
    regime_label: Literal["Risk-On", "Neutral", "Risk-Off"] = "Neutral"
    currency_pressure: float = 0.0
    crude_pressure: float = 0.0
    vol_regime: float = 0.0
    global_risk_tone: float = 0.0
    rationale: str = ""
    sector_note: str = ""


class TechnicalReport(BaseModel):
    trend: Literal["uptrend", "downtrend", "range"] = "range"
    trend_score: float = 0.0
    timing_score: float = 0.0
    ema20: float = 0.0
    ema50: float = 0.0
    ema200: float = 0.0
    atr: float = 0.0
    rsi: float = 50.0
    adx: float = 15.0
    volume_expansion_ratio: float = 1.0
    rolling_volatility: float = 0.0
    demand_zone: tuple[float, float] | None = None
    supply_zone: tuple[float, float] | None = None
    breakout_level: float | None = None
    breakdown_level: float | None = None
    entry_timing_note: str = ""


class FundamentalReport(BaseModel):
    score: float = 0.0
    pe_ttm: float | None = None
    pe_forward: float | None = None
    debt_to_equity: float | None = None
    roe: float | None = None
    roce: float | None = None
    revenue_growth_qoq: list[float] = Field(default_factory=list)
    profit_growth_qoq: list[float] = Field(default_factory=list)
    op_margin_trend: list[float] = Field(default_factory=list)
    eps_trend: list[float] = Field(default_factory=list)
    narrative: str = ""


class ValuationReport(BaseModel):
    score: float = 0.0
    classification: Literal["undervalued", "fair", "expensive"] = "fair"
    pe_vs_history: float | None = None
    pe_vs_sector: float | None = None
    archetype: str = "quality compounder at fair price"
    note: str = ""


class SentimentItem(BaseModel):
    headline: str
    source: str
    timestamp: datetime
    classification: Literal["bullish", "bearish", "neutral"]
    catalyst_type: Literal["priced_in", "incremental", "regime_shift"] = "priced_in"
    tag: Literal["one_off", "continuation", "earnings", "regulatory", "macro_linked"] = "one_off"


class SentimentReport(BaseModel):
    score: float = 0.0
    confidence: float = 0.5
    evidence: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    items: list[SentimentItem] = Field(default_factory=list)


class DerivativesReport(BaseModel):
    score: float = 0.0
    pcr: float | None = None
    max_pain: float | None = None
    call_oi_wall: float | None = None
    put_oi_wall: float | None = None
    structure: Literal["bullish", "bearish", "neutral"] = "neutral"
    note: str = ""


class FlowReport(BaseModel):
    score: float = 0.0
    fii_cash: float | None = None
    dii_cash: float | None = None
    delivery_pct: float | None = None
    block_deal_signal: str | None = None
    note: str = ""


class JuryReport(BaseModel):
    weighted_score: float = 0.0
    signal: Signal = "HOLD"
    confidence_score: float = 0.5
    conviction_band: Conviction = "Low"
    setup_type: str = "indeterminate"
    rationale_tree: list[str] = Field(default_factory=list)
    regime_compatibility: str = ""


class RiskReport(BaseModel):
    entry: float = 0.0
    entry_zone: tuple[float, float] = (0.0, 0.0)
    stop_loss: float = 0.0
    targets: list[float] = Field(default_factory=list)
    risk_reward: float = 0.0
    position_size_pct: float = 0.0
    kelly_fraction: float = 0.0
    sizing_mode: Literal["aggressive", "balanced", "conservative"] = "balanced"
    invalidation: str = ""


class FinalVerdict(BaseModel):
    signal: Signal = "HOLD"
    confidence_score: float = 0.5
    conviction_band: Conviction = "Low"
    rationale: str = ""


class ResearchState(BaseModel):
    ticker: str
    company_name: str | None = None
    sector: str | None = None
    macro_context: MacroContext = Field(default_factory=MacroContext)
    technical_metrics: TechnicalReport = Field(default_factory=TechnicalReport)
    fundamental_score: FundamentalReport = Field(default_factory=FundamentalReport)
    valuation_report: ValuationReport = Field(default_factory=ValuationReport)
    sentiment_report: SentimentReport = Field(default_factory=SentimentReport)
    derivatives_report: DerivativesReport = Field(default_factory=DerivativesReport)
    flow_report: FlowReport = Field(default_factory=FlowReport)
    risk_report: RiskReport = Field(default_factory=RiskReport)
    jury_report: JuryReport = Field(default_factory=JuryReport)
    final_verdict: FinalVerdict = Field(default_factory=FinalVerdict)
    markdown_report: str = ""
    json_summary: dict = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    research_freshness_ts: datetime | None = None
