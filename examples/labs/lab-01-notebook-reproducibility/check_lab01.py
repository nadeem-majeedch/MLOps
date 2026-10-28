"""Acceptance check for Lab 01.

Runs a candidate script three times, each in a fresh interpreter with a
different PYTHONHASHSEED, and compares the reports line by line.

    python check_lab01.py notebook_v1.py

Exit code 0 means the three reports were identical.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "_shared"))

from labkit import Lab  # noqa: E402

SEEDS = ["0", "1", "42"]


def run_once(script: Path, hashseed: str) -> tuple[int, str]:
    env = dict(os.environ, PYTHONHASHSEED=hashseed)
    proc = subprocess.run(
        [sys.executable, str(script)], cwd=ROOT, capture_output=True, text=True, env=env
    )
    return proc.returncode, proc.stdout


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("script", nargs="?", default="notebook_v1.py")
    parser.add_argument("--expect", choices=["stable", "unstable"], default="stable")
    args = parser.parse_args()
    lab = Lab("L01", "Reproducible notebook report")

    script = (ROOT / args.script).resolve()
    if not lab.check("script exists", script.exists(), str(script)):
        return lab.finish()

    runs = [(seed, *run_once(script, seed)) for seed in SEEDS]
    for seed, code, out in runs:
        lab.check(f"run with PYTHONHASHSEED={seed} exits 0", code == 0, f"exit {code}")

    outputs = [out for _, _, out in runs]
    identical = len(set(outputs)) == 1
    differing = [line for line in outputs[0].splitlines() if any(line not in o.splitlines() for o in outputs[1:])]
    if args.expect == "stable":
        lab.check("three reports are byte-identical", identical, f"{len(set(outputs))} distinct reports")
        lab.check("report still contains a metric line", "MAE:" in outputs[0], "look for 'MAE: <float>'")
    else:
        lab.check("reports differ across hash seeds", not identical, f"{len(set(outputs))} distinct reports")
        lab.check("at least one line differs", bool(differing), f"example: {differing[0][:60] if differing else 'none'}")

    return lab.finish()


if __name__ == "__main__":
    raise SystemExit(main())
