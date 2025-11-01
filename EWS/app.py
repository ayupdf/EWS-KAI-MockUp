import streamlit as st

# Streamlit configuration
st.set_page_config(page_title="Railway Safety Dashboard", layout="wide")

st.sidebar.success("Select a dashboard from the menu above 👆")

st.markdown("""
# 🚆 Railway Safety Dashboard

Welcome to the **Railway Safety Dashboard** — a collection of visual performance insights
covering safety, efficiency, and operational reliability metrics.

Use the **sidebar** to navigate between dashboards:
- Derailment Rate Trend  
- Locomotive Availability  
- Proactive Safety: Leading Indicators  
- On-Time Performance  
- Terminal Dwell Time Trend
""")
