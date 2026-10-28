"""Acceptance check for Lab 07.

    python check_lab07.py [--tests tests] [--fixed pipeline]

A leak test is only useful if it goes red on the leaky code. This runs the
student's suite twice: once against `leaky_pipeline`, once against the fixed
`pipeline`, and requires a specific failure in the first case and none in the
second.
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

REQUIRED_FAILURES = {
    "test_no_target_derived_feature",
    "test_students_do_not_cross_the_split",
    "test_imputer_is_fitted_on_training_rows_only",
}


def pytest_run(test_dir: str, module: str) -> subprocess.CompletedProcess:
    env = dict(os.environ, LAB07_PIPELINE=module)
    return subprocess.run(
        [sys.executable, "-m", "pytest", test_dir, "-q", "--tb=no", "-rf"],
        cwd=ROOT, capture_output=True, text=True, env=env,
    )


def failed_names(output: str) -> set[str]:
    names = set()
    for line in output.splitlines():
        if "::" in line and ("FAILED" in line or "ERROR" in line):
            names.add(line.split("::")[-1].split()[0])
    return names


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tests", default="tests")
    parser.add_argument("--fixed", default="pipeline")
    args = parser.parse_args()
    lab = Lab("L07", "Tests that catch leakage")

    red = pytest_run(args.tests, "leaky_pipeline")
    lab.check("suite fails against the leaky pipeline", red.returncode != 0, f"exit {red.returncode}")
    caught = failed_names(red.stdout)
    for name in sorted(REQUIRED_FAILURES):
        lab.check(f"catches {name.removeprefix('test_')}", name in caught, f"failed: {sorted(caught)}" or "none")

    green = pytest_run(args.tests, args.fixed)
    lab.check("suite passes against the fixed pipeline", green.returncode == 0,
              (green.stdout.strip().splitlines() or ["no output"])[-1])

    extra = failed_names(red.stdout) - REQUIRED_FAILURES
    lab.check("no unrelated tests fail on the leaky pipeline", not extra, f"also failed: {sorted(extra)}" if extra else "clean")

    return lab.finish()


if __name__ == "__main__":
    raise SystemExit(main())
