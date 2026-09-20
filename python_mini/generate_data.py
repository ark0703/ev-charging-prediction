"""Create synthetic EV charging sessions for supervised learning."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

STATIONS = ["downtown", "airport", "highway", "suburban", "mall"]
CHARGERS = ["level2", "dc_fast"]
RNG = np.random.default_rng(42)


def generate_rows(count: int) -> pd.DataFrame:
    hours = RNG.integers(0, 24, size=count)
    days = RNG.integers(0, 7, size=count)
    stations = RNG.choice(STATIONS, size=count)
    chargers = RNG.choice(CHARGERS, size=count, p=[0.6, 0.4])
    battery = RNG.uniform(45, 100, size=count)
    start_soc = RNG.uniform(10, 75, size=count)
    temp = RNG.normal(18, 8, size=count).clip(-5, 38)
    occupancy = RNG.beta(2, 2.5, size=count) * 100

    energy = []
    for i in range(count):
        needed = battery[i] * (1 - start_soc[i] / 100)
        if chargers[i] == "level2":
            needed *= RNG.uniform(0.5, 0.9)
        if hours[i] in (8, 9, 17, 18, 19):
            needed *= 1.1
        if days[i] >= 5:
            needed *= 1.08
        needed *= 1 - 0.06 * (occupancy[i] / 100)
        needed += RNG.normal(0, 2)
        energy.append(max(2, min(needed, battery[i] * 0.95)))

    return pd.DataFrame(
        {
            "hour_of_day": hours,
            "day_of_week": days,
            "station_id": stations,
            "charger_type": chargers,
            "vehicle_battery_kwh": battery.round(1),
            "starting_soc_pct": start_soc.round(1),
            "ambient_temp_c": temp.round(1),
            "station_occupancy_pct": occupancy.round(1),
            "session_energy_kwh": np.round(energy, 2),
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
