
import requests

PVGIS_URL = "https://re.jrc.ec.europa.eu/api/v5_3/PVcalc"

DEMO_ANNUAL_YIELD = 1750.0
DEMO_MONTHLY_YIELD = {
    "Jan": 115.0, "Feb": 125.0, "Mar": 145.0, "Apr": 155.0,
    "May": 165.0, "Jun": 160.0, "Jul": 145.0, "Aug": 145.0,
    "Sep": 145.0, "Oct": 140.0, "Nov": 125.0, "Dec": 100.0,
}

def demo_data():
    return {
        "source": "Demo fallback dataset",
        "annual_specific_yield": DEMO_ANNUAL_YIELD,
        "monthly": DEMO_MONTHLY_YIELD.copy(),
        "error": None,
    }

def get_pvgis_data(lat: float, lon: float, losses: float = 14.0) -> dict:
    """Fetch PVGIS data only when explicitly requested by the user."""
    params = {
        "lat": float(lat),
        "lon": float(lon),
        "peakpower": 1,
        "loss": float(losses),
        "outputformat": "json",
        "pvtechchoice": "crystSi",
        "mountingplace": "free",
        "angle": 25,
        "aspect": 0,
    }

    try:
        response = requests.get(
            PVGIS_URL,
            params=params,
            timeout=(5, 12),  # connect timeout, read timeout
            headers={"User-Agent": "SolarShakti-Academic-Prototype/1.0"},
        )
        response.raise_for_status()
        data = response.json()

        outputs = data.get("outputs", {})
        totals = outputs.get("totals", {})
        fixed_total = totals.get("fixed", {})
        annual = fixed_total.get("E_y")

        monthly_raw = outputs.get("monthly", {}).get("fixed", [])
        names = ["Jan","Feb","Mar","Apr","May","Jun",
                 "Jul","Aug","Sep","Oct","Nov","Dec"]
        monthly = {}

        for row in monthly_raw:
            month = int(row["month"])
            energy = float(row["E_m"])
            if 1 <= month <= 12:
                monthly[names[month - 1]] = energy

        if annual is None or len(monthly) != 12:
            raise ValueError("PVGIS returned an unexpected response format.")

        return {
            "source": "PVGIS",
            "annual_specific_yield": float(annual),
            "monthly": monthly,
            "error": None,
        }

    except Exception as exc:
        fallback = demo_data()
        fallback["error"] = str(exc)
        return fallback
