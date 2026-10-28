"""Stage 3: fit the model and write the artefact plus its metadata."""

from __future__ import annotations

import hashlib
import json

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from .config import load_params, project_path
from .features import feature_columns, feature_frame


def build_model(params: dict, numeric: list[str], categorical: list[str]) -> Pipeline:
    model = params["model"]
    pre = ColumnTransformer(
        [
            ("num", "passthrough", numeric),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
        ]
    )
    forest = RandomForestRegressor(
        n_estimators=int(model["n_estimators"]),
        max_depth=int(model["max_depth"]),
        min_samples_leaf=int(model["min_samples_leaf"]),
        random_state=int(model["random_state"]),
        n_jobs=1,
    )
    return Pipeline([("pre", pre), ("rf", forest)])


def file_sha256(path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    params = load_params()
    set_name = params["features"]["set"]
    train = pd.read_csv(project_path("data", "features", "train.csv"), parse_dates=["requested_at"])
    numeric, categorical = feature_columns(set_name)

    model = build_model(params, numeric, categorical)
    model.fit(feature_frame(train, set_name), train["duration_min"])

    project_path("models").mkdir(parents=True, exist_ok=True)
    artefact = project_path("models", "model.joblib")
    joblib.dump(model, artefact)
    meta = {
        "feature_set": set_name,
        "numeric": numeric,
        "categorical": categorical,
        "train_rows": int(len(train)),
        "train_sha256": file_sha256(project_path("data", "features", "train.csv")),
        "model_sha256": file_sha256(artefact),
        "params": params["model"],
    }
    (project_path("models", "run_meta.json")).write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(f"trained {set_name} model on {len(train)} rows -> model.joblib")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
