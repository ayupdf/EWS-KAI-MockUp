import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="Proactive Safety — Leading Indicators", layout="wide")

# Light theme CSS and neat card styles
_CSS = """
<style>
body {font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;}
.stApp { background: #000000; color: #E6EEF8; }
.card {background: linear-gradient(180deg,#0b0b0b 0%, #070707 100%); padding: 14px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.02); box-shadow: 0 6px 18px rgba(0,0,0,0.6);} 
.metric-card {background: linear-gradient(180deg,#081018 0%, #07101a 100%); padding: 14px; border-radius: 8px; border:1px solid rgba(255,255,255,0.02);}
.metric-label {color:#9fb0d6; font-size:13px;}
.metric-value {color:#E6EEF8; font-size:22px; font-weight:600;}
.metric-delta {color:#7ee787; font-size:13px;}
h2, h1 {color: #E6EEF8}
.muted {color: #9fb0d6}
</style>
"""

st.markdown(_CSS, unsafe_allow_html=True)

# Header
st.markdown("## 🧯 Proactive Safety — Leading Indicators")


# Filters (placed under header for quick access)
indicator_options = ["Track Defects Found", "Signal Failures", "Close Calls Reported"]
filters_col1, filters_col2 = st.columns([3,1])
with filters_col1:
    selected = st.multiselect("Indicators", indicator_options, default=indicator_options)
with filters_col2:
    show_pct = st.checkbox("Show percent change on bars", value=True)

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
    st.header("Export & Options")
    st.download_button("Download CSV", df.to_csv(index=False).encode('utf-8'), file_name='leading_indicators.csv', mime='text/csv')

# Compute top metrics (3 neat cards)
total_this = int(df['this_month'].sum())
total_last = int(df['last_month'].sum())
tot_change = total_this - total_last
tot_pct = (tot_change / total_last * 100) if total_last != 0 else 0
avg_change = df['change'].mean() if len(df) else 0

# largest increase / decrease
if len(df):
    max_idx = int(df['change'].idxmax())
    min_idx = int(df['change'].idxmin())
    largest_inc_label = df.at[max_idx, 'indicator']
    largest_inc_val = int(df.at[max_idx, 'change'])
    largest_dec_label = df.at[min_idx, 'indicator']
    largest_dec_val = int(df.at[min_idx, 'change'])
else:
    largest_inc_label = largest_dec_label = "-"
    largest_inc_val = largest_dec_val = 0

card1, card2, card3 = st.columns([1.5,1.5,3])
with card1:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Total events (this month)</div><div class='metric-value'>{total_this}</div><div class='metric-delta'>Δ {tot_change:+d} ({tot_pct:+.1f}%)</div></div>", unsafe_allow_html=True)
with card2:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Avg change per indicator</div><div class='metric-value'>{avg_change:.1f}</div><div class='metric-delta muted'>Average of selected indicators</div></div>", unsafe_allow_html=True)
with card3:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Largest move</div><div style='display:flex;gap:12px;align-items:center'><div style='flex:1'><div class='metric-value'>+{largest_inc_val}</div><div class='muted'>{largest_inc_label} (increase)</div></div><div style='flex:1'><div class='metric-value'>{largest_dec_val}</div><div class='muted'>{largest_dec_label} (decrease)</div></div></div></div>", unsafe_allow_html=True)

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
    paper_bgcolor='#000000',
    plot_bgcolor='#000000',
    font=dict(color="#E6EEF8", size=13),
    margin=dict(l=24,r=24,t=28,b=24),
    height=420,
    hovermode='closest',
    legend=dict(bgcolor='rgba(255,255,255,0.03)')
)

fig.update_xaxes(title_text='Indicator', color='#E6EEF8')
fig.update_yaxes(title_text='Number of events', color='#E6EEF8')

st.plotly_chart(fig, use_container_width=True, key='proactive_leading_chart')

