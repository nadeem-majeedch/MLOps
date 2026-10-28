"""Reference solution for Lab 06: every run says what it did."""

from __future__ import annotations

import hashlib
from pathlib import Path

import mlflow
import mlflow.sklearn
import pandas as pd
from mlflow.models import infer_signature
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

DATA = Path("data/sessions.csv")
EXPERIMENT = "lab06-comparison"
SEED = 42
CODE_VERSION = "l06-1"

CONFIGS = {
    "baseline": {"trees": 120, "depth": 8, "features": ["hours", "prior_score", "sleep_hours"]},
    "deep": {"trees": 300, "depth": 14, "features": ["hours", "prior_score", "sleep_hours"]},
    "shallow": {"trees": 60, "depth": 4, "features": ["hours", "prior_score", "sleep_hours"]},
    "no_sleep": {"trees": 120, "depth": 8, "features": ["hours", "prior_score"]},
}


def data_hash() -> str:
    return hashlib.sha256(DATA.read_bytes()).hexdigest()[:12]


def main() -> None:
    frame = pd.read_csv(DATA)
    mlflow.set_tracking_uri(Path("mlruns").resolve().as_uri())
    mlflow.set_experiment(EXPERIMENT)

    for name, config in CONFIGS.items():
        features = config["features"]
        train, test = train_test_split(frame, test_size=0.25, random_state=SEED)
        model = RandomForestRegressor(
            n_estimators=config["trees"], max_depth=config["depth"], random_state=SEED
        )
        model.fit(train[features], train["score"])
        predictions = model.predict(test[features])
        error = (predictions - test["score"]).abs()

        metrics = {
            "mae": round(float(mean_absolute_error(test["score"], predictions)), 4),
            "rmse": round(float(mean_squared_error(test["score"], predictions) ** 0.5), 4),
            "r2": round(float(r2_score(test["score"], predictions)), 4),
            "p95_abs_error": round(float(error.quantile(0.95)), 4),
        }
        for section in ("A", "B", "C"):
            mask = (test["section"] == section).to_numpy()
            metrics[f"mae_section_{section}"] = round(float(error[mask].mean()), 4)

        signature = infer_signature(test[features].head(3), model.predict(test[features].head(3)))
        with mlflow.start_run(run_name=name) as run:
            mlflow.log_params(
                {
                    "trees": config["trees"],
                    "depth": config["depth"],
                    "features": ",".join(features),
                    "seed": SEED,
                    "train_rows": len(train),
                }
            )
            mlflow.set_tags({"data_hash": data_hash(), "code_version": CODE_VERSION})
            mlflow.log_metrics(metrics)
            mlflow.log_dict(metrics, "evaluation/metrics.json")
            mlflow.sklearn.log_model(model, artifact_path="model", signature=signature,
                                     input_example=test[features].head(3))
            print(f"{name}: mae {metrics['mae']} run {run.info.run_id[:8]}")


if __name__ == "__main__":
    main()
