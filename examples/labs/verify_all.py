"""Verify every lab kit end to end, without touching the lab directories.

    python examples/labs/verify_all.py            # all labs
    python examples/labs/verify_all.py --only 07  # one lab

For each lab:

1. copy the lab directory to `.verify/lab-NN/`;
2. overlay the reference solution, if the lab has one;
3. run the data generator (setup);
4. run the acceptance checker;
5. report pass or fail with the last useful line of output.

This is the command to run after editing a kit. It is also the honest record of
what was executed: a skipped check would show as a failure, not as a pass.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOLUTIONS = ROOT.parent / "solutions"
SCRATCH = ROOT / ".verify"


@dataclass
class LabCase:
    key: str
    folder: str
    setup: list[list[str]] = field(default_factory=list)
    check: list[str] = field(default_factory=list)
    extra_files: list[tuple[str, str]] = field(default_factory=list)


CASES = [
    LabCase("01", "lab-01-notebook-reproducibility",
            [["../_shared/make_sessions.py", "--out", "data/sessions.csv"]],
            ["check_lab01.py", "notebook_v2.py"]),
    LabCase("02", "lab-02-refactor-to-project",
            [["../_shared/make_sessions.py", "--out", "data/sessions.csv"]],
            ["check_lab02.py", "--module", "sessionlab.train"]),
    LabCase("03", "lab-03-data-defects", [["make_batches.py"]], ["check_lab03.py"]),
    LabCase("04", "lab-04-dataset-versioning",
            [["../_shared/make_sessions.py", "--out", "data/sessions.csv"]], ["check_lab04.py"]),
    LabCase("05", "lab-05-deterministic-pipeline",
            [["../_shared/make_sessions.py", "--out", "data/sessions.csv"]], ["check_lab05.py"]),
    LabCase("06", "lab-06-experiment-comparison",
            [["../_shared/make_sessions.py", "--out", "data/sessions.csv"]], ["check_lab06.py"]),
    LabCase("07", "lab-07-leakage-tests", [["make_data.py"]], ["check_lab07.py"]),
    LabCase("08", "lab-08-quality-gate", [], ["check_lab08.py"]),
    LabCase("09", "lab-09-release-candidates", [], ["check_lab09.py"]),
    LabCase("10", "lab-10-fastapi-service",
            [["../_shared/make_sessions.py", "--out", "data/sessions.csv"]], ["check_lab10.py"]),
    LabCase("11", "lab-11-request-triage",
            [["../_shared/make_sessions.py", "--out", "data/sessions.csv"]], ["check_lab11.py"]),
    LabCase("12", "lab-12-docker-image",
            [["../_shared/make_sessions.py", "--out", "data/sessions.csv"], ["make_model.py"]],
            ["check_lab12.py"]),
    LabCase("13", "lab-13-dependency-conflict", [["make_data.py"]], ["check_lab13.py"]),
    LabCase("14", "lab-14-actions-workflow", [], ["check_lab14.py"],
            extra_files=[("quality.yml", ".github/workflows/quality.yml")]),
    LabCase("15", "lab-15-release-validation", [], ["check_lab15.py"],
            extra_files=[("release.yml", ".github/workflows/release.yml")]),
    LabCase("16", "lab-16-orchestration", [["make_data.py"]], ["check_lab16.py"]),
    LabCase("17", "lab-17-drift-detection", [["make_batches.py"]], ["check_lab17.py"]),
    LabCase("18", "lab-18-regression-rollback", [["make_logs.py"]], ["check_lab18.py"]),
    LabCase("19", "lab-19-security-review", [], ["check_lab19.py"]),
    LabCase("20", "lab-20-incident", [], ["check_lab20.py"]),
]


def overlay(solution: Path, destination: Path, extra: list[tuple[str, str]]) -> None:
    if not solution.exists():
        return
    shutil.copytree(solution, destination, dirs_exist_ok=True)
    for source, target in extra:
        origin = solution / source
        if origin.exists():
            (destination / target).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(origin, destination / target)


def run_case(case: LabCase) -> tuple[bool, str, float]:
    work = SCRATCH / f"lab-{case.key}"
    shutil.rmtree(work, ignore_errors=True)
    shutil.copytree(ROOT / case.folder, work)
    shutil.copytree(ROOT / "_shared", SCRATCH / "_shared", dirs_exist_ok=True)
    overlay(SOLUTIONS / f"lab-{case.key}", work, case.extra_files)

    started = time.perf_counter()
    for command in case.setup:
        result = subprocess.run([sys.executable, *command], cwd=work, capture_output=True, text=True)
        if result.returncode != 0:
            tail = (result.stdout + result.stderr).strip().splitlines()[-3:]
            return False, "setup failed: " + " | ".join(tail), time.perf_counter() - started

    check = subprocess.run([sys.executable, *case.check], cwd=work, capture_output=True, text=True)
    elapsed = time.perf_counter() - started
    lines = [line for line in check.stdout.strip().splitlines() if line.strip()]
    summary = next((line for line in reversed(lines) if "checks passed" in line), lines[-1] if lines else "no output")
    if check.returncode != 0:
        failing = [line.strip() for line in lines if "still failing" in line]
        detail = "; ".join(failing[:3]) if failing else (check.stderr.strip().splitlines() or [""])[-1]
        return False, (summary + "; " + detail).strip("; "), elapsed
    return True, summary, elapsed


def preflight() -> list[str]:
    problems = []
    for module in ("pandas", "sklearn", "mlflow", "yaml", "pytest"):
        probe = subprocess.run([sys.executable, "-c", f"import {module}"], capture_output=True, text=True)
        if probe.returncode != 0:
            problems.append(f"{module} is missing")
    ruff = subprocess.run([sys.executable, "-m", "ruff", "--version"], capture_output=True, text=True)
    if ruff.returncode != 0:
        problems.append("ruff is missing")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", nargs="*", help="lab numbers, e.g. 03 07")
    parser.add_argument("--keep", action="store_true", help="keep the scratch copies")
    args = parser.parse_args()

    cases = [case for case in CASES if not args.only or case.key in args.only]
    problems = preflight()
    if problems:
        print(f"this interpreter ({sys.executable}) cannot run every lab:")
        for problem in problems:
            print(f"  - {problem}")
        print("\ninstall the lab requirements and run this script with that interpreter:")
        print("  python -m pip install -r examples/requirements-labs.txt")
        return 2

    SCRATCH.mkdir(exist_ok=True)
    results = []
    for case in cases:
        ok, summary, elapsed = run_case(case)
        results.append((case.key, ok, summary, elapsed))
        print(f"  [{'PASS' if ok else 'FAIL'}] lab {case.key} ({elapsed:.1f}s) {summary}")

    passed = sum(1 for _, ok, _, _ in results if ok)
    print(f"\n{passed}/{len(results)} labs verified")
    if not args.keep:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
