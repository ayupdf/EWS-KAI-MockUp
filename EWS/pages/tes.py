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
.card, .metric-card {
    background: linear-gradient(180deg,#0b0b0b 0%, #070707 100%);
    padding: 14px; border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.05);
}
.metric-label {color:#9fb0d6; font-size:13px;}
.metric-value {color:#E6EEF8; font-size:22px; font-weight:600;}
.metric-delta {color:#7ee787; font-size:13px;}
h2, h1 {color: #E6EEF8}
.muted {color: #9fb0d6}
</style>
"""
st.markdown(_CSS, unsafe_allow_html=True)

# --- HEADER ---
st.markdown("## 🧯 Proactive Safety — Leading Indicators")

# --- METRIC CARDS ---
data = pd.DataFrame({
    "provinsi": ["Jawa Barat", "Jawa Tengah", "Sumatera Utara"],
    "indikator": ["Track Defects Found", "Signal Failures", "Close Calls Reported"],
    "last_month": [120, 50, 90],
    "this_month": [130, 45, 100],
})
data["change"] = data["this_month"] - data["last_month"]
data["pct_change"] = np.where(data["last_month"] == 0, np.nan, data["change"] / data["last_month"] * 100)
data["ratio"] = np.where(data["last_month"] == 0, np.nan, data["this_month"] / data["last_month"])
data["ratio_scaled"] = (data["ratio"] / 2).clip(0, 10)

total_this = data["this_month"].sum()
total_last = data["last_month"].sum()
tot_change = total_this - total_last
tot_pct = (tot_change / total_last * 100) if total_last != 0 else np.nan
avg_ratio = data["ratio"].mean()

card1, card2, card3 = st.columns([1.5, 1.5, 3])
with card1:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Total events (This Month)</div><div class='metric-value'>{total_this}</div><div class='metric-delta'>Δ {tot_change:+d} ({tot_pct:+.1f}%)</div></div>", unsafe_allow_html=True)
with card2:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Average Ratio</div><div class='metric-value'>{avg_ratio:.2f}×</div><div class='metric-delta muted'>Across all indicators</div></div>", unsafe_allow_html=True)
with card3:
    idx_inc = data["change"].idxmax()
    idx_dec = data["change"].idxmin()
    inc_label = data.loc[idx_inc, "indikator"]
    inc_val = data.loc[idx_inc, "change"]
    dec_label = data.loc[idx_dec, "indikator"]
    dec_val = data.loc[idx_dec, "change"]
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Biggest Moving</div><div style='display:flex;gap:12px;align-items:center'><div style='flex:1'><div class='metric-value'>+{inc_val}</div><div class='muted'>{inc_label} (increase)</div></div><div style='flex:1'><div class='metric-value'>{dec_val}</div><div class='muted'>{dec_label} (decrease)</div></div></div></div>", unsafe_allow_html=True)

st.markdown("---")

# --- FILTERS ---
indicator_options = ["Track Defects Found", "Signal Failures", "Close Calls Reported"]
selected = st.multiselect("Select indicator", indicator_options, default=indicator_options)

df = data[data["indikator"].isin(selected)].copy()

# --- GEOJSON ---
geojson = requests.get("https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia-province-simple.json").json()
def _norm(s): 
    return re.sub(r'[^a-z0-9]', '', str(s).lower()) if s else ""

for feat in geojson.get('features', []):
    for v in feat.get('properties', {}).values():
        if isinstance(v, str):
            feat['id'] = _norm(v)
            break

df['geo_id'] = df['provinsi'].astype(str).apply(_norm)

# --- MERGE GEOJSON ---
provs = []
for feat in geojson.get('features', []):
    gid = feat.get('id', '')
    name = next((feat['properties'].get(k) for k in ('NAME_1', 'Propinsi', 'provinsi', 'name') if k in feat['properties']), gid)
    provs.append({'geo_id': gid, 'name': name})
all_provs = pd.DataFrame(provs)
merged = all_provs.merge(df, how='left', on='geo_id')

# --- COLOR MAP ---
prov_colors = {
    "sumaterautara": "#90EE90",
    "jawabarat": "#E5FF00",
    "jawatengah": "#FF4C4C"
}
merged["color"] = merged["geo_id"].map(prov_colors).fillna("#2f2f2f")

# --- LAYOUT: map lebar ---
col_bar, col_map = st.columns([0.6, 2.6])

# --- LEFT BAR CHART ---
with col_bar:
    bar = px.bar(
        df,
        x="ratio_scaled",
        y="provinsi",
        color="indikator",
        orientation="h",
        color_discrete_sequence=["#E5FF00", "#FF4C4C", "#00FF7F"],
        text=df["ratio_scaled"].round(2).astype(str) + "×",
    )
    bar.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E6EEF8"),
        xaxis_title="Ratio (Scaled 0–10)",
        yaxis_title="",
        xaxis=dict(range=[0, 5]),
        showlegend=False,
        height=550,
        margin=dict(l=0, r=10, t=30, b=10)
    )
    st.plotly_chart(bar, use_container_width=True)

# --- RIGHT MAP with hover info lengkap ---
with col_map:
    fig = go.Figure()

    for i, row in merged.iterrows():
        gid = row["geo_id"]
        feat = next((f for f in geojson.get('features', []) if f.get('id') == gid), None)
        if not feat:
            continue

        geom = feat.get("geometry", {})
        color = row["color"]

        # Tooltip HTML
        hovertext = (
            f"<b>{row['provinsi']}</b><br>"
            f"{row['indikator']}<br>"
            f"<b>This Month:</b> {row['this_month']} | <b>Last Month:</b> {row['last_month']}<br>"
            f"<b>Change:</b> {row['change']:+.1f} ({row['pct_change']:+.1f}%)"

        )

        poly_groups = geom.get("coordinates", [])
        if geom.get("type") == "Polygon":
            poly_groups = [poly_groups]

        for poly in poly_groups:
            exterior = poly[0]
            lons, lats = zip(*exterior)
            fig.add_trace(go.Scattermapbox(
                lon=lons, lat=lats,
                mode="lines", fill="toself",
                fillcolor=color,
                line=dict(color="white", width=1),
                hoverinfo="text",
                hovertext=hovertext,
                showlegend=False
            ))

    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            center={"lat": -2.5, "lon": 118.0},
            zoom=4.1
        ),
        height=550,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(
            bgcolor="#1a1a1a",
            font=dict(color="white"),
            bordercolor="#ffffff"
        ),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("💡 *Gunakan data nyata agar pola antar-provinsi lebih akurat. Warna tiap provinsi menggambarkan area fokus berbeda.*")
