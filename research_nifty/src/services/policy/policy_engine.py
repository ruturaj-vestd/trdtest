from __future__ import annotations

import json
from pathlib import Path

from config import get_settings

DEFAULT_POLICY = {
    "weights": {
        "macro": 0.10,
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
    "max_position_pct": 0.08,
}


class PolicyEngine:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.current = self._load(self.settings.policy_path)

    def _load(self, path: Path) -> dict:
        if path.exists():
            return json.loads(path.read_text())
        path.write_text(json.dumps(DEFAULT_POLICY, indent=2))
        return DEFAULT_POLICY

    def save_candidate(self, policy: dict) -> None:
        self.settings.candidate_policy_path.write_text(json.dumps(policy, indent=2))

    def load_candidate(self) -> dict:
        path = self.settings.candidate_policy_path
        if not path.exists():
            return self.current
        return json.loads(path.read_text())
