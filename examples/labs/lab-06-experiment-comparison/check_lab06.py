"""Acceptance check for Lab 06.

    python check_lab06.py [--experiments experiments.py] [--compare compare.py]
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "_shared"))

from labkit import Lab  # noqa: E402

EXPERIMENT = "lab06-comparison"
TRACKING = ROOT / "mlruns"


def run(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, script, *args], cwd=ROOT, capture_output=True, text=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiments", default="experiments.py")
    parser.add_argument("--compare", default="compare.py")
    args = parser.parse_args()
    lab = Lab("L06", "Compare experiments from the tracking store")

    shutil.rmtree(TRACKING, ignore_errors=True)
    shutil.rmtree(ROOT / "artifacts", ignore_errors=True)

    trained = run(args.experiments)
    lab.check("experiments.py completes", trained.returncode == 0,
              (trained.stderr.strip().splitlines() or ["no stderr"])[-1])
    if trained.returncode != 0:
        return lab.finish()

    from mlflow import MlflowClient

    client = MlflowClient(tracking_uri=TRACKING.as_uri())
    experiment = client.get_experiment_by_name(EXPERIMENT)
    if not lab.check("experiment exists in the local store", experiment is not None, EXPERIMENT):
        return lab.finish()

    runs = client.search_runs([experiment.experiment_id], order_by=["metrics.mae ASC"])
    lab.equal("four runs are recorded", len(runs), 4)
    if not runs:
        return lab.finish()

    required_params = {"trees", "depth", "features", "seed"}
    required_metrics = {"mae", "rmse", "r2", "mae_section_A", "mae_section_B", "mae_section_C"}
    required_tags = {"data_hash", "code_version"}

    params_ok, metrics_ok, tags_ok, models_ok = [], [], [], []
    for recorded in runs:
        params_ok.append(required_params <= set(recorded.data.params))
        metrics_ok.append(required_metrics <= set(recorded.data.metrics))
        tags_ok.append(required_tags <= set(recorded.data.tags))
        artifacts = [a.path for a in client.list_artifacts(recorded.info.run_id, "model")]
        models_ok.append("model/MLmodel" in artifacts)

    lab.check("every run logs its parameters", all(params_ok), f"{sum(params_ok)}/4 runs")
    lab.check("every run logs per-section metrics", all(metrics_ok), f"{sum(metrics_ok)}/4 runs")
    lab.check("every run is tagged with data and code versions", all(tags_ok), f"{sum(tags_ok)}/4 runs")
    lab.check("every run stores a model artifact", all(models_ok), f"{sum(models_ok)}/4 runs")

    names = sorted(recorded.data.tags.get("mlflow.runName") for recorded in runs)
    lab.equal("the four configurations are present", names, ["baseline", "deep", "no_sleep", "shallow"])

    compared = run(args.compare, "--json", "artifacts/comparison.json")
    report_path = ROOT / "artifacts/comparison.json"
    lab.check("compare.py writes a report", compared.returncode == 0 and report_path.exists(),
              (compared.stderr.strip().splitlines() or ["no stderr"])[-1])
    if not report_path.exists():
        return lab.finish()

    report = json.loads(report_path.read_text(encoding="utf-8"))
    best_run = runs[0]
    best_name = best_run.data.tags.get("mlflow.runName")
    lab.equal("best run is the lowest MAE in the store", report.get("best", {}).get("run_name"), best_name)
    lab.equal("best MAE matches the store", round(report.get("best", {}).get("mae", -1), 4),
              round(best_run.data.metrics["mae"], 4))

    slices = {k.removeprefix("mae_section_"): v for k, v in best_run.data.metrics.items()
              if k.startswith("mae_section_")}
    weakest = max(slices, key=slices.get)
    lab.equal("weakest slice is the worst section of the best run",
              report.get("weakest_slice", {}).get("slice"), weakest)
    lab.equal("weakest slice MAE matches the store",
              report.get("weakest_slice", {}).get("mae"), round(slices[weakest], 4))
    lab.check("weakest slice is reported relative to overall MAE",
              abs(report["weakest_slice"]["relative"] - round((slices[weakest] - best_run.data.metrics["mae"]) / best_run.data.metrics["mae"], 4)) < 1e-6,
              f"relative={report['weakest_slice'].get('relative')}")
    lab.equal("the comparison table lists every run", len(report.get("table", [])), 4)

    return lab.finish()


if __name__ == "__main__":
    raise SystemExit(main())
