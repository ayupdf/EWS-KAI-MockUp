import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# Page title
st.markdown("### 🚄 Derailment Rate Trend")
st.markdown("""
Tracking derailments per million train-miles over the last 12 months helps identify seasonal or operational trends.  
A **downward trend** is the goal, indicating systemic safety improvements.
""")

# Mock data
months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
values = [0.45,0.43,0.41,0.39,0.36,0.38,0.40,0.37,0.35,0.33,0.30,0.28]

# Plotly chart
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=months, y=values, mode='lines+markers',
    line=dict(color="#ED6B23", width=4),
    fill='tozeroy', fillcolor='rgba(237,107,35,0.1)',
    name="Rate per Million Train-Miles"
))
fig.update_layout(
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFF7F2",
    font=dict(color="#2D2A70", size=14),
    margin=dict(l=40,r=40,t=30,b=30),
    height=400,
    showlegend=True,
)
st.plotly_chart(fig, use_container_width=True)
