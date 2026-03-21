from __future__ import annotations

import json

from services.policy import PolicyEngine


if __name__ == "__main__":
    pe = PolicyEngine()
    candidate = pe.current.copy()
    candidate["buy_threshold"] = 0.64
    candidate["risk_off_penalty"] = 0.1
    pe.save_candidate(candidate)
    print("Candidate policy saved", json.dumps(candidate, indent=2))
