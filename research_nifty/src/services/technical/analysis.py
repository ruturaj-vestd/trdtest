from __future__ import annotations

import numpy as np
import pandas as pd

from models import TechnicalReport


REQUIRED_OHLCV_COLUMNS = ("Open", "High", "Low", "Close", "Volume")


def _to_1d_series(values: pd.Series | pd.DataFrame) -> pd.Series:
    if isinstance(values, pd.DataFrame):
        if values.shape[1] == 0:
            raise ValueError("Expected at least one column for OHLCV field")
        values = values.iloc[:, 0]
    return pd.Series(values).astype(float)


def _ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def compute_technical_report(d1: pd.DataFrame, h1: pd.DataFrame | None = None) -> TechnicalReport:
    missing = [c for c in REQUIRED_OHLCV_COLUMNS if c not in d1.columns]
    if missing:
        raise ValueError(f"Missing OHLCV columns: {missing}")

    close = _to_1d_series(d1["Close"])
    high = _to_1d_series(d1["High"])
    low = _to_1d_series(d1["Low"])
    vol = _to_1d_series(d1["Volume"])

    ema20 = float(_ema(close, 20).iloc[-1])
    ema50 = float(_ema(close, 50).iloc[-1])
    ema200 = float(_ema(close, 200).iloc[-1]) if len(close) >= 200 else float(_ema(close, min(50, len(close))).iloc[-1])

    prev_close = close.shift(1)
    tr = pd.concat([(high - low), (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
    atr = float(tr.rolling(14, min_periods=1).mean().iloc[-1])

    delta = close.diff()
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)
    rs = pd.Series(gain, index=close.index).rolling(14, min_periods=1).mean() / pd.Series(loss, index=close.index).rolling(14, min_periods=1).mean().replace(0, np.nan)
    rsi = float((100 - (100 / (1 + rs))).fillna(50).iloc[-1])

    vol_ratio = float((vol.iloc[-1] / (vol.rolling(20, min_periods=1).mean().iloc[-1] + 1e-9)))
    swing_high = float(high.tail(20).max())
    swing_low = float(low.tail(20).min())

    trend = "uptrend" if ema20 > ema50 > ema200 else "downtrend" if ema20 < ema50 < ema200 else "range"
    trend_score = 0.7 if trend == "uptrend" else 0.3 if trend == "downtrend" else 0.5
    timing_score = min(1.0, max(0.0, (rsi - 40) / 30)) if trend == "uptrend" else 0.5
    roll_vol = float(close.pct_change().rolling(20, min_periods=1).std().iloc[-1] * np.sqrt(252))

    ob_size = max(atr, (swing_high - swing_low) * 0.15)
    demand = (max(0.0, swing_low - 0.2 * ob_size), swing_low + 0.6 * ob_size)
    supply = (swing_high - 0.6 * ob_size, swing_high + 0.2 * ob_size)

    return TechnicalReport(
        trend=trend,
        trend_score=trend_score,
        timing_score=timing_score,
        ema20=ema20,
        ema50=ema50,
        ema200=ema200,
        atr=atr if np.isfinite(atr) else 0.0,
        rsi=rsi,
        adx=min(50.0, abs(ema20 - ema50) / (abs(ema50) + 1e-9) * 1000),
        volume_expansion_ratio=vol_ratio,
        rolling_volatility=roll_vol if np.isfinite(roll_vol) else 0.0,
        demand_zone=demand,
        supply_zone=supply,
        breakout_level=swing_high,
        breakdown_level=swing_low,
        entry_timing_note="Momentum aligned" if trend == "uptrend" and rsi < 70 else "Wait for pullback",
    )
