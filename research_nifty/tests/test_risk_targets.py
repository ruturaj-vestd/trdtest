from services.risk import build_risk_plan


def test_hold_signal_still_emits_three_targets():
    report = build_risk_plan(100.0, atr=2.0, confidence=0.6, signal="HOLD", regime="Neutral", trend="uptrend")
    assert len(report.targets) == 3
    assert report.targets[0] != report.entry
    assert report.estimated_entry_date is not None
