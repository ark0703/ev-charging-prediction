# EV Charging Time Prediction — Python Mini Project

A **small supervised machine learning project in Python only** (no web app, no API).

Predict **how long a charging session will take (minutes)** from time, station, charger type, vehicle, target SOC, and weather features.

## What you get

| File | Purpose |
| --- | --- |
| `generate_data.py` | Create synthetic training CSV |
| `train.py` | Train scikit-learn model + print metrics |
| `predict.py` | Predict charging time from CLI |
| `run.py` | Demo: generate → train → predict in one go |

## Setup (Windows / macOS / Linux)

```bash
cd python_mini
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

## Quick demo

```bash
python run.py
```

## Step by step

```bash
# 1) Create dataset
python generate_data.py

# 2) Train model (80/20 split, saves models/model.joblib)
python train.py

# 3) Predict charging time
python predict.py --interactive
```

### Example (non-interactive)

```bash
python predict.py --hour 18 --day 2 --station airport --charger dc_fast --battery 82 --soc 28 --target-soc 80 --temp 12 --occupancy 64
```

Example output:

```json
{
  "predicted_session_duration_minutes": 24.6,
  "human_readable": "25m (25 minutes)"
}
```

## Use your own dataset

Put a CSV at `data/sessions.csv` with these columns:

- `hour_of_day`, `day_of_week`
- `station_id`, `charger_type`
- `vehicle_battery_kwh`, `starting_soc_pct`, `target_soc_pct`
- `ambient_temp_c`, `station_occupancy_pct`
- **`session_duration_minutes`** (target label — how long the session lasted)

Then run:

```bash
python train.py --data data/sessions.csv
python predict.py --interactive
```

## Model

- **Type:** Supervised regression
- **Algorithm:** `GradientBoostingRegressor` (scikit-learn)
- **Target:** `session_duration_minutes`
- **Metrics:** RMSE and MAE in minutes, plus R² on held-out test set

Synthetic data approximates duration from energy needed, charger power, temperature, and SOC range. Real-world accuracy depends on your dataset.

## Project layout

```
python_mini/
  generate_data.py
  train.py
  predict.py
  run.py
  requirements.txt
  data/sessions.csv      # generated
  models/model.joblib    # trained model
  models/metrics.json    # evaluation scores
```

This folder is intentionally separate from the full-stack app in the repo root (which still predicts energy unless you update it separately).
