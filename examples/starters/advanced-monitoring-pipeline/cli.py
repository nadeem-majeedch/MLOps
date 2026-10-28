"""One command per stage, and one command that runs the lot.

    python cli.py validate
    python cli.py train
    python cli.py promote --note "baseline"
    python cli.py monitor
    python cli.py rollback
    python cli.py all

Exit codes, because CI reads them:

    0  every step passed
    1  validation, training, or a promotion gate failed
    2  drift exceeded the threshold (the model may still be fine -- read the report)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from pipeline import Registry, load, report, train  # noqa: E402
from pipeline.data import FEATURES  # noqa: E402


def read_config(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def cmd_validate(config: dict) -> int:
    frame = load(ROOT / config["data"])
    print(f"valid       {len(frame)} rows, {frame['machine_id'].nunique()} machines, "
          f"{int(frame['failure_within_7d'].sum())} positives")
    batch = load(ROOT / config["batch"], require_target=False)
    print(f"valid batch {len(batch)} rows, {batch['machine_id'].nunique()} machines, unlabelled")
    return 0


def cmd_train(config: dict) -> tuple[int, dict | None]:
    frame = load(ROOT / config["data"])
    meta = train(
        frame,
        output_dir=ROOT / config["artifacts"],
        seed=int(config["seed"]),
        target_recall=float(config["target_recall"]),
        holdout_machines=int(config["holdout_machines"]),
    )
    metrics = meta["metrics"]
    print(f"train rows  {meta['train_rows']}  machines {meta['train_machines']}")
    print(f"test        {metrics['test_rows']} rows  held out {meta['test_machines']}")
    print(f"roc_auc     {metrics['roc_auc']:.4f}")
    print(f"pr_auc      {metrics['pr_auc']:.4f}")
    print(f"recall      {metrics['recall']:.4f} at threshold {metrics['threshold']:.4f} "
          f"(chosen for {meta['params']['target_recall']:.0%} train recall)")
    print(f"precision   {metrics['precision']:.4f}")
    print(f"confusion   tp={metrics['true_positives']} fn={metrics['false_negatives']} "
          f"fp={metrics['false_positives']}")
    print(f"artifact    {ROOT / config['artifacts'] / 'model.joblib'}")
    return 0, meta


def cmd_promote(config: dict, meta: dict, note: str) -> int:
    registry = Registry(ROOT / config["registry"])
    policy = config["policy"]
    ok, reasons = registry.decision(meta, policy)
    if not ok:
        print("BLOCKED by promotion policy:")
        for reason in reasons:
            print(f"  - {reason}")
        return 1
    entry = registry.register(meta, ROOT / config["artifacts"] / "model.joblib", note)
    registry.promote(entry["version"])
    print(f"registered version {entry['version']} and promoted it to champion")
    return 0


def cmd_monitor(config: dict) -> int:
    reference = load(ROOT / config["data"])
    batch = load(ROOT / config["batch"], require_target=False)
    result = report(reference, batch, FEATURES, float(config["drift"]["psi_threshold"]))
    for name, entry in result["features"].items():
        print(f"{name:22} PSI {entry['psi']:6.3f}  {entry['status']:7} "
              f"mean {entry['reference_mean']} -> {entry['current_mean']}")
    print(f"verdict     {result['verdict']}")
    if result["verdict"] == "drift":
        print("ALERT: input distribution moved. Find the cause before retraining.")
        print(f"drifted: {', '.join(result['drifted'])}")
        return 2
    print("no retraining trigger from input drift alone")
    return 0


def cmd_rollback(config: dict) -> int:
    registry = Registry(ROOT / config["registry"])
    entry = registry.rollback()
    print(f"champion is now version {entry['version']} (roc_auc {entry['metrics']['roc_auc']})")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("stage", choices=["validate", "train", "promote", "monitor", "rollback", "all"])
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "pipeline.yaml")
    parser.add_argument("--note", default="", help="note stored with the registered version")
    args = parser.parse_args()

    config = read_config(args.config)

    if args.stage == "validate":
        return cmd_validate(config)
    if args.stage == "train":
        return cmd_train(config)[0]
    if args.stage == "promote":
        metrics_path = ROOT / config["artifacts"] / "run_meta.json"
        if not metrics_path.exists():
            print(f"nothing to promote: {metrics_path} is missing; run `python cli.py train`")
            return 1
        return cmd_promote(config, json.loads(metrics_path.read_text(encoding="utf-8")), args.note)
    if args.stage == "monitor":
        return cmd_monitor(config)
    if args.stage == "rollback":
        return cmd_rollback(config)

    # `all`: validate, train, gate, promote, monitor.
    if cmd_validate(config) != 0:
        return 1
    code, meta = cmd_train(config)
    if code != 0 or meta is None:
        return code
    code = cmd_promote(config, meta, args.note or "cli all")
    if code != 0:
        return code
    return cmd_monitor(config)


if __name__ == "__main__":
    raise SystemExit(main())
