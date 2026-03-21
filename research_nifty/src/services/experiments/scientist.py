from __future__ import annotations

from datetime import datetime
from pathlib import Path


def generate_improvement_notes(failures: list[dict], out_dir: Path = Path("reports/improvement_notes")) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"proposal_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"
    notes = ["# Improvement Proposal", ""]
    notes.append("- Reduce confidence when macro=Risk-Off and technical bullish but weak derivatives confirmation.")
    notes.append("- Enforce volume expansion ratio >= 1.2 for breakout BUY setups.")
    notes.append("- Disable mean-reversion entries during high VIX regime.")
    notes.append(f"- Failure sample size reviewed: {len(failures)}")
    p.write_text("\n".join(notes))
    return p
