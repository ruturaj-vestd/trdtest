from __future__ import annotations

import pandas as pd


def reliability_table(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["bucket", "count", "win_rate"])
    bins = [0.0, 0.5, 0.6, 0.7, 0.8, 1.0]
    df = df.copy()
    df["bucket"] = pd.cut(df["confidence"], bins=bins, include_lowest=True)
    out = df.groupby("bucket", observed=False).agg(count=("result", "count"), win_rate=("result", lambda s: (s == "win").mean())).reset_index()
    return out
