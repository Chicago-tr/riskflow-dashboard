from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd
from .config import ReplayConfig


# script for generating synthetic market data

@dataclass
class ReplayState:
    last_mid: float
    last_ts: pd.Timestamp

class MarketReplay:
    def __init__(self, cfg: ReplayConfig):
        self.cfg = cfg
        self.rng = np.random.default_rng(cfg.seed)

    def generate(self) -> pd.DataFrame:
        n = self.cfg.n_events
        ts = pd.date_range("2026-01-01 09:30:00", periods=n, freq="s")
        rets = self.rng.normal(0, 0.00015, n).cumsum()
        mid = self.cfg.start_price * (1 + rets)
        spread = np.clip(self.rng.normal(0.4, 0.15, n), 0.25, 1.5)
        bid = mid - spread / 2
        ask = mid + spread / 2
        bid_size = self.rng.integers(1, 40, n)
        ask_size = self.rng.integers(1, 40, n)
        trade_side = self.rng.choice([-1, 1], size=n)
        trade_px = np.where(trade_side > 0, ask, bid)
        latency_ms = np.clip(self.rng.normal(60, 20, n), 5, 250)

        df = pd.DataFrame(
            {
                "ts": ts,
                "bid": bid,
                "ask": ask,
                "mid": mid,
                "bid_size": bid_size,
                "ask_size": ask_size,
                "trade_px": trade_px,
                "trade_side": trade_side,
                "latency_ms": latency_ms,
            }
        )
        df["spread"] = df["ask"] - df["bid"]
        df["spread_bps"] = 10000 * df["spread"] / df["mid"]
        df["imbalance"] = (df["bid_size"] - df["ask_size"]) / (
            df["bid_size"] + df["ask_size"]
        )
        df["mid_ret"] = df["mid"].pct_change().fillna(0.0)
        return df
