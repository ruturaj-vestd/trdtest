from services.policy import compare_policies


def test_policy_gate_promotable():
    baseline = {}
    candidate = {}
    metrics = {
        "baseline": {"expectancy": 0.1, "max_drawdown": 0.1, "calibration": 0.6},
        "candidate": {"expectancy": 0.2, "max_drawdown": 0.1, "calibration": 0.61},
    }
    cmp = compare_policies(baseline, candidate, metrics)
    assert cmp.promotable is True
