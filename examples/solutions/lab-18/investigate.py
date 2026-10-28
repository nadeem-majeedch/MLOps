"""Reference solution for Lab 18: locate, attribute, decide."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

LOGS = Path("data/predictions.jsonl")
SLICES = {
    "hours>6": lambda frame: frame["hours"] > 6,
    "hours<=6": lambda frame: frame["hours"] <= 6,
    "prior_score<50": lambda frame: frame["prior_score"] < 50,
    "prior_score>=50": lambda frame: frame["prior_score"] >= 50,
}


def mae(series: pd.Series) -> float:
    return round(float(series.mean()), 4)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()

    frame = pd.read_json(LOGS, lines=True)
    frame["when"] = pd.to_datetime(frame["when"])
    frame["date"] = frame["when"].dt.strftime("%Y-%m-%d")
    frame["error"] = (frame["prediction"] - frame["actual"]).abs()

    daily = (
        frame.groupby(["date", "version"])
        .agg(rows=("error", "size"), mae=("error", "mean"))
        .reset_index()
        .sort_values("date")
    )
    daily["mae"] = daily["mae"].round(4)

    before = frame[frame["version"] == "v3"]
    after = frame[frame["version"] == "v4"]

    # The overall daily average does not move: v4 is better on short sessions
    # and much worse on long ones. The change point has to be found where the
    # regression lives, so track the long-session slice by day.
    long_sessions = frame[frame["hours"] > 6]
    long_daily = (
        long_sessions.groupby(["date", "version"])
        .agg(rows=("error", "size"), mae=("error", "mean"))
        .reset_index()
        .sort_values("date")
    )
    baseline = float(long_daily[long_daily["version"] == "v3"]["mae"].median())
    jumped = long_daily[long_daily["mae"] > baseline * 1.5]
    if jumped.empty:
        raise SystemExit("no change point found in the long-session slice")
    onset = jumped.iloc[0]
    suspect = str(onset["version"])
    onset_date = str(onset["date"])

    slices = []
    for name, selector in SLICES.items():
        old_mae = mae(before.loc[selector(before), "error"])
        new_mae = mae(after.loc[selector(after), "error"])
        slices.append({"name": name, "v3_mae": old_mae, "v4_mae": new_mae,
                       "delta": round(new_mae - old_mae, 4)})
    worst = max(slices, key=lambda row: row["delta"])

    overall_before = mae(before["error"])
    overall_after = mae(after["error"])
    share = round(100 * float((after["hours"] > 6).mean()), 1)
    rationale = (
        f"The overall number understates the damage: MAE {overall_before} -> {overall_after} looks like a "
        f"bad week, while {worst['name']} ({share}% of traffic) went {worst['v3_mae']} -> {worst['v4_mae']} "
        f"(+{worst['delta']} minutes) and short sessions actually improved. "
        f"The step change is on {onset_date}, the day {suspect} took over. Restore v3 now; retrain only "
        f"after the long-session rows are back in the training data."
    )

    report = {
        "onset_date": onset_date,
        "suspect_version": suspect,
        "daily": daily.to_dict(orient="records"),
        "slice_daily": long_daily.round(4).to_dict(orient="records"),
        "slices": slices,
        "worst_slice": worst["name"],
        "decision": {"action": "rollback", "target_version": "v3", "rationale": rationale},
    }

    print(f"onset {onset_date} on {suspect} (v3 long-session median mae {baseline:.3f})")
    print(f"overall: v3 {overall_before} -> v4 {overall_after} -- the average understates the change")
    for row in slices:
        print(f"  {row['name']:<15} v3 {row['v3_mae']:.3f}  v4 {row['v4_mae']:.3f}  delta {row['delta']:+.3f}")
    print(f"decision: {report['decision']['action']} to {report['decision']['target_version']}")

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
