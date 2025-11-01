import streamlit as st
import plotly.graph_objects as go

st.markdown("### 🚉 Terminal Dwell Time Trend")
st.markdown("""
This chart shows the **average dwell time (in hours)** a freight car spends idle at a terminal.  
Reducing dwell time improves asset utilization, network velocity, and service speed.
""")

# Data
months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
values = [27.5,27.8,27.6,26.9,26.4,25.8,25.0,24.7,24.3,23.9,23.7,23.5]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=months, y=values,
    mode='lines+markers',
    line=dict(color="#FFB300", width=4),
    fill='tozeroy', fillcolor='rgba(255,179,0,0.1)',
    name="Average Dwell (Hours)"
))
fig.update_layout(
    paper_bgcolor="#FFFDF5",
    plot_bgcolor="#FFFDF5",
    font=dict(color="#2D2A70", size=14),
    margin=dict(l=40,r=40,t=30,b=30),
    height=400,
    showlegend=True
)
st.plotly_chart(fig, use_container_width=True)
