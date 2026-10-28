"""Acceptance check for Lab 14.

    python check_lab14.py

The workflow must lint, test, and fail when the code is wrong. The last part is
the only one that matters: a gate nobody has seen fail is a decoration.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "_shared"))

from labkit import Lab  # noqa: E402


def run(args: list[str]) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONPATH=str(ROOT / "src"))
    return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True, env=env)


def main() -> int:
    lab = Lab("L14", "A workflow that can fail")

    linted = run(["lint_workflow.py"])
    lab.check("the workflow passes every structural check", linted.returncode == 0,
              (linted.stdout.strip().splitlines() or ["no output"])[-1])
    for line in linted.stdout.splitlines():
        if line.strip().startswith("[FAIL]"):
            print("       " + line.strip())

    simulated = run(["simulate_ci.py"])
    lab.check("the workflow's commands pass locally", simulated.returncode == 0,
              (simulated.stdout.strip().splitlines() or ["no output"])[-1])
    lab.check("lint runs before tests",
              simulated.stdout.find("ruff") != -1 and
              simulated.stdout.find("ruff") < simulated.stdout.find("pytest"),
              "order in the simulated log")

    caught = run(["simulate_ci.py", "--inject-lint-error"])
    lab.check("an injected defect fails the gate", caught.returncode == 0,
              (caught.stdout.strip().splitlines() or ["no output"])[-1])
    lab.check("the simulation says it caught the defect", "caught the injected defect" in caught.stdout,
              caught.stdout.strip().splitlines()[-1] if caught.stdout else "no output")

    workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
    lab.check("no step swallows a failure", "|| true" not in workflow and "continue-on-error" not in workflow,
              "searched for || true and continue-on-error")
    lab.check("the workflow runs on pull requests", "pull_request" in workflow, "trigger")
    lab.check("permissions are read-only", "write-all" not in workflow, "permissions block")

    return lab.finish()


if __name__ == "__main__":
    raise SystemExit(main())
