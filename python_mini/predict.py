"""Predict charging session duration from the command line."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd

STATIONS = ["downtown", "airport", "highway", "suburban", "mall"]
CHARGERS = ["level2", "dc_fast"]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def format_duration(minutes: float) -> str:
    total = max(0, int(round(minutes)))
    hours, mins = divmod(total, 60)
    if hours:
        return f"{hours}h {mins}m ({total} minutes)"
    return f"{mins}m ({total} minutes)"


def predict(
    model_path: Path,
    hour: int,
    day: int,
    station: str,
    charger: str,
    battery: float,
    soc: float,
    target_soc: float,
    temp: float,
    occupancy: float,
) -> float:
    model = joblib.load(model_path)
    row = pd.DataFrame(
        [
            {
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
        ]
    )
    return float(model.predict(row)[0])


def interactive(model_path: Path) -> None:
    print("\nEV Charging Time Predictor (Python mini project)")
    print("Enter values, or press Enter to keep the default in [brackets].\n")

    hour = int(input("Hour of day (0-23) [18]: ") or 18)
    day = int(input("Day of week (0=Mon ... 6=Sun) [2]: ") or 2)
    station = input(f"Station {STATIONS} [downtown]: ") or "downtown"
    charger = input(f"Charger {CHARGERS} [dc_fast]: ") or "dc_fast"
    battery = float(input("Battery kWh [75]: ") or 75)
    soc = float(input("Starting SOC % [35]: ") or 35)
    target_soc = float(input("Target SOC % [80]: ") or 80)
    temp = float(input("Temperature C [18]: ") or 18)
    occupancy = float(input("Station occupancy % [50]: ") or 50)

    minutes = predict(
        model_path, hour, day, station, charger, battery, soc, target_soc, temp, occupancy
    )
    print(f"\nPredicted charging time: {format_duration(minutes)}")
    print(
        f"Context: {DAYS[day]} {hour:02d}:00, {station}, {charger}, "
        f"battery {battery} kWh, {soc}% -> {target_soc}%"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Predict EV charging session duration")
    parser.add_argument("--model", type=Path, default=Path("models/model.joblib"))
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

    if not args.model.exists():
        raise SystemExit("Model not found. Run: python train.py")

    if args.interactive:
        interactive(args.model)
        return

    minutes = predict(
        args.model,
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
    print(
        json.dumps(
            {
                "predicted_session_duration_minutes": round(minutes, 1),
                "human_readable": format_duration(minutes),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
