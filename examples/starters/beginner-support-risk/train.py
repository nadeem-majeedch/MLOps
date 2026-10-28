"""Train the support-risk model.

    python make_data.py
    python train.py
    python train.py --model forest --config config.yaml

Writes `artifacts/model.joblib`, `artifacts/metrics.json`, and
`artifacts/run_meta.json`. Exit code is non-zero if the model misses the metric
floor in the config, which is what makes this script usable in CI later.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from support_risk import load_frame, train  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config.yaml")
    parser.add_argument("--data", type=Path, default=None,
                        help="override the data path from the config")
    parser.add_argument("--model", choices=["logistic", "forest"], default=None,
                        help="override the model kind from the config")
    args = parser.parse_args()

    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    data_path = args.data or ROOT / config["data"]
    output_dir = ROOT / config["output"]
    kind = args.model or config["model"]

    frame = load_frame(data_path)
    meta = train(
        frame,
        output_dir=output_dir,
        kind=kind,
        seed=int(config["seed"]),
        test_size=float(config["test_size"]),
    )

    metrics = meta["metrics"]
    print(f"model        {meta['model_kind']}")
    print(f"train rows   {meta['train_rows']}")
    print(f"test rows    {metrics['test_rows']}")
    print(f"roc_auc      {metrics['roc_auc']:.4f}")
    print(f"accuracy     {metrics['accuracy']:.4f}")
    print(f"recall       {metrics['recall']:.4f}")
    print(f"artifacts    {output_dir}")

    floor = float(config.get("min_roc_auc", 0.0))
    if metrics["roc_auc"] < floor:
        print(f"FAIL: roc_auc {metrics['roc_auc']:.4f} is below the floor {floor:.4f}")
        return 1
    print(f"PASS: roc_auc {metrics['roc_auc']:.4f} >= floor {floor:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
