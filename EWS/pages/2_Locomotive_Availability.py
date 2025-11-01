import streamlit as st
import plotly.graph_objects as go

st.markdown("### 🚂 Locomotive Availability")
st.markdown("""
This metric shows the percentage of the locomotive fleet available for service versus those down for maintenance.  
High availability is crucial for service, but must be balanced with preventative maintenance schedules.
""")

# Data
labels = ['Available', 'In Maintenance']
values = [85, 15]
colors = ['#3BA55D', '#355C7D']

# Donut Chart
fig = go.Figure(data=[go.Pie(
    labels=labels,
    values=values,
    hole=0.6,
    marker=dict(colors=colors),
    textinfo='label+percent'
)])
fig.update_layout(
    paper_bgcolor="#F8FFF9",
    font=dict(color="#2D2A70"),
    showlegend=True,
    height=400,
)
st.plotly_chart(fig, use_container_width=True)
