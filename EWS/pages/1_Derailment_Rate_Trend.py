import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ==============================
# ⚙️ Page Config
# ==============================
st.set_page_config(page_title="Derailment Rate Trend", layout="wide")

# ==============================
# 🎨 Global CSS
# ==============================
st.markdown("""
<style>
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.stApp {
    background: linear-gradient(180deg,#0b1220 0%, #07101a 100%);
    color: #E6EEF8;
}
h1, h2, h3, h4 {
    color: #E6EEF8;
    margin-bottom: 0.4rem;
}

/* Section Spacing */
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 1rem;
}

/* Control Title */
.control-title {
    font-size: 15px;
    font-weight: 600;
    color: #E6EEF8;
    margin-top: 10px;
    margin-bottom: 4px;
    letter-spacing: 0.3px;
}
.control-title::before {
    content: "";
    display: inline-block;
    width: 6px;
    height: 16px;
    border-radius: 3px;
    background: linear-gradient(180deg,#3B82F6,#6366F1);
    margin-right: 8px;
    vertical-align: middle;
}

/* KPI Metric Cards */
.metric-card {
    background: linear-gradient(180deg,#0f1724 0%, #0b1220 100%);
    padding: 14px 16px;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.06);
    box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    text-align: center;
    transition: all 0.3s ease;
    margin-top: 6px;
}
.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 22px rgba(0,0,0,0.7);
}
.metric-label {
    color: #9FB0D6;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}
.metric-value {
    color: #E6EEF8;
    font-weight: 600;
    font-size: 22px;
    margin-top: 4px;
}
.metric-delta {
    font-size: 13px;
    color: #39D98A;
    font-weight: 500;
}
.metric-delta.negative { color: #F87171; }

/* Make everything compact */
div[data-testid="stMarkdownContainer"] p {
    margin-bottom: 0.4rem;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# 🚄 Title + Controls
# ==============================
st.markdown("## 🚄 Derailment Rate Trend")

st.markdown("<div class='control-title'>Controls</div>", unsafe_allow_html=True)

months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
month_range = st.select_slider('Month range', options=months, value=(months[0], months[-1]))
smoothing = st.checkbox('Show 3-month moving average', value=True)

# ==============================
# 📊 Mock Data
# ==============================
months_full = months
values_full = np.array([0.45,0.43,0.41,0.39,0.36,0.38,0.40,0.37,0.35,0.33,0.30,0.28])
start_idx = months_full.index(month_range[0])
end_idx = months_full.index(month_range[1]) + 1
months_sub = months_full[start_idx:end_idx]
values = values_full[start_idx:end_idx]
df = pd.DataFrame({"month": months_sub, "derail_rate": values})

with st.sidebar:
    st.header('Export & Options')
    st.download_button(
        'Download CSV',
        df.to_csv(index=False).encode('utf-8'),
        file_name='derailment_rate.csv',
        mime='text/csv'
    )

# ==============================
# 📉 KPI METRICS
# ==============================
current = df['derail_rate'].iat[-1]
prev = df['derail_rate'].iat[-2] if len(df) > 1 else current
delta = current - prev
delta_pct = (delta / prev * 100) if prev != 0 else 0
avg_rate = df['derail_rate'].mean()

# KPI Cards
mc1, mc2 = st.columns([1, 1])

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

with mc2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Period average</div>
        <div class="metric-value">{avg_rate:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

# ==============================
# 📈 Trend Chart
# ==============================
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
    fig.add_trace(go.Scatter(
        x=df['month'], y=ma, mode='lines',
        line=dict(color='#9FB0D6', dash='dash'),
        name='3-mo MA'
    ))

fig.update_layout(
    template='plotly_dark',
    paper_bgcolor='#07101a',
    plot_bgcolor='#07101a',
    font=dict(color="#E6EEF8", size=13),
    margin=dict(l=24,r=24,t=20,b=20),
    height=380,
    hovermode='x unified',
    legend=dict(bgcolor='rgba(255,255,255,0.03)')
)
fig.update_xaxes(title_text='Month')
fig.update_yaxes(title_text='Derailments per million train-miles')

st.plotly_chart(fig, use_container_width=True)

# ==============================
# ℹ️ Notes
# ==============================
with st.expander('How to read this'):
    st.write('The shaded area shows the monthly derailment rate. A downward trend indicates improvement. Use the moving average to smooth short-term volatility.')

st.caption('Chart includes hover tooltips. Latest rate is exposed as a metric for screen-reader users.')
