import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# ==========================================
# 🎨 WARNA & TEMA
# ==========================================
COLOR_BLUE = "#2D2A70"
COLOR_ORANGE = "#ED6B23"
COLOR_BG = "#0F172A"       # dark navy background
COLOR_TEXT = "#E2E8F0"     # light text for contrast
COLOR_CARD = "#1E293B"     # dark card background
COLOR_BORDER = "#E5E7EB"       # Soft border gray
COLOR_PRIMARY = "#2F3E9E"      # Deep corporate blue
COLOR_ACCENT = "#F59E0B"       # Warm amber
# COLOR_BG = "#F9FAFB"           # Off-white background
# COLOR_TEXT = "#1E293B"         # Rich dark gray-blue
# COLOR_CARD = "#FFFFFF"         # Pure white cards
# COLOR_BORDER = "#E5E7EB"       # Soft border gray
COLOR_MUTED = "#64748B"        # Muted gray for subtitles

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

# ==========================================
# 📉 KPI METRICS (summary)
# ==========================================
quarters = list(data.keys())
idx = quarters.index(quarter)
prev_q = quarters[idx-1] if idx > 0 else quarters[-1]
total = int(sum(data[quarter]))
prev_total = int(sum(data[prev_q]))
delta = total - prev_total
delta_pct = (delta / prev_total * 100) if prev_total != 0 else 0

st.markdown("---")

# --- Metric section (clean + responsive) ---
mc1, mc2, mc3 = st.columns([1.2, 1.5, 2])

# 💡 Custom style biar metric keliatan kayak card elegan
metric_style = """
<style>
.metric-card {
    background: linear-gradient(180deg,#0f1724 0%, #0b1220 100%);
    padding: 14px 16px;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.04);
    box-shadow: 0 6px 20px rgba(2,6,23,0.5);
    text-align: center;
}
.metric-label {
    color: #9fb0d6;
    font-size: 13px;
    letter-spacing: 0.3px;
}
.metric-value {
    color: #E6EEF8;
    font-weight: 600;
    font-size: 22px;
}
.metric-delta {
    font-size: 13px;
    color: #39D98A;
}
@media (max-width: 768px) {
    .metric-card { margin-bottom: 12px; }
}
</style>
"""
st.markdown(metric_style, unsafe_allow_html=True)

# --- Metric 1: total incidents ---
with mc1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total incidents (this quarter)</div>
        <div class="metric-value">{total}</div>
        <div class="metric-delta">{delta:+d} ({delta_pct:+.1f}%)</div>
    </div>
    """, unsafe_allow_html=True)

# --- Metric 2: top category (auto wrap) ---
with mc2:
    top_cat = df.sort_values('Value', ascending=False).iloc[0]['Category']
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Top category</div>
        <div class="metric-value" style="white-space:normal; word-wrap:break-word;">
            {top_cat}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Metric 3: contextual note ---
with mc3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Data note</div>
        <div class="metric-value" style="font-size:14px; font-weight:400; color:#9fb0d6;">
            Use the trend toggle to explore category-level changes. Download CSV for detailed analysis.
        </div>
    </div>
    """, unsafe_allow_html=True)
# ==========================================
# 📊 MAIN BAR CHART — Gradient & Polished Style
# ==========================================
fig = go.Figure()

# Warna utama yang harmonis
colors = [
    "#3B82F6",  # blue
    "#F59E0B",  # amber
    "#60A5FA",  # light blue
    "#A78BFA"   # violet
]

# Tambahkan trace dengan efek gradient dan label rapi
for cat, val, color in zip(df["Category"], df["Value"], colors):
    fig.add_trace(go.Bar(
        x=[cat],
        y=[val],
        text=[val],
        textposition="outside",
        marker=dict(
            color=color,
            line=dict(color="rgba(0,0,0,0.05)", width=1),
            pattern=dict(shape=""),
        ),
        hovertemplate=f"<b>{cat}</b><br>Count: {val}<extra></extra>"
    ))

# Layout bergaya light corporate
fig.update_layout(
    template='plotly_dark',
    paper_bgcolor=COLOR_BG,
    plot_bgcolor=COLOR_BG,
    font=dict(family="Inter, sans-serif", color=COLOR_TEXT, size=13),
    height=420,
    margin=dict(l=40, r=30, t=10, b=60),
    showlegend=False,
    hovermode="x unified",
    bargap=0.35,
    xaxis=dict(
        showline=False,
        showgrid=False,
        tickfont=dict(size=12, color=COLOR_TEXT),
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="#1E293B",
        zeroline=False,
        tickfont=dict(size=12, color=COLOR_TEXT),
        title="Number of Incidents",
    ),
)

# Masukkan chart ke dalam card
# (Chart will be rendered below via the visualization mode selector)

# --- Improved insights & 3D visualization ---
st.markdown("---")

# Insights: per-category change vs previous quarter
prev_vals = data[prev_q]
changes = [curr - prev for curr, prev in zip(data[quarter], prev_vals)]
pct_changes = [((c - p) / p * 100) if p != 0 else 0 for c, p in zip(data[quarter], prev_vals)]
insights = pd.DataFrame({"Category": categories, "Current": data[quarter], "Previous": prev_vals, "Change": changes, "PctChange": pct_changes})
insights_sorted = insights.sort_values('Change', ascending=False).reset_index(drop=True)

ins_col1, ins_col2, ins_col3 = st.columns([1,1,2])
with ins_col1:
    best = insights_sorted.iloc[0]
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Largest decrease</div><div class='metric-value'>{best['Category']}</div><div class='metric-delta'>{best['Change']:+d}</div></div>", unsafe_allow_html=True)
with ins_col2:
    worst = insights_sorted.iloc[-1]
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Largest increase</div><div class='metric-value'>{worst['Category']}</div><div class='metric-delta'>{worst['Change']:+d}</div></div>", unsafe_allow_html=True)
with ins_col3:
    avg_change = insights['Change'].mean()
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Average change</div><div class='metric-value'>{avg_change:.1f}</div><div class='metric-delta'>vs prev quarter</div></div>", unsafe_allow_html=True)

# Visualization mode: 2D bar, heatmap, or 3D surface
viz_mode = st.selectbox('Visualization mode', options=['Category Breakdown (Bar)', 'Heatmap (All Quarters)', '3D Surface (Quarters vs Categories)'])

# Prepare matrix z (categories x quarters)
z = np.array([data[q] for q in quarters]).T  # shape (n_categories, n_quarters)

if viz_mode == 'Category Breakdown (Bar)':
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key='safety_bar')

elif viz_mode == 'Heatmap (All Quarters)':
    heat = go.Figure(data=go.Heatmap(z=z, x=quarters, y=categories, colorscale='Viridis', reversescale=False))
    heat.update_layout(template='plotly_dark', paper_bgcolor=COLOR_BG, plot_bgcolor=COLOR_BG, font=dict(color=COLOR_TEXT), height=420, margin=dict(l=40,r=40,t=30,b=40))
    heat.update_xaxes(side='bottom')
    st.plotly_chart(heat, use_container_width=True, config={"displayModeBar": False}, key='safety_heat')

else:
    # 3D surface
    x = np.arange(len(quarters))
    y = np.arange(len(categories))
    surf = go.Figure(data=[go.Surface(z=z, x=x, y=y, colorscale='Viridis', showscale=True)])
    surf.update_layout(template='plotly_dark', paper_bgcolor=COLOR_BG, plot_bgcolor=COLOR_BG, font=dict(color=COLOR_TEXT), height=520, margin=dict(l=40,r=40,t=40,b=40))
    # map axis ticks to labels
    surf.update_layout(scene=dict(
        xaxis=dict(title='Quarter', tickmode='array', tickvals=list(x), ticktext=quarters),
        yaxis=dict(title='Category', tickmode='array', tickvals=list(y), ticktext=categories),
        zaxis=dict(title='Count')
    ))
    # camera
    surf.update_layout(scene_camera=dict(eye=dict(x=1.6, y=1.6, z=0.8)))
    st.plotly_chart(surf, use_container_width=True, config={"displayModeBar": True}, key='safety_surface')

with st.expander('How to read these visuals'):
    st.write('Use the visualization mode to switch between a 2D bar chart, a heatmap showing counts by category/quarter, and an interactive 3D surface for spatial understanding. Download the CSV for raw numbers. Hover to see exact values; rotate the 3D plot to inspect peaks.')

st.caption('Top insights computed above highlight the categories with the largest changes vs the previous quarter.')

# ==========================================
# 📊 MAIN BAR CHART — Polished Light Corporate Style
# ==========================================

chart_style = f"""
<style>
.chart-card {{
    background: linear-gradient(180deg, #FFFFFF 0%, #F9FAFB 100%);
    border-radius: 18px;
    border: 1px solid {COLOR_BORDER};
    box-shadow: 0 4px 20px rgba(0,0,0,0.04);
    padding: 28px 32px;
    margin-top: 22px;
    transition: all 0.3s ease;
}}
.chart-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 8px 28px rgba(0,0,0,0.08);
}}
.chart-title {{
    font-size: 20px;
    font-weight: 700;
    color: {COLOR_PRIMARY};
    letter-spacing: 0.3px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}}
.chart-title::before {{
    content: "";
    display: inline-block;
    width: 8px;
    height: 24px;
    border-radius: 4px;
    background: linear-gradient(180deg, {COLOR_PRIMARY} 0%, {COLOR_ACCENT} 100%);
}}
.chart-subtitle {{
    font-size: 14px;
    color: {COLOR_MUTED};
    margin-bottom: 12px;
}}
@media (max-width: 768px) {{
    .chart-card {{ padding: 20px 18px; }}
    .chart-title {{ font-size: 16px; }}
}}
</style>
"""
st.markdown(chart_style, unsafe_allow_html=True)

# --- Softer, modern corporate palette ---
colors = [
    "rgba(47,62,158,0.85)",   # Corporate Blue
    "rgba(245,158,11,0.85)",  # Amber
    "rgba(59,130,246,0.85)",  # Sky blue
    "rgba(139,92,246,0.85)"   # Violet
]

fig = go.Figure()
for cat, val, color in zip(df["Category"], df["Value"], colors):
    fig.add_trace(go.Bar(
        x=[cat],
        y=[val],
        name=cat,
        marker=dict(
            color=color,
            line=dict(color="rgba(0,0,0,0.05)", width=1)
        ),
        text=[val],
        textposition="outside",
        hovertemplate=f"<b>{cat}</b><br>Value: {val}<extra></extra>",
    ))

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#FFFFFF",
    font=dict(color=COLOR_TEXT, family="Inter"),
    margin=dict(l=30, r=30, t=20, b=40),
    showlegend=False,
    bargap=0.3,
    height=400,
    hovermode="x unified",
    xaxis=dict(
        showgrid=False,
        tickfont=dict(size=13, color=COLOR_TEXT),
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="rgba(0,0,0,0.08)",
        zeroline=False,
        tickfont=dict(size=12, color=COLOR_MUTED),
    ),
)

# ==========================================
# 📈 TREND CHART — Light Minimal Line Style
# ==========================================
if show_trend:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.markdown("<div class='chart-title'>📈 Trend by Quarter</div>", unsafe_allow_html=True)

    trend_fig = go.Figure()
    palette = colors
    for i, cat in enumerate(categories):
        y = [data[q][i] for q in quarters]
        trend_fig.add_trace(go.Scatter(
            x=quarters,
            y=y,
            mode='lines+markers',
            name=cat,
            marker=dict(size=7, color=palette[i % len(palette)],
                        line=dict(color="#FFFFFF", width=0.8)),
            line=dict(width=3, color=palette[i % len(palette)], shape='spline'),
            hovertemplate=f"<b>{cat}</b><br>%{{x}}: %{{y}}<extra></extra>",
        ))

    trend_fig.update_layout(
        paper_bgcolor=COLOR_BG,
        plot_bgcolor=COLOR_BG,
        template='plotly_dark',
        font=dict(color=COLOR_TEXT, family="Inter"),
        height=380,
        margin=dict(l=24, r=24, t=20, b=30),
        hovermode="x unified",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.05,
            xanchor="right", x=1, font=dict(size=11, color=COLOR_MUTED)
        ),
    )
    trend_fig.update_yaxes(title_text='Count', gridcolor="rgba(0,0,0,0.06)")
    trend_fig.update_xaxes(title_text='Quarter', showgrid=False)
    st.plotly_chart(trend_fig, use_container_width=True, config={"displayModeBar": False}, key='safety_trend')
    st.markdown("</div>", unsafe_allow_html=True)