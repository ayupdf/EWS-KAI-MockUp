import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Page config
st.set_page_config(page_title="On-Time Performance", layout="wide")

# --- Global CSS Styling ---
_CSS = """
<style>
body {font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;}
.stApp { background: linear-gradient(180deg,#0b1220 0%, #07101a 100%); color: #E6EEF8; }
.card {background: linear-gradient(180deg,#0f1724 0%, #0b1220 100%);
       padding: 12px; border-radius: 10px;
       border: 1px solid rgba(255,255,255,0.04);
       box-shadow: 0 8px 24px rgba(2,6,23,0.6);}
.muted {color: #9fb0d6;}
.stSidebar { background: linear-gradient(180deg,#0f1724 0%, #0b1220 100%); }
a, .st-a {color: #9fd1ff}
h2, h1 {color: #E6EEF8}
</style>
"""
st.markdown(_CSS, unsafe_allow_html=True)

# --- Header & Controls ---
title_col, controls_col = st.columns([3,1])
with title_col:
    st.markdown("## ⏱️ On-Time Performance")
    st.markdown("""
    The **on-time performance rate** shows the percentage of shipments delivered within their scheduled window.
    High values reflect strong service reliability and operational efficiency.
    """)

with controls_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Controls**")
    region = st.selectbox("Region", ["All regions", "North", "South", "East", "West"])
    service_type = st.selectbox("Service Type", ["All services", "Intermodal", "Local", "Express"])
    show_ma = st.checkbox("Show 3-month moving average", value=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Data setup ---
months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
base_values = np.array([90.1,90.5,91.0,91.3,91.7,92.0,92.3,92.5,92.1,91.8,92.0,92.5])

def adjust_values(vals, region_name, service_name):
    seed = (abs(hash(region_name)) + abs(hash(service_name))) % 97
    rng = np.random.default_rng(seed)
    offsets = rng.normal(loc=0.0, scale=0.25, size=len(vals))
    return np.clip(vals + offsets, 0, 100)

values = adjust_values(base_values, region, service_type)
df = pd.DataFrame({"month": months, "ontime_pct": values})

# --- Sidebar ---
with st.sidebar:
    st.header("Filters & Export")
    start_month, end_month = st.select_slider(
        "Month range", options=months, value=(months[0], months[-1])
    )
    start_idx = months.index(start_month)
    end_idx = months.index(end_month) + 1
    df = df.iloc[start_idx:end_idx].reset_index(drop=True)

    st.download_button(
        "Download CSV",
        df.to_csv(index=False).encode("utf-8"),
        file_name="on_time_performance.csv",
        mime="text/csv"
    )

# --- Metrics ---
current = df['ontime_pct'].iat[-1]
previous = df['ontime_pct'].iat[-2] if len(df) > 1 else current
delta = current - previous
delta_pct = (delta / previous * 100) if previous != 0 else 0

col1, col2, col3 = st.columns([1.2, 1.2, 2])
with col1:
    st.metric("Current On-Time %", value=f"{current:.1f}%", delta=f"{delta:+.2f}% ({delta_pct:+.1f}%)")
with col2:
    st.metric("Period Average (%)", value=f"{df['ontime_pct'].mean():.1f}%")
with col3:
    st.markdown("<div class='card'><span class='muted'>Target:</span> ≥ 90% — higher values indicate stronger reliability.</div>", unsafe_allow_html=True)

# --- Chart ---
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df['month'], y=df['ontime_pct'],
    mode='lines+markers',
    line=dict(color="#FF7A00", width=3),
    marker=dict(size=8, color="#FF7A00"),
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
    paper_bgcolor="#07101a",
    plot_bgcolor="#07101a",
    font=dict(color="#E6EEF8", size=13),
    margin=dict(l=20,r=20,t=30,b=20),
    height=460,
    hovermode="x unified",
    legend=dict(bgcolor='rgba(255,255,255,0.03)')
)

fig.update_xaxes(title_text="Month")
fig.update_yaxes(title_text="On-Time Performance (%)", range=[0,100])

st.plotly_chart(fig, use_container_width=True)

# --- Help section ---
with st.expander("How to read this chart"):
    st.write("""
    The solid green line represents monthly on-time performance.
    The dashed line (if enabled) shows the 3-month moving average for trend stability.
    Use filters to focus on specific regions or service types.
    Higher values indicate better operational reliability.
    """)

st.caption("Chart includes hover tooltips. The latest value is shown above as a metric for screen-reader users.")
