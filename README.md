# EV Charging Time Estimator

Estimate **how long an EV charging session will take** using a simple energy/power formula, with a FastAPI backend and Next.js web UI.

> **Python-only mini project:** see [`python_mini/`](python_mini/README.md) for the same formula in a CLI-only version.

## What it estimates

**Target:** `session_duration_minutes` — charging time from plug-in to target SOC.

**Formula:**

```text
energy_kwh = battery × (target_soc - start_soc) / 100 × temperature_efficiency
time_hours = energy_kwh / average_charger_power
time_minutes = time_hours × 60
```

**Average charger power:**

| Charger | Power |
| --- | --- |
| `level2` | 11 kW |
| `dc_fast` | 120 kW |

Adjustments include cold/hot weather, DC fast taper above 80% SOC, and a small occupancy factor.

## Quick start

### 1. Install dependencies

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm install
```

**Windows (PowerShell)**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
npm install
```

### 2. Run the app

```bash
npm run dev
```

No training step required.

This starts:

- **FastAPI** on `http://127.0.0.1:8765`
- **Next.js** UI on `http://127.0.0.1:4321`

### Optional: legacy ML training scripts

The older supervised ML pipeline (`ml/generate_data.py`, `ml/train.py`, `npm run train`) is still in the repo but **not used** by the web app anymore.

## Project layout

```
api/main.py              FastAPI formula estimator
ml/calculate_time.py     Core time calculation
python_mini/             CLI-only version of the same formula
src/                     Next.js + shadcn/ui frontend
```

## Manual API usage

```bash
python -m uvicorn api.main:app --host 127.0.0.1 --port 8765
```

```bash
curl -X POST http://127.0.0.1:8765/predict \
  -H 'Content-Type: application/json' \
  -d '{
    "hour_of_day": 18,
    "day_of_week": 2,
    "station_id": "airport",
    "charger_type": "dc_fast",
    "vehicle_battery_kwh": 82,
    "starting_soc_pct": 28,
    "target_soc_pct": 80,
    "ambient_temp_c": 12,
    "station_occupancy_pct": 64
  }'
```

## Tech stack

- Python 3.12, FastAPI, uvicorn
- Next.js 16, TypeScript, Tailwind CSS v4, shadcn/ui

No authentication, database, or external services required.
