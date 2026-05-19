from __future__ import annotations

import pandas as pd
from .config import ReplayConfig, RiskLimits
from .replay import MarketReplay
from .risk import PositionBook, RiskEngine
from .microstructure import add_microstructure_features

def build_demo_frame(n_events: int = 1000):
    cfg = ReplayConfig(n_events=n_events)
    raw = MarketReplay(cfg).generate()
    feat = add_microstructure_features(raw)
    pos = PositionBook()
    engine = RiskEngine(RiskLimits())
    rows = []
    for _, r in feat.iterrows():
        if r["signal"] > 1.2 and pos.qty <= 0:
            pos.update_trade(1, 1, r["trade_px"])
        elif r["signal"] < -1.2 and pos.qty >= 0:
            pos.update_trade(-1, 1, r["trade_px"])
        rows.append(engine.evaluate(r, pos))
    risk = pd.DataFrame(rows)
    out = feat.merge(risk, on="ts", how="left")
    out["breach_count"] = out["breaches"].apply(lambda x: len(x) if isinstance(x, list) else 0)
    out["alert_flag"] = out["breach_count"] > 0
    return out
