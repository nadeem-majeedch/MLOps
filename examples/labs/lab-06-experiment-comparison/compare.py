"""Lab 06 starter: turn the tracking store into a decision.

    python compare.py --json artifacts/comparison.json

Required output shape:

    {"experiment": "lab06-comparison",
     "best": {"run_name": str, "mae": float},
     "weakest_slice": {"run_name": str, "slice": str, "mae": float, "relative": float},
     "table": [{"run_name": str, "mae": float, "mae_section_A": float,
                "mae_section_B": float, "mae_section_C": float}, ...]}

`weakest_slice` is the section with the highest MAE for the best run, expressed
against that run's overall MAE: relative = (slice_mae - mae) / mae.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def comparison(tracking_uri: str, experiment: str) -> dict:
    raise NotImplementedError("read the runs with MlflowClient and build the report")


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
