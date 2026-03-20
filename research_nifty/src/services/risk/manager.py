from __future__ import annotations

from models import RiskReport


def build_risk_plan(last_price: float, atr: float, confidence: float, signal: str, regime: str, sizing_mode: str = "balanced") -> RiskReport:
    atr = max(0.01, atr)
    stop_gap = max(1.5 * atr, last_price * 0.01)
    if signal == "BUY":
        entry = last_price
        stop = last_price - stop_gap
        targets = [last_price + stop_gap * m for m in (1.0, 2.0, 3.0)]
    elif signal == "SELL":
        entry = last_price
        stop = last_price + stop_gap
        targets = [last_price - stop_gap * m for m in (1.0, 2.0, 3.0)]
    else:
        entry = last_price
        stop = last_price - stop_gap
        targets = [last_price]
    win_prob = min(0.9, max(0.1, confidence))
    rr = abs((targets[1] - entry) / (entry - stop)) if len(targets) > 1 else 1.0
    kelly = max(0.0, min(0.25, win_prob - (1 - win_prob) / max(rr, 0.2)))
    mode_mult = {"aggressive": 1.0, "balanced": 0.6, "conservative": 0.35}.get(sizing_mode, 0.6)
    regime_cut = 0.6 if regime == "Risk-Off" else 1.0
    position = min(0.08, kelly * mode_mult * regime_cut)
    return RiskReport(
        entry=entry,
        entry_zone=(entry * 0.995, entry * 1.005),
        stop_loss=stop,
        targets=targets,
        risk_reward=rr,
        position_size_pct=position,
        kelly_fraction=kelly,
        sizing_mode=sizing_mode,
        invalidation="Break of stop or thesis contradiction from macro/news shock.",
    )
