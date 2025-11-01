import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Page config
st.set_page_config(page_title="On-Time Performance", layout="wide")

# --- Global CSS Styling (Black theme) ---
_CSS = """
<style>
body {font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;}
.stApp { background: #000000; color: #E6EEF8; }
.card {background: linear-gradient(180deg,#071018 0%, #000000 100%);
    padding: 12px; border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.02);
    box-shadow: 0 8px 24px rgba(0,0,0,0.6);}
.metric-card {background: linear-gradient(180deg,#081018 0%, #07101a 100%); padding:8px; border-radius:8px; border:1px solid rgba(255,255,255,0.02);} 
.metric-label {color:#9fb0d6; font-size:12px}
.metric-value {color:#E6EEF8; font-size:18px; font-weight:600}
.metric-delta.good {color:#7ee787}
.metric-delta.bad {color:#ff6b6b}
.muted {color: #9fb0d6}
.stSidebar { background: linear-gradient(180deg,#071018 0%, #000000 100%); }
h2, h1 {color: #E6EEF8}
</style>
"""
st.markdown(_CSS, unsafe_allow_html=True)

# --- Header ---
title_col, _ = st.columns([3,1])
with title_col:
    st.markdown("## ⏱️ On-Time Performance")


# --- Variables used by controls ---
months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
base_values = np.array([90.1,90.5,91.0,91.3,91.7,92.0,92.3,92.5,92.1,91.8,92.0,92.5])

# Controls (compact row under header)
ctrl_a, ctrl_b, ctrl_c, ctrl_d = st.columns([2,1,1.4,0.8])
with ctrl_a:
    region = st.selectbox("Region", ["All regions", "North", "South", "East", "West"], index=0)
with ctrl_b:
    service_type = st.selectbox("Service Type", ["All services", "Intermodal", "Local", "Express"], index=0)
with ctrl_c:
    start_month, end_month = st.select_slider("Month range", options=months, value=(months[0], months[-1]))
with ctrl_d:
    show_ma = st.checkbox("3-mo MA", value=True)

# --- Data setup ---
def adjust_values(vals, region_name, service_name):
    seed = (abs(hash(region_name)) + abs(hash(service_name))) % 97
    rng = np.random.default_rng(seed)
    offsets = rng.normal(loc=0.0, scale=0.25, size=len(vals))
    return np.clip(vals + offsets, 0, 100)

values = adjust_values(base_values, region, service_type)
df = pd.DataFrame({"month": months, "ontime_pct": values})

# --- Sidebar ---
with st.sidebar:
    st.header("Export")
    st.download_button(
        "Download CSV",
        df.to_csv(index=False).encode("utf-8"),
        file_name="on_time_performance.csv",
        mime="text/csv"
    )

# apply month range slice (compact control already defined)
start_idx = months.index(start_month)
end_idx = months.index(end_month) + 1
df = df.iloc[start_idx:end_idx].reset_index(drop=True)

# --- Metrics ---
current = df['ontime_pct'].iat[-1]
previous = df['ontime_pct'].iat[-2] if len(df) > 1 else current
delta = current - previous
delta_pct = (delta / previous * 100) if previous != 0 else 0

col1, col2, col3 = st.columns([1.5,1.5,3])
with col1:
    delta_class = 'metric-delta good' if delta >= 0 else 'metric-delta bad'
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Current On-Time %</div><div class='metric-value'>{current:.1f}%</div><div class='{delta_class}'>Δ {delta:+.2f}% ({delta_pct:+.1f}%)</div></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Period Average</div><div class='metric-value'>{df['ontime_pct'].mean():.1f}%</div><div class='muted'>Range shown: {start_month} — {end_month}</div></div>", unsafe_allow_html=True)
with col3:
    st.markdown("<div class='card'><span class='muted'>Target:</span> ≥ 90% — higher values indicate stronger reliability.</div>", unsafe_allow_html=True)

# --- Chart ---
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df['month'], y=df['ontime_pct'],
    mode='lines+markers',
    line=dict(color="#FF7A00", width=3),
    marker=dict(size=6, color="#FF7A00"),
    name="On-Time %",
    hovertemplate='%{x}: %{y:.1f}%'
))

if show_ma and len(df) >= 3:
    ma = df['ontime_pct'].rolling(window=3, min_periods=1).mean()
    fig.add_trace(go.Scatter(
        x=df['month'], y=ma,
        mode='lines',
        line=dict(color="#2D2A70", width=2, dash='dash'),
        name="3-month MA"
    ))

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="#000000",
    plot_bgcolor="#000000",
    font=dict(color="#E6EEF8", size=13),
    margin=dict(l=20,r=20,t=30,b=20),
    height=380,
    hovermode="x unified",
    legend=dict(bgcolor='rgba(255,255,255,0.03)')
)

fig.update_xaxes(title_text="Month", color='#E6EEF8')
fig.update_yaxes(title_text="On-Time Performance (%)", range=[0,100], color='#E6EEF8')

st.plotly_chart(fig, use_container_width=True, key='ontime_chart')

# --- Help section ---
with st.expander("How to read this chart"):
    st.write("""
    The solid green line represents monthly on-time performance.
    The dashed line (if enabled) shows the 3-month moving average for trend stability.
    Use filters to focus on specific regions or service types.
    Higher values indicate better operational reliability.
    """)

st.caption("Chart includes hover tooltips. The latest value is shown above as a metric for screen-reader users.")
