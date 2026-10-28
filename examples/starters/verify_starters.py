"""Run every starter project the way a student would, and report what happened.

    python examples/starters/verify_starters.py
    python examples/starters/verify_starters.py --only advanced

Each project is run in its own directory with the interpreter running this
script, so the virtual environment you invoke it from is the one used. Expected
exit codes are explicit: the advanced pipeline deliberately exits 2 on drift, and
a checker that treats that as failure would teach the wrong lesson.

Nothing is installed. If a dependency is missing, the script says so instead of
attempting a network install.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable


def run(project: Path, args: list[str], expected: tuple[int, ...] = (0,)) -> tuple[bool, str]:
    result = subprocess.run(
        [PY, *args], cwd=project, capture_output=True, text=True, timeout=300
    )
    ok = result.returncode in expected
    output = (result.stdout + result.stderr).strip().splitlines()
    tail = output[-1] if output else "(no output)"
    return ok, f"exit {result.returncode}: {tail[:110]}"


def beginner() -> list[tuple[str, bool, str]]:
    project = HERE / "beginner-support-risk"
    checks = [
        ("generate data", *run(project, ["make_data.py"])),
        ("train", *run(project, ["train.py"])),
        ("tests", *run(project, ["-m", "pytest"])),
    ]
    return [(f"beginner: {name}", ok, detail) for name, ok, detail in checks]


def intermediate() -> list[tuple[str, bool, str]]:
    project = HERE / "intermediate-eta-service"
    checks = [
        ("generate data", *run(project, ["make_data.py"])),
        ("train", *run(project, ["train.py"])),
        ("tests", *run(project, ["-m", "pytest"])),
    ]
    return [(f"intermediate: {name}", ok, detail) for name, ok, detail in checks]


def advanced() -> list[tuple[str, bool, str]]:
    project = HERE / "advanced-monitoring-pipeline"
    checks = [
        ("generate data", *run(project, ["make_data.py"])),
        ("tests", *run(project, ["-m", "pytest"])),
        ("validate", *run(project, ["cli.py", "validate"])),
        ("train", *run(project, ["cli.py", "train"])),
        ("promote", *run(project, ["cli.py", "promote", "--note", "verify"])),
        # Drift is expected on the generated batch: exit 2 is the correct result.
        ("monitor (drift expected)", *run(project, ["cli.py", "monitor"], expected=(2,))),
    ]
    return [(f"advanced: {name}", ok, detail) for name, ok, detail in checks]


RUNNERS = {"beginner": beginner, "intermediate": intermediate, "advanced": advanced}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", choices=sorted(RUNNERS), action="append")
    args = parser.parse_args()

    selected = args.only or sorted(RUNNERS)
    results: list[tuple[str, bool, str]] = []
    for name in selected:
        results.extend(RUNNERS[name]())

    width = max(len(name) for name, _, _ in results)
    failures = 0
    for name, ok, detail in results:
        print(f"{'PASS' if ok else 'FAIL'}  {name:<{width}}  {detail}")
        failures += 0 if ok else 1

    print(f"\n{len(results) - failures}/{len(results)} checks passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
