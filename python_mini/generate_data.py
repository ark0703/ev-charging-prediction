"""Create synthetic EV charging sessions for supervised learning."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

STATIONS = ["downtown", "airport", "highway", "suburban", "mall"]
CHARGERS = ["level2", "dc_fast"]
RNG = np.random.default_rng(42)


def _thermal_factor(temp_c: float) -> float:
    factor = 1.0
    if temp_c < 5:
        factor -= 0.08
    if temp_c < 0:
        factor -= 0.05
    if temp_c > 32:
        factor -= 0.04
    return max(0.75, factor)


def _average_power_kw(charger_type: str, temp_c: float) -> float:
    if charger_type == "dc_fast":
        power = RNG.uniform(85, 145)
        power *= _thermal_factor(temp_c)
        return power
    return 11 * RNG.uniform(0.88, 1.0)


def generate_rows(count: int) -> pd.DataFrame:
    hours = RNG.integers(0, 24, size=count)
    days = RNG.integers(0, 7, size=count)
    stations = RNG.choice(STATIONS, size=count)
    chargers = RNG.choice(CHARGERS, size=count, p=[0.6, 0.4])
    battery = RNG.uniform(45, 100, size=count)
    start_soc = RNG.uniform(10, 75, size=count)
    target_soc = RNG.uniform(75, 95, size=count)
    temp = RNG.normal(18, 8, size=count).clip(-5, 38)
    occupancy = RNG.beta(2, 2.5, size=count) * 100

    durations = []
    for i in range(count):
        end_soc = max(start_soc[i] + 5, target_soc[i])
        energy_needed = battery[i] * (end_soc - start_soc[i]) / 100
        energy_needed *= _thermal_factor(temp[i])

        avg_power = _average_power_kw(chargers[i], temp[i])
        minutes = (energy_needed / avg_power) * 60

        if chargers[i] == "level2":
            minutes *= RNG.uniform(0.75, 1.05)
        else:
            minutes *= RNG.uniform(0.92, 1.08)

        if occupancy[i] > 70:
            minutes *= RNG.uniform(1.02, 1.08)

        minutes += RNG.normal(0, 4)
        durations.append(float(np.clip(minutes, 8, 240)))

    return pd.DataFrame(
        {
            "hour_of_day": hours,
            "day_of_week": days,
            "station_id": stations,
            "charger_type": chargers,
            "vehicle_battery_kwh": battery.round(1),
            "starting_soc_pct": start_soc.round(1),
            "target_soc_pct": target_soc.round(1),
            "ambient_temp_c": temp.round(1),
            "station_occupancy_pct": occupancy.round(1),
            "session_duration_minutes": np.round(durations, 1),
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=5000)
    parser.add_argument("--output", type=Path, default=Path("data/sessions.csv"))
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    df = generate_rows(args.rows)
    df.to_csv(args.output, index=False)
    print(f"Saved {len(df):,} rows to {args.output}")


if __name__ == "__main__":
    main()
