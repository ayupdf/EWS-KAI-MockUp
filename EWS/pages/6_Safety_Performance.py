import streamlit as st
import pandas as pd
import numpy as np
from streamlit_echarts import st_echarts  # ✅ added for ECharts support

# ==========================================
# 🎨 WARNA & TEMA
# ==========================================
COLOR_BLUE = "#2D2A70"
COLOR_ORANGE = "#ED6B23"
COLOR_BG = "#000000"       # pure black background
COLOR_TEXT = "#E2E8F0"     # light text for contrast
COLOR_CARD = "#07101a"     # very dark card background
COLOR_BORDER = "#E5E7EB"   # Soft border gray
COLOR_PRIMARY = "#2F3E9E"  # Deep corporate blue
COLOR_ACCENT = "#F59E0B"   # Warm amber
COLOR_MUTED = "#64748B"    # Muted gray for subtitles

# ==========================================
# 📊 DATA
# ==========================================
data = {
    "Quarter 1": [5, 2, 11, 8],
    "Quarter 2": [3, 1, 8, 6],
    "Quarter 3": [4, 3, 9, 7],
    "Quarter 4": [2, 1, 5, 4],
}
categories = [
    "Derailments",
    "Collisions",
    "Highway-Rail Crossing Incidents",
    "Employee Reportable Injuries"
]

# ==========================================
# ⚙️ STREAMLIT PAGE CONFIG
# ==========================================
st.set_page_config(page_title="Safety Performance (trimmed)", layout="wide")

# Minimal black theme CSS
_CSS = '''
<style>
body { background: #000000; color: #E6EEF8; font-family: Inter, sans-serif; }
.title { font-size: 28px; font-weight:700; color:#ED6B23; margin-bottom:6px }
.subtitle { color:#94A3B8; margin-bottom:12px }
.metric-card { background: linear-gradient(180deg,#071018 0%, #000000 100%); padding:10px 12px; border-radius:10px; border:1px solid rgba(255,255,255,0.02); text-align:center }
.metric-label { color:#94A3B8; font-size:12px }
.metric-value { color:#E6EEF8; font-weight:600; font-size:18px }
.metric-delta { color:#7ee787; font-size:12px }
</style>
'''
st.markdown(_CSS, unsafe_allow_html=True)

# ==========================================
# 🧾 HEADER
# ==========================================
st.markdown('''
<div style="display:flex;align-items:center;gap:10px">
    <svg width="28" height="28" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <path d="M12 2l8 4v6c0 5-3.9 9.7-8 11-4.1-1.3-8-6-8-11V6l8-4z" fill="#FFFFFF"/>
        <circle cx="12" cy="12" r="3" fill="rgba(0,0,0,0.12)"/>
    </svg>
    <div class="title" style="color:#FFFFFF">Safety Performance</div>
</div>
''', unsafe_allow_html=True)

# ==========================================
# 📅 QUARTER FILTER
# ==========================================
quarter = st.selectbox("Select Quarter", options=list(data.keys()), index=2)

df = pd.DataFrame({"Category": categories, "Value": data[quarter]})

# Sidebar download
with st.sidebar:
    st.download_button("Download CSV", df.to_csv(index=False).encode('utf-8'),
                       file_name='safety_trimmed.csv', mime='text/csv')

# ==========================================
# 📈 METRICS
# ==========================================
total = int(df['Value'].sum())
top_cat = df.sort_values('Value', ascending=False).iloc[0]['Category']
minmax = f"{int(df['Value'].min())} / {int(df['Value'].max())}"

col1, col2, col3 = st.columns([1.2,1.5,2])
with col1:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Total incidents</div><div class='metric-value'>{total}</div></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Top category</div><div class='metric-value'>{top_cat}</div></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Min / Max</div><div class='metric-value'>{minmax}</div></div>", unsafe_allow_html=True)

# ==========================================
# 📊 MAIN CHART (ECharts)
# ==========================================
options = {
    "backgroundColor": "#000000",
    "tooltip": {"trigger": "axis"},
    "xAxis": {
        "type": "category",
        "data": df["Category"].tolist(),
        "axisLabel": {"color": "#E6EEF8"},
    },
    "yAxis": {
        "type": "value",
        "axisLabel": {"color": "#E6EEF8"},
        "splitLine": {"lineStyle": {"color": "#222"}}
    },
    "series": [{
        "data": df["Value"].tolist(),
        "type": "bar",
        "barWidth": "45%",
        "itemStyle": {
            "borderRadius": [6, 6, 0, 0],
            "color": {
                "type": "linear",
                "x": 0, "y": 0, "x2": 0, "y2": 1,
                "colorStops": [
                    {"offset": 0, "color": "#3B82F6"},
                    {"offset": 1, "color": "#1E3A8A"}
                ],
            },
        },
        "label": {
            "show": True,
            "position": "top",
            "color": "#E6EEF8",
            "fontSize": 12
        },
        "animationDuration": 1200
    }]
}

st_echarts(options=options, height="420px", key="echart_safety_bar")
