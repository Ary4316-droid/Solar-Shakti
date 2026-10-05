
import requests

PVGIS_URL = "https://re.jrc.ec.europa.eu/api/v5_3/PVcalc"

# Clearly labelled demo values used only when the live PVGIS request fails.
DEMO_ANNUAL_YIELD = 1750.0
DEMO_MONTHLY_YIELD = {
    "Jan": 115, "Feb": 125, "Mar": 145, "Apr": 155,
    "May": 165, "Jun": 160, "Jul": 145, "Aug": 145,
    "Sep": 145, "Oct": 140, "Nov": 125, "Dec": 100,
}

def get_pvgis_data(lat: float, lon: float, losses: float = 14.0) -> dict:
    params = {
        "lat": lat,
        "lon": lon,
        "peakpower": 1,
        "loss": losses,
        "outputformat": "json",
        "pvtechchoice": "crystSi",
        "mountingplace": "free",
        "angle": 25,
        "aspect": 0,
    }
    try:
        response = requests.get(PVGIS_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        outputs = data.get("outputs", {})
        monthly_raw = outputs.get("monthly", {}).get("fixed", [])
        totals = outputs.get("totals", {})

        annual = totals.get("fixed", {}).get("E_y")
        if annual is None:
            annual = totals.get("E_y")

        monthly = {}
        for row in monthly_raw:
            month = row.get("month")
            energy = row.get("E_m")
            if month is not None and energy is not None:
                names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
                monthly[names[int(month)-1]] = float(energy)

        if annual is None or len(monthly) != 12:
            raise ValueError("PVGIS response did not contain the expected PV output fields.")

        return {
            "source": "PVGIS",
            "annual_specific_yield": float(annual),
            "monthly": monthly,
            "raw": data,
        }

    except Exception as exc:
        return {
            "source": "Demo fallback dataset",
            "annual_specific_yield": DEMO_ANNUAL_YIELD,
            "monthly": DEMO_MONTHLY_YIELD,
            "error": str(exc),
            "raw": None,
        }
