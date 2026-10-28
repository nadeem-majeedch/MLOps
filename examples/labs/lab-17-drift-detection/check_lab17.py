"""Acceptance check for Lab 17.

    python check_lab17.py [--monitor monitor.py]

Four weeks, two signals, and the two cases that keep them apart: drift without
regression, and regression without drift.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "_shared"))

from labkit import Lab  # noqa: E402

BATCHES = ["week0", "week1", "week2", "week3"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--monitor", default="monitor.py")
    args = parser.parse_args()
    lab = Lab("L17", "Detect drift and decide what to do")

    built = subprocess.run([sys.executable, "make_batches.py"], cwd=ROOT, capture_output=True, text=True)
    lab.check("the four batches are built", built.returncode == 0, (built.stderr.strip().splitlines() or [""])[-1])

    out = ROOT / "artifacts/monitor.json"
    proc = subprocess.run([sys.executable, args.monitor, "--json", str(out)], cwd=ROOT, capture_output=True, text=True)
    lab.check("the monitor runs", proc.returncode == 0 and out.exists(),
              (proc.stderr.strip().splitlines() or [""])[-1])
    if not out.exists():
        return lab.finish()

    report = json.loads(out.read_text(encoding="utf-8"))
    rows = {row["batch"]: row for row in report.get("batches", [])}
    lab.equal("all four weeks are reported", sorted(rows), BATCHES)
    if sorted(rows) != BATCHES:
        return lab.finish()

    for name, row in rows.items():
        lab.check(f"{name} reports a psi for every feature",
                  all("psi" in value and "severity" in value for value in row["features"].values()),
                  str(row["features"])[:80])

    lab.equal("the reference week is stable", rows["week0"]["decision"], "ok")
    lab.check("the reference week reports no drift",
              all(value["severity"] == "stable" for value in rows["week0"]["features"].values()),
              str({k: v["psi"] for k, v in rows["week0"]["features"].items()}))

    week1 = rows["week1"]
    hours_severity = week1["features"]["hours"]["severity"]
    lab.check("week1's shift in hours is detected", hours_severity in {"warn", "alert"},
              f"psi {week1['features']['hours']['psi']} -> {hours_severity}")
    lab.check("week1's accuracy holds", week1["performance"]["relative_change"] < 0.15,
              f"relative {week1['performance']['relative_change']}")
    lab.equal("drift without regression leads to investigation, not retraining", week1["decision"], "investigate")

    week2 = rows["week2"]
    lab.check("week2's inputs look unchanged",
              max(value["psi"] for value in week2["features"].values()) < 0.10,
              f"max psi {max(v['psi'] for v in week2['features'].values())}")
    lab.check("week2's accuracy has fallen", week2["performance"]["relative_change"] >= 0.15,
              f"relative {week2['performance']['relative_change']}")
    lab.equal("a regression with no drift is a retraining decision", week2["decision"], "retrain")

    lab.equal("the control week is quiet", rows["week3"]["decision"], "ok")
    lab.check("the control week stays under the warning threshold",
              max(value["psi"] for value in rows["week3"]["features"].values()) < 0.10,
              f"max psi {max(v['psi'] for v in rows['week3']['features'].values())}")

    lab.equal("only the two interesting weeks are alerted", sorted(report.get("alerts", [])),
              ["week1: investigate", "week2: retrain"])
    lab.check("the drift measure is sensitive to shape, not only to the mean",
              abs(week2["features"]["hours"]["psi"]) < 0.05 and week1["features"]["hours"]["psi"] > 0.10,
              "week2 mean shifted with the labels, week1 inputs moved")

    return lab.finish()


if __name__ == "__main__":
    raise SystemExit(main())
