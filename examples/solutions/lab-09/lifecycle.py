"""Reference solution for Lab 09."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import mlflow
import mlflow.sklearn
import pandas as pd
import yaml
from mlflow import MlflowClient
from sklearn.dummy import DummyRegressor

MODEL_NAME = "session-score"
POLICY = Path("policy.yaml")
TRACKING = Path("mlruns")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def client() -> MlflowClient:
    mlflow.set_tracking_uri(TRACKING.resolve().as_uri())
    return MlflowClient(tracking_uri=TRACKING.resolve().as_uri())


def register(path: Path) -> int:
    payload = json.loads(path.read_text(encoding="utf-8"))
    metrics = payload["metrics"]
    c = client()
    mlflow.set_experiment("lab09-registry")

    model = DummyRegressor(strategy="constant", constant=metrics["mae"]).fit(
        pd.DataFrame({"x": [0.0, 1.0]}), [0.0, 1.0]
    )
    with mlflow.start_run(run_name=payload["candidate"]) as run:
        mlflow.set_tags(
            {
                "candidate": payload["candidate"],
                "data_hash": payload["data_hash"],
                "git_commit": "lab09",
                "dropped_zones": ",".join(payload.get("dropped_zones", [])),
            }
        )
        mlflow.log_metrics(
            {"mae": metrics["mae"], "p95_abs_error": metrics["p95_abs_error"],
             **{f"mae_zone_{z}": v["mae"] for z, v in metrics["zones"].items()}}
        )
        mlflow.log_dict(payload, "evaluation/candidate.json")
        mlflow.sklearn.log_model(model, artifact_path="model")
        run_id = run.info.run_id

    version = mlflow.register_model(f"runs:/{run_id}/model", MODEL_NAME)
    for key, value in {
        "candidate": payload["candidate"],
        "data_hash": payload["data_hash"],
        "run_id": run_id,
        "dropped_zones": ",".join(payload.get("dropped_zones", [])),
    }.items():
        c.set_model_version_tag(MODEL_NAME, version.version, key, value)
    print(f"registered {payload['candidate']} as version {version.version}")
    return int(version.version)


def champion_version(c: MlflowClient) -> int | None:
    try:
        return int(c.get_model_version_by_alias(MODEL_NAME, "champion").version)
    except Exception:  # noqa: BLE001
        return None


def run_metrics(c: MlflowClient, version: int) -> dict:
    tags = c.get_model_version(MODEL_NAME, str(version)).tags
    metrics = dict(c.get_run(tags["run_id"]).data.metrics)
    metrics["zones"] = {k.removeprefix("mae_zone_"): v for k, v in metrics.items() if k.startswith("mae_zone_")}
    return metrics


def gate(version: int) -> tuple[bool, list[str]]:
    policy = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
    c = client()
    candidate = run_metrics(c, version)
    current = champion_version(c)
    reasons: list[str] = []

    dropped = c.get_model_version(MODEL_NAME, str(version)).tags.get("dropped_zones", "")
    if policy.get("forbid_dropped_zones") and dropped:
        reasons.append(f"training data excludes production zones: {dropped}")

    if candidate["mae"] > policy["overall_ceiling"]:
        reasons.append(f"overall_mae {candidate['mae']:.3f} exceeds ceiling {policy['overall_ceiling']}")

    if current is not None and current != version:
        base = run_metrics(c, current)
        allowed = round(base["mae"] * (1 + policy["max_regression"]), 4)
        if candidate["mae"] > allowed:
            reasons.append(
                f"overall_mae {candidate['mae']:.3f} exceeds champion v{current} by more than "
                f"{policy['max_regression']:.0%} (allowed {allowed})"
            )
        for zone, limit in policy.get("zone_limits", {}).items():
            if zone not in candidate["zones"] or zone not in base["zones"]:
                continue
            allowed_zone = round(base["zones"][zone] * (1 + limit), 4)
            if candidate["zones"][zone] > allowed_zone:
                reasons.append(
                    f"zone {zone} mae {candidate['zones'][zone]:.3f} exceeds champion "
                    f"{base['zones'][zone]:.3f} by more than {limit:.0%} (allowed {allowed_zone})"
                )
    return (not reasons), reasons


def promote(version: int, force: bool = False) -> int:
    c = client()
    ok, reasons = gate(version)
    if not ok and not force:
        print(f"BLOCKED v{version}:")
        for reason in reasons:
            print(f"  - {reason}")
        return 1

    previous = champion_version(c)
    c.set_registered_model_alias(MODEL_NAME, "champion", str(version))
    c.set_model_version_tag(MODEL_NAME, str(version), "promoted_at", utc_now())
    c.set_model_version_tag(MODEL_NAME, str(version), "promoted_from", str(previous) if previous else "none")
    print(f"champion -> v{version} (was v{previous})")
    return 0


def rollback(to: int | None = None) -> int:
    c = client()
    current = champion_version(c)
    if current is None:
        print("no champion to roll back")
        return 2
    target = to if to is not None else c.get_model_version(MODEL_NAME, str(current)).tags.get("promoted_from")
    if not target or str(target) == "none":
        print(f"no previous champion recorded for v{current}; pass --to VERSION")
        return 2
    c.set_registered_model_alias(MODEL_NAME, "champion", str(target))
    c.set_model_version_tag(MODEL_NAME, str(target), "rollback_at", utc_now())
    print(f"rolled back: v{current} -> v{target}")
    return 0


def show(as_json: Path | None = None) -> int:
    c = client()
    champion = champion_version(c)
    versions = sorted(c.search_model_versions(f"name='{MODEL_NAME}'"), key=lambda v: int(v.version))
    rows = []
    for version in versions:
        metrics = run_metrics(c, int(version.version))
        rows.append(
            {
                "version": int(version.version),
                "candidate": version.tags.get("candidate", ""),
                "mae": round(metrics.get("mae", float("nan")), 4),
                "aliases": list(version.aliases or []),
                "promoted_from": version.tags.get("promoted_from", ""),
            }
        )
    report = {"champion": champion, "versions": rows}
    if as_json:
        as_json.parent.mkdir(parents=True, exist_ok=True)
        as_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{'v':>3} {'mae':>7} {'aliases':<12} {'from':>5} candidate")
    for row in rows:
        print(f"{row['version']:>3} {row['mae']:>7.3f} {','.join(row['aliases']):<12} "
              f"{row['promoted_from']:>5} {row['candidate']}")
    print(f"champion: v{champion}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    reg = sub.add_parser("register")
    reg.add_argument("path", type=Path)
    pro = sub.add_parser("promote")
    pro.add_argument("version", type=int)
    pro.add_argument("--force", action="store_true")
    rb = sub.add_parser("rollback")
    rb.add_argument("--to", type=int)
    show_parser = sub.add_parser("show")
    show_parser.add_argument("--json", type=Path)
    args = parser.parse_args()

    if args.command == "register":
        register(args.path)
        return 0
    if args.command == "promote":
        return promote(args.version, args.force)
    if args.command == "rollback":
        return rollback(args.to)
    return show(args.json)


if __name__ == "__main__":
    raise SystemExit(main())
