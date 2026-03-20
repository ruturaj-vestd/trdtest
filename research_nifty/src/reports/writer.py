from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from config import get_settings
from models import ResearchState


def build_markdown_report(state: ResearchState) -> str:
    return f"""# {state.ticker} Research Report
Generated: {datetime.utcnow().isoformat()} UTC

## Stock Overview
- Company: {state.company_name or 'N/A'}
- Sector: {state.sector or 'N/A'}

## Macro Regime
- Regime: **{state.macro_context.regime_label}**
- Macro score: {state.macro_context.macro_score:.2f}
- Rationale: {state.macro_context.rationale}

## Technical Summary
- Trend: {state.technical_metrics.trend}
- EMA20/50/200: {state.technical_metrics.ema20:.2f}/{state.technical_metrics.ema50:.2f}/{state.technical_metrics.ema200:.2f}
- RSI: {state.technical_metrics.rsi:.1f}, ATR: {state.technical_metrics.atr:.2f}

## Fundamentals
- Score: {state.fundamental_score.score:.2f}
- Narrative: {state.fundamental_score.narrative}

## Valuation
- Classification: {state.valuation_report.classification}
- Note: {state.valuation_report.note}

## Sentiment
- Score: {state.sentiment_report.score:.2f}
- Evidence: {'; '.join(state.sentiment_report.evidence[:3])}

## Derivatives + Flow
- Derivatives: {state.derivatives_report.structure} (PCR: {state.derivatives_report.pcr})
- Flow score: {state.flow_report.score:.2f}

## Jury Consensus
- Signal: **{state.jury_report.signal}**
- Confidence: {state.jury_report.confidence_score:.2f}
- Setup: {state.jury_report.setup_type}
- Rationale tree: {' | '.join(state.jury_report.rationale_tree)}

## Trade Plan
- Entry: {state.risk_report.entry:.2f}
- Entry zone: {state.risk_report.entry_zone}
- Stop: {state.risk_report.stop_loss:.2f}
- Targets: {', '.join(f'{t:.2f}' for t in state.risk_report.targets)}
- Position size (%): {state.risk_report.position_size_pct * 100:.2f}

## Risks / Invalidation
{state.risk_report.invalidation}

## Final Recommendation
**{state.final_verdict.signal}** with {state.final_verdict.conviction_band} conviction ({state.final_verdict.confidence_score:.2f}).
"""


def build_json_summary(state: ResearchState) -> dict:
    return {
        "ticker": state.ticker,
        "signal": state.final_verdict.signal,
        "confidence_score": state.final_verdict.confidence_score,
        "conviction_band": state.final_verdict.conviction_band,
        "entry": state.risk_report.entry,
        "entry_zone": state.risk_report.entry_zone,
        "targets": state.risk_report.targets,
        "stop_loss": state.risk_report.stop_loss,
        "risk_reward": state.risk_report.risk_reward,
        "position_size_pct": state.risk_report.position_size_pct,
        "rationale": state.final_verdict.rationale,
        "setup_type": state.jury_report.setup_type,
        "macro_regime": state.macro_context.regime_label,
        "timestamp": datetime.utcnow().isoformat(),
    }


def persist_outputs(state: ResearchState) -> tuple[Path, Path]:
    settings = get_settings()
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    md = settings.output_dir / "reports" / f"{state.ticker}_{stamp}.md"
    js = settings.output_dir / "json" / f"{state.ticker}_{stamp}.json"
    md.parent.mkdir(parents=True, exist_ok=True)
    js.parent.mkdir(parents=True, exist_ok=True)
    md.write_text(state.markdown_report)
    js.write_text(json.dumps(state.json_summary, indent=2))
    return md, js
