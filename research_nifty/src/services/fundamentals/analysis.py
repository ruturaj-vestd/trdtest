from __future__ import annotations

from models import FundamentalReport


def compute_fundamental_report(info: dict) -> FundamentalReport:
    pe_ttm = info.get("trailingPE")
    pe_fwd = info.get("forwardPE")
    dte = info.get("debtToEquity")
    roe = info.get("returnOnEquity")
    margin = info.get("operatingMargins")

    score = 0.5
    score += 0.1 if (roe or 0) > 0.15 else -0.05
    score += 0.1 if (dte or 200) < 100 else -0.08
    score += 0.08 if (margin or 0) > 0.15 else -0.04
    score = float(min(1.0, max(0.0, score)))

    return FundamentalReport(
        score=score,
        pe_ttm=pe_ttm,
        pe_forward=pe_fwd,
        debt_to_equity=dte,
        roe=(roe * 100 if isinstance(roe, (float, int)) else None),
        narrative="Healthy profitability and leverage" if score > 0.6 else "Mixed quality profile",
    )
