from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
import yfinance as yf
from tenacity import retry, stop_after_attempt, wait_exponential

NIFTY50 = [
    "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
    "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BEL.NS", "BHARTIARTL.NS",
    "BPCL.NS", "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DRREDDY.NS",
    "EICHERMOT.NS", "ETERNAL.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS",
    "HDFCLIFE.NS", "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS",
    "INDUSINDBK.NS", "INFY.NS", "ITC.NS", "JIOFIN.NS", "JSWSTEEL.NS",
    "KOTAKBANK.NS", "LT.NS", "M&M.NS", "MARUTI.NS", "NESTLEIND.NS",
    "NTPC.NS", "ONGC.NS", "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS",
    "SBIN.NS", "SHRIRAMFIN.NS", "SUNPHARMA.NS", "TATACONSUM.NS", "TATAMOTORS.NS",
    "TATASTEEL.NS", "TCS.NS", "TECHM.NS", "TITAN.NS", "ULTRACEMCO.NS",
]


def _normalize_ohlcv_columns(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        if ticker in df.columns.get_level_values(-1):
            df = df.xs(ticker, axis=1, level=-1, drop_level=True)
        else:
            df.columns = df.columns.get_level_values(0)
    if isinstance(df.columns, pd.Index):
        df = df.loc[:, ~df.columns.duplicated()]
    return df


def _as_float(value: Any) -> float | None:
    try:
        if value is None or pd.isna(value):
            return None
        return float(value)
    except Exception:
        return None


class MarketDataProvider:
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=4))
    def load_ohlcv(self, ticker: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
        df = yf.Ticker(ticker).history(period=period, interval=interval, auto_adjust=True)
        if df.empty:
            raise ValueError(f"No OHLCV data for {ticker}")
        df = _normalize_ohlcv_columns(df, ticker)
        required = ["Open", "High", "Low", "Close", "Volume"]
        if not all(c in df.columns for c in required):
            raise ValueError(f"Missing OHLCV columns for {ticker}: {set(required) - set(df.columns)}")
        return df[required].dropna(how="any")

    def get_info(self, ticker: str) -> dict:
        try:
            return yf.Ticker(ticker).info or {}
        except Exception:
            return {}

    def get_news(self, ticker: str) -> list[dict]:
        try:
            return yf.Ticker(ticker).news or []
        except Exception:
            return []

    def _download_close(self, symbol: str) -> pd.Series:
        try:
            hist = yf.Ticker(symbol).history(period="5d", interval="1d", auto_adjust=True)
            hist = _normalize_ohlcv_columns(hist, symbol)
            return hist["Close"] if "Close" in hist.columns else pd.Series(dtype=float)
        except Exception:
            return pd.Series(dtype=float)

    def load_macro_snapshot(self) -> dict:
        symbols = {
            "usdinr": "INR=X",
            "brent": "BZ=F",
            "vix": "^INDIAVIX",
            "spx": "^GSPC",
            "nasdaq": "^IXIC",
            "gold": "GC=F",
            # Yahoo has intermittent no-data on ^INDIAGB10Y; use US10Y as fallback proxy.
            "india10y_proxy": "^TNX",
        }
        out: dict[str, float | str | None] = {}
        for k, s in symbols.items():
            close = self._download_close(s)
            out[k] = _as_float(close.iloc[-1]) if not close.empty else None
            out[f"{k}_ret1d"] = _as_float(close.pct_change().iloc[-1]) if len(close) > 1 else 0.0
        out["timestamp"] = datetime.utcnow().isoformat()
        return out
