"""FastAPI inference service for EV session energy predictions."""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path
from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "model.joblib"
METRICS_PATH = ROOT / "models" / "metrics.json"

STATIONS = ["downtown", "airport", "highway", "suburban", "mall"]
CHARGER_TYPES = ["level2", "dc_fast"]
DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

recent_predictions: deque[dict] = deque(maxlen=8)


class PredictRequest(BaseModel):
    hour_of_day: int = Field(ge=0, le=23)
    day_of_week: int = Field(ge=0, le=6)
    station_id: Literal["downtown", "airport", "highway", "suburban", "mall"]
    charger_type: Literal["level2", "dc_fast"]
    vehicle_battery_kwh: float = Field(ge=20, le=150)
    starting_soc_pct: float = Field(ge=5, le=95)
    ambient_temp_c: float = Field(ge=-15, le=45)
    station_occupancy_pct: float = Field(ge=0, le=100)


class PredictResponse(BaseModel):
    predicted_session_energy_kwh: float
    confidence_band_kwh: float
    summary: str


app = FastAPI(title="EV Charging Prediction API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_pipeline = None
_metrics: dict | None = None


def load_artifacts() -> None:
    global _pipeline, _metrics
    if not MODEL_PATH.exists():
        raise RuntimeError(
            "Model not found. Run `python ml/generate_data.py && python ml/train.py` first."
        )
    _pipeline = joblib.load(MODEL_PATH)
    if METRICS_PATH.exists():
        _metrics = json.loads(METRICS_PATH.read_text())
    else:
        _metrics = None


@app.on_event("startup")
def startup() -> None:
    load_artifacts()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model_loaded": _pipeline is not None}


@app.get("/metrics")
def metrics() -> dict:
    if _metrics is None:
        raise HTTPException(status_code=503, detail="Metrics not available.")
    return _metrics


@app.get("/schema")
def schema() -> dict:
    return {
        "stations": STATIONS,
        "charger_types": CHARGER_TYPES,
        "day_names": DAY_NAMES,
        "target": "session_energy_kwh",
        "features": [
            "hour_of_day",
            "day_of_week",
            "station_id",
            "charger_type",
            "vehicle_battery_kwh",
            "starting_soc_pct",
            "ambient_temp_c",
            "station_occupancy_pct",
        ],
    }


@app.get("/recent")
def recent() -> list[dict]:
    return list(recent_predictions)


@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest) -> PredictResponse:
    if _pipeline is None:
        raise HTTPException(status_code=503, detail="Model not loaded.")

    row = pd.DataFrame([payload.model_dump()])
    prediction = float(_pipeline.predict(row)[0])
    mae = float(_metrics["mae_kwh"]) if _metrics else 3.5
    band = round(mae * 1.2, 2)

    day = DAY_NAMES[payload.day_of_week]
    summary = (
        f"{payload.charger_type.replace('_', ' ').title()} session at "
        f"{payload.station_id} on {day} around {payload.hour_of_day:02d}:00 "
        f"is expected to deliver about {prediction:.1f} kWh."
    )

    record = {
        "predicted_session_energy_kwh": round(prediction, 2),
        "hour_of_day": payload.hour_of_day,
        "day_of_week": payload.day_of_week,
        "station_id": payload.station_id,
        "charger_type": payload.charger_type,
        "starting_soc_pct": payload.starting_soc_pct,
    }
    recent_predictions.appendleft(record)

    return PredictResponse(
        predicted_session_energy_kwh=round(prediction, 2),
        confidence_band_kwh=band,
        summary=summary,
    )
