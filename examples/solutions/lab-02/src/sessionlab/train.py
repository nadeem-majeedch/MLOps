"""Train and report. One command, explicit inputs, explicit outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

from .config import TARGET, Settings
from .data import load, split
from .features import feature_frame


def train(data_path: Path, out_path: Path, seed: int) -> dict:
    settings = Settings(seed=seed)
    frame = load(data_path)
    train_frame, test_frame = split(frame, settings)

    model = RandomForestRegressor(
        n_estimators=settings.n_estimators, max_depth=settings.max_depth, random_state=seed
    )
    model.fit(feature_frame(train_frame), train_frame[TARGET])
    predictions = model.predict(feature_frame(test_frame))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    model_path = out_path.with_suffix(".joblib")
    joblib.dump(model, model_path)

    return {
        "mae": round(float(mean_absolute_error(test_frame[TARGET], predictions)), 4),
        "r2": round(float(r2_score(test_frame[TARGET], predictions)), 4),
        "rows_train": int(len(train_frame)),
        "rows_test": int(len(test_frame)),
        "seed": seed,
        "model_path": str(model_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Train the session score model")
    parser.add_argument("--data", type=Path, default=Path("data/sessions.csv"))
    parser.add_argument("--out", type=Path, default=Path("artifacts/run.json"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    metrics = train(args.data, args.out, args.seed)
    args.out.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(f"mae {metrics['mae']} -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
