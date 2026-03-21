from __future__ import annotations

from services.policy import PolicyEngine, compare_policies


if __name__ == "__main__":
    pe = PolicyEngine()
    metrics = {
        "baseline": {"expectancy": 0.18, "max_drawdown": 0.11, "calibration": 0.62},
        "candidate": {"expectancy": 0.22, "max_drawdown": 0.10, "calibration": 0.64},
    }
    cmp = compare_policies(pe.current, pe.load_candidate(), metrics)
    print(cmp)
