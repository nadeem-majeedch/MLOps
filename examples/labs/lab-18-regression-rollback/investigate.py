"""Lab 18 starter: a weekly average that hides the problem.

    python make_logs.py
    python investigate.py --json artifacts/investigation.json

The report below groups by week, which is the interval the dashboard uses. It
says things got worse. It cannot say when, for whom, or what to do.

Your job:

1. Compute MAE per day so the change point is visible, not averaged away.
2. Compute MAE per version and per slice, and find the slice where the new
   version is materially worse. Slice on `hours` (above and below 6) and on
   `prior_score` (below and above 50).
3. Decide: roll back, retrain, or keep monitoring. Justify with the numbers you
   computed and name the version you would restore.

Report contract (`--json`):

    {"onset_date": "YYYY-MM-DD", "suspect_version": "v4",
     "daily": [{"date": str, "version": str, "rows": int, "mae": float}, ...],
     "slice_daily": [...same shape, for the slice where the regression lives...],
     "slices": [{"name": str, "v3_mae": float, "v4_mae": float, "delta": float}, ...],
     "worst_slice": str,
     "decision": {"action": "rollback" | "retrain" | "monitor",
                  "target_version": str, "rationale": str}}
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

LOGS = Path("data/predictions.jsonl")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()

    frame = pd.read_json(LOGS, lines=True)
    frame["when"] = pd.to_datetime(frame["when"])
    frame["error"] = (frame["prediction"] - frame["actual"]).abs()
    frame["week"] = frame["when"].dt.isocalendar().week

    print("week  version  rows   mae")
    weekly = frame.groupby(["week", "version"]).agg(rows=("error", "size"), mae=("error", "mean"))
    for (week, version), row in weekly.iterrows():
        print(f"{week:>4}  {version:<7}  {int(row['rows']):>4}  {row['mae']:.3f}")

    # TODO: per-day mae and the change point.
    # TODO: per-slice mae for both versions and the worst slice.
    # TODO: a decision with a target version and a rationale grounded in the
    #       numbers above.

    report = {"onset_date": "", "suspect_version": "", "daily": [], "slice_daily": [], "slices": [],
              "worst_slice": "", "decision": {"action": "", "target_version": "", "rationale": ""}}
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
