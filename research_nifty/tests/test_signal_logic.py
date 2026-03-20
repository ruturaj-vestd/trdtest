from models import MacroContext, ResearchState, TechnicalReport
from services.evaluation import build_consensus


def test_consensus_penalizes_risk_off_conflict():
    state = ResearchState(ticker="TEST.NS")
    state.macro_context = MacroContext(macro_score=0.3, regime_label="Risk-Off")
    state.technical_metrics = TechnicalReport(trend="uptrend", trend_score=0.9)
    policy = {
        "weights": {
            "macro": 0.1,
            "technical": 0.24,
            "fundamental": 0.18,
            "valuation": 0.12,
            "sentiment": 0.12,
            "derivatives": 0.12,
            "flow": 0.12,
        },
        "buy_threshold": 0.62,
        "sell_threshold": 0.38,
        "risk_off_penalty": 0.08,
        "black_swan_penalty": 0.12,
    }
    jury = build_consensus(state, policy)
    assert jury.weighted_score < 0.62
