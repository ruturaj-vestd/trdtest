from __future__ import annotations

from datetime import datetime

import pandas as pd
import yfinance as yf
from tenacity import retry, stop_after_attempt, wait_exponential

NIFTY50 = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "LT.NS", "ITC.NS", "SBIN.NS", "KOTAKBANK.NS", "BHARTIARTL.NS"
]


class MarketDataProvider:
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=4))
    def load_ohlcv(self, ticker: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
        df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
        if df.empty:
            raise ValueError(f"No OHLCV data for {ticker}")
        return df.dropna()

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

    def load_macro_snapshot(self) -> dict:
        symbols = {
            "usdinr": "INR=X",
            "brent": "BZ=F",
            "vix": "^INDIAVIX",
            "spx": "^GSPC",
            "nasdaq": "^IXIC",
            "gold": "GC=F",
            "india10y": "^INDIAGB10Y",
        }
        out = {}
        for k, s in symbols.items():
            try:
                hist = yf.download(s, period="5d", interval="1d", progress=False)
                out[k] = float(hist["Close"].iloc[-1]) if not hist.empty else None
                if not hist.empty and len(hist) > 1:
                    out[f"{k}_ret1d"] = float(hist["Close"].pct_change().iloc[-1])
                else:
                    out[f"{k}_ret1d"] = 0.0
            except Exception:
                out[k] = None
                out[f"{k}_ret1d"] = 0.0
        out["timestamp"] = datetime.utcnow().isoformat()
        return out
