"""Reference solution for Lab 05: stable order, explicit seeds, content keys."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

RAW = Path("data/sessions.csv")
ARTIFACTS = Path("artifacts")
CACHE = Path(".cache")
FEATURES = ["hours", "prior_score", "sleep_hours", "study_ratio"]
TARGET = "score"
SEED = 42
CODE_VERSION = "l05-1"


def digest(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def frame_digest(frame: pd.DataFrame) -> str:
    return digest(frame.to_csv(index=False, float_format="%.6f"))


def stage_key(name: str, upstream: str, params: dict) -> str:
    return digest(json.dumps({"stage": name, "upstream": upstream, "params": params,
                              "code": CODE_VERSION}, sort_keys=True))


def prepare(raw: pd.DataFrame) -> pd.DataFrame:
    frame = raw.drop_duplicates(subset="session_id", keep="first")
    return frame.sort_values("session_id", kind="stable").reset_index(drop=True)


def make_features(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["study_ratio"] = out["hours"] / out["prior_score"].clip(lower=1)
    return out[FEATURES + [TARGET, "session_id"]]


def train(frame: pd.DataFrame, trees: int) -> dict:
    train_frame, test_frame = train_test_split(frame, test_size=0.25, random_state=SEED)
    model = RandomForestRegressor(n_estimators=trees, max_depth=8, random_state=SEED)
    model.fit(train_frame[FEATURES], train_frame[TARGET])
    predictions = model.predict(test_frame[FEATURES])
    return {
        "mae": round(float(mean_absolute_error(test_frame[TARGET], predictions)), 6),
        "predictions_sha256": hashlib.sha256(predictions.round(6).tobytes()).hexdigest(),
        "review": list(frame.sample(n=3, random_state=SEED)["session_id"]),
    }


def load_cached_frame(key: str) -> pd.DataFrame | None:
    path = CACHE / f"frame-{key}.csv"
    return pd.read_csv(path) if path.exists() else None


def save_frame(key: str, frame: pd.DataFrame) -> None:
    frame.to_csv(CACHE / f"frame-{key}.csv", index=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reuse", action="store_true")
    parser.add_argument("--trees", type=int, default=120)
    args = parser.parse_args()

    ARTIFACTS.mkdir(exist_ok=True)
    CACHE.mkdir(exist_ok=True)

    raw = pd.read_csv(RAW)
    stages: list[dict] = []

    prepare_key = stage_key("prepare", digest(RAW.read_bytes().hex()), {})
    cached = load_cached_frame(prepare_key) if args.reuse else None
    if cached is not None:
        prepared, status = cached, "hit"
    else:
        prepared, status = prepare(raw), "computed"
        save_frame(prepare_key, prepared)
    stages.append({"name": "prepare", "key": prepare_key, "status": status, "rows": len(prepared)})

    feature_key = stage_key("features", prepare_key, {"features": FEATURES})
    cached = load_cached_frame(feature_key) if args.reuse else None
    if cached is not None:
        featured, status = cached, "hit"
    else:
        featured, status = make_features(prepared), "computed"
        save_frame(feature_key, featured)
    stages.append({"name": "features", "key": feature_key, "status": status, "rows": len(featured)})

    train_key = stage_key("train", frame_digest(featured), {"trees": args.trees, "seed": SEED})
    metrics_path = CACHE / f"metrics-{train_key}.json"
    if args.reuse and metrics_path.exists():
        metrics, status = json.loads(metrics_path.read_text(encoding="utf-8")), "hit"
    else:
        metrics, status = train(featured, args.trees), "computed"
        metrics_path.write_text(json.dumps(metrics, sort_keys=True), encoding="utf-8")
    stages.append({"name": "train", "key": train_key, "status": status, "rows": len(featured)})

    manifest = {"stages": stages, "metrics": metrics, "features": FEATURES}
    (ARTIFACTS / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"mae {metrics['mae']} stages " + " ".join(f"{s['name']}={s['status']}" for s in stages))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
