
def calculate_site(
    land_ha: float,
    usable_pct: float,
    capacity_density: float,
    annual_specific_yield: float,
    losses_pct: float = 14.0,
) -> dict:
    usable_area = land_ha * usable_pct / 100.0
    capacity_kwp = usable_area * capacity_density
    annual_kwh = capacity_kwp * annual_specific_yield
    annual_mwh = annual_kwh / 1000.0
    capacity_factor = annual_kwh / (capacity_kwp * 8760.0) if capacity_kwp else 0

    return {
        "usable_area_ha": usable_area,
        "capacity_kwp": capacity_kwp,
        "annual_kwh": annual_kwh,
        "annual_mwh": annual_mwh,
        "capacity_factor_pct": capacity_factor * 100,
    }


def assess_solar_potential(annual_specific_yield: float) -> dict:
    # Screening thresholds are intentionally documented here rather than hidden.
    # They are broad prototype screening bands, not official engineering standards.
    if annual_specific_yield >= 1700:
        return {
            "label": "Good Solar Potential",
            "emoji": "🟢",
            "reason": "The PVGIS-specific yield is in the prototype's high screening band (≥ 1,700 kWh/kWp/year).",
        }
    elif annual_specific_yield >= 1300:
        return {
            "label": "Moderate Solar Potential",
            "emoji": "🟡",
            "reason": "The PVGIS-specific yield falls within the prototype's moderate screening band (1,300–1,699 kWh/kWp/year).",
        }
    return {
        "label": "Low Solar Potential",
        "emoji": "🔴",
        "reason": "The PVGIS-specific yield is below the prototype's moderate screening band (< 1,300 kWh/kWp/year).",
    }
