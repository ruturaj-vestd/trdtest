from __future__ import annotations

from datetime import datetime, timedelta

from models import RiskReport


def _estimate_entry_date(confidence: float) -> str:
    days = 1 if confidence >= 0.75 else 2 if confidence >= 0.55 else 3
    return (datetime.utcnow() + timedelta(days=days)).date().isoformat()


def build_risk_plan(
    last_price: float,
    atr: float,
    confidence: float,
    signal: str,
    regime: str,
    trend: str = "range",
    sizing_mode: str = "balanced",
) -> RiskReport:
    atr = max(0.01, atr)
    stop_gap = max(1.5 * atr, last_price * 0.01)

    directional_signal = signal
    if directional_signal == "HOLD":
        directional_signal = "BUY" if trend == "uptrend" else "SELL" if trend == "downtrend" else "BUY"

    entry = last_price
    if directional_signal == "BUY":
        stop = last_price - stop_gap
        targets = [last_price + stop_gap * m for m in (1.0, 2.0, 3.0)]
    else:
        stop = last_price + stop_gap
        targets = [last_price - stop_gap * m for m in (1.0, 2.0, 3.0)]

    win_prob = min(0.9, max(0.1, confidence))
    rr = abs((targets[1] - entry) / (entry - stop)) if len(targets) > 1 else 1.0
    kelly = max(0.0, min(0.25, win_prob - (1 - win_prob) / max(rr, 0.2)))
    mode_mult = {"aggressive": 1.0, "balanced": 0.6, "conservative": 0.35}.get(sizing_mode, 0.6)
    regime_cut = 0.6 if regime == "Risk-Off" else 1.0
    position = min(0.08, kelly * mode_mult * regime_cut)

    return RiskReport(
        entry=entry,
        estimated_entry_date=_estimate_entry_date(confidence),
        entry_zone=(entry * 0.995, entry * 1.005),
        stop_loss=stop,
        targets=targets,
        risk_reward=rr,
        position_size_pct=position,
        kelly_fraction=kelly,
        sizing_mode=sizing_mode,
        invalidation="Break of stop or thesis contradiction from macro/news shock.",
    )
