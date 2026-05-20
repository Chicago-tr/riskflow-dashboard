import streamlit as st
import plotly.express as px
import pandas as pd

from src.pipeline import build_demo_frame
from src.replay_state import DemoReplayState

st.set_page_config(page_title="Micro Risk Dashboard", layout="wide")
st.title("Futures Risk Monitor")
st.caption("Replay-driven demo of live monitoring, microstructure signals, and latency awareness.")


@st.cache_data
def load_data():
    return build_demo_frame(1200)


def init_state():
    if "replay_state" not in st.session_state:
        df = load_data()
        st.session_state.replay_state = DemoReplayState(df=df, start_idx=50)
    if "playing" not in st.session_state:
        st.session_state.playing = False
    if "step_size" not in st.session_state:
        st.session_state.step_size = 5
    if "interval_label" not in st.session_state:
        st.session_state.interval_label = "5s"


def advance_n(state, n: int):
    return state.advance_n(n)


INTERVAL_MAP = {
    "1s": 1,
    "2s": 2,
    "5s": 5,
    "10s": 10,
}

init_state()

with st.sidebar:
    st.header("Replay Controls")
    st.session_state.playing = st.toggle("Play", value=st.session_state.playing)
    st.session_state.step_size = st.slider("Step size", 1, 50, st.session_state.step_size)
    st.session_state.interval_label = st.selectbox(
        "Play interval",
        options=list(INTERVAL_MAP.keys()),
        index=list(INTERVAL_MAP.keys()).index(st.session_state.interval_label),
    )

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Step"):
            state = st.session_state.replay_state
            advance_n(state, st.session_state.step_size)
            st.rerun()

    with col_b:
        if st.button("Reset"):
            df = load_data()
            st.session_state.replay_state = DemoReplayState(df=df, start_idx=50)
            st.session_state.playing = False
            st.rerun()


run_every = INTERVAL_MAP[st.session_state.interval_label] if st.session_state.playing else None


@st.fragment(run_every=run_every)
def live_panel():
    state = st.session_state.replay_state

    if st.session_state.playing and not state.is_done():
        advance_n(state, st.session_state.step_size)

    snap = state.latest_snapshot()
    if snap is None:
        snap = state.advance_one()

    current = state.current_slice()

    trade_events = []
    for s in state.history:
        if s.trade_side != 0:
            trade_events.append(
                {
                    "ts": s.ts,
                    "price": float(s.row["trade_px"]),
                    "side": s.trade_side,
                    "action": s.trade_action,
                }
            )
    trade_df = pd.DataFrame(trade_events)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Net Pos", snap.net_pos)
    col2.metric("Unrealized PnL", f"{snap.unrealized_pnl:,.0f}")
    col3.metric("Total PnL", f"{snap.total_pnl:,.0f}")
    col4.metric("Breaches", len(snap.breaches))

    st.caption(f"As of: {snap.ts}")

    st.subheader("Market State")
    fig = px.line(current, x="ts", y="mid", title="Mid Price (demo)")
    fig.update_traces(mode="lines")
    fig.update_layout(hovermode="closest")

    if not trade_df.empty:
        fig.add_scatter(
            x=trade_df["ts"],
            y=trade_df["price"],
            mode="markers",
            name="Trades",
            showlegend=False,
            marker=dict(
                size=11,
                color=trade_df["side"].map({1: "green", -1: "red"}),
                symbol=trade_df["side"].map({1: "triangle-up", -1: "triangle-down"}),
                line=dict(width=1, color="white"),
            ),
            text=trade_df["action"],
            hovertemplate="%{text}<br>%{x}<br>Price: %{y}<extra></extra>",
        )

    fig.update_xaxes(title_text="Time")
    fig.update_yaxes(title_text="Price")
    st.plotly_chart(fig, use_container_width=True)

    col5, col6 = st.columns(2)
    with col5:
        st.subheader("Signal")
        fig2 = px.line(current, x="ts", y="signal", title="Signal (demo)")
        fig2.update_xaxes(title_text="Time")
        fig2.update_yaxes(title_text="Signal")
        st.plotly_chart(fig2, use_container_width=True)

    with col6:
        st.subheader("Latency")
        fig3 = px.histogram(current, x="latency_ms", nbins=40, title="Latency (demo)")
        fig3.update_xaxes(title_text="ms")
        fig3.update_yaxes(title_text="Count")
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Recent Alerts")
    alerts = current[current["alert_flag"]][["ts", "breaches", "latency_ms", "spread_bps"]].tail(20)
    st.dataframe(alerts, use_container_width=True)

    st.subheader("Feature Snapshot")
    st.dataframe(
        current[["ts", "bid", "ask", "mid", "spread_bps", "imbalance", "ewma_var", "signal"]].tail(15),
        use_container_width=True,
    )


live_panel()