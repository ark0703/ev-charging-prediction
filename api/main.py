"""FastAPI service for formula-based EV charging time estimates."""

from __future__ import annotations

from collections import deque
from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ml.calculate_time import charging_time_minutes, format_duration

STATIONS = ["downtown", "airport", "highway", "suburban", "mall"]
CHARGER_TYPES = ["level2", "dc_fast"]
DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

recent_predictions: deque[dict] = deque(maxlen=8)

FORMULA_INFO = {
    "method": "formula",
    "target": "session_duration_minutes",
    "formula": "time_hours = energy_kwh / average_power_kw",
    "energy_formula": "energy_kwh = battery_kwh × (target_soc - start_soc) / 100 × temp_efficiency",
    "average_power_kw": {"level2": 11.0, "dc_fast": 120.0},
    "features": [
        "hour_of_day",
        "day_of_week",
        "station_id",
        "charger_type",
        "vehicle_battery_kwh",
        "starting_soc_pct",
        "target_soc_pct",
        "ambient_temp_c",
        "station_occupancy_pct",
    ],
    "adjustments": [
        "Thermal efficiency penalty in cold/hot weather",
        "DC fast taper above 80% state of charge",
        "5% longer estimate when station occupancy exceeds 75%",
    ],
}


class PredictRequest(BaseModel):
    hour_of_day: int = Field(ge=0, le=23)
    day_of_week: int = Field(ge=0, le=6)
    station_id: Literal["downtown", "airport", "highway", "suburban", "mall"]
    charger_type: Literal["level2", "dc_fast"]
    vehicle_battery_kwh: float = Field(ge=20, le=150)
    starting_soc_pct: float = Field(ge=5, le=95)
    target_soc_pct: float = Field(ge=10, le=100)
    ambient_temp_c: float = Field(ge=-15, le=45)
    station_occupancy_pct: float = Field(ge=0, le=100)


class PredictResponse(BaseModel):
    predicted_session_duration_minutes: float
    human_readable: str
    energy_kwh: float
    average_power_kw: float
    summary: str


app = FastAPI(title="EV Charging Time Estimator API", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "estimator_ready": True}


@app.get("/metrics")
def metrics() -> dict:
    return FORMULA_INFO


@app.get("/schema")
def schema() -> dict:
    return {
        "stations": STATIONS,
        "charger_types": CHARGER_TYPES,
        "day_names": DAY_NAMES,
        "target": "session_duration_minutes",
        "features": FORMULA_INFO["features"],
    }


@app.get("/recent")
def recent() -> list[dict]:
    return list(recent_predictions)


@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest) -> PredictResponse:
    result = charging_time_minutes(
        payload.vehicle_battery_kwh,
        payload.starting_soc_pct,
        payload.target_soc_pct,
        payload.charger_type,
        payload.ambient_temp_c,
        payload.station_occupancy_pct,
    )
    minutes = float(result["session_duration_minutes"])
    readable = format_duration(minutes)
    day = DAY_NAMES[payload.day_of_week]
    summary = (
        f"{payload.charger_type.replace('_', ' ').title()} at {payload.station_id} on "
        f"{day} around {payload.hour_of_day:02d}:00 should take about {readable} "
        f"to charge from {payload.starting_soc_pct:.0f}% to {payload.target_soc_pct:.0f}%."
    )

    recent_predictions.appendleft(
        {
            "predicted_session_duration_minutes": minutes,
            "human_readable": readable,
            "hour_of_day": payload.hour_of_day,
            "day_of_week": payload.day_of_week,
            "station_id": payload.station_id,
            "charger_type": payload.charger_type,
            "starting_soc_pct": payload.starting_soc_pct,
            "target_soc_pct": payload.target_soc_pct,
        }
    )

    return PredictResponse(
        predicted_session_duration_minutes=minutes,
        human_readable=readable,
        energy_kwh=float(result["energy_kwh"]),
        average_power_kw=float(result["average_power_kw"]),
        summary=summary,
    )
