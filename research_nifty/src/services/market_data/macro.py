from __future__ import annotations

from models import MacroContext


def compute_macro_context(snapshot: dict, sector: str | None = None) -> MacroContext:
    usd = snapshot.get("usdinr_ret1d", 0.0)
    brent = snapshot.get("brent_ret1d", 0.0)
    vix = snapshot.get("vix_ret1d", 0.0)
    global_tone = (snapshot.get("spx_ret1d", 0.0) + snapshot.get("nasdaq_ret1d", 0.0)) / 2

    score = 0.5 - usd * 2 - brent * 1.5 - max(vix, 0) * 1.2 + global_tone * 2
    score = max(0.0, min(1.0, score))
    regime = "Risk-On" if score > 0.62 else "Risk-Off" if score < 0.38 else "Neutral"

    sector_note = ""
    if sector:
        s = sector.lower()
        if "it" in s or "pharma" in s:
            sector_note = "Export-heavy: INR weakness can help revenue translation."
        elif "oil" in s or "paint" in s or "aviation" in s:
            sector_note = "Import/energy sensitive: crude spikes can pressure margins."
        else:
            sector_note = "Moderate macro sensitivity."

    return MacroContext(
        macro_score=score,
        regime_label=regime,
        currency_pressure=usd,
        crude_pressure=brent,
        vol_regime=vix,
        global_risk_tone=global_tone,
        rationale=f"USDINR {usd:.3f}, Brent {brent:.3f}, VIX {vix:.3f}, Global {global_tone:.3f}",
        sector_note=sector_note,
    )
