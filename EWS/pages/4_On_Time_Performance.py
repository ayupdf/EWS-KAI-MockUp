import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="On-Time Performance", layout="wide")

_CSS = """
<style>
body {font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;}
.stApp { background: linear-gradient(180deg,#0b1220 0%, #07101a 100%); color: #E6EEF8; }
.card {background: linear-gradient(180deg,#0f1724 0%, #0b1220 100%); padding: 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.04); box-shadow: 0 8px 24px rgba(2,6,23,0.6);}
.muted {color: #9fb0d6;}
</style>
"""

st.markdown(_CSS, unsafe_allow_html=True)

title_col, controls_col = st.columns([3,1])
with title_col:
    st.markdown("## ⏱️ On-Time Performance")
    st.markdown(
        """
        The percentage of shipments delivered within the scheduled window.  
        This is a key driver of customer satisfaction and network efficiency.
        """
    )

with controls_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('**Controls**')
    region = st.selectbox('Region', ['All regions', 'North', 'South', 'East', 'West'])
    service_type = st.selectbox('Service type', ['All services', 'Intermodal', 'Local', 'Express'])
    show_ma = st.checkbox('Show 3-month moving average', value=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Sample monthly on-time percentages
months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
values = np.array([90.1,90.5,91.0,91.3,91.7,92.0,92.3,92.5,92.1,91.8,92.0,92.5])

# Slight deterministic adjustment per region/service for demo interactivity
def adjust_values(vals, region_name, service_name):
    seed = (abs(hash(region_name)) + abs(hash(service_name))) % 97
    rng = np.random.default_rng(seed)
    offsets = rng.normal(loc=0.0, scale=0.25, size=len(vals))
    return np.clip(vals + offsets, 0, 100)

values = adjust_values(values, region, service_type)
df = pd.DataFrame({"month": months, "ontime_pct": values})

with st.sidebar:
    st.header('Export')
    st.download_button('Download CSV', df.to_csv(index=False).encode('utf-8'), file_name='on_time_performance.csv', mime='text/csv')

# Metrics
current = df['ontime_pct'].iat[-1]
previous = df['ontime_pct'].iat[-2] if len(df) > 1 else current
delta = current - previous
delta_pct = (delta / previous * 100) if previous != 0 else 0

col1, col2, col3 = st.columns([1.2,1.2,2])
with col1:
    st.metric('Current on-time %', value=f"{current:.1f}%", delta=f"{delta:+.2f}% ({delta_pct:+.1f}%)")
with col2:
    st.metric('Period average', value=f"{df['ontime_pct'].mean():.1f}%")
with col3:
    st.markdown("<div class='card'><span class='muted'>Target: 90%</span> — higher is better. Use filters to focus by region or service.</div>", unsafe_allow_html=True)

# Plotly line chart
fig = go.Figure()
fig.add_trace(go.Scatter(x=df['month'], y=df['ontime_pct'], mode='lines+markers', name='On-time %',
                         line=dict(color='#39D98A', width=3), marker=dict(size=7),
                         hovertemplate='%{x}: %{y:.1f} %'))

if show_ma and len(df) >= 3:
    ma = df['ontime_pct'].rolling(window=3, min_periods=1).mean()
    fig.add_trace(go.Scatter(x=df['month'], y=ma, mode='lines', name='3-mo MA', line=dict(color='#9FB0D6', dash='dash')))

fig.update_layout(template='plotly_dark', paper_bgcolor='#07101a', plot_bgcolor='#07101a', font=dict(color="#E6EEF8", size=13), height=420, margin=dict(l=24,r=24,t=28,b=24))
fig.update_xaxes(title_text='Month')
fig.update_yaxes(title_text='On-time %', range=[0,100])

st.plotly_chart(fig, use_container_width=True)

with st.expander('How to interpret'):
    st.write('On-time performance measures the share of shipments delivered within the scheduled window. Track trends and compare across regions/service types to identify operational issues.')

st.caption('Chart has hover tooltips; the current on-time % is exposed as a metric for screen-reader users.')
