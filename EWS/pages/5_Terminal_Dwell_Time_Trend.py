import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import io

st.set_page_config(page_title="Terminal Dwell Time Trend", layout="wide")

_CSS = """
<style>
body {font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;}
.stApp { background: linear-gradient(180deg,#0b1220 0%, #07101a 100%); color: #E6EEF8; }
.card {background: linear-gradient(180deg,#0f1724 0%, #0b1220 100%); padding: 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.04); box-shadow: 0 8px 24px rgba(2,6,23,0.6);}
.muted {color: #9fb0d6;}
.stSidebar { background: linear-gradient(180deg,#0f1724 0%, #0b1220 100%); }
a, .st-a {color: #9fd1ff}
h2, h1 {color: #E6EEF8}
</style>
"""

st.markdown(_CSS, unsafe_allow_html=True)

title_col, controls_col = st.columns([3,1])
with title_col:
    st.markdown("## 🚉 Terminal Dwell Time Trend")
    st.markdown("""
    This visualization shows the **average dwell time (hours)** that freight cars spend idle at terminals.
    Lower dwell time improves asset utilization, network velocity, and service levels.
    """)

with controls_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("\n")
    st.markdown("**Controls**")
    available_stations = ["All terminals","Terminal A","Terminal B","Terminal C"]
    station = st.selectbox("Station", available_stations, index=0)
    smoothing = st.checkbox("Show 3-month moving average", value=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Data (sample monthly values) ---
months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
base_values = np.array([27.5,27.8,27.6,26.9,26.4,25.8,25.0,24.7,24.3,23.9,23.7,23.5])

def station_adjust(values, station_name: str):
    # deterministic small adjustment per station so selection feels interactive
    if station_name == "All terminals" or station_name is None:
        return values
    seed = abs(hash(station_name)) % 97
    rng = np.random.default_rng(seed)
    offsets = rng.normal(loc=0.0, scale=0.35, size=len(values))
    return values + offsets

values = station_adjust(base_values, station)

# Sidebar filters for month range and download
with st.sidebar:
    st.header("Filters")
    start_month, end_month = st.select_slider(
        'Month range', options=months, value=(months[0], months[-1])
    )
    start_idx = months.index(start_month)
    end_idx = months.index(end_month) + 1
    df = pd.DataFrame({"month": months, "dwell_hours": values})
    df = df.iloc[start_idx:end_idx].reset_index(drop=True)
    st.download_button("Download CSV", df.to_csv(index=False).encode('utf-8'), file_name='terminal_dwell.csv', mime='text/csv')

# Metrics row
current = df['dwell_hours'].iat[-1]
previous = df['dwell_hours'].iat[-2] if len(df) > 1 else df['dwell_hours'].iat[-1]
delta = current - previous
delta_pct = (delta / previous) * 100 if previous != 0 else 0

m1, m2, m3 = st.columns([1.2,1.2,2])
with m1:
    st.metric(label="Current avg dwell (hrs)", value=f"{current:.1f}", delta=f"{delta:+.2f} ({delta_pct:+.1f}%)")
with m2:
    seasonal = df['dwell_hours'].mean()
    st.metric(label="Period average (hrs)", value=f"{seasonal:.1f}")
with m3:
    st.markdown("<div class='card'><span class='muted'>Data note:</span> Values are sample data for demo purposes. Select a station to see deterministic adjustments.</div>", unsafe_allow_html=True)

# Prepare traces
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df['month'], y=df['dwell_hours'],
    mode='lines+markers',
    line=dict(color="#FF7A00", width=3),
    marker=dict(size=8, color="#FF7A00"),
    name="Average Dwell (hrs)",
    hovertemplate='%{x}: %{y:.2f} hrs'
))

if smoothing and len(df) >= 3:
    window = 3
    ma = df['dwell_hours'].rolling(window=window, min_periods=1).mean()
    fig.add_trace(go.Scatter(
        x=df['month'], y=ma,
        mode='lines',
        line=dict(color="#2D2A70", width=2, dash='dash'),
        name=f'{window}-month MA'
    ))

fig.update_layout(
    template='plotly_dark',
    paper_bgcolor='#07101a',
    plot_bgcolor='#07101a',
    font=dict(color="#E6EEF8", size=13),
    margin=dict(l=20,r=20,t=30,b=20),
    height=460,
    hovermode='x unified',
    legend=dict(bgcolor='rgba(255,255,255,0.03)')
)

fig.update_xaxes(title_text='Month')
fig.update_yaxes(title_text='Average dwell (hours)')

# Chart + explanation
st.plotly_chart(fig, use_container_width=True)

with st.expander("How to read this chart"):
    st.write("The solid orange line shows monthly average dwell time; the dashed line is the moving average (if enabled). Use the filters to focus the timeframe or station. Lower dwell times indicate better terminal efficiency.")

## Accessibility note
st.caption("Chart includes hover tooltips. For screen-reader users, the latest value is shown above as a metric.")
