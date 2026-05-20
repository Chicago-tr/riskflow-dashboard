from __future__ import annotations

import numpy as np
import pandas as pd

def add_microstructure_features(df: pd.DataFrame, window: int = 50, entry_z: float = 1.5) -> pd.DataFrame:
    out = df.copy()

    out["ewma_var"] = out["mid_ret"].ewm(span=window, adjust=False).var().fillna(0.0)

    past_mean = out["mid_ret"].shift(1).rolling(window).mean()
    past_std = out["mid_ret"].shift(1).rolling(window).std(ddof=0).replace(0, np.nan)

    out["zscore"] = ((out["mid_ret"] - past_mean) / past_std).replace([np.inf, -np.inf], 0.0).fillna(0.0)
    out["quote_trade_ratio"] = (1 + out["spread_bps"]) / (1 + out["imbalance"].abs())

    out["signal"] = 0
    out.loc[out["zscore"] >= entry_z, "signal"] = -1
    out.loc[out["zscore"] <= -entry_z, "signal"] = 1
    out["signal_strength"] = out["zscore"].abs()
    out.loc[out["signal"] == 0, "signal_strength"] = 0.0

    return out