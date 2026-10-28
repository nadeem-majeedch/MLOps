"""Acceptance check for Lab 02.

Checks the shape of the refactor, not its style:

    python check_lab02.py [--module sessionlab.train]

A package under src/, a CLI that explains itself, one command that writes a
metrics file, no import-time I/O, and a test suite that passes.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "_shared"))

from labkit import Lab  # noqa: E402

SRC = ROOT / "src"


def run(args: list[str], cwd: Path, extra_env: dict | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONPATH=str(SRC), **(extra_env or {}))
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=env)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--module", default="sessionlab.train")
    args = parser.parse_args()
    lab = Lab("L02", "Notebook script to maintainable project")

    packages = sorted(p for p in SRC.glob("*") if p.is_dir() and (p / "__init__.py").exists())
    lab.check("package exists under src/", bool(packages), ", ".join(p.name for p in packages) or "none found")
    if not packages:
        return lab.finish()

    modules = sorted(p.name for p in SRC.glob("*/*.py") if p.name != "__init__.py")
    lab.check("training code split across at least two modules", len(modules) >= 2, f"{len(modules)}: {modules}")

    longest = max(modules_size(SRC, modules), default=0)
    lab.check("no module over 200 lines", longest <= 200, f"longest {longest} lines")

    help_run = run([sys.executable, "-m", args.module, "--help"], cwd=ROOT)
    lab.check(
        "the training entry point answers --help",
        help_run.returncode == 0,
        (help_run.stderr.strip().splitlines() or ["no output"])[-1],
    )

    import_run = run([sys.executable, "-c", f"import {args.module}"], cwd=ROOT.parent)
    lab.check("importing the module does no work", import_run.returncode == 0 and import_run.stdout.strip() == "",
              f"exit {import_run.returncode}, stdout {import_run.stdout.strip()[:60]!r}")

    out = Path("artifacts/run.json")
    if out.exists():
        out.unlink()
    train_run = run(
        [sys.executable, "-m", args.module, "--data", "data/sessions.csv", "--out", str(out), "--seed", "7"],
        cwd=ROOT,
    )
    produced = out.exists()
    lab.check("one command writes artifacts/run.json", train_run.returncode == 0 and produced,
              (train_run.stderr.strip().splitlines() or ["no stderr"])[-1])
    if produced:
        payload = json.loads(out.read_text(encoding="utf-8"))
        missing = [k for k in ("mae", "rows_train", "rows_test", "model_path") if k not in payload]
        lab.check("metrics file has the agreed keys", not missing, f"missing {missing}" if missing else "all present")
        lab.check("mae is a finite number", isinstance(payload.get("mae"), (int, float)) and payload["mae"] < 15,
                  f"mae={payload.get('mae')}")

    tests = sorted((ROOT / "tests").glob("test_*.py"))
    lab.check("tests/ holds at least one test file", bool(tests), ", ".join(t.name for t in tests) or "none")
    if tests:
        pytest_run = run([sys.executable, "-m", "pytest", "-q", "tests"], cwd=ROOT)
        tail = (pytest_run.stdout.strip().splitlines() or ["no output"])[-1]
        lab.check("the test suite passes", pytest_run.returncode == 0, tail)

    hardcoded = [str(p) for p in SRC.rglob("*.py") if "C:\\" in p.read_text(encoding="utf-8", errors="ignore")]
    lab.check("no absolute Windows paths in the package", not hardcoded, str(hardcoded))

    return lab.finish()


def modules_size(src: Path, names: list[str]) -> list[int]:
    return [len(p.read_text(encoding="utf-8").splitlines()) for p in src.glob("*/*.py") if p.name in names]


if __name__ == "__main__":
    raise SystemExit(main())
