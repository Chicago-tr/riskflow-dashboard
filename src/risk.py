from __future__ import annotations

from dataclasses import dataclass, field
import pandas as pd
from .config import RiskLimits

#script for tracking positions

@dataclass
class PositionBook:
    qty: int = 0
    avg_px: float = 0.0
    realized_pnl: float = 0.0
    history: list = field(default_factory=list)

    def update_trade(self, side: int, qty: int, px: float):
        signed = side * qty

        if self.qty == 0 or self.qty * signed > 0:
            total = abs(self.qty) + abs(signed)
            self.avg_px = (abs(self.qty) * self.avg_px + abs(signed) * px) / total
            self.qty += signed
        else:
            close_qty = min(abs(self.qty), abs(signed))
            pnl = close_qty * (px - self.avg_px) * (1 if self.qty > 0 else -1)
            self.realized_pnl += pnl
            self.qty += signed
            if self.qty == 0:
                self.avg_px = 0.0
            elif self.qty * signed > 0:
                self.avg_px = px

        self.history.append((side, qty, px))

    def mark_to_market(self, mid: float):
        unrealized = self.qty * (mid - self.avg_px) * 50.0
        return unrealized, self.realized_pnl

class RiskEngine:
    def __init__(self, limits: RiskLimits):
        self.limits = limits

    def evaluate(self, row: pd.Series, pos: PositionBook):
        unrealized, realized = pos.mark_to_market(row["mid"])
        net = pos.qty
        gross_notional = abs(net) * row["mid"] * 50.0
        breaches = []

        if gross_notional > self.limits.max_gross_notional:
            breaches.append("gross_notional")
        if abs(net) > self.limits.max_net_position:
            breaches.append("net_position")
        if abs(unrealized + realized) > self.limits.max_abs_pnl:
            breaches.append("pnl")
        if row["spread_bps"] > self.limits.max_spread_bps:
            breaches.append("spread")
        if row["latency_ms"] > self.limits.max_latency_ms:
            breaches.append("latency")

        return {
            "ts": row["ts"],
            "unrealized_pnl": unrealized,
            "realized_pnl": realized,
            "net_pos": net,
            "gross_notional": gross_notional,
            "breaches": breaches,
        }
