# SolarShakti

Rural Solar Energy Assessment & Planning — academic mid-term prototype.

## Deploy

Main Streamlit file: `app.py`

The app intentionally makes **no PVGIS network request at startup**. PVGIS is queried only after the user clicks **Assess Solar Potential**, with connection/read timeouts and a clearly labelled fallback dataset.

## Local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Method

PVGIS supplies site-specific PV yield. Preliminary capacity is calculated from usable land × editable capacity density. Annual generation is capacity × PVGIS specific yield.

AI/ML is **not implemented** in this prototype. The UI reserves a future layer for demand estimation, site suitability and prioritization.
