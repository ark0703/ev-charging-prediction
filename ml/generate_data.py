"""Generate synthetic EV charging session data with plausible distributions."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

STATIONS = ["downtown", "airport", "highway", "suburban", "mall"]
CHARGER_TYPES = ["level2", "dc_fast"]
RNG = np.random.default_rng(42)


def _time_demand_multiplier(hour: int, day_of_week: int) -> float:
    """Higher demand during commute windows and weekends."""
    commute = 1.0 + 0.25 * np.exp(-0.5 * ((hour - 8) / 2) ** 2)
    commute += 0.35 * np.exp(-0.5 * ((hour - 18) / 2.5) ** 2)
    weekend = 1.12 if day_of_week >= 5 else 1.0
    return commute * weekend


def _station_bias(station: str) -> float:
    return {
        "downtown": 1.08,
        "airport": 1.15,
        "highway": 1.05,
        "suburban": 0.92,
        "mall": 1.0,
    }[station]


def _charger_power_kw(charger_type: str) -> float:
    return 150.0 if charger_type == "dc_fast" else 11.0


def generate_sessions(n_rows: int) -> pd.DataFrame:
    hours = RNG.integers(0, 24, size=n_rows)
    days = RNG.integers(0, 7, size=n_rows)
    stations = RNG.choice(STATIONS, size=n_rows)
    charger_types = RNG.choice(CHARGER_TYPES, size=n_rows, p=[0.62, 0.38])
    battery_kwh = RNG.uniform(45, 100, size=n_rows)
    starting_soc = RNG.uniform(12, 75, size=n_rows)
    ambient_temp = RNG.normal(18, 8, size=n_rows).clip(-8, 38)
    occupancy = RNG.beta(2.2, 2.8, size=n_rows) * 100

    session_energy = []
    for i in range(n_rows):
        usable_fraction = 1.0 - starting_soc[i] / 100.0
        thermal_eff = 1.0 - 0.004 * max(0.0, 10.0 - ambient_temp[i])
        thermal_eff -= 0.0015 * max(0.0, ambient_temp[i] - 30.0)

        target_energy = battery_kwh[i] * usable_fraction * thermal_eff
        target_energy *= _time_demand_multiplier(int(hours[i]), int(days[i]))
        target_energy *= _station_bias(stations[i])

        if charger_types[i] == "dc_fast":
            target_energy *= RNG.uniform(0.92, 1.08)
        else:
            dwell_factor = RNG.uniform(0.55, 0.95)
            target_energy *= dwell_factor

        occupancy_penalty = 1.0 - 0.08 * (occupancy[i] / 100.0)
        target_energy *= occupancy_penalty
        target_energy += RNG.normal(0, 1.8)
        session_energy.append(max(2.0, min(target_energy, battery_kwh[i] * 0.95)))

    return pd.DataFrame(
        {
            "hour_of_day": hours,
            "day_of_week": days,
            "station_id": stations,
            "charger_type": charger_types,
            "vehicle_battery_kwh": battery_kwh.round(1),
            "starting_soc_pct": starting_soc.round(1),
            "ambient_temp_c": ambient_temp.round(1),
            "station_occupancy_pct": occupancy.round(1),
            "session_energy_kwh": np.round(session_energy, 2),
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic EV charging sessions.")
    parser.add_argument("--rows", type=int, default=8000, help="Number of sessions to generate.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("ml/data/charging_sessions.csv"),
        help="Output CSV path.",
    )
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    df = generate_sessions(args.rows)
    df.to_csv(args.output, index=False)
    print(f"Wrote {len(df):,} sessions to {args.output}")


if __name__ == "__main__":
    main()
