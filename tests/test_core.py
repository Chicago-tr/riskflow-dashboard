from src.config import ReplayConfig, RiskLimits
from src.replay import MarketReplay
from src.risk import PositionBook, RiskEngine
from src.microstructure import add_microstructure_features
from src.pipeline import build_demo_frame

def test_replay_shape():
    df = MarketReplay(ReplayConfig(n_events=10)).generate()
    assert len(df) == 10
    assert {"bid", "ask", "mid", "latency_ms"}.issubset(df.columns)

def test_features_added():
    df = MarketReplay(ReplayConfig(n_events=50)).generate()
    feat = add_microstructure_features(df)
    assert {"ewma_var", "zscore", "signal"}.issubset(feat.columns)

def test_breach_detection():
    pos = PositionBook(qty=100, avg_px=5000)
    engine = RiskEngine(RiskLimits(max_net_position=10))
    row = MarketReplay(ReplayConfig(n_events=1)).generate().iloc[0]
    res = engine.evaluate(row, pos)
    assert "net_position" in res["breaches"]

def test_pipeline_runs():
    df = build_demo_frame(120)
    assert len(df) == 120
    assert "breach_count" in df.columns
