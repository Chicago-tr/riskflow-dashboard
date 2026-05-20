from __future__ import annotations

from dataclasses import dataclass
import pandas as pd

from .config import RiskLimits
from .risk import PositionBook, RiskEngine


@dataclass
class ReplaySnapshot:
    ts: pd.Timestamp
    net_pos: int
    unrealized_pnl: float
    realized_pnl: float
    total_pnl: float
    gross_notional: float
    breaches: list
    trade_side: int
    trade_action: str
    row: pd.Series


class DemoReplayState:
    def __init__(self, df: pd.DataFrame, limits: RiskLimits | None = None, start_idx: int = 50):
        self.df = df.reset_index(drop=True)
        self.pos = PositionBook()
        self.engine = RiskEngine(limits or RiskLimits())
        self.idx = min(start_idx, len(self.df))
        self.history: list[ReplaySnapshot] = []

    def advance_n(self, n: int = 1) -> ReplaySnapshot | None:
        snap = None
        for _ in range(n):
            if self.is_done():
                break

            row = self.df.iloc[self.idx - 1]
            trade_side = 0
            trade_action = ""

            if row["signal"] == 1 and self.pos.qty <= 0:
                trade_action = "open_long" if self.pos.qty == 0 else "flip_long"
                self.pos.update_trade(1, 1, float(row["trade_px"]))
                trade_side = 1
            elif row["signal"] == -1 and self.pos.qty >= 0:
                trade_action = "open_short" if self.pos.qty == 0 else "flip_short"
                self.pos.update_trade(-1, 1, float(row["trade_px"]))
                trade_side = -1

            eval_row = self.engine.evaluate(row, self.pos)
            total_pnl = float(eval_row["realized_pnl"]) + float(eval_row["unrealized_pnl"])

            snap = ReplaySnapshot(
                ts=eval_row["ts"],
                net_pos=int(eval_row["net_pos"]),
                unrealized_pnl=float(eval_row["unrealized_pnl"]),
                realized_pnl=float(eval_row["realized_pnl"]),
                total_pnl=total_pnl,
                gross_notional=float(eval_row["gross_notional"]),
                breaches=list(eval_row["breaches"]),
                trade_side=trade_side,
                trade_action=trade_action,
                row=row,
            )
            self.history.append(snap)
            self.idx = min(self.idx + 1, len(self.df))
        return snap

    def advance_one(self) -> ReplaySnapshot | None:
        return self.advance_n(1)

    def current_slice(self) -> pd.DataFrame:
        return self.df.iloc[:self.idx].copy()

    def is_done(self) -> bool:
        return self.idx >= len(self.df)

    def latest_snapshot(self) -> ReplaySnapshot | None:
        return self.history[-1] if self.history else None