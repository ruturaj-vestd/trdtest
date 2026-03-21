import numpy as np
import pandas as pd

from services.market_data.provider import _normalize_ohlcv_columns
from services.technical import compute_technical_report


def test_compute_technical_report_handles_2d_column_slices():
    idx = pd.date_range("2025-01-01", periods=124, freq="D")
    base = pd.DataFrame(
        {
            "Open": np.linspace(100, 150, len(idx)),
            "High": np.linspace(101, 151, len(idx)),
            "Low": np.linspace(99, 149, len(idx)),
            "Close": np.linspace(100, 152, len(idx)),
            "Volume": np.linspace(1_000_000, 1_400_000, len(idx)),
        },
        index=idx,
    )
    # Simulate yfinance multi-index format: (field, ticker)
    multi = pd.concat({"MOCK.NS": base}, axis=1).swaplevel(axis=1)
    normalized = _normalize_ohlcv_columns(multi, "MOCK.NS")
    report = compute_technical_report(normalized)
    assert report.atr >= 0.0
    assert report.trend in {"uptrend", "downtrend", "range"}
