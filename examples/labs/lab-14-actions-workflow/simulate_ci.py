"""Run a workflow's `run:` steps locally, in order, and stop at the first failure.

    python simulate_ci.py
    python simulate_ci.py --inject-lint-error

This is not GitHub Actions. It does not run `uses:` steps, it does not have a
clean runner, and it assumes dependencies are already installed. What it does
have is the same commands in the same order, which is enough to prove that the
gate fails when the code is wrong. Installation steps are listed and skipped,
so the simulation never reaches the network.

Tool commands are run through the same interpreter as this script, so `ruff`
and `pytest` resolve even when the environment's Scripts directory is not on
PATH -- the usual case on Windows.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
PROBE = ROOT / "src/sessionlab/_ci_probe.py"
PROBE_SOURCE = "import json  # unused on purpose\n\n\ndef probe():\n    return 1\n"


def localise(command: str) -> str:
    """Run tools with this interpreter instead of relying on PATH."""
    for tool in ("ruff", "pytest"):
        if command.strip().startswith(f"{tool} ") or command.strip() == tool:
            return f'"{sys.executable}" -m {tool}' + command.strip()[len(tool):]
    return command


def commands(workflow_path: Path) -> list[tuple[str, str]]:
    workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8")) or {}
    collected: list[tuple[str, str]] = []
    for job in (workflow.get("jobs") or {}).values():
        for step in job.get("steps") or []:
            run = step.get("run")
            if run:
                collected.append((step.get("name", "run"), str(run)))
    return collected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workflow", default=".github/workflows/quality.yml")
    parser.add_argument("--inject-lint-error", action="store_true",
                        help="add a file the linter must reject, then expect a failure")
    args = parser.parse_args()

    workflow_path = ROOT / args.workflow
    if not workflow_path.exists():
        print(f"no workflow at {workflow_path}")
        return 2

    if args.inject_lint_error:
        PROBE.write_text(PROBE_SOURCE, encoding="utf-8")

    failures = 0
    try:
        print(f"simulating {args.workflow} (installation steps are skipped)")
        for name, command in commands(workflow_path):
            if "pip install" in command or "pip upgrade" in command:
                print(f"  [SKIP] {name}: {command}")
                continue
            started = time.perf_counter()
            result = subprocess.run(localise(command), cwd=ROOT, shell=True, capture_output=True, text=True)
            elapsed = time.perf_counter() - started
            status = "PASS" if result.returncode == 0 else "FAIL"
            print(f"  [{status}] {name}: {command} ({elapsed:.2f}s)")
            if result.returncode != 0:
                failures += 1
                tail = (result.stdout + result.stderr).strip().splitlines()[-6:]
                for line in tail:
                    print(f"         {line}")
                print("  stopped: the gate failed, which is what a real runner would do")
                break
    finally:
        if PROBE.exists():
            PROBE.unlink()

    if args.inject_lint_error:
        print("\ngate verdict:", "caught the injected defect" if failures else "MISSED the injected defect")
        return 0 if failures else 1

    print(f"\nworkflow simulation: {'failed' if failures else 'passed'}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
