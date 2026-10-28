"""Lab 05 starter: three stages, two ways to get a different answer.

    python pipeline.py
    python pipeline.py --reuse          # accepted, but nothing is cached yet
    python pipeline.py --trees 60

It runs, and it even produces a sensible MAE. Run it twice and compare
`artifacts/manifest.json`: the stage list, the metric, and the feature order can
all differ. Your job is to make the pipeline deterministic and to make `--reuse`
skip work that has not changed.

The manifest contract the checker uses:

    {"stages": [{"name": "prepare", "key": "<hex>", "status": "computed|hit",
                 "rows": <int>}, ...],
     "metrics": {"mae": <float>, "predictions_sha256": "<hex>"},
     "features": ["hours", ...]}

Stage order is prepare, features, train.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

RAW = Path("data/sessions.csv")
ARTIFACTS = Path("artifacts")
CACHE = Path(".cache")
FEATURES = ["hours", "prior_score", "sleep_hours", "study_ratio"]
TARGET = "score"


def prepare(raw: pd.DataFrame) -> pd.DataFrame:
    frame = raw.drop_duplicates(subset="session_id", keep="first")
    return frame.sort_values("hours")  # ties keep the incoming order: unstable


def make_features(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["study_ratio"] = out["hours"] / out["prior_score"].clip(lower=1)
    columns = {name for name in FEATURES}  # a set: order is not defined
    return out[list(columns) + [TARGET, "session_id"]]


def train(frame: pd.DataFrame, trees: int) -> dict:
    train_frame, test_frame = train_test_split(frame, test_size=0.25)  # no seed
    model = RandomForestRegressor(n_estimators=trees, max_depth=8, random_state=42)
    model.fit(train_frame[FEATURES], train_frame[TARGET])
    predictions = model.predict(test_frame[FEATURES])
    return {
        "mae": float(mean_absolute_error(test_frame[TARGET], predictions)),
        "predictions_sha256": hashlib.sha256(predictions.round(6).tobytes()).hexdigest(),
        "review": list(frame.sample(n=3)["session_id"]),  # no seed
    }


def stage_key(name: str, upstream: str, params: dict) -> str:
    """A key that changes when the inputs or the parameters change.

    TODO: hash the upstream key and the stage's own parameters. Two stages with
    different inputs must never share a cache entry.
    """
    return ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reuse", action="store_true", help="reuse cached stage outputs")
    parser.add_argument("--trees", type=int, default=120)
    args = parser.parse_args()

    ARTIFACTS.mkdir(exist_ok=True)
    CACHE.mkdir(exist_ok=True)

    raw = pd.read_csv(RAW)
    prepared = prepare(raw)
    featured = make_features(prepared)
    metrics = train(featured, args.trees)

    manifest = {
        "stages": [
            {"name": "prepare", "key": stage_key("prepare", "raw", {}), "status": "computed", "rows": len(prepared)},
            {"name": "features", "key": stage_key("features", "prepared", {}), "status": "computed", "rows": len(featured)},
            {"name": "train", "key": stage_key("train", "featured", {"trees": args.trees}), "status": "computed", "rows": len(featured)},
        ],
        "metrics": metrics,
        "features": list(featured.columns[:4]),
    }
    (ARTIFACTS / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
