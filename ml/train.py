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
CATEGORICAL = ["station_id", "charger_type"]
NUMERIC = [f for f in FEATURES if f not in CATEGORICAL]


def build_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
        ]
    )
    model = GradientBoostingRegressor(
        n_estimators=250,
        learning_rate=0.08,
        max_depth=4,
        random_state=42,
    )
    return Pipeline(steps=[("preprocessor", preprocessor), ("model", model)])


def train(data_path: Path, model_dir: Path) -> dict:
    df = pd.read_csv(data_path)
    x = df[FEATURES]
    y = df[TARGET]

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42
    )

    pipeline = build_pipeline()
    pipeline.fit(x_train, y_train)
    predictions = pipeline.predict(x_test)

    metrics = {
        "target": TARGET,
        "features": FEATURES,
        "train_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "rmse_kwh": float(np.sqrt(mean_squared_error(y_test, predictions))),
        "mae_kwh": float(mean_absolute_error(y_test, predictions)),
        "r2": float(r2_score(y_test, predictions)),
        "model": "GradientBoostingRegressor",
    }

    model_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, model_dir / "model.joblib")
    (model_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Train EV session energy model.")
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("ml/data/charging_sessions.csv"),
        help="Training CSV path.",
    )
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=Path("models"),
        help="Directory for saved model and metrics.",
    )
    args = parser.parse_args()

    metrics = train(args.data, args.model_dir)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
