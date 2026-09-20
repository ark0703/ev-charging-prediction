"""Estimate EV charging time using energy needed and average charger power."""

from __future__ import annotations

CHARGER_AVERAGE_KW = {
    "level2": 11.0,
    "dc_fast": 120.0,
}


def thermal_efficiency(temp_c: float) -> float:
    factor = 1.0
    if temp_c < 5:
        factor -= 0.08
    if temp_c < 0:
        factor -= 0.05
    if temp_c > 32:
        factor -= 0.04
    return max(0.75, factor)


def soc_taper_factor(start_soc: float, target_soc: float, charger_type: str) -> float:
    if charger_type != "dc_fast":
        return 1.0
    if target_soc <= 80:
        return 1.0
    if start_soc >= 80:
        return 1.35
    fill_above_80 = max(0.0, target_soc - 80.0)
    fill_total = max(1.0, target_soc - start_soc)
    high_soc_share = fill_above_80 / fill_total
    return 1.0 + 0.5 * high_soc_share


def energy_needed_kwh(
    battery_kwh: float,
    starting_soc_pct: float,
    target_soc_pct: float,
    ambient_temp_c: float,
) -> float:
    if target_soc_pct <= starting_soc_pct:
        return 0.0
    delta = (target_soc_pct - starting_soc_pct) / 100.0
    return battery_kwh * delta * thermal_efficiency(ambient_temp_c)


def effective_power_kw(charger_type: str, ambient_temp_c: float) -> float:
    base = CHARGER_AVERAGE_KW[charger_type]
    if charger_type == "dc_fast" and ambient_temp_c < 5:
        base *= 0.82
    return base


def charging_time_minutes(
    battery_kwh: float,
    starting_soc_pct: float,
    target_soc_pct: float,
    charger_type: str,
    ambient_temp_c: float,
    station_occupancy_pct: float = 0.0,
) -> dict:
    energy = energy_needed_kwh(
        battery_kwh, starting_soc_pct, target_soc_pct, ambient_temp_c
    )
    power = effective_power_kw(charger_type, ambient_temp_c)
    taper = soc_taper_factor(starting_soc_pct, target_soc_pct, charger_type)

    if energy <= 0:
        return {
            "energy_kwh": 0.0,
            "average_power_kw": round(power, 1),
            "taper_factor": round(taper, 2),
            "occupancy_adjustment": 1.0,
            "session_duration_minutes": 0.0,
        }

    hours = (energy / power) * taper
    minutes = hours * 60
    occupancy_adjustment = 1.05 if station_occupancy_pct > 75 else 1.0
    minutes *= occupancy_adjustment

    return {
        "energy_kwh": round(energy, 2),
        "average_power_kw": round(power, 1),
        "taper_factor": round(taper, 2),
        "occupancy_adjustment": occupancy_adjustment,
        "session_duration_minutes": round(minutes, 1),
    }


def format_duration(minutes: float) -> str:
    total = max(0, int(round(minutes)))
    hours, mins = divmod(total, 60)
    if hours:
        return f"{hours}h {mins}m ({total} minutes)"
    return f"{mins}m ({total} minutes)"
