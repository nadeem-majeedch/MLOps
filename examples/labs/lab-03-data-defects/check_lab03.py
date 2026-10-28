"""Acceptance check for Lab 03.

    python check_lab03.py [--validator validate.py]

Runs the candidate validator against three drops and compares the reported
defects with the ones that were planted.
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

EXPECTED = {
    "data/bad_batch.csv": ({"missing_values": 6, "hours_range": 3, "duplicate_ids": 4, "unknown_section": 2}, 5),
    # The renamed column arrives as one missing and one extra column. A
    # validator cannot know the rename, so both are reported and the column
    # checks do not run.
    "data/schema_change.csv": ({"schema_missing": 1, "schema_extra": 2}, 1),
}


def run_validator(script: Path, data: Path, report_dir: Path) -> tuple[int, dict | None]:
    report = report_dir / (data.stem + ".json")
    proc = subprocess.run(
        [sys.executable, str(script), str(data), "--json", str(report)],
        cwd=ROOT, capture_output=True, text=True,
    )
    payload = json.loads(report.read_text(encoding="utf-8")) if report.exists() else None
    return proc.returncode, payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validator", default="validate.py")
    args = parser.parse_args()
    lab = Lab("L03", "Validate a defective data drop")
    script = (ROOT / args.validator).resolve()
    if not lab.check("validator exists", script.exists(), str(script)):
        return lab.finish()

    reports = ROOT / "artifacts"
    reports.mkdir(exist_ok=True)

    for rel, (expected, min_checks) in EXPECTED.items():
        data = ROOT / rel
        code, payload = run_validator(script, data, reports)
        lab.check(f"{rel} rejected with exit 1", code == 1, f"exit {code}")
        if payload is None:
            lab.fail(f"{rel} writes a JSON report", "no report file produced")
            continue
        found = {f["code"]: f["count"] for f in payload.get("failures", [])}
        lab.check(f"{rel} names every defect", set(expected) <= set(found), f"found {sorted(found)}")
        for code_name, count in expected.items():
            lab.equal(f"{rel} {code_name} count", found.get(code_name), count)
        lab.check(f"{rel} report is not ok", payload.get("ok") is False, f"ok={payload.get('ok')}")
        lab.check(f"{rel} ran {min_checks}+ checks", len(payload.get("checks_run", [])) >= min_checks,
                  f"{len(payload.get('checks_run', []))} checks")

    clean = ROOT / "data/clean_batch.csv"
    code, payload = run_validator(script, clean, reports)
    lab.check("clean_batch.csv accepted with exit 0", code == 0, f"exit {code}")
    if payload is not None:
        lab.check("clean batch has no failures", payload.get("failures") == [], str(payload.get("failures")))

    return lab.finish()


if __name__ == "__main__":
    raise SystemExit(main())
