
import streamlit as st

st.set_page_config(
    page_title="SolarShakti | Rural Solar Assessment",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Imports that can occasionally cause deployment/import problems are kept
# after Streamlit has configured the page.
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from pvgis import get_pvgis_data
from calculations import calculate_site, assess_solar_potential

st.markdown("""
<style>
.block-container {padding-top:1.4rem;padding-bottom:2rem}
.hero {padding:1.3rem 1.5rem;border-radius:18px;background:linear-gradient(135deg,#071d2b,#0b4650);color:white;margin-bottom:1rem}
.hero h1 {margin:0;font-size:2.45rem;letter-spacing:.08em}
.hero p {margin:.3rem 0;color:#cfe9e5}
.badge {display:inline-block;margin-top:.7rem;padding:.3rem .7rem;border-radius:999px;background:#153f48;color:#9de8d4;border:1px solid #2c6870;font-size:.78rem}
.kpi {padding:1rem;border:1px solid #dce7e7;border-radius:15px;background:#fff;min-height:118px}
.kpi-label {font-size:.78rem;color:#607277;text-transform:uppercase;letter-spacing:.07em}
.kpi-value {font-size:1.7rem;font-weight:700;margin-top:.35rem;color:#0b3039}
.kpi-note {font-size:.76rem;color:#718287;margin-top:.25rem}
.future {padding:1.15rem;border-radius:16px;background:#f2f7f7;border:1px solid #d5e4e4}
.node {display:inline-block;padding:.6rem .7rem;margin:.2rem;border-radius:10px;background:white;border:1px solid #cbdcdc;font-size:.82rem}
.small {font-size:.82rem;color:#617276}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>☀️ SOLARSHAKTI</h1>
<p>Rural Solar Energy Assessment & Planning</p>
<span class="badge">Prototype — Mid-Term</span>
<div style="margin-top:.55rem;font-size:.9rem">AI-Assisted Rural Renewable Energy Planning</div>
</div>
""", unsafe_allow_html=True)

# Session state: app renders immediately without making any network call.
if "assessment" not in st.session_state:
    st.session_state.assessment = None

with st.sidebar:
    st.header("📍 Site Configuration")

    preset = st.selectbox(
        "Example Location",
        ["Rajasthan Demonstration", "Custom Location"]
    )

    if preset == "Rajasthan Demonstration":
        preset_lat, preset_lon = 26.9124, 75.7873
    else:
        preset_lat, preset_lon = 26.9124, 75.7873

    lat = st.number_input("Latitude", -90.0, 90.0, preset_lat, format="%.5f")
    lon = st.number_input("Longitude", -180.0, 180.0, preset_lon, format="%.5f")

    st.divider()
    st.header("🌱 Site Inputs")

    land = st.number_input("Available land (hectares)", 0.1, 100000.0, 5.0, 0.5)
    usable_pct = st.slider("Usable land (%)", 10, 100, 80)
    technology = st.selectbox(
        "PV technology",
        ["Crystalline Silicon", "Thin Film", "Other / Generic"]
    )
    losses = st.slider("System losses (%)", 0, 30, 14)
    efficiency = st.slider("Panel efficiency (%)", 10.0, 30.0, 20.0, 0.5)
    density = st.number_input(
        "Capacity density (kWp/hectare)",
        10.0, 500.0, 180.0, 5.0
    )

    st.caption("Assumptions are editable and are not engineering-certified.")

    assess = st.button(
        "⚡ Assess Solar Potential",
        type="primary",
        use_container_width=True
    )

if assess:
    # This is the ONLY point where PVGIS is contacted.
    with st.spinner("Retrieving PVGIS solar-resource data..."):
        result = get_pvgis_data(lat, lon, losses)

    site = calculate_site(
        land, usable_pct, density, result["annual_specific_yield"]
    )
    screening = assess_solar_potential(result["annual_specific_yield"])

    st.session_state.assessment = {
        "result": result,
        "site": site,
        "screening": screening,
        "lat": lat,
        "lon": lon,
        "land": land,
        "usable_pct": usable_pct,
        "technology": technology,
        "losses": losses,
        "efficiency": efficiency,
        "density": density,
    }

data = st.session_state.assessment

if data is None:
    st.info("👈 Configure a site in the sidebar and click **Assess Solar Potential**.")
    st.markdown("""
### SolarShakti MVP

This prototype evaluates a selected site using:

**Location → PVGIS Solar Resource → PV Calculations → Site Assessment → Dashboard**

The current version uses **physics-based PV calculations**, not AI/ML, to estimate generation.
""")
    st.divider()
    st.caption("SolarShakti — Academic PBL Prototype | Mid-Term")
    st.stop()

result = data["result"]
site = data["site"]
emoji, label, reason = data["screening"]

if result["source"] == "PVGIS":
    st.success("Live PVGIS data retrieved successfully. **Data source: PVGIS**")
else:
    st.warning(
        "PVGIS could not be reached. A clearly labelled **demo fallback dataset** is being used. "
        "No fallback value is presented as live PVGIS data."
    )
    if result.get("error"):
        with st.expander("PVGIS connection details"):
            st.code(result["error"])

st.header("Assessment Overview")

cols = st.columns(4)
cards = [
    ("Solar Yield", f"{result['annual_specific_yield']:,.0f} kWh/kWp/year", "PVGIS-specific yield"),
    ("Estimated Capacity", f"{site['capacity_kwp']:,.1f} kWp", "Preliminary capacity estimate"),
    ("Annual Generation", f"{site['annual_mwh']:,.1f} MWh/year", "Physics-based estimate"),
    ("Usable Land", f"{site['usable_area_ha']:.2f} hectares", f"{data['usable_pct']}% of available land"),
]
for col, (title, value, note) in zip(cols, cards):
    with col:
        st.markdown(
            f'<div class="kpi"><div class="kpi-label">{title}</div>'
            f'<div class="kpi-value">{value}</div><div class="kpi-note">{note}</div></div>',
            unsafe_allow_html=True
        )

st.header("☀️ Solar Resource & Generation")

months = result["monthly"]
chart_df = pd.DataFrame({
    "Month": list(months.keys()),
    "Estimated Generation (MWh)": [
        value * site["capacity_kwp"] / 1000 for value in months.values()
    ]
})

left, right = st.columns([1.5, 1])

with left:
    fig = px.bar(
        chart_df,
        x="Month",
        y="Estimated Generation (MWh)",
        title="Estimated Monthly Solar Generation"
    )
    fig.update_layout(height=400, margin=dict(l=10, r=10, t=55, b=10))
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Preliminary Site Assessment")
    st.markdown(f"## {emoji} {label}")
    st.write(reason)
    st.caption("Preliminary screening — not a final engineering feasibility assessment.")
    st.metric("Capacity Factor", f"{site['capacity_factor_pct']:.1f}%")

st.header("📍 Selected Site")

m = folium.Map(
    location=[data["lat"], data["lon"]],
    zoom_start=10,
    control_scale=True
)

popup = folium.Popup(
    f"<b>SolarShakti Site</b><br>"
    f"Latitude: {data['lat']:.5f}<br>"
    f"Longitude: {data['lon']:.5f}<br>"
    f"Estimated Capacity: {site['capacity_kwp']:.1f} kWp<br>"
    f"Annual Generation: {site['annual_mwh']:.1f} MWh/year",
    max_width=300
)

folium.Marker(
    [data["lat"], data["lon"]],
    popup=popup,
    tooltip="SolarShakti Site"
).add_to(m)

st_folium(m, height=420, use_container_width=True)

with st.expander("🧮 How was this calculated?"):
    st.markdown(f"""
### 1. Usable Area

`usable area = total land × usable percentage`

`= {data['land']:.2f} × {data['usable_pct']/100:.2f} = {site['usable_area_ha']:.2f} hectares`

### 2. Preliminary PV Capacity

`capacity = usable area × capacity density`

`= {site['usable_area_ha']:.2f} × {data['density']:.1f} = {site['capacity_kwp']:.1f} kWp`

### 3. Annual Generation

`annual generation = capacity × specific PV yield`

`= {site['capacity_kwp']:.1f} × {result['annual_specific_yield']:,.1f}`

`= {site['annual_kwh']:,.0f} kWh/year = {site['annual_mwh']:,.1f} MWh/year`

### 4. Capacity Factor

`capacity factor = annual generation / (capacity × 8760)`

`= {site['capacity_factor_pct']:.1f}%`

**Method note:** PVGIS supplies the location-specific PV performance/yield. The dashboard scales that specific yield from 1 kWp to the preliminary site capacity. Panel efficiency is displayed as an input assumption and is not double-counted against PVGIS output.
""")

st.header("🧠 Future AI/ML Planning Layer")

st.markdown("""
<div class="future">
<b>Future Development — Not Yet Implemented</b><br><br>
<span class="node">🛰️ Satellite Imagery</span> →
<span class="node">Land Cover / Remote Sensing</span> →
<span class="node">AI/ML Demand Analysis</span> →
<span class="node">Solar Resource Analysis</span> →
<span class="node">Site Suitability</span> →
<span class="node">Optimization</span> →
<span class="node">Village Priority Ranking</span>
<br><br>
<span class="small"><b>Physics-based:</b> “What can this location generate?” &nbsp; | &nbsp;
<b>Future AI/ML:</b> “Which locations should be prioritized?”</span>
</div>
""", unsafe_allow_html=True)

st.subheader("🗺️ Development Roadmap")
st.markdown("""
| Phase | Status | Scope |
|---|---|---|
| **Phase 1 — Current** | 🟢 Implemented | Solar resource assessment · PV generation estimation · Interactive dashboard |
| **Phase 2 — In Development** | 🟡 Planned | Satellite imagery analysis · Land-use classification · Energy-access prediction |
| **Phase 3 — Future** | ⚪ Planned | AI site suitability · Village prioritization · Multi-factor optimization · Grid/infrastructure constraints |
""")

with st.expander("📊 Technical Inputs"):
    st.write(f"**Data source:** {result['source']}")
    st.write(f"**PV technology:** {data['technology']}")
    st.write(f"**System losses:** {data['losses']}%")
    st.write(f"**Panel efficiency input:** {data['efficiency']}%")
    st.write(f"**Coordinates:** {data['lat']:.5f}, {data['lon']:.5f}")

st.divider()
st.caption(
    "SolarShakti is an academic prototype intended for preliminary renewable-energy assessment. "
    "Results are indicative and should not replace detailed engineering, financial, environmental, "
    "land-title, grid-connection, or feasibility studies."
)
