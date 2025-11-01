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

title_col, controls_col = st.columns([3,1])
with title_col:
    st.markdown("## 🚄 Derailment Rate Trend")
    st.markdown(
        """
        Tracking derailments per million train-miles over the last 12 months helps identify seasonal or operational trends.  
        A **downward trend** is the goal, indicating systemic safety improvements.
        """
    )

with controls_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('**Controls**')
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    month_range = st.select_slider('Month range', options=months, value=(months[0], months[-1]))
    smoothing = st.checkbox('Show 3-month moving average', value=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Mock data (rate per million train-miles)
months_full = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
values_full = np.array([0.45,0.43,0.41,0.39,0.36,0.38,0.40,0.37,0.35,0.33,0.30,0.28])

start_idx = months_full.index(month_range[0])
end_idx = months_full.index(month_range[1]) + 1
months_sub = months_full[start_idx:end_idx]
values = values_full[start_idx:end_idx]

df = pd.DataFrame({"month": months_sub, "derail_rate": values})

with st.sidebar:
    st.header('Export & Options')
    st.download_button('Download CSV', df.to_csv(index=False).encode('utf-8'), file_name='derailment_rate.csv', mime='text/csv')

# Metrics
current = df['derail_rate'].iat[-1]
prev = df['derail_rate'].iat[-2] if len(df) > 1 else current
delta = current - prev
delta_pct = (delta / prev * 100) if prev != 0 else 0

metric_col1, metric_col2, metric_col3 = st.columns([1.2,1.2,2])
with metric_col1:
    st.metric('Current rate (per M train-miles)', value=f"{current:.2f}", delta=f"{delta:+.3f} ({delta_pct:+.1f}%)")
with metric_col2:
    st.metric('Period average', value=f"{df['derail_rate'].mean():.2f}")
with metric_col3:
    st.markdown("<div class='card'><span class='muted'>Note:</span> These are mock values for UI demonstration. Replace with production data for analysis.</div>", unsafe_allow_html=True)

# Plotly area chart
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df['month'], y=df['derail_rate'], mode='lines+markers',
    line=dict(color="#FF8A3D", width=3),
    fill='tozeroy', fillcolor='rgba(255,138,61,0.08)',
    name='Rate per M train-miles',
    hovertemplate='%{x}: %{y:.2f} per M'
))

if smoothing and len(df) >= 3:
    ma = df['derail_rate'].rolling(window=3, min_periods=1).mean()
    fig.add_trace(go.Scatter(x=df['month'], y=ma, mode='lines', line=dict(color='#9FB0D6', dash='dash'), name='3-mo MA'))

fig.update_layout(
    template='plotly_dark',
    paper_bgcolor='#07101a',
    plot_bgcolor='#07101a',
    font=dict(color="#E6EEF8", size=13),
    margin=dict(l=24,r=24,t=28,b=24),
    height=420,
    hovermode='x unified',
    legend=dict(bgcolor='rgba(255,255,255,0.03)')
)
fig.update_xaxes(title_text='Month')
fig.update_yaxes(title_text='Derailments per million train-miles')

st.plotly_chart(fig, use_container_width=True)

with st.expander('How to read this'):
    st.write('The shaded area shows the monthly derailment rate. A downward trend indicates improvement. Use the moving average to smooth short-term volatility.')

st.caption('Chart includes hover tooltips. Latest rate is exposed as a metric for screen-reader users.')
