"""Local model registry: train candidates, gate them, promote and roll back.

Uses MLflow's file store, so no server or account is required.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
import yaml
from mlflow import MlflowClient
from mlflow.models import infer_signature
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raviride_eta.config import load_params  # noqa: E402
from raviride_eta.features import feature_columns, feature_frame  # noqa: E402
from raviride_eta.train import build_model  # noqa: E402

MODEL_NAME = "raviride-eta"
POLICY = ROOT / "registry" / "promotion_policy.yaml"


def tracking_uri() -> str:
    return (ROOT / "mlruns").as_uri()


def client() -> MlflowClient:
    mlflow.set_tracking_uri(tracking_uri())
    return MlflowClient(tracking_uri=tracking_uri())


def data_hash() -> str:
    digest = hashlib.sha256()
    for name in ("train.csv", "test.csv"):
        digest.update((ROOT / "data" / "features" / name).read_bytes())
    return digest.hexdigest()[:16]


def git_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception:  # noqa: BLE001 - a missing commit must not block a run
        return "unknown"


def score(model, test: pd.DataFrame, set_name: str) -> dict:
    pred = model.predict(feature_frame(test, set_name))
    truth = test["duration_min"].to_numpy()
    error = np.abs(pred - truth)
    zones = {}
    for zone in sorted(test["pickup_zone"].unique()):
        mask = test["pickup_zone"] == zone
        zones[zone] = {
            "mae": round(float(mean_absolute_error(truth[mask], pred[mask])), 4),
            "rows": int(mask.sum()),
        }
    return {
        "mae": round(float(mean_absolute_error(truth, pred)), 4),
        "rmse": round(float(mean_squared_error(truth, pred) ** 0.5), 4),
        "r2": round(float(r2_score(truth, pred)), 4),
        "p95_abs_error": round(float(np.percentile(error, 95)), 4),
        "mae_peak": round(float(mean_absolute_error(truth[test["is_peak"] == 1], pred[test["is_peak"] == 1])), 4),
        "mae_off_peak": round(float(mean_absolute_error(truth[test["is_peak"] == 0], pred[test["is_peak"] == 0])), 4),
        "zones": zones,
        "rows": int(len(test)),
    }


def train(name: str, override: dict, feature_set: str | None = None,
          drop_zones: list[str] | None = None) -> tuple[str, int, dict]:
    c = client()
    mlflow.set_experiment("raviride-registry")
    params = load_params()
    model_params = dict(params["model"], **override)
    set_name = feature_set or params["features"]["set"]
    numeric, categorical = feature_columns(set_name)
    train_df = pd.read_csv(ROOT / "data" / "features" / "train.csv", parse_dates=["requested_at"])
    test_df = pd.read_csv(ROOT / "data" / "features" / "test.csv", parse_dates=["requested_at"])
    if drop_zones:
        train_df = train_df[~train_df["pickup_zone"].isin(drop_zones)].reset_index(drop=True)

    model = build_model({"model": model_params}, numeric, categorical)
    model.fit(feature_frame(train_df, set_name), train_df["duration_min"])
    metrics = score(model, test_df, set_name)

    example = feature_frame(test_df, set_name).head(3)
    signature = infer_signature(example, model.predict(example))

    with mlflow.start_run(run_name=name) as run:
        mlflow.log_params({"feature_set": set_name, "train_rows": len(train_df), **model_params})
        mlflow.set_tags({
            "data_hash": data_hash(),
            "git_commit": git_commit(),
            "candidate": name,
            "dropped_zones": ",".join(sorted(drop_zones or [])),
        })
        mlflow.log_metrics({k: v for k, v in metrics.items() if isinstance(v, int | float)})
        mlflow.log_metrics({f"mae_zone_{z}": v["mae"] for z, v in metrics["zones"].items()})
        mlflow.log_dict(metrics, "evaluation/metrics.json")
        mlflow.sklearn.log_model(model, artifact_path="model", signature=signature, input_example=example)
        run_id = run.info.run_id

    registered = mlflow.register_model(f"runs:/{run_id}/model", MODEL_NAME)
    c.set_model_version_tag(MODEL_NAME, registered.version, "candidate", name)
    c.set_model_version_tag(MODEL_NAME, registered.version, "data_hash", data_hash())
    c.set_model_version_tag(MODEL_NAME, registered.version, "git_commit", git_commit())
    c.set_model_version_tag(MODEL_NAME, registered.version, "run_id", run_id)
    c.set_model_version_tag(MODEL_NAME, registered.version, "dropped_zones", ",".join(sorted(drop_zones or [])))
    (ROOT / "candidates").mkdir(exist_ok=True)
    (ROOT / "candidates" / f"{name}.json").write_text(
        json.dumps({"version": registered.version, "run_id": run_id, "metrics": metrics}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"{name}: version {registered.version} run {run_id[:8]} MAE {metrics['mae']}")
    return run_id, int(registered.version), metrics


def champion_version(c: MlflowClient) -> int | None:
    try:
        return int(c.get_model_version_by_alias(MODEL_NAME, "champion").version)
    except Exception:  # noqa: BLE001 - no alias yet
        return None


def run_metrics(c: MlflowClient, version: int) -> dict:
    run_id = c.get_model_version(MODEL_NAME, str(version)).tags["run_id"]
    data = c.get_run(run_id).data
    metrics = dict(data.metrics)
    metrics["zones"] = {
        k.replace("mae_zone_", ""): v for k, v in metrics.items() if k.startswith("mae_zone_")
    }
    return metrics


def gates(version: int) -> tuple[bool, list[str]]:
    policy = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
    c = client()
    candidate = run_metrics(c, version)
    current = champion_version(c)
    reasons: list[str] = []

    ceiling = policy["overall_ceiling"]
    if policy.get("forbid_dropped_zones"):
        dropped = c.get_model_version(MODEL_NAME, str(version)).tags.get("dropped_zones", "")
        if dropped:
            reasons.append(f"training data excludes production zones: {dropped}")
    if candidate["mae"] > ceiling:
        reasons.append(f"overall_mae {candidate['mae']:.3f} exceeds ceiling {ceiling}")

    if current is not None:
        base = run_metrics(c, current)
        allowed = round(base["mae"] * (1 + policy["max_regression"]), 4)
        if candidate["mae"] > allowed:
            reasons.append(
                f"overall_mae {candidate['mae']:.3f} exceeds champion v{current} "
                f"by more than {policy['max_regression']:.0%} (allowed {allowed})"
            )
        for zone, limit in policy["zone_limits"].items():
            if zone not in candidate["zones"] or zone not in base["zones"]:
                continue
            allowed_zone = round(base["zones"][zone] * (1 + limit), 4)
            if candidate["zones"][zone] > allowed_zone:
                reasons.append(
                    f"zone {zone} mae {candidate['zones'][zone]:.3f} exceeds champion "
                    f"{base['zones'][zone]:.3f} by more than {limit:.0%} "
                    f"(allowed {allowed_zone})"
                )

    return (not reasons), reasons


def promote(version: int, force: bool = False) -> int:
    c = client()
    ok, reasons = gates(version)
    if not ok and not force:
        print(f"BLOCKED v{version}:")
        for reason in reasons:
            print(f"  - {reason}")
        return 1
    previous = champion_version(c)
    c.set_registered_model_alias(MODEL_NAME, "champion", str(version))
    c.set_model_version_tag(MODEL_NAME, str(version), "promoted_at", datetime.now(UTC).isoformat(timespec="seconds"))
    c.set_model_version_tag(MODEL_NAME, str(version), "promoted_from", str(previous) if previous else "none")
    print(f"champion -> v{version} (was v{previous})")
    return 0


def rollback(to: int | None) -> int:
    c = client()
    current = champion_version(c)
    target = to if to is not None else c.get_model_version(MODEL_NAME, str(current)).tags.get("promoted_from")
    if not target or str(target) == "none":
        print(f"no previous champion recorded for v{current}; pass --to VERSION")
        return 2
    c.set_registered_model_alias(MODEL_NAME, "champion", str(target))
    c.set_model_version_tag(MODEL_NAME, str(target), "rollback_at", datetime.now(UTC).isoformat(timespec="seconds"))
    print(f"rolled back: v{current} -> v{target}")
    return 0


def show() -> int:
    c = client()
    champion = champion_version(c)
    versions = c.search_model_versions(f"name='{MODEL_NAME}'")
    print(f"{'version':>7} {'mae':>7} {'run':>9} {'aliases':>12} candidate")
    for v in sorted(versions, key=lambda m: int(m.version)):
        run = c.get_run(v.tags.get("run_id", ""))
        aliases = ",".join(c.get_model_version(MODEL_NAME, v.version).aliases or [])
        marker = "*" if champion == int(v.version) else " "
        mae = run.data.metrics.get("mae", float("nan"))
        run_id = v.tags.get("run_id", "")[:8]
        print(
            f"{marker}{v.version:>6} {mae:>7.3f} {run_id:>9} "
            f"{aliases:>12} {v.tags.get('candidate','')}"
        )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    t = sub.add_parser("train")
    t.add_argument("name")
    t.add_argument("--set-json", default="{}")
    t.add_argument("--feature-set")
    t.add_argument("--drop-zones", nargs="*")
    g = sub.add_parser("gate")
    g.add_argument("version", type=int)
    p = sub.add_parser("promote")
    p.add_argument("version", type=int)
    p.add_argument("--force", action="store_true")
    r = sub.add_parser("rollback")
    r.add_argument("--to", type=int)
    sub.add_parser("show")
    args = parser.parse_args()

    if args.command == "train":
        train(args.name, json.loads(args.set_json), args.feature_set, args.drop_zones)
        return 0
    if args.command == "gate":
        ok, reasons = gates(args.version)
        print("PASS" if ok else "FAIL")
        for reason in reasons:
            print(f"  - {reason}")
        return 0 if ok else 1
    if args.command == "promote":
        return promote(args.version, args.force)
    if args.command == "rollback":
        return rollback(args.to)
    return show()


if __name__ == "__main__":
    raise SystemExit(main())
