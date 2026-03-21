from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PolicyComparison:
    baseline_expectancy: float
    candidate_expectancy: float
    baseline_drawdown: float
    candidate_drawdown: float
    calibration_delta: float
    promotable: bool


def compare_policies(baseline: dict, candidate: dict, metrics: dict) -> PolicyComparison:
    be = metrics["baseline"]["expectancy"]
    ce = metrics["candidate"]["expectancy"]
    bd = metrics["baseline"]["max_drawdown"]
    cd = metrics["candidate"]["max_drawdown"]
    cal = metrics["candidate"]["calibration"] - metrics["baseline"]["calibration"]
    promotable = ce > be and cd <= bd * 1.10 and cal >= -0.02
    return PolicyComparison(be, ce, bd, cd, cal, promotable)
