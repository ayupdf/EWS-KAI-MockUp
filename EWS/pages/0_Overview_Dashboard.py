import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Overview Dashboard", layout="wide")

# Small shared theme
CSS = """
<style>
body {font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;}
.stApp { background: #FFFFFF; color: #0F172A; }
.card {background: #FFFFFF; padding: 12px; border-radius: 10px; border: 1px solid rgba(15,23,42,0.06); box-shadow: 0 6px 20px rgba(2,6,23,0.04);}
.small {font-size:12px; color:#64748B}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

st.markdown("## 🚆 Network Overview — Key KPIs")
st.markdown("A compact dashboard consolidating key safety, availability and performance metrics. Below are quick insights generated from the latest data for each area — useful for stand-up meetings and executive summaries.")

# Sample source arrays (same as other pages)
months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
derail_values = np.array([0.45,0.43,0.41,0.39,0.36,0.38,0.40,0.37,0.35,0.33,0.30,0.28])
dwell_values = np.array([27.5,27.8,27.6,26.9,26.4,25.8,25.0,24.7,24.3,23.9,23.7,23.5])
avail_trend = np.array([82,83,84,85,85,86,86,87,86,87,88,87])
ontime = np.array([90.1,90.5,91.0,91.3,91.7,92.0,92.3,92.5,92.1,91.8,92.0,92.5])

# Proactive safety and safety performance sample data
proactive_categories = ["Track Defects Found","Signal Failures","Close Calls Reported"]
proactive_last = np.array([120,50,90])
proactive_this = np.array([130,45,100])

safety_categories = ["Derailments","Collisions","Crossing Incidents","Employee Injuries"]
safety_data = {
    "Quarter 1": [5,2,11,8],
    "Quarter 2": [3,1,8,6],
    "Quarter 3": [4,3,9,7],
    "Quarter 4": [2,1,5,4]
}
quarters = list(safety_data.keys())

# Top KPI cards
k1 = f"{avail_trend[-1]}%"
k2 = f"{ontime[-1]:.1f}%"
k3 = f"{dwell_values[-1]:.1f} hrs"

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"<div class='card'><h3 style='margin:0'>{k1}</h3><div class='small'>Locomotive availability (current)</div></div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='card'><h3 style='margin:0'>{k2}</h3><div class='small'>On-time performance (current)</div></div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='card'><h3 style='margin:0'>{k3}</h3><div class='small'>Terminal dwell (current)</div></div>", unsafe_allow_html=True)

st.markdown("---")

# Compact grid of mini-charts
row1 = st.columns(3)

# Derailment mini area
with row1[0]:
    st.markdown("**Derailment rate (12m)**")
    fig_d = go.Figure()
    fig_d.add_trace(go.Scatter(x=months, y=derail_values, mode='lines', line=dict(color='#FF8A3D'), fill='tozeroy'))
    fig_d.update_layout(template='simple_white', height=240, margin=dict(t=30,b=20,l=20,r=20), paper_bgcolor='#FFFFFF', plot_bgcolor='#FFFFFF', font=dict(color="#0F172A"))
    st.plotly_chart(fig_d, use_container_width=True, key='ov_derail')
    # Insight for derailments
    change_pct = (derail_values[-1] - derail_values[0]) / derail_values[0] * 100
    trend = "decreasing" if derail_values[-1] < derail_values[0] else "increasing" if derail_values[-1] > derail_values[0] else "flat"
    st.markdown(f"<div class='small'>Insight: Derailment rate is {trend} over the 12-month window ({change_pct:+.1f}% vs start). Continued focus on track maintenance correlates with reducing derailments.</div>", unsafe_allow_html=True)

# Locomotive donut
with row1[1]:
    st.markdown("**Locomotive availability**")
    avail = [int(avail_trend[-1]), 100-int(avail_trend[-1])]
    fig_a = go.Figure(data=[go.Pie(labels=['Available','In Maintenance'], values=avail, hole=0.6, marker=dict(colors=['#39D98A','#FF6B6B']))])
    fig_a.update_layout(template='simple_white', height=240, margin=dict(t=30,b=20,l=20,r=20), paper_bgcolor='#FFFFFF', plot_bgcolor='#FFFFFF', font=dict(color="#0F172A"))
    st.plotly_chart(fig_a, use_container_width=True, key='ov_avail')
    # Insight for availability
    avail_delta = avail_trend[-1] - avail_trend[-2]
    st.markdown(f"<div class='small'>Insight: Availability at {avail_trend[-1]}% (Δ {avail_delta:+d} pp vs prior month). Monitor maintenance throughput to sustain gains.</div>", unsafe_allow_html=True)

# Dwell mini line
with row1[2]:
    st.markdown("**Terminal dwell (12m)**")
    fig_dw = go.Figure(go.Scatter(x=months, y=dwell_values, mode='lines+markers', line=dict(color='#FFB300')))
    fig_dw.update_layout(template='simple_white', height=240, margin=dict(t=30,b=20,l=20,r=20), paper_bgcolor='#FFFFFF', plot_bgcolor='#FFFFFF', font=dict(color="#0F172A"))
    st.plotly_chart(fig_dw, use_container_width=True, key='ov_dwell')
    # Insight for dwell
    dwell_change = dwell_values[-1] - dwell_values[0]
    st.markdown(f"<div class='small'>Insight: Terminal dwell has {'improved' if dwell_change<0 else 'worsened'} by {abs(dwell_change):.1f} hrs since Jan. Lower dwell generally improves asset utilization.</div>", unsafe_allow_html=True)

# Second row of charts
row2 = st.columns(3)

# On-time performance
with row2[0]:
    st.markdown("**On-time performance (12m)**")
    fig_ot = go.Figure(go.Scatter(x=months, y=ontime, mode='lines+markers', line=dict(color='#39D98A')))
    fig_ot.update_layout(template='simple_white', height=240, margin=dict(t=30,b=20,l=20,r=20), paper_bgcolor='#FFFFFF', plot_bgcolor='#FFFFFF', font=dict(color="#0F172A"))
    st.plotly_chart(fig_ot, use_container_width=True, key='ov_ontime')
    # Insight for on-time
    ot_change = ontime[-1] - ontime[0]
    st.markdown(f"<div class='small'>Insight: On-time performance is {ontime[-1]:.1f}% (Δ {ot_change:+.1f} pp vs Jan). Small sustained improvements indicate stronger schedule adherence.</div>", unsafe_allow_html=True)

# Proactive safety grouped bars
with row2[1]:
    st.markdown("**Proactive safety (this vs last)**")
    fig_p = go.Figure()
    fig_p.add_trace(go.Bar(x=proactive_categories, y=proactive_last, name='Last Month', marker_color='#6B7FD6'))
    fig_p.add_trace(go.Bar(x=proactive_categories, y=proactive_this, name='This Month', marker_color='#39D98A'))
    fig_p.update_layout(barmode='group', template='simple_white', height=240, margin=dict(t=30,b=20), paper_bgcolor='#FFFFFF', plot_bgcolor='#FFFFFF', font=dict(color="#0F172A"))
    st.plotly_chart(fig_p, use_container_width=True, key='ov_proactive')
    # Insight for proactive safety
    total_last = proactive_last.sum()
    total_this = proactive_this.sum()
    tot_delta = total_this - total_last
    st.markdown(f"<div class='small'>Insight: Proactive events { 'increased' if tot_delta>0 else 'decreased' } by {abs(tot_delta)} events vs last month. Track Defects show the largest absolute change.</div>", unsafe_allow_html=True)

# Safety heatmap
with row2[2]:
    st.markdown("**Safety (quarters heatmap)**")
    z = np.array([safety_data[q] for q in quarters]).T
    fig_h = go.Figure(data=go.Heatmap(z=z, x=quarters, y=safety_categories, colorscale='Viridis'))
    fig_h.update_layout(template='simple_white', height=240, margin=dict(t=30,b=20), paper_bgcolor='#FFFFFF', plot_bgcolor='#FFFFFF', font=dict(color="#0F172A"))
    st.plotly_chart(fig_h, use_container_width=True, key='ov_safety_heat')
    # Insight for safety performance
    total_by_quarter = [sum(safety_data[q]) for q in quarters]
    recent_trend = 'down' if total_by_quarter[-1] < total_by_quarter[0] else 'up' if total_by_quarter[-1] > total_by_quarter[0] else 'flat'
    st.markdown(f"<div class='small'>Insight: Quarterly incidents are trending {recent_trend} from Q1 to Q4 (Q1={total_by_quarter[0]}, Q4={total_by_quarter[-1]}). Focus on top categories to drive reductions.</div>", unsafe_allow_html=True)

st.markdown("---")

# Download combined CSV
all_rows = []
for q, vals in safety_data.items():
    for cat, v in zip(safety_categories, vals):
        all_rows.append({'Quarter': q, 'Category': cat, 'Value': v})

combined_df = pd.DataFrame(all_rows)
st.sidebar.download_button('Download safety CSV', combined_df.to_csv(index=False).encode('utf-8'), file_name='safety_combined.csv', mime='text/csv')

st.caption('This overview page aggregates the core charts from the project for quick visibility. I can delete the other pages if you want to keep only this consolidated view.')
st.markdown("---")
st.markdown("## Brief Recommendations")
st.markdown("- Continue targeted track inspections where derailment improvements are largest.\n- Maintain the maintenance throughput that increased availability while monitoring mean time to repair.\n- Push operational changes that sustain lower terminal dwell (dispatch/ground ops).\n- Prioritize proactive inspections in categories showing month-over-month increases.")
