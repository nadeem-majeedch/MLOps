"""Lab 03 starter: a validator that catches two of the six risks.

Run it against each drop:

    python validate.py data/clean_batch.csv
    python validate.py data/bad_batch.csv --json artifacts/bad_report.json

Exit code 0 means the batch is accepted, 1 means it is rejected. A rejected
batch must still produce a complete report: an operator needs every defect in
one pass, not the first one.

Your job is to add the missing checks without changing the report contract.
The contract is:

    {"path": str, "rows": int, "ok": bool, "checks_run": [str], "failures": [
        {"code": str, "count": int, "example": str}
    ]}
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

REQUIRED = ["session_id", "section", "hours", "prior_score", "sleep_hours", "score"]
KNOWN_SECTIONS = ["A", "B", "C"]


@dataclass
class Report:
    path: str
    rows: int
    checks_run: list[str] = field(default_factory=list)
    failures: list[dict] = field(default_factory=list)

    def fail(self, code: str, count: int, example: str) -> None:
        self.failures.append({"code": code, "count": int(count), "example": str(example)})

    def run(self, name: str) -> None:
        self.checks_run.append(name)

    @property
    def ok(self) -> bool:
        return not self.failures

    def as_dict(self) -> dict:
        return {
            "path": self.path,
            "rows": self.rows,
            "ok": self.ok,
            "checks_run": self.checks_run,
            "failures": self.failures,
        }


def validate(frame: pd.DataFrame, path: str) -> Report:
    report = Report(path=path, rows=len(frame))

    report.run("schema")
    missing = [c for c in REQUIRED if c not in frame.columns]
    extra = [c for c in frame.columns if c not in REQUIRED]
    if missing:
        report.fail("schema_missing", len(missing), ", ".join(missing))
    if extra:
        report.fail("schema_extra", len(extra), ", ".join(extra))
    if missing:
        # Column checks cannot run on a frame that is missing columns. Stop
        # here, but the report still says why.
        return report

    report.run("duplicate_ids")
    duplicated = frame["session_id"].duplicated()
    if duplicated.any():
        first = frame.loc[duplicated, "session_id"].iloc[0]
        report.fail("duplicate_ids", int(duplicated.sum()), str(first))

    # TODO 1: missing_values -- count nulls across hours, prior_score,
    #         sleep_hours and score in one failure.
    # TODO 2: hours_range -- hours must be within [0.25, 16].
    # TODO 3: score_range -- prior_score and score must be within [0, 100].
    # TODO 4: unknown_section -- section must be one of KNOWN_SECTIONS.

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a session drop")
    parser.add_argument("path")
    parser.add_argument("--json", type=Path, help="write the full report here")
    args = parser.parse_args()

    frame = pd.read_csv(args.path)
    report = validate(frame, args.path)
    payload = report.as_dict()

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    verdict = "PASS" if report.ok else "FAIL"
    print(f"{verdict} {args.path}: {report.rows} rows, {len(report.checks_run)} checks")
    for failure in report.failures:
        print(f"  - {failure['code']}: {failure['count']} ({failure['example']})")
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
