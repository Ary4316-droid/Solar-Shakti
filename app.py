
import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from pvgis import get_pvgis_data
from calculations import calculate_site, assess_solar_potential

st.set_page_config(
    page_title="SolarShakti | Rural Solar Assessment",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
.hero {padding: 1.2rem 1.4rem; border-radius: 18px; background: linear-gradient(135deg,#071d2b,#0b3b46); color:white; margin-bottom:1.2rem;}
.hero h1 {font-size:2.5rem; margin:0; letter-spacing:.08em;}
.hero p {margin:.35rem 0 0; color:#cfe9e5;}
.badge {display:inline-block; margin-top:.8rem; padding:.28rem .65rem; border-radius:999px; background:#163f49; color:#9de8d4; font-size:.78rem; border:1px solid #2c6870;}
.kpi {padding:1rem 1.1rem; border:1px solid #dce7e7; border-radius:15px; background:#fff; min-height:120px; box-shadow:0 2px 10px rgba(0,0,0,.035);}
.kpi-label {font-size:.8rem; color:#607277; text-transform:uppercase; letter-spacing:.07em;}
.kpi-value {font-size:1.75rem; font-weight:700; margin-top:.35rem; color:#0b3039;}
.kpi-note {font-size:.78rem; color:#718287; margin-top:.25rem;}
.section {margin-top:1.4rem;}
.future {padding:1.2rem; border-radius:16px; background:#f2f7f7; border:1px solid #d5e4e4;}
.arch {display:flex; flex-wrap:wrap; gap:.5rem; align-items:center; margin:.8rem 0;}
.node {padding:.65rem .8rem; border-radius:10px; background:white; border:1px solid #cbdcdc; font-size:.85rem; text-align:center;}
.arrow {font-weight:700; color:#789;}
.small {font-size:.82rem; color:#617276;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>☀️ SOLARSHAKTI</h1>
  <p>Rural Solar Energy Assessment & Planning</p>
  <span class="badge">Prototype — Mid-Term</span>
  <div style="margin-top:.6rem;font-size:.9rem;">AI-Assisted Rural Renewable Energy Planning</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("📍 Site Configuration")
    preset = st.selectbox("Example Village Preset", ["Custom Location", "Rajasthan Demonstration"])
    if preset == "Rajasthan Demonstration":
        default_lat, default_lon = 26.9124, 75.7873
    else:
        default_lat, default_lon = 26.9124, 75.7873

    lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=default_lat, format="%.5f")
    lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=default_lon, format="%.5f")

    st.divider()
    st.header("🌱 Site Inputs")
    land = st.number_input("Available land (hectares)", min_value=0.1, value=5.0, step=0.5)
    usable_pct = st.slider("Usable land (%)", 10, 100, 80)
    technology = st.selectbox("PV technology", ["Crystalline Silicon", "Thin Film", "Other / Generic"])
    losses = st.slider("System losses (%)", 0, 30, 14)
    efficiency = st.slider("Panel efficiency (%)", 10.0, 30.0, 20.0, 0.5)
    density = st.number_input("Capacity density (kWp/hectare)", min_value=10.0, max_value=500.0, value=180.0, step=5.0)

    st.caption("Capacity density, efficiency and losses are user assumptions. They are not engineering-certified values.")
    run = st.button("⚡ Assess Solar Potential", type="primary", use_container_width=True)

if "run" not in st.session_state:
    st.session_state.run = True
if run:
    st.session_state.run = True

if st.session_state.run:
    with st.spinner("Querying PVGIS and calculating site performance..."):
        pvgis_result = get_pvgis_data(lat, lon, losses=losses)

    if pvgis_result["source"] == "PVGIS":
        st.success("Live solar data retrieved successfully. Data source: PVGIS")
    else:
        st.warning("PVGIS could not be reached. The clearly labelled demo dataset is being used; no live data is being presented as real.")

    site = calculate_site(
        land_ha=land,
        usable_pct=usable_pct,
        capacity_density=density,
        annual_specific_yield=pvgis_result["annual_specific_yield"],
        losses_pct=losses,
    )

    assessment = assess_solar_potential(pvgis_result["annual_specific_yield"])

    st.markdown('<div class="section"><h2>Assessment Overview</h2></div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    cards = [
        ("Solar Yield", f"{pvgis_result['annual_specific_yield']:,.0f} kWh/kWp/year", "PVGIS-specific yield"),
        ("Estimated Capacity", f"{site['capacity_kwp']:,.1f} kWp", "Preliminary capacity estimate"),
        ("Annual Generation", f"{site['annual_mwh']:,.1f} MWh/year", "Physics-based estimate"),
        ("Usable Land", f"{site['usable_area_ha']:.2f} ha", f"{usable_pct}% of available land"),
    ]
    for col, (label, value, note) in zip([c1,c2,c3,c4], cards):
        with col:
            st.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-note">{note}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section"><h2>☀️ Solar Resource & Generation</h2></div>', unsafe_allow_html=True)
    left, right = st.columns([1.5, 1])

    months = pvgis_result["monthly"]
    df = pd.DataFrame({"Month": list(months.keys()), "Generation (MWh)": [v * site["capacity_kwp"] / 1000 for v in months.values()]})
    with left:
        fig = px.bar(df, x="Month", y="Generation (MWh)", title="Estimated Monthly Solar Generation")
        fig.update_layout(height=390, margin=dict(l=10,r=10,t=55,b=10))
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader("Preliminary Site Assessment")
        st.markdown(f"### {assessment['emoji']} {assessment['label']}")
        st.write(assessment["reason"])
        st.caption("Preliminary screening — not a final engineering feasibility assessment.")
        st.divider()
        st.metric("Capacity factor", f"{site['capacity_factor_pct']:.1f}%")
        st.caption("Derived from annual generation ÷ (capacity × 8,760 hours).")

    st.markdown('<div class="section"><h2>📍 Selected Site</h2></div>', unsafe_allow_html=True)
    m = folium.Map(location=[lat, lon], zoom_start=10, control_scale=True)
    popup = folium.Popup(
        f"<b>SolarShakti Site</b><br>Latitude: {lat:.5f}<br>Longitude: {lon:.5f}"
        f"<br>Estimated Capacity: {site['capacity_kwp']:.1f} kWp"
        f"<br>Annual Generation: {site['annual_mwh']:.1f} MWh/year",
        max_width=300,
    )
    folium.Marker([lat, lon], popup=popup, tooltip="SolarShakti Site").add_to(m)
    st_folium(m, height=420, use_container_width=True)

    with st.expander("🧮 How was this calculated?"):
        st.markdown(f"""
**1. Usable Area**

`usable area = total land × usable percentage`

`= {land:.2f} ha × {usable_pct/100:.2f} = {site['usable_area_ha']:.2f} ha`

**2. Preliminary PV Capacity**

`capacity = usable area × capacity density`

`= {site['usable_area_ha']:.2f} ha × {density:.1f} kWp/ha = {site['capacity_kwp']:.1f} kWp`

**3. Annual Generation**

`annual generation = capacity × PVGIS specific yield`

`= {site['capacity_kwp']:.1f} kWp × {pvgis_result['annual_specific_yield']:,.0f} kWh/kWp/year`

`= {site['annual_kwh']:,.0f} kWh/year = {site['annual_mwh']:,.1f} MWh/year`

**4. Capacity Factor**

`capacity factor = annual generation / (capacity × 8760)`

`= {site['capacity_factor_pct']:.1f}%`

**Important:** PVGIS provides the site-specific solar/PV performance information. The dashboard scales the 1 kWp-specific yield to the preliminary capacity estimate. Panel efficiency is retained as a site-input assumption but is not double-counted against PVGIS's PV performance output.
""")

    st.markdown('<div class="section"><h2>🧠 Future AI/ML Planning Layer</h2></div>', unsafe_allow_html=True)
    st.markdown("""
<div class="future">
<b>Future Development — Not Yet Implemented</b>
<div class="arch">
<div class="node">🛰️ Satellite Imagery</div><div class="arrow">→</div>
<div class="node">Land Cover / Remote Sensing Features</div><div class="arrow">→</div>
<div class="node">AI/ML Energy Access & Demand Analysis</div><div class="arrow">→</div>
<div class="node">Solar Resource Analysis</div><div class="arrow">→</div>
<div class="node">Site Suitability</div><div class="arrow">→</div>
<div class="node">Optimization</div><div class="arrow">→</div>
<div class="node">Village / Site Priority Ranking</div>
</div>
<div class="small"><b>Physics-based calculation:</b> “What can this location generate?” &nbsp; | &nbsp; <b>Future AI/ML:</b> “Which locations should be prioritized?”</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
### 🗺️ Development Roadmap

| Phase | Status | Scope |
|---|---|---|
| **Phase 1 — Current** | 🟢 Implemented | Solar resource assessment · PV generation estimation · Interactive dashboard |
| **Phase 2 — In Development** | 🟡 Planned | Satellite imagery analysis · Land-use classification · Energy-access prediction |
| **Phase 3 — Future** | ⚪ Planned | AI-based site suitability · Village prioritization · Multi-factor optimization · Infrastructure/grid constraints |
""")

    with st.expander("📊 PVGIS / Technical Data"):
        st.write(f"**Data source:** {pvgis_result['source']}")
        st.write(f"**PV technology assumption:** {technology}")
        st.write(f"**System losses:** {losses}%")
        st.write(f"**Panel efficiency input:** {efficiency}%")
        st.write(f"**Coordinates:** {lat:.5f}, {lon:.5f}")
        st.write(f"**Annual specific yield:** {pvgis_result['annual_specific_yield']:,.1f} kWh/kWp/year")

    st.divider()
    st.caption("SolarShakti is an academic prototype intended for preliminary renewable-energy assessment. Results are indicative and should not be used as a substitute for detailed engineering, financial, environmental, land-title, grid-connection, or feasibility studies.")
else:
    st.info("Configure the site in the sidebar and click **Assess Solar Potential**.")
