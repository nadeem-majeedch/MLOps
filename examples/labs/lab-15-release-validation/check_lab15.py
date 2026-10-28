"""Acceptance check for Lab 15.

    python check_lab15.py [--validator validate_release.py]

A gate is judged by what it rejects. The tempting bundle has a good MAE and
three real defects; the clean bundle must still pass, or the gate is just a
wall.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "_shared"))

from labkit import Lab  # noqa: E402


def run(script: Path, bundle: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(script), "--bundle", bundle], cwd=ROOT, capture_output=True, text=True)


def reasons(script: Path, bundle: str) -> tuple[int, set[str]]:
    out = ROOT / "artifacts" / (Path(bundle).name + ".json")
    proc = subprocess.run([sys.executable, str(script), "--bundle", bundle, "--json", str(out)],
                          cwd=ROOT, capture_output=True, text=True)
    rules = set()
    if out.exists():
        rules = {reason["rule"] for reason in json.loads(out.read_text(encoding="utf-8")).get("reasons", [])}
    return proc.returncode, rules


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validator", default="validate_release.py")
    args = parser.parse_args()
    lab = Lab("L15", "Stop a defective model at release")
    script = (ROOT / args.validator).resolve()

    built = subprocess.run([sys.executable, "make_bundles.py"], cwd=ROOT, capture_output=True, text=True)
    lab.check("release bundles are built", built.returncode == 0, (built.stderr.strip().splitlines() or [""])[-1])

    code, rules = reasons(script, "release/clean")
    lab.equal("the honest bundle passes", code, 0)
    lab.equal("the honest bundle reports no reasons", rules, set())

    code, rules = reasons(script, "release/tempting")
    lab.equal("the tempting bundle is blocked", code, 1)
    for rule in ("artifact_hash", "tests_evidence", "missing_metadata"):
        lab.check(f"the block names {rule}", rule in rules, f"reasons: {sorted(rules)}")
    lab.check("a good MAE does not buy a pass", "metric_ceiling" not in rules,
              "the defect is not the metric")

    no_tests = ROOT / "release/no_tests"
    shutil.rmtree(no_tests, ignore_errors=True)
    shutil.copytree(ROOT / "release/clean", no_tests)
    (no_tests / "tests.json").unlink()
    code, rules = reasons(script, "release/no_tests")
    lab.equal("a bundle with no test evidence is blocked", code, 1)
    lab.check("missing evidence is named", "tests_evidence" in rules, str(sorted(rules)))

    no_sums = ROOT / "release/no_checksums"
    shutil.rmtree(no_sums, ignore_errors=True)
    shutil.copytree(ROOT / "release/clean", no_sums)
    (no_sums / "checksums.txt").unlink()
    code, rules = reasons(script, "release/no_checksums")
    lab.equal("a bundle with no checksums is blocked", code, 1)
    lab.check("the missing manifest is named", "artifact_hash" in rules, str(sorted(rules)))

    workflow_path = ROOT / ".github/workflows/release.yml"
    lab.check("the release workflow exists", workflow_path.exists(), str(workflow_path))
    if workflow_path.exists():
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8")) or {}
        steps = [step for job in (workflow.get("jobs") or {}).values() for step in job.get("steps") or []]
        validate_at = next((i for i, step in enumerate(steps) if "validate_release" in str(step.get("run", ""))), None)
        upload_at = next((i for i, step in enumerate(steps) if "upload-artifact" in str(step.get("uses", ""))), None)
        lab.check("validation runs", validate_at is not None,
                  f"validate step at index {validate_at}" if validate_at is not None else "no validate step")
        lab.check("publishing happens after validation",
                  validate_at is not None and upload_at is not None and validate_at < upload_at,
                  f"validate at {validate_at}, upload at {upload_at}")
        lab.check("no release step is allowed to fail silently",
                  not any(step.get("continue-on-error") for step in steps), "continue-on-error")
        lab.check("the release job has a timeout",
                  all(job.get("timeout-minutes") for job in (workflow.get("jobs") or {}).values()), "timeout-minutes")

    return lab.finish()


if __name__ == "__main__":
    raise SystemExit(main())
