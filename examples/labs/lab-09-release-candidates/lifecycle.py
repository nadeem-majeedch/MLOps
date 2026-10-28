"""Lab 09 starter: versions, aliases, promotion, rollback.

    python lifecycle.py register candidates/baseline_v1.json
    python lifecycle.py register candidates/deeper_v2.json
    python lifecycle.py promote 1
    python lifecycle.py promote 2
    python lifecycle.py rollback
    python lifecycle.py show --json artifacts/history.json

The registry is MLflow's file store in `./mlruns`: no server, no account. Every
command below is implemented except the parts marked TODO.

What "promote" must mean here:

* The gate from the policy file runs first; a blocked candidate must not move
  the alias.
* Promotion records `promoted_at` and `promoted_from` on the version, so a
  rollback does not need a human to remember what was there before.
* Rollback moves `champion` back to `promoted_from` and tags `rollback_at`.
"""

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
    """Create a run and a model version from a candidate metrics file."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    metrics = payload["metrics"]
    c = client()
    mlflow.set_experiment("lab09-registry")

    # A real artifact, so loading a version is a real operation.
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
    except Exception:  # noqa: BLE001 - no alias yet is a normal state
        return None


def run_metrics(c: MlflowClient, version: int) -> dict:
    tags = c.get_model_version(MODEL_NAME, str(version)).tags
    metrics = dict(c.get_run(tags["run_id"]).data.metrics)
    metrics["zones"] = {k.removeprefix("mae_zone_"): v for k, v in metrics.items() if k.startswith("mae_zone_")}
    return metrics


def gate(version: int) -> tuple[bool, list[str]]:
    """Apply policy.yaml against the current champion.

    TODO 1: implement the same rules as the Module 09 gate: absolute ceiling,
            overall regression, per-zone limits, and the dropped-zone rule
            (the dropped zones are stored as a comma-separated tag).
    """
    raise NotImplementedError("gate")


def promote(version: int, force: bool = False) -> int:
    """Move the champion alias, after the gate, recording where it came from.

    TODO 2: implement. Blocked candidates return exit code 1 and leave the
            alias untouched.
    """
    raise NotImplementedError("promote")


def rollback(to: int | None = None) -> int:
    """Move the champion back to `promoted_from`, or to an explicit version.

    TODO 3: implement. Return exit code 2 when there is nothing to roll back to.
    """
    raise NotImplementedError("rollback")


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
