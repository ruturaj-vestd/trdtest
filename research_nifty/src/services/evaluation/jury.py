from __future__ import annotations

from models import JuryReport, ResearchState


def build_consensus(state: ResearchState, policy: dict) -> JuryReport:
    w = policy["weights"]
    score = (
        state.macro_context.macro_score * w["macro"]
        + state.technical_metrics.trend_score * w["technical"]
        + state.fundamental_score.score * w["fundamental"]
        + state.valuation_report.score * w["valuation"]
        + state.sentiment_report.score * w["sentiment"]
        + state.derivatives_report.score * w["derivatives"]
        + state.flow_report.score * w["flow"]
    )
    rationale = []
    if state.macro_context.regime_label == "Risk-Off" and state.technical_metrics.trend == "uptrend":
        score -= policy.get("risk_off_penalty", 0.08)
        rationale.append("Technical bullishness discounted due to Risk-Off macro regime.")
    if any("volatility" in r.lower() for r in state.sentiment_report.risks):
        score -= policy.get("black_swan_penalty", 0.12)
        rationale.append("Event risk detected; conviction reduced.")
    if state.derivatives_report.structure == "bullish" and state.technical_metrics.trend == "uptrend":
        score += 0.03
        rationale.append("Derivatives and structure aligned; conviction uplift.")

    score = max(0.0, min(1.0, score))
    signal = "BUY" if score >= policy["buy_threshold"] else "SELL" if score <= policy["sell_threshold"] else "HOLD"
    band = "High" if score > 0.75 else "Medium" if score > 0.55 else "Low"
    setup = "trend_continuation" if state.technical_metrics.trend == "uptrend" else "mean_reversion" if state.technical_metrics.trend == "range" else "trend_breakdown"
    rationale.append(f"Composite score={score:.2f}")
    return JuryReport(
        weighted_score=score,
        signal=signal,
        confidence_score=score,
        conviction_band=band,
        setup_type=setup,
        rationale_tree=rationale,
        regime_compatibility=f"{state.macro_context.regime_label} vs {setup}",
    )
