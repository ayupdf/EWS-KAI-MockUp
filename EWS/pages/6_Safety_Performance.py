import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ==========================================
# 🎨 WARNA & TEMA
# ==========================================
COLOR_BLUE = "#2D2A70"
COLOR_ORANGE = "#ED6B23"
COLOR_BG = "#0F172A"       # dark navy background
COLOR_TEXT = "#E2E8F0"     # light text for contrast
COLOR_CARD = "#1E293B"     # dark card background

# ==========================================
# 📊 DATA
# ==========================================
data = {
    "Quarter 1": [5, 2, 11, 8],
    "Quarter 2": [3, 1, 8, 6],
    "Quarter 3": [4, 3, 9, 7],
    "Quarter 4": [2, 1, 5, 4],
}
categories = [
    "Derailments",
    "Collisions",
    "Highway-Rail Crossing Incidents",
    "Employee Reportable Injuries"
]

# ==========================================
# ⚙️ STREAMLIT PAGE CONFIG
# ==========================================
st.set_page_config(page_title="Safety Performance Dashboard", layout="wide")

st.markdown(
    f"""
    <style>
    body {{
        background-color: {COLOR_BG};
        color: {COLOR_TEXT};
        font-family: "Inter", sans-serif;
    }}
    .title {{
        font-size: 34px;
        font-weight: 800;
        color: {COLOR_ORANGE};
        text-align: center;
        margin-bottom: 10px;
    }}
    .subtitle {{
        font-size: 16px;
        color: #94A3B8;
        text-align: center;
        margin-bottom: 40px;
    }}
    .card {{
        background-color: {COLOR_CARD};
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
        text-align: center;
    }}
    .card h3 {{
        color: {COLOR_TEXT};
        margin: 0;
        font-size: 22px;
        font-weight: 700;
    }}
    .card p {{
        color: #CBD5E1;
        font-size: 14px;
        margin-top: 6px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 🧭 HEADER
# ==========================================
st.markdown('<div class="title">Safety Performance: Lagging Indicators</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Monitoring safety incidents per quarter — lower numbers indicate better performance.</div>',
    unsafe_allow_html=True
)

# ==========================================
# 🕹️ FILTER (HARDCODED)
# ==========================================

quarter = st.selectbox("Select Quarter", options=["Quarter 1", "Quarter 2", "Quarter 3", "Quarter 4"], index=2)

df = pd.DataFrame({
    "Category": categories,
    "Value": data[quarter]
})

# Sidebar: export full dataset & options
with st.sidebar:
    st.header("Export & options")
    full_df = pd.DataFrame({"Quarter": [], "Category": [], "Value": []})
    for q, vals in data.items():
        tmp = pd.DataFrame({"Quarter": [q]*len(categories), "Category": categories, "Value": vals})
        full_df = pd.concat([full_df, tmp], ignore_index=True)
    st.download_button("Download full safety CSV", full_df.to_csv(index=False).encode('utf-8'), file_name='safety_performance_all_quarters.csv', mime='text/csv')
    show_trend = st.checkbox("Show trend across quarters", value=False)

# ==========================================
# 📈 KPI CARDS
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)
cols = st.columns(4)

for i, (category, value) in enumerate(zip(categories, data[quarter])):
    with cols[i]:
        st.markdown(
            f"""
            <div class="card">
                <h3>{value}</h3>
                <p>{category}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

# Overview metrics (total incidents this quarter, change vs previous quarter)
quarters = list(data.keys())
idx = quarters.index(quarter)
prev_q = quarters[idx-1] if idx > 0 else quarters[-1]
total = int(sum(data[quarter]))
prev_total = int(sum(data[prev_q]))
delta = total - prev_total
delta_pct = (delta / prev_total * 100) if prev_total != 0 else 0

st.markdown("---")
mc1, mc2, mc3 = st.columns([1.2,1.2,2])
with mc1:
    st.metric("Total incidents (this quarter)", value=f"{total}", delta=f"{delta:+d} ({delta_pct:+.1f}%)")
with mc2:
    top_cat = df.sort_values('Value', ascending=False).iloc[0]['Category']
    st.metric("Top category", value=top_cat)
with mc3:
    st.markdown("<div class='card'><p class='muted'>Use the trend toggle to see category-level trends across quarters. Download the full CSV for offline analysis.</p></div>", unsafe_allow_html=True)

# ==========================================
# 📊 ROUNDED BAR CHART
# ==========================================
fig = go.Figure()

colors = [COLOR_BLUE, COLOR_ORANGE, COLOR_BLUE, COLOR_ORANGE]

for cat, val, color in zip(df["Category"], df["Value"], colors):
    fig.add_trace(go.Bar(
        x=[cat],
        y=[val],
        name=cat,
        marker=dict(
            color=color,
            line=dict(width=0),
            opacity=0.9
        ),
        width=0.6,
        text=[val],
        textposition="outside",
        hovertemplate=f"<b>{cat}</b><br>Value: {val}<extra></extra>",
    ))

# Gunakan shapes untuk efek rounded bar
fig.update_traces(
    marker_line_width=0,
    hoverlabel=dict(font_size=13, font_family="Inter"),
)

fig.update_layout(
    paper_bgcolor=COLOR_BG,
    plot_bgcolor=COLOR_BG,
    font=dict(color=COLOR_TEXT, family="Inter"),
    xaxis=dict(showgrid=False, tickfont=dict(size=13)),
    yaxis=dict(showgrid=True, gridcolor="#1E293B", zeroline=False),
    margin=dict(l=40, r=40, t=40, b=40),
    showlegend=False,
    bargap=0.4,
)

# Custom rounded bar trick — gunakan layout radius (pseudo effect)
fig.update_traces(marker=dict(line=dict(width=0, color=COLOR_BG)))

st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# Optional trend chart
if 'show_trend' in locals() and show_trend:
    trend_fig = go.Figure()
    for i, cat in enumerate(categories):
        y = [data[q][i] for q in quarters]
        trend_fig.add_trace(go.Scatter(x=quarters, y=y, mode='lines+markers', name=cat, marker=dict(size=8)))
    trend_fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=COLOR_BG,
        plot_bgcolor=COLOR_BG,
        font=dict(color=COLOR_TEXT),
        height=380,
        margin=dict(l=24,r=24,t=24,b=24)
    )
    trend_fig.update_yaxes(title_text='Count')
    trend_fig.update_xaxes(title_text='Quarter')
    st.plotly_chart(trend_fig, use_container_width=True, config={"displayModeBar": False})

with st.expander('How to read this'):
    st.write('KPI cards show counts by category for the selected quarter. The total incidents metric compares to the previous quarter. Use the trend chart to observe category-level changes across quarters.')

st.caption('Chart includes hover details. For screen-reader users, top-line metrics are exposed above.')
