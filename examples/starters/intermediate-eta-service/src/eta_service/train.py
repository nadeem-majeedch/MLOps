"""Train the ETA model and write an artifact a service can load.

The artifact directory contains three files that must stay together:

* `model.joblib`   -- the fitted pipeline (preprocessing inside)
* `metrics.json`   -- MAE, RMSE, and a baseline comparison
* `run_meta.json`  -- data hash, feature order, parameters, versions

A service that loads only the joblib file is one deployment away from a feature
order mismatch it cannot detect.
"""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path

import joblib
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from .features import CATEGORICAL, NUMERIC, TARGET, add_features, feature_frame


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def build_pipeline(seed: int = 42, n_estimators: int = 150) -> Pipeline:
    pre = ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
            ("num", "passthrough", NUMERIC),
        ]
    )
    forest = RandomForestRegressor(
        n_estimators=n_estimators, min_samples_leaf=2, random_state=seed, n_jobs=1
    )
    return Pipeline([("pre", pre), ("model", forest)])


def load_frame(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    required = {"requested_at", "distance_km", *CATEGORICAL, TARGET}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{path} is missing columns: {missing}")
    if frame.empty:
        raise ValueError(f"{path} has no rows")
    if (frame["distance_km"] <= 0).any():
        raise ValueError("distance_km must be positive")
    return frame


def train(
    data_path: Path,
    output_dir: Path,
    seed: int = 42,
    test_size: float = 0.25,
    n_estimators: int = 150,
) -> dict:
    frame = add_features(load_frame(data_path))
    train_frame, test_frame = train_test_split(
        frame, test_size=test_size, random_state=seed
    )
    model = build_pipeline(seed, n_estimators).fit(
        feature_frame(train_frame), train_frame[TARGET]
    )

    predictions = model.predict(feature_frame(test_frame))
    baseline = [float(train_frame[TARGET].median())] * len(test_frame)
    metrics = {
        "mae": round(float(mean_absolute_error(test_frame[TARGET], predictions)), 4),
        "rmse": round(float(mean_squared_error(test_frame[TARGET], predictions) ** 0.5), 4),
        "baseline_mae": round(float(mean_absolute_error(test_frame[TARGET], baseline)), 4),
        "test_rows": int(len(test_frame)),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / "model.joblib"
    joblib.dump(model, model_path)
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
    )
    meta = {
        "target": TARGET,
        "features": {"numeric": NUMERIC, "categorical": CATEGORICAL},
        "params": {"seed": seed, "test_size": test_size, "n_estimators": n_estimators},
        "train_rows": int(len(train_frame)),
        "data_file": data_path.name,
        "data_sha256": file_sha256(data_path),
        "model_sha256": file_sha256(model_path),
        "versions": {
            "python": platform.python_version(),
            "scikit_learn": sklearn.__version__,
            "pandas": pd.__version__,
        },
        "metrics": metrics,
    }
    (output_dir / "run_meta.json").write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8"
    )
    return meta
