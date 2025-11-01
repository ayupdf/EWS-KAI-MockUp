import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="Derailment Rate Trend", layout="wide")

_CSS = """
<style>
body {font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;}
.stApp { background: linear-gradient(180deg,#0b1220 0%, #07101a 100%); color: #E6EEF8; }
.card {background: linear-gradient(180deg,#0f1724 0%, #0b1220 100%); padding: 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.04); box-shadow: 0 8px 24px rgba(2,6,23,0.6);}
.muted {color: #9fb0d6;}
h2, h1 {color: #E6EEF8}
</style>
"""

st.markdown(_CSS, unsafe_allow_html=True)

# (Header and interactive filter controls removed by request.)
# Defaults: show full-year range and enable smoothing by default.
smoothing = True

# Mock data (rate per million train-miles)
months_full = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
values_full = np.array([0.45,0.43,0.41,0.39,0.36,0.38,0.40,0.37,0.35,0.33,0.30,0.28])

# Use full range by default (filters removed)
start_idx = 0
end_idx = len(months_full)
months_sub = months_full[start_idx:end_idx]
values = values_full[start_idx:end_idx]

df = pd.DataFrame({"month": months_sub, "derail_rate": values})

with st.sidebar:
    st.header('Export & Options')
    st.download_button('Download CSV', df.to_csv(index=False).encode('utf-8'), file_name='derailment_rate.csv', mime='text/csv')


# ==========================================
# 📉 KPI METRICS — Dark Theme (Derailment Rate)
# ==========================================
current = df['derail_rate'].iat[-1]
prev = df['derail_rate'].iat[-2] if len(df) > 1 else current
delta = current - prev
delta_pct = (delta / prev * 100) if prev != 0 else 0
avg_rate = df['derail_rate'].mean()

st.markdown("---")

# --- Columns for metrics ---
mc1, mc2 = st.columns([1.2, 1.2])

# --- DARK METRIC CARD STYLE ---
metric_style = """
<style>
.metric-card {
    background: linear-gradient(180deg,#0f1724 0%, #0b1220 100%);
    padding: 16px 18px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.06);
    box-shadow: 0 4px 16px rgba(0,0,0,0.6);
    text-align: center;
    transition: all 0.3s ease;
}
.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 28px rgba(0,0,0,0.8);
}
.metric-label {
    color: #9FB0D6;
    font-size: 13px;
    letter-spacing: 0.3px;
    text-transform: uppercase;
}
.metric-value {
    color: #E6EEF8;
    font-weight: 600;
    font-size: 22px;
    margin-top: 6px;
}
.metric-delta {
    font-size: 13px;
    color: #39D98A;
    font-weight: 500;
}
.metric-delta.negative {
    color: #F87171;
}
@media (max-width: 768px) {
    .metric-card { margin-bottom: 10px; }
}
</style>
"""
st.markdown(metric_style, unsafe_allow_html=True)

# --- Metric 1: Current rate ---
with mc1:
    delta_class = "negative" if delta > 0 else ""
    delta_arrow = "⬆" if delta > 0 else "⬇" if delta < 0 else "→"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Current rate<br>(per M train-miles)</div>
        <div class="metric-value">{current:.2f}</div>
        <div class="metric-delta {delta_class}">
            {delta_arrow} {delta:+.3f} ({delta_pct:+.1f}%)
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Metric 2: Period average ---
with mc2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Period average</div>
        <div class="metric-value">{avg_rate:.2f}</div>
    </div>
    """, unsafe_allow_html=True)


# Metrics
current = df['derail_rate'].iat[-1]
prev = df['derail_rate'].iat[-2] if len(df) > 1 else current
delta = current - prev
delta_pct = (delta / prev * 100) if prev != 0 else 0

# Plot removed per request (header, filters, and chart removed). Metrics remain visible above.