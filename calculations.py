
def calculate_site(land_ha, usable_pct, capacity_density, annual_specific_yield):
    usable_area = float(land_ha) * float(usable_pct) / 100
    capacity_kwp = usable_area * float(capacity_density)
    annual_kwh = capacity_kwp * float(annual_specific_yield)
    annual_mwh = annual_kwh / 1000
    capacity_factor_pct = (
        annual_kwh / (capacity_kwp * 8760) * 100
        if capacity_kwp > 0 else 0
    )

    return {
        "usable_area_ha": usable_area,
        "capacity_kwp": capacity_kwp,
        "annual_kwh": annual_kwh,
        "annual_mwh": annual_mwh,
        "capacity_factor_pct": capacity_factor_pct,
    }


def assess_solar_potential(yield_value):
    # Transparent prototype screening bands; not an official engineering standard.
    if yield_value >= 1700:
        return ("🟢", "Good Solar Potential",
                "PVGIS-specific yield is in the prototype's high screening band (≥ 1,700 kWh/kWp/year).")
    if yield_value >= 1300:
        return ("🟡", "Moderate Solar Potential",
                "PVGIS-specific yield is in the prototype's moderate screening band (1,300–1,699 kWh/kWp/year).")
    return ("🔴", "Low Solar Potential",
            "PVGIS-specific yield is below the prototype's moderate screening band (< 1,300 kWh/kWp/year).")
