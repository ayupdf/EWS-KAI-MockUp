import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import requests
import re
import json

# --- PAGE CONFIG ---
st.set_page_config(page_title="Proactive Safety — Leading Indicators", layout="wide")

# --- CUSTOM DARK THEME CSS ---
_CSS = """
<style>
body {font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;}
.stApp { background: #000000; color: #E6EEF8; }
.card, .metric-card {background: linear-gradient(180deg,#0b0b0b 0%, #070707 100%);
    padding: 14px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05);}
.metric-label {color:#9fb0d6; font-size:13px;}
.metric-value {color:#E6EEF8; font-size:22px; font-weight:600;}
.metric-delta {color:#7ee787; font-size:13px;}
h2, h1 {color: #E6EEF8}
.muted {color: #9fb0d6}
</style>
"""
st.markdown(_CSS, unsafe_allow_html=True)

# --- HEADER ---
st.markdown("## 🧯 Proactive Safety — Leading Indicators (Peta Indonesia)")

# --- METRIC CARDS SECTION ---
data = pd.DataFrame({
    "provinsi": ["Jawa Barat", "Jawa Tengah", "Sumatera Utara"],
    "indikator": ["Track Defects Found", "Signal Failures", "Close Calls Reported"],
    "last_month": [120, 50, 90],
    "this_month": [130, 45, 100],
})
data["change"] = data["this_month"] - data["last_month"]
data["pct_change"] = np.where(data["last_month"]==0, np.nan, data["change"] / data["last_month"] * 100)
data["ratio"] = np.where(data["last_month"]==0, np.nan, data["this_month"] / data["last_month"])

total_this = data["this_month"].sum()
total_last = data["last_month"].sum()
tot_change = total_this - total_last
tot_pct = (tot_change / total_last *100) if total_last!=0 else np.nan
avg_ratio = data["ratio"].mean()

card1, card2, card3 = st.columns([1.5, 1.5, 3])
with card1:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Total events (bulan ini)</div><div class='metric-value'>{total_this}</div><div class='metric-delta'>Δ {tot_change:+d} ({tot_pct:+.1f}%)</div></div>", unsafe_allow_html=True)
with card2:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Rata-rata rasio</div><div class='metric-value'>{avg_ratio:.2f}×</div><div class='metric-delta muted'>Across all indicators</div></div>", unsafe_allow_html=True)
with card3:
    idx_inc = data["change"].idxmax()
    idx_dec = data["change"].idxmin()
    inc_label = data.loc[idx_inc, "indikator"]
    inc_val = data.loc[idx_inc, "change"]
    dec_label = data.loc[idx_dec, "indikator"]
    dec_val = data.loc[idx_dec, "change"]
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Pergerakan terbesar</div><div style='display:flex;gap:12px;align-items:center'><div style='flex:1'><div class='metric-value'>+{inc_val}</div><div class='muted'>{inc_label} (naik)</div></div><div style='flex:1'><div class='metric-value'>{dec_val}</div><div class='muted'>{dec_label} (turun)</div></div></div></div>", unsafe_allow_html=True)

st.markdown("---")

# --- FILTERS ---
indicator_options = ["Track Defects Found", "Signal Failures", "Close Calls Reported"]
selected = st.multiselect("Pilih indikator", indicator_options, default=indicator_options)
show_pct = st.checkbox("Tampilkan rasio di peta", value=True)

df = data[data["indikator"].isin(selected)].copy()

# --- GEOJSON SETUP ---
geojson = requests.get("https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia-province-simple.json").json()
def _norm(s): return re.sub(r'[^a-z0-9]', '', str(s).lower()) if s else ""

for feat in geojson.get('features', []):
    for v in feat.get('properties', {}).values():
        if isinstance(v, str):
            feat['id'] = _norm(v)
            break

df['geo_id'] = df['provinsi'].astype(str).apply(_norm)

# --- BUILD FULL PROVINCE MAP BASE ---
provs = []
for feat in geojson.get('features', []):
    gid = feat.get('id', '')
    name = next((feat['properties'].get(k) for k in ('NAME_1','Propinsi','provinsi','name') if k in feat['properties']), gid)
    provs.append({'geo_id': gid, 'name': name})
all_provs = pd.DataFrame(provs)

merged = all_provs.merge(df, how='left', on='geo_id')

# --- COLOR SETTINGS ---
highlight_colors = {
    "Track Defects Found": "#00BFFF",
    "Signal Failures": "#FF4C4C",
    "Close Calls Reported": "#00FF7F"
}

merged["color"] = merged["indikator"].map(highlight_colors)

# --- LAYOUT: SPLIT BETWEEN BAR AND MAP ---
col_bar, col_map = st.columns([0.6, 3])

# --- LEFT: COMPACT / SLIM RATIO LIST ---
with col_bar:
    st.markdown("### 📊 Ratio (compact)")
    province_colors = {
        "Jawa Barat": "#0077FF",
        "Jawa Tengah": "#FF3333",
        "Sumatera Utara": "#7FFF7F",
    }
    df['prov_color'] = df['provinsi'].map(province_colors).fillna('#6e6e6e')

    mini = px.bar(
        df.sort_values('ratio', ascending=True),
        x='ratio',
        y='provinsi',
        orientation='h',
        color='provinsi',
        color_discrete_map=province_colors,
        text=df['ratio'].round(2).astype(str) + '×',
        height=180,
    )
    mini.update_traces(marker_line_width=0, textposition='outside')
    mini.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=6, b=6),
        xaxis=dict(title='Ratio (This / Last Month)', showgrid=False),
        yaxis=dict(title='', showticklabels=True),
        showlegend=False,
        font=dict(color='#E6EEF8')
    )
    st.plotly_chart(mini, use_container_width=True)

# --- RIGHT: MAP with fixed province colors (no gradient, no borders, no legend) ---
with col_map:
    merged["value"] = merged["ratio"].fillna(0) if show_pct else merged["this_month"].fillna(0)

    def _hex_to_rgba(hex_color, alpha=0.95):
        h = hex_color.lstrip('#')
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f'rgba({r},{g},{b},{alpha})'

    province_colors_norm = {
        'jawabarat': '#0077FF',
        'jawatengah': '#FF3333',
        'sumaterautara': '#7FFF7F'
    }

    fig = go.Figure()

    highlighted = merged[merged['provinsi'].notna()].reset_index(drop=True)
    for i, row in highlighted.iterrows():
        gid = row['geo_id']
        feat = next((f for f in geojson.get('features', []) if f.get('id') == gid), None)
        if not feat:
            continue
        geom = feat.get('geometry', {})
        color = province_colors_norm.get(gid, row.get('color', '#7f7f7f'))
        fillcolor = _hex_to_rgba(color, alpha=0.95)

        poly_groups = geom.get('coordinates', [])
        if geom.get('type') == 'Polygon':
            poly_groups = [poly_groups]
        for poly in poly_groups:
            exterior = poly[0]
            try:
                lons, lats = zip(*exterior)
            except Exception:
                continue
            fig.add_trace(go.Scattermapbox(
                lon=lons, lat=lats,
                mode='none',
                fill='toself',
                fillcolor=fillcolor,
                line=dict(color='rgba(0,0,0,0)', width=0),
                hoverinfo='text',
                hovertext=row.get('provinsi', ''),
                showlegend=False
            ))

    # paint other provinces muted for context
    others = merged[merged['provinsi'].isna()].reset_index(drop=True)
    for i, row in others.iterrows():
        gid = row['geo_id']
        feat = next((f for f in geojson.get('features', []) if f.get('id') == gid), None)
        if not feat:
            continue
        geom = feat.get('geometry', {})
        poly_groups = geom.get('coordinates', [])
        if geom.get('type') == 'Polygon':
            poly_groups = [poly_groups]
        for poly in poly_groups:
            exterior = poly[0]
            try:
                lons, lats = zip(*exterior)
            except Exception:
                continue
            fig.add_trace(go.Scattermapbox(
                lon=lons, lat=lats,
                mode='none',
                fill='toself',
                fillcolor='rgba(48,48,48,0.95)',
                line=dict(color='rgba(0,0,0,0)', width=0),
                hoverinfo='none',
                showlegend=False
            ))

    fig.update_layout(
        mapbox=dict(style='open-street-map', center={'lat': -2.5, 'lon': 118.0}, zoom=4),
        height=720, margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("💡 *Gunakan data nyata agar pola antar-provinsi lebih akurat. Warna tiap indikator menggambarkan area fokus investigasi berbeda.*")
