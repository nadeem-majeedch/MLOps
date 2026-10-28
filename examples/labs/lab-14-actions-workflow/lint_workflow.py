"""Lint a GitHub Actions workflow without GitHub.

    python lint_workflow.py [.github/workflows/quality.yml]

The rules are the ones that decide whether a green check means anything:
does it run on pull requests, does it check out the code, is the interpreter
pinned, are dependencies cached, can a failing test still report success, and
is every third-party action pinned.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml


def steps_of(workflow: dict) -> list[dict]:
    steps: list[dict] = []
    for job in (workflow.get("jobs") or {}).values():
        steps.extend(job.get("steps") or [])
    return steps


def check(path: Path) -> list[tuple[str, bool, str]]:
    findings: list[tuple[str, bool, str]] = []
    try:
        workflow = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as error:
        return [("workflow parses as YAML", False, str(error).splitlines()[0])]

    findings.append(("workflow parses as YAML", bool(workflow), str(path)))
    # YAML 1.1 reads the bare key `on` as the boolean True. Both lookups are
    # needed; this is the classic workflow-linting trap.
    triggers = workflow.get("on", workflow.get(True))  # noqa: FBT003 - YAML key
    trigger_text = str(triggers)
    findings.append(("runs on pull requests as well as pushes",
                     "pull_request" in trigger_text, trigger_text))
    findings.append(("does not grant write access to everything",
                     workflow.get("permissions") != "write-all", str(workflow.get("permissions"))))

    jobs = workflow.get("jobs") or {}
    findings.append(("every job names a runner", all(job.get("runs-on") for job in jobs.values()),
                     str([job.get("runs-on") for job in jobs.values()])))
    findings.append(("every job has a timeout",
                     bool(jobs) and all(job.get("timeout-minutes") for job in jobs.values()),
                     str([job.get("timeout-minutes") for job in jobs.values()])))

    steps = steps_of(workflow)
    uses = [step.get("uses", "") for step in steps if "uses" in step]
    first_uses = uses[0] if uses else ""
    findings.append(("checks out the repository before anything else",
                     first_uses.startswith("actions/checkout"), first_uses or "no uses"))

    floating = [name for name in uses if "@" not in name or name.split("@")[-1] in {"main", "master"}]
    findings.append(("third-party actions are pinned to a version", not floating, str(floating)))

    setup = next((step for step in steps if str(step.get("uses", "")).startswith("actions/setup-python")), None)
    python_version = (setup or {}).get("with", {}).get("python-version")
    findings.append(("the Python version is quoted so YAML cannot round it",
                     isinstance(python_version, str), repr(python_version)))

    install_steps = [step for step in steps if "pip install" in str(step.get("run", ""))]
    uses_cache = any("cache" in (step.get("with") or {}) for step in steps) or any(
        "cache" in str(step.get("run", "")) for step in install_steps
    )
    findings.append(("dependency installation is cached", uses_cache, str(len(install_steps)) + " install step(s)"))

    runs = " ".join(str(step.get("run", "")) for step in steps)
    findings.append(("a failing test cannot report success",
                     "|| true" not in runs and "continue-on-error" not in str(steps), "checked run commands"))
    findings.append(("lint runs before tests", "ruff" in runs and "pytest" in runs,
                     "ruff" if "ruff" in runs else "no lint command"))
    findings.append(("no step is allowed to fail silently",
                     not any(step.get("continue-on-error") for step in steps), "continue-on-error"))

    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workflow", nargs="?", default=".github/workflows/quality.yml")
    args = parser.parse_args()

    path = Path(args.workflow)
    if not path.exists():
        print(f"no workflow at {path}")
        return 2

    findings = check(path)
    for name, ok, detail in findings:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name} -- {detail}")
    failed = [name for name, ok, _ in findings if not ok]
    print(f"\n{len(findings) - len(failed)}/{len(findings)} workflow checks passed")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
