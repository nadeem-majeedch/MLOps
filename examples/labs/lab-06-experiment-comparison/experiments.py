"""Lab 06 starter: four experiments that record too little to compare.

    python experiments.py

Four configurations are trained against the same split. Each run logs its
overall MAE, which is enough to rank them and not enough to trust the ranking:
no parameters, no tags, no per-zone score, no model artifact. A week later
nobody can tell what "deep" meant.

Your job: make every run self-describing, then write `compare.py` so the
comparison is derived from the tracking store rather than from memory.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

DATA = Path("data/sessions.csv")
EXPERIMENT = "lab06-comparison"
SEED = 42

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
        mae = mean_absolute_error(test["score"], predictions)

        with mlflow.start_run(run_name=name):
            # TODO 1: log every parameter that changes the model.
            # TODO 2: log the data hash and a code version as tags.
            # TODO 3: log per-section MAE next to the overall score.
            # TODO 4: log the fitted model so the run can be reproduced.
            mlflow.log_metric("mae", mae)
        print(f"{name}: mae {mae:.4f}")


if __name__ == "__main__":
    main()
