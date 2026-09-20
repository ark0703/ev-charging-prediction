# EV Charging Time Estimator — Python Mini Project

A **small Python-only mini project** that estimates **how long an EV charging session will take**.

Uses **Option B: a simple formula**, not machine learning:

```text
time (hours) ≈ energy_needed (kWh) / average_charger_power (kW)
time (minutes) = time (hours) × 60
```

Where:

```text
energy_needed = battery_kwh × (target_soc - start_soc) / 100 × temperature_efficiency
```

## Files

| File | Purpose |
| --- | --- |
| `calculate_time.py` | Core formula |
| `predict.py` | CLI to estimate time |
| `run.py` | Print a few example estimates |

No training step. No model file.

## Setup

```bash
cd python_mini
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS / Linux
# source .venv/bin/activate
```

No extra packages required (Python standard library only).

## Quick demo

```bash
python run.py
```

## Interactive estimate

```bash
python predict.py --interactive
```

## One-line example

```bash
python predict.py --hour 18 --day 2 --station airport --charger dc_fast --battery 82 --soc 28 --target-soc 80 --temp 12 --occupancy 64
```

Example output:

```json
{
  "energy_kwh": 42.62,
  "average_power_kw": 120.0,
  "session_duration_minutes": 23.5,
  "human_readable": "24m (24 minutes)"
}
```

## Assumptions

| Charger | Average power used |
| --- | --- |
| `dc_fast` | 120 kW |
| `level2` | 11 kW |

Also applied:

- **Cold/hot weather** reduces effective energy efficiency
- **DC fast taper** above 80% SOC (charging slows near full)
- **High station occupancy** adds a small 5% adjustment

These are approximations, not exact vehicle-specific curves.

## Inputs

- `starting_soc_pct` — battery level when you plug in
- `target_soc_pct` — desired battery level when you unplug
- `vehicle_battery_kwh` — pack size
- `charger_type` — `level2` or `dc_fast`
- `ambient_temp_c` — weather effect
- `station_id`, `hour_of_day`, etc. — kept for context in output

## Accuracy note

This is a **rough estimate**. Real charging time varies by:

- Vehicle max charge rate
- Battery curve above 80%
- Cable/shared power limits
- Queue/wait time before plugging in

Good for a mini project demo; use real session logs if you need high accuracy later.

## Legacy ML files

`train.py`, `generate_data.py`, and `requirements.txt` are kept from an earlier ML version but are **not required** for this formula-based flow.
