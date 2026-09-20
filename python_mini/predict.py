"""Predict charging time from the command line using a simple formula."""

from __future__ import annotations

import argparse
import json

from calculate_time import charging_time_minutes, format_duration

STATIONS = ["downtown", "airport", "highway", "suburban", "mall"]
CHARGERS = ["level2", "dc_fast"]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def build_result(
    hour: int,
    day: int,
    station: str,
    charger: str,
    battery: float,
    soc: float,
    target_soc: float,
    temp: float,
    occupancy: float,
) -> dict:
    result = charging_time_minutes(battery, soc, target_soc, charger, temp)

    # Small congestion adjustment: busy stations may imply slightly longer effective sessions.
    if occupancy > 75:
        result["session_duration_minutes"] = round(
            result["session_duration_minutes"] * 1.05, 1
        )
        result["occupancy_adjustment"] = 1.05
    else:
        result["occupancy_adjustment"] = 1.0

    result["human_readable"] = format_duration(result["session_duration_minutes"])
    result["context"] = {
        "hour_of_day": hour,
        "day_of_week": day,
        "station_id": station,
        "charger_type": charger,
        "vehicle_battery_kwh": battery,
        "starting_soc_pct": soc,
        "target_soc_pct": target_soc,
        "ambient_temp_c": temp,
        "station_occupancy_pct": occupancy,
    }
    return result


def interactive() -> None:
    print("\nEV Charging Time Estimator (formula-based)")
    print("Formula: time ≈ energy_needed / average_charger_power\n")

    hour = int(input("Hour of day (0-23) [18]: ") or 18)
    day = int(input("Day of week (0=Mon ... 6=Sun) [2]: ") or 2)
    station = input(f"Station {STATIONS} [downtown]: ") or "downtown"
    charger = input(f"Charger {CHARGERS} [dc_fast]: ") or "dc_fast"
    battery = float(input("Battery kWh [75]: ") or 75)
    soc = float(input("Starting SOC % [35]: ") or 35)
    target_soc = float(input("Target SOC % [80]: ") or 80)
    temp = float(input("Temperature C [18]: ") or 18)
    occupancy = float(input("Station occupancy % [50]: ") or 50)

    result = build_result(hour, day, station, charger, battery, soc, target_soc, temp, occupancy)
    print(f"\nEstimated charging time: {result['human_readable']}")
    print(f"Energy needed: {result['energy_kwh']} kWh at ~{result['average_power_kw']} kW average")
    print(
        f"Context: {DAYS[day]} {hour:02d}:00, {station}, {charger}, "
        f"{soc}% -> {target_soc}%"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Estimate EV charging time using energy/power formula"
    )
    parser.add_argument("--interactive", action="store_true", help="Run Q&A mode")
    parser.add_argument("--hour", type=int, default=18)
    parser.add_argument("--day", type=int, default=2)
    parser.add_argument("--station", choices=STATIONS, default="downtown")
    parser.add_argument("--charger", choices=CHARGERS, default="dc_fast")
    parser.add_argument("--battery", type=float, default=75)
    parser.add_argument("--soc", type=float, default=35)
    parser.add_argument("--target-soc", type=float, default=80)
    parser.add_argument("--temp", type=float, default=18)
    parser.add_argument("--occupancy", type=float, default=50)
    args = parser.parse_args()

    if args.interactive:
        interactive()
        return

    result = build_result(
        args.hour,
        args.day,
        args.station,
        args.charger,
        args.battery,
        args.soc,
        args.target_soc,
        args.temp,
        args.occupancy,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
