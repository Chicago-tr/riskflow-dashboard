from dataclasses import dataclass

@dataclass(frozen=True)
class RiskLimits:
    max_gross_notional: float = 500000.0
    max_net_position: int = 20
    max_abs_pnl: float = 200.0
    max_spread_bps: float = 12.0
    max_latency_ms: float = 85.0

@dataclass(frozen=True)
class ReplayConfig:
    symbol: str = "ES"
    tick_size: float = 0.25
    contract_multiplier: float = 50.0
    seed: int = 42
    n_events: int = 2000
    start_price: float = 5000.0
