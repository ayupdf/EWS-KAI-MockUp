import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="Proactive Safety — Leading Indicators", layout="wide")

_CSS = """
<style>
body {font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;}
.stApp { background: linear-gradient(180deg,#0b1220 0%, #07101a 100%); color: #E6EEF8; }
.card {background: linear-gradient(180deg,#0f1724 0%, #0b1220 100%); padding: 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.04); box-shadow: 0 8px 24px rgba(2,6,23,0.6);}
.muted {color: #9fb0d6;}
.stSidebar { background: linear-gradient(180deg,#0f1724 0%, #0b1220 100%); }
h2, h1 {color: #E6EEF8}
</style>
"""

st.markdown(_CSS, unsafe_allow_html=True)

title_col, ctl_col = st.columns([3,1])
with title_col:
    st.markdown("## 🧯 Proactive Safety: Leading Indicators")
    st.markdown("""
    Leading indicators measure proactive efforts to prevent incidents.
    This chart compares the volume of reported defects, failures, and close calls **this month vs last month**.
    """)

with ctl_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('**Controls**')
    indicator_options = ["Track Defects Found", "Signal Failures", "Close Calls Reported"]
    selected = st.multiselect("Indicators", indicator_options, default=indicator_options)
    show_pct = st.checkbox("Show percent change on bars", value=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Sample data (replace with real dataset when available)
categories = indicator_options
last_month = np.array([120, 50, 90])
this_month = np.array([130, 45, 100])

# filter based on selection
mask = [c in selected for c in categories]
cats = [c for c, m in zip(categories, mask) if m]
lm = last_month[mask]
tm = this_month[mask]

df = pd.DataFrame({"indicator": cats, "last_month": lm, "this_month": tm})
df['change'] = df['this_month'] - df['last_month']
df['pct_change'] = np.where(df['last_month'] == 0, 0, df['change'] / df['last_month'] * 100)

with st.sidebar:
    st.header("Export & Filters")
    st.download_button("Download CSV", df.to_csv(index=False).encode('utf-8'), file_name='leading_indicators.csv', mime='text/csv')

# top metrics
total_this = int(df['this_month'].sum())
total_last = int(df['last_month'].sum())
tot_change = total_this - total_last
tot_pct = (tot_change / total_last * 100) if total_last != 0 else 0

col1, col2, col3 = st.columns([1.2,1.2,2])
with col1:
    st.metric("Total events (this month)", value=f"{total_this}", delta=f"{tot_change:+d} ({tot_pct:+.1f}%)")
with col2:
    avg_change = df['change'].mean() if len(df) else 0
    st.metric("Avg change per indicator", value=f"{avg_change:.1f}")
with col3:
    st.markdown("<div class='card'><span class='muted'>Tip:</span> Use the indicator picker to focus the chart and export the results to CSV.</div>", unsafe_allow_html=True)

# Build Plotly figure
colors = {"last":"#6B7FD6","this":"#39D98A"}
fig = go.Figure()
fig.add_trace(go.Bar(
    x=df['indicator'], y=df['last_month'], name='Last Month', marker_color=colors['last'], offsetgroup=1,
    hovertemplate='%{x}<br>Last: %{y}<extra></extra>'
))
fig.add_trace(go.Bar(
    x=df['indicator'], y=df['this_month'], name='This Month', marker_color=colors['this'], offsetgroup=2,
    text=(df['pct_change'].apply(lambda v: f"{v:.1f}%") if show_pct else None), textposition='outside' if show_pct else None,
    hovertemplate='%{x}<br>This: %{y}<br>Change: %{customdata[0]:+.0f} (%{customdata[1]:.1f}%)<extra></extra>',
    customdata=np.stack([df['change'], df['pct_change']], axis=-1)
))

fig.update_layout(
    barmode='group',
    template='plotly_dark',
    paper_bgcolor='#07101a',
    plot_bgcolor='#07101a',
    font=dict(color="#E6EEF8", size=13),
    margin=dict(l=24,r=24,t=28,b=24),
    height=420,
    hovermode='closest',
    legend=dict(bgcolor='rgba(255,255,255,0.03)')
)

fig.update_xaxes(title_text='Indicator')
fig.update_yaxes(title_text='Number of events')

st.plotly_chart(fig, use_container_width=True)

with st.expander("About these metrics"):
    st.write("Leading indicators are proactive measurements — increases may indicate more detection/reporting or an emerging safety issue. Use trends together with operational context to interpret changes.")

st.caption("Chart includes hover tooltips. Download the CSV for offline analysis.")
