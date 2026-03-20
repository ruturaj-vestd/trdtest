from __future__ import annotations


def estimate_daily_cost(single_scan_calls: int, batch_scans: int, policy: str = "balanced") -> float:
    multipliers = {"low-cost": 0.6, "balanced": 1.0, "premium": 1.8}
    per_call = 0.003
    return single_scan_calls * batch_scans * per_call * multipliers.get(policy, 1.0)
