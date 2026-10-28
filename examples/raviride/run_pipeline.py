"""The single documented command: preflight, then dvc repro, logged.

Exit codes: 0 success, 1 pipeline stage failed, 2 preflight failed.
"""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQUIRED = [
    "params.yaml",
    "dvc.yaml",
    "data/raw/trips.csv",
    "src/raviride_eta/prepare.py",
    "src/raviride_eta/train.py",
]


def preflight() -> list[str]:
    problems = []
    # Kept deliberately: the package metadata requires 3.11, but a script run
    # outside the environment should fail with a readable message, not an
    # ImportError several frames later.
    if sys.version_info < (3, 11):  # noqa: UP036
        problems.append(f"Python 3.11+ required, found {platform.python_version()}")
    for rel in REQUIRED:
        if not (ROOT / rel).exists():
            problems.append(f"missing required file: {rel}")
    if shutil.which("dvc") is None:
        problems.append("dvc not on PATH; activate the project environment")
    try:
        import yaml

        yaml.safe_load((ROOT / "params.yaml").read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - report, do not hide
        problems.append(f"params.yaml is not valid YAML: {exc}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate the raw data first")
    parser.add_argument("--force", action="store_true", help="ignore every cache")
    parser.add_argument("--only", help="reproduce one stage and its dependencies")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    problems = preflight()
    if problems:
        print("PREFLIGHT FAILED")
        for problem in problems:
            print(f"  - {problem}")
        return 2

    logs = ROOT / "logs"
    logs.mkdir(exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    log_path = logs / f"pipeline-{stamp}.log"

    command = ["dvc", "repro"]
    if args.force:
        command.append("--force")
    if args.only:
        command += ["--single-item", args.only]
    if args.dry_run:
        command.append("--dry")

    if args.check:
        check = subprocess.run(
            [sys.executable, "-m", "raviride_eta.data", "data/raw/trips.csv"],
            cwd=ROOT, capture_output=True, text=True,
        )
        print(check.stdout.strip())
        if check.returncode != 0:
            print("data validation rejected the batch; nothing was trained")
            return 1

    started = time.perf_counter()
    lines: list[str] = []
    with subprocess.Popen(
        command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    ) as process:
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="")
            lines.append(line)
    elapsed = time.perf_counter() - started

    log_path.write_text("".join(lines), encoding="utf-8")
    summary = {
        "command": " ".join(command),
        "exit_code": process.returncode,
        "elapsed_s": round(elapsed, 2),
        "log": str(log_path.relative_to(ROOT)),
    }
    (ROOT / ".pipeline").mkdir(exist_ok=True)
    (ROOT / ".pipeline" / "last_run.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"\n{summary['exit_code']=} {summary['elapsed_s']=}s log={summary['log']}")
    return 0 if process.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
