"""Acceptance check for Lab 18.

    python check_lab18.py [--investigator investigate.py]

The report has to agree with the logs. A convincing narrative built on wrong
numbers is the most expensive kind of wrong.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "_shared"))

from labkit import Lab  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--investigator", default="investigate.py")
    args = parser.parse_args()
    lab = Lab("L18", "Find the regression and decide whether to roll back")

    built = subprocess.run([sys.executable, "make_logs.py"], cwd=ROOT, capture_output=True, text=True)
    lab.check("the logs are generated", built.returncode == 0, (built.stderr.strip().splitlines() or [""])[-1])

    out = ROOT / "artifacts/investigation.json"
    proc = subprocess.run([sys.executable, args.investigator, "--json", str(out)], cwd=ROOT, capture_output=True, text=True)
    lab.check("the investigation runs", proc.returncode == 0 and out.exists(),
              (proc.stderr.strip().splitlines() or [""])[-1])
    if not out.exists():
        return lab.finish()

    report = json.loads(out.read_text(encoding="utf-8"))
    frame = pd.read_json(ROOT / "data/predictions.jsonl", lines=True)
    frame["error"] = (frame["prediction"] - frame["actual"]).abs()

    lab.equal("the change point is the release date", report.get("onset_date"), "2026-10-11")
    lab.equal("the new version is named", report.get("suspect_version"), "v4")
    lab.equal("the worst slice is long sessions", report.get("worst_slice"), "hours>6")

    slices = {row["name"]: row for row in report.get("slices", [])}
    lab.check("both hour slices are reported", {"hours>6", "hours<=6"} <= set(slices), str(sorted(slices)))
    if "hours>6" in slices:
        long_v3 = float(frame[(frame["version"] == "v3") & (frame["hours"] > 6)]["error"].mean())
        long_v4 = float(frame[(frame["version"] == "v4") & (frame["hours"] > 6)]["error"].mean())
        row = slices["hours>6"]
        lab.check("the long-session MAE matches the logs", abs(row["v3_mae"] - long_v3) < 0.02
                  and abs(row["v4_mae"] - long_v4) < 0.02,
                  f"report {row['v3_mae']}/{row['v4_mae']} vs logs {long_v3:.3f}/{long_v4:.3f}")
        lab.check("the long-session regression is material", row["delta"] > 3.0, f"delta {row['delta']}")

    lab.equal("daily detail covers every day", len({row["date"] for row in report.get("daily", [])}), 14)
    lab.check("a slice-level daily series is present", len(report.get("slice_daily", [])) >= 7,
              f"{len(report.get('slice_daily', []))} rows")

    decision = report.get("decision", {})
    lab.equal("the decision is to roll back", decision.get("action"), "rollback")
    lab.equal("the previous version is named", decision.get("target_version"), "v3")
    rationale = str(decision.get("rationale", "")).lower()
    lab.check("the rationale names the slice", "hour" in rationale or "long" in rationale or ">6" in rationale,
              rationale[:100])
    lab.check("the rationale carries a number", any(ch.isdigit() for ch in rationale), rationale[:100])
    lab.check("the rationale says why the average hid it",
              "average" in rationale or "overall" in rationale or "unchanged" in rationale, rationale[:100])

    overall_v3 = float(frame[frame["version"] == "v3"]["error"].mean())
    overall_v4 = float(frame[frame["version"] == "v4"]["error"].mean())
    print(f"\n  evidence: overall v3 {overall_v3:.3f} -> v4 {overall_v4:.3f}; "
          f"long-session error tripled on a fifth of traffic")

    return lab.finish()


if __name__ == "__main__":
    raise SystemExit(main())
