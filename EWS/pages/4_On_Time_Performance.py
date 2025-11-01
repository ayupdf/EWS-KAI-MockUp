import streamlit as st

st.markdown("### ⏱️ On-Time Performance")
st.markdown("""
The percentage of shipments delivered within the scheduled window.  
This is a key driver of customer satisfaction and network efficiency.
""")

# KPI Display
st.markdown("""
<div style='background-color:#EEF2FF; padding:40px; border-radius:14px; text-align:center;'>
    <h1 style='color:#2D2A70; font-size:64px; margin:0;'>92.5%</h1>
    <p style='color:#475569; font-size:20px; margin-top:8px;'>Target: 90%</p>
</div>
""", unsafe_allow_html=True)
