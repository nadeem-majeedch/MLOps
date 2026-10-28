"""Acceptance check for Lab 13.

    python check_lab13.py

Four conditions: the requirement files agree, the pinned environment is the one
the code needs, the pipeline runs, and the suite that protects the API passes.
"""

from __future__ import annotations

import glob
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "_shared"))

from labkit import Lab  # noqa: E402


def run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True)


def main() -> int:
    lab = Lab("L13", "Identify an incompatibility with automated tests")

    files = sorted(glob.glob(str(ROOT / "requirements*.txt")))
    resolved = run(["resolve.py", *[str(Path(f).name) for f in files]])
    lab.check("requirement files install together", resolved.returncode == 0,
              (resolved.stdout.strip().splitlines() or ["no output"])[-1])

    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8") if (ROOT / "requirements.txt").exists() else ""
    pandas_pin = re.search(r"^pandas\s*==\s*(\d+)\.", requirements, re.MULTILINE)
    lab.check("pandas is pinned to the major the code runs on",
              bool(pandas_pin) and int(pandas_pin.group(1)) >= 2,
              pandas_pin.group(0) if pandas_pin else "no pandas pin")

    source = (ROOT / "pipeline.py").read_text(encoding="utf-8")
    lab.check("the pipeline no longer calls the removed DataFrame.append",
              not re.search(r"\.append\(\s*extra", source), "look for frame.append(extra...)")

    ran = run(["pipeline.py"])
    lab.check("the pipeline runs on the pinned environment", ran.returncode == 0,
              (ran.stderr.strip().splitlines() or [""])[-1])
    summary_path = ROOT / "artifacts/summary.json"
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        lab.equal("both extracts are summarised", summary.get("rows"), 600)
        lab.check("the summary has no nulls", all(value is not None for value in summary.values()), str(summary))

    tested = run(["-m", "pytest", "tests", "-q"])
    lab.check("the test suite passes", tested.returncode == 0,
              (tested.stdout.strip().splitlines() or ["no output"])[-1])
    count = len(re.findall(r"^def test_", (ROOT / "tests/test_pipeline.py").read_text(encoding="utf-8"), re.MULTILINE))
    lab.check("the suite has at least three tests", count >= 3, f"{count} tests")

    env = subprocess.run(
        [sys.executable, "-c", "import pandas, numpy, sklearn; print(pandas.__version__, numpy.__version__, sklearn.__version__)"],
        cwd=ROOT, capture_output=True, text=True, env=os.environ,
    )
    versions = env.stdout.strip().split()
    lab.check("the installed pandas is 2.x", bool(versions) and versions[0].startswith("2."), str(versions))

    return lab.finish()


if __name__ == "__main__":
    raise SystemExit(main())
