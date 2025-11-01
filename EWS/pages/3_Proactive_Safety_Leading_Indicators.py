import streamlit as st
import plotly.graph_objects as go

st.markdown("### 🧯 Proactive Safety: Leading Indicators")
st.markdown("""
Leading indicators measure proactive efforts to prevent incidents.  
This chart compares the volume of reported defects, failures, and close calls **this month vs last month.**
""")

# Data
categories = ["Track Defects Found", "Signal Failures", "Close Calls Reported"]
last_month = [120, 50, 90]
this_month = [130, 45, 100]

fig = go.Figure()
fig.add_trace(go.Bar(
    x=categories, y=last_month, name="Last Month",
    marker_color="#2D2A70"
))
fig.add_trace(go.Bar(
    x=categories, y=this_month, name="This Month",
    marker_color="#3BA55D"
))
fig.update_layout(
    barmode='group',
    paper_bgcolor="#F7FCFB",
    plot_bgcolor="#FFFFFF",
    font=dict(color="#2D2A70", size=14),
    showlegend=True,
    margin=dict(l=40,r=40,t=30,b=30),
    height=400
)
st.plotly_chart(fig, use_container_width=True)
