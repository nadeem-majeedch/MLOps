"""Reference solution for Lab 03: six checks in one pass."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

REQUIRED = ["session_id", "section", "hours", "prior_score", "sleep_hours", "score"]
KNOWN_SECTIONS = ["A", "B", "C"]
NUMERIC_COLUMNS = ["hours", "prior_score", "sleep_hours", "score"]


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


def first_id(frame: pd.DataFrame, mask: pd.Series) -> str:
    return str(frame.loc[mask, "session_id"].iloc[0]) if mask.any() else "-"


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
        return report

    report.run("duplicate_ids")
    duplicated = frame["session_id"].duplicated()
    if duplicated.any():
        report.fail("duplicate_ids", int(duplicated.sum()), first_id(frame, duplicated))

    report.run("missing_values")
    nulls = frame[NUMERIC_COLUMNS].isna().any(axis=1)
    if nulls.any():
        column = frame[NUMERIC_COLUMNS].isna().any(axis=0)
        report.fail("missing_values", int(nulls.sum()), ", ".join(column[column].index))

    report.run("hours_range")
    bad = ~frame["hours"].between(0.25, 16)
    bad &= frame["hours"].notna()
    if bad.any():
        report.fail("hours_range", int(bad.sum()), f"{first_id(frame, bad)} hours={frame.loc[bad, 'hours'].iloc[0]}")

    report.run("score_range")
    bad = (~frame["prior_score"].between(0, 100)) | (~frame["score"].between(0, 100))
    bad &= frame["prior_score"].notna() & frame["score"].notna()
    if bad.any():
        report.fail("score_range", int(bad.sum()), first_id(frame, bad))

    report.run("unknown_section")
    bad = ~frame["section"].isin(KNOWN_SECTIONS)
    if bad.any():
        report.fail("unknown_section", int(bad.sum()), f"{first_id(frame, bad)} section={frame.loc[bad, 'section'].iloc[0]}")

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a session drop")
    parser.add_argument("path")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()

    frame = pd.read_csv(args.path)
    report = validate(frame, args.path)
    payload = report.as_dict()
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print(f"{'PASS' if report.ok else 'FAIL'} {args.path}: {report.rows} rows, {len(report.checks_run)} checks")
    for failure in report.failures:
        print(f"  - {failure['code']}: {failure['count']} ({failure['example']})")
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
