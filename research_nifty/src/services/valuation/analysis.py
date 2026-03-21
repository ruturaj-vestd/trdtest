from __future__ import annotations

from models import ValuationReport


def compute_valuation_report(fundamental_pe: float | None, sector_pe: float | None = None, history_pe: float | None = None) -> ValuationReport:
    sector_pe = sector_pe or 25.0
    history_pe = history_pe or sector_pe
    pe = fundamental_pe or sector_pe
    rel_sector = pe / sector_pe
    rel_hist = pe / history_pe

    if rel_sector < 0.85 and rel_hist < 0.9:
        c, score = "undervalued", 0.7
    elif rel_sector > 1.2 and rel_hist > 1.15:
        c, score = "expensive", 0.35
    else:
        c, score = "fair", 0.55

    return ValuationReport(
        score=score,
        classification=c,
        pe_vs_history=rel_hist,
        pe_vs_sector=rel_sector,
        archetype="quality compounder at fair price" if c == "fair" else "good company / bad price" if c == "expensive" else "cyclical / regime-sensitive value",
        note=f"PE relative to sector: {rel_sector:.2f}",
    )
