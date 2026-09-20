"""Train a supervised model to predict EV session energy (kWh)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

TARGET = "session_energy_kwh"
FEATURES = [
    "hour_of_day",
    "day_of_week",
    "station_id",
    "charger_type",
    "vehicle_battery_kwh",
    "starting_soc_pct",
    "ambient_temp_c",
    "station_occupancy_pct",
]
CAT_COLS = ["station_id", "charger_type"]
NUM_COLS = [c for c in FEATURES if c not in CAT_COLS]


def build_model() -> Pipeline:
    prep = ColumnTransformer(
        [
            ("num", StandardScaler(), NUM_COLS),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CAT_COLS),
        ]
    )
    regressor = GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.08,
        max_depth=4,
        random_state=42,
    )
    return Pipeline([("prep", prep), ("model", regressor)])


def train(csv_path: Path, model_dir: Path) -> dict:
    df = pd.read_csv(csv_path)
    x = df[FEATURES]
    y = df[TARGET]

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42
    )

    model = build_model()
    model.fit(x_train, y_train)
    preds = model.predict(x_test)

    metrics = {
        "target": TARGET,
        "train_rows": len(x_train),
        "test_rows": len(x_test),
        "rmse_kwh": float(np.sqrt(mean_squared_error(y_test, preds))),
        "mae_kwh": float(mean_absolute_error(y_test, preds)),
        "r2": float(r2_score(y_test, preds)),
    }

    model_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_dir / "model.joblib")
    (model_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data/sessions.csv"))
    parser.add_argument("--model-dir", type=Path, default=Path("models"))
    args = parser.parse_args()

    metrics = train(args.data, args.model_dir)
    print("Training complete")
    print(f"  RMSE: {metrics['rmse_kwh']:.2f} kWh")
    print(f"  MAE:  {metrics['mae_kwh']:.2f} kWh")
    print(f"  R2:   {metrics['r2']:.3f}")
    print(f"  Saved: {args.model_dir / 'model.joblib'}")


if __name__ == "__main__":
    main()
