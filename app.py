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
latest = df.iloc[-1]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Net Pos", int(latest["net_pos"]))
col2.metric("Unrealized PnL", f"{latest['unrealized_pnl']:.0f}")
col3.metric("Gross Notional", f"{latest['gross_notional']:.0f}")
col4.metric("Breaches", int(latest["breach_count"]))

st.subheader("Market State")
fig = px.line(df, x="ts", y=["mid"], title="Mid Price (demo)")
fig.update_xaxes(title_text="Time")
fig.update_yaxes(title_text="Price")
st.plotly_chart(fig, use_container_width=True)

col5, col6 = st.columns(2)
with col5:
    st.subheader("Signal")
    fig2 = px.line(df, x="ts", y="signal", title="Signal (demo)")
    fig2.update_xaxes(title_text="Time")
    fig2.update_yaxes(title_text="Signal")
    st.plotly_chart(fig2, use_container_width=True)
with col6:
    st.subheader("Latency")
    fig3 = px.histogram(df, x="latency_ms", nbins=40, title="Latency (demo)")
    fig3.update_xaxes(title_text="ms")
    fig3.update_yaxes(title_text="Count")
    st.plotly_chart(fig3, use_container_width=True)

st.subheader("Recent Alerts")
alerts = df[df["alert_flag"]][["ts", "breaches", "latency_ms", "spread_bps"]].tail(20)
st.dataframe(alerts, use_container_width=True)

st.subheader("Feature Snapshot")
st.dataframe(df[["ts", "bid", "ask", "mid", "spread_bps", "imbalance", "ewma_var", "signal"]].tail(15), use_container_width=True)
