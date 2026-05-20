import streamlit as st
import plotly.express as px
from src.pipeline import build_demo_frame

st.set_page_config(page_title="Micro Risk Dashboard", layout="wide")
st.title("Futures Risk Monitor")
st.caption("Replay-driven demo of live monitoring, microstructure signals, and latency awareness.")

@st.cache_data
def load_data():
    return build_demo_frame(1200)

df = load_data()

if "replay_idx" not in st.session_state:
    st.session_state.replay_idx = 200

if "playing" not in st.session_state:
    st.session_state.playing = True

if "step" not in st.session_state:
    st.session_state.step = 20

with st.sidebar:
    st.header("Replay Controls")
    st.session_state.playing = st.checkbox("Play", value=st.session_state.playing)
    st.session_state.step = st.slider("Step size", 1, 100, st.session_state.step)
    if st.button("Reset"):
        st.session_state.replay_idx = 200
        st.rerun()

if st.session_state.playing:
    st.session_state.replay_idx = min(
        st.session_state.replay_idx + st.session_state.step,
        len(df)
    )

current = df.iloc[:st.session_state.replay_idx].copy()
latest = current.iloc[-1]

net_pos = int(latest["net_pos"])
unrealized = float(latest["unrealized_pnl"])
gross_notional = float(latest["gross_notional"])
breaches = int(current["breach_count"].sum())

col1, col2, col3, col4 = st.columns(4)
col1.metric("Net Pos", net_pos)
col2.metric("Unrealized PnL", f"{unrealized:,.0f}")
col3.metric("Gross Notional", f"{gross_notional:,.0f}")
col4.metric("Breaches", breaches)

st.caption(f"As of: {latest['ts']}")

st.subheader("Market State")
fig = px.line(current, x="ts", y="mid", title="Mid Price (demo)")
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
    use_container_width=True
)