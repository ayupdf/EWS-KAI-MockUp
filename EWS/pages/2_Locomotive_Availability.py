import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="Locomotive Availability", layout="wide")

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
    st.markdown("## 🚂 Locomotive Availability")
    st.markdown("""
    Shows the percentage of the locomotive fleet available for service versus those down for maintenance.
    High availability improves service reliability but must be balanced with preventative maintenance.
    """)

with controls_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('**Controls**')
    region = st.selectbox('Region / Fleet', ['All fleets', 'North', 'South', 'East', 'West'])
    show_trend_smooth = st.checkbox('Smooth trend (3-mo MA)', value=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Sample data (monthly trend + current split)
months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
availability_trend = np.array([82,83,84,85,85,86,86,87,86,87,88,87])  # percent available monthly
current_available = int(availability_trend[-1])
current_in_maintenance = 100 - current_available

# Build small dataframe for download
df = pd.DataFrame({"month": months, "availability_pct": availability_trend})

with st.sidebar:
    st.header('Export')
    st.download_button('Download availability CSV', df.to_csv(index=False).encode('utf-8'), file_name='locomotive_availability.csv', mime='text/csv')

# Metrics
prev = availability_trend[-2] if len(availability_trend) > 1 else availability_trend[-1]
delta = availability_trend[-1] - prev
delta_pct = (delta / prev * 100) if prev != 0 else 0

col_a, col_b, col_c = st.columns([1.2,1.2,2])
with col_a:
    st.metric('Available (current %)', value=f"{current_available}%", delta=f"{delta:+.1f}% ({delta_pct:+.1f}%)")
with col_b:
    st.metric('In Maintenance (current %)', value=f"{current_in_maintenance}%")
with col_c:
    st.markdown("<div class='card'><span class='muted'>Note:</span> Values shown are sample data for UI demo. Replace with fleet data to reflect real availability.</div>", unsafe_allow_html=True)

# Layout: donut on left, trend on right
donut_col, trend_col = st.columns([1,2])

with donut_col:
    labels = ['Available', 'In Maintenance']
    values = [current_available, current_in_maintenance]
    colors = ['#39D98A', '#FF6B6B']
    fig1 = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.6,
                                 marker=dict(colors=colors), textinfo='label+percent')])
    fig1.update_layout(template='plotly_dark', paper_bgcolor='#07101a', plot_bgcolor='#07101a', font=dict(color="#E6EEF8"), height=360)
    st.plotly_chart(fig1, use_container_width=True)

with trend_col:
    fig2 = go.Figure()
    y = pd.Series(availability_trend)
    if show_trend_smooth and len(y) >= 3:
        ma = y.rolling(window=3, min_periods=1).mean()
        fig2.add_trace(go.Scatter(x=months, y=ma, mode='lines', name='3-mo MA', line=dict(color='#9FB0D6', dash='dash')))
    fig2.add_trace(go.Scatter(x=months, y=y, mode='markers+lines', name='Availability %', line=dict(color='#39D98A', width=3), marker=dict(size=7)))
    fig2.update_layout(template='plotly_dark', paper_bgcolor='#07101a', plot_bgcolor='#07101a', font=dict(color="#E6EEF8"), height=360, margin=dict(l=10,r=10,t=20,b=10))
    fig2.update_xaxes(title_text='Month')
    fig2.update_yaxes(title_text='Availability (%)', range=[0,100])
    st.plotly_chart(fig2, use_container_width=True)

with st.expander('How to interpret'):
    st.write('The donut shows the current split between available and in-maintenance locomotives. The trend shows monthly availability — use smoothing to see underlying trends.')

st.caption('Chart tooltips provide details. For screen-reader users, the current availability is shown as a metric.')
