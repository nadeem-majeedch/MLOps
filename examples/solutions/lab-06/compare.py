"""Reference solution for Lab 06: read the store, not your memory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from mlflow import MlflowClient

SLICE_PREFIX = "mae_section_"


def comparison(tracking_uri: str, experiment: str) -> dict:
    client = MlflowClient(tracking_uri=tracking_uri)
    found = client.get_experiment_by_name(experiment)
    if found is None:
        raise SystemExit(f"experiment {experiment!r} not found at {tracking_uri}")

    runs = client.search_runs([found.experiment_id], order_by=["metrics.mae ASC"])
    table = []
    for run in runs:
        metrics = run.data.metrics
        row = {"run_name": run.data.tags.get("mlflow.runName", run.info.run_id[:8]),
               "mae": round(metrics["mae"], 4)}
        for key, value in metrics.items():
            if key.startswith(SLICE_PREFIX):
                row[key] = round(value, 4)
        table.append(row)

    if not table:
        raise SystemExit("no runs to compare")

    best = table[0]
    slices = {k: v for k, v in best.items() if k.startswith(SLICE_PREFIX)}
    weakest_name = max(slices, key=slices.get)
    weakest = {
        "run_name": best["run_name"],
        "slice": weakest_name.removeprefix(SLICE_PREFIX),
        "mae": slices[weakest_name],
        "relative": round((slices[weakest_name] - best["mae"]) / best["mae"], 4),
    }
    return {
        "experiment": experiment,
        "best": {"run_name": best["run_name"], "mae": best["mae"]},
        "weakest_slice": weakest,
        "table": table,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tracking-uri", default=str(Path("mlruns").resolve().as_uri()))
    parser.add_argument("--experiment", default="lab06-comparison")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()

    report = comparison(args.tracking_uri, args.experiment)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
