"""One-command demo: generate data, train model, make one prediction."""

from generate_data import generate_rows
from pathlib import Path

from train import train
from predict import predict


def main() -> None:
    data_path = Path("data/sessions.csv")
    model_dir = Path("models")

    data_path.parent.mkdir(parents=True, exist_ok=True)
    generate_rows(5000).to_csv(data_path, index=False)
    print(f"Generated data -> {data_path}")

    metrics = train(data_path, model_dir)
    print(
        f"Metrics: RMSE={metrics['rmse_kwh']:.2f} kWh, "
        f"MAE={metrics['mae_kwh']:.2f} kWh, R2={metrics['r2']:.3f}"
    )

    kwh = predict(
        model_dir / "model.joblib",
        hour=18,
        day=2,
        station="airport",
        charger="dc_fast",
        battery=82,
        soc=28,
        temp=12,
        occupancy=64,
    )
    print(f"Sample prediction (airport, Wed 18:00): {kwh:.1f} kWh")


if __name__ == "__main__":
    main()
