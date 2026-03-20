from __future__ import annotations

from models import DerivativesReport


def compute_derivatives_report(ticker: str) -> DerivativesReport:
    # Interface kept deterministic; can be replaced by nsepython in production.
    proxy = sum(ord(c) for c in ticker) % 100
    pcr = 0.8 + (proxy / 500)
    structure = "bullish" if pcr > 1.0 else "bearish" if pcr < 0.85 else "neutral"
    score = 0.65 if structure == "bullish" else 0.35 if structure == "bearish" else 0.5
    return DerivativesReport(
        score=score,
        pcr=round(pcr, 2),
        max_pain=proxy * 10.0,
        call_oi_wall=(proxy + 10) * 10.0,
        put_oi_wall=(proxy - 10) * 10.0,
        structure=structure,
        note="Proxy OI map; replace with live NSE option chain adapter where available.",
    )
