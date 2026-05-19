from __future__ import annotations

import pandas as pd

def add_microstructure_features(df: pd.DataFrame, window: int = 30) -> pd.DataFrame:
    out = df.copy()
    out["ewma_var"] = out["mid_ret"].ewm(span=window, adjust=False).var().fillna(0.0)
    roll_mean = out["mid_ret"].rolling(window).mean()
    roll_std = out["mid_ret"].rolling(window).std()
    out["zscore"] = (
        (out["mid_ret"] - roll_mean) / roll_std
    ).replace([float("inf"), float("-inf")], 0.0).fillna(0.0)
    out["quote_trade_ratio"] = (1 + out["spread_bps"]) / (1 + out["imbalance"].abs())
    out["signal"] = -out["zscore"].clip(-3, 3)
    out["signal_strength"] = out["signal"].abs()
    return out
