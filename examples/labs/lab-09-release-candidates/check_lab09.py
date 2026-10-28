"""Acceptance check for Lab 09.

    python check_lab09.py [--lifecycle lifecycle.py]

Registers four candidates, promotes one, blocks two, rolls back, and reads the
history from the registry rather than from the script's own claims.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "_shared"))

from labkit import Lab  # noqa: E402

MODEL = "session-score"
CANDIDATES = [
    "candidates/baseline_v1.json",
    "candidates/deeper_v2.json",
    "candidates/shallow_v3.json",
    "candidates/zone_regression_v6.json",
]


def run(script: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(script), *args], cwd=ROOT, capture_output=True, text=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lifecycle", default="lifecycle.py")
    args = parser.parse_args()
    lab = Lab("L09", "Register, promote, and roll back a model")
    script = (ROOT / args.lifecycle).resolve()

    shutil.rmtree(ROOT / "mlruns", ignore_errors=True)
    shutil.rmtree(ROOT / "artifacts", ignore_errors=True)

    for candidate in CANDIDATES:
        proc = run(script, "register", candidate)
        lab.check(f"register {Path(candidate).stem}", proc.returncode == 0,
                  (proc.stderr.strip().splitlines() or [""])[-1])

    from mlflow import MlflowClient

    client = MlflowClient(tracking_uri=(ROOT / "mlruns").resolve().as_uri())
    versions = client.search_model_versions(f"name='{MODEL}'")
    lab.equal("four versions are registered", len(versions), 4)
    if len(versions) != 4:
        return lab.finish()

    tagged = all({"data_hash", "run_id"} <= set(v.tags) for v in versions)
    lab.check("every version carries its data hash and run id", tagged,
              str([sorted(set(v.tags)) for v in versions][:1]))
    artifacts = [a.path for a in client.list_artifacts(versions[0].tags["run_id"], "model")]
    lab.check("a model artifact exists for a version", "model/MLmodel" in artifacts, str(artifacts))

    first = run(script, "promote", "1")
    lab.check("promote 1 succeeds", first.returncode == 0, (first.stdout + first.stderr).strip().splitlines()[-1])
    lab.equal("champion alias points at v1",
              int(client.get_model_version_by_alias(MODEL, "champion").version), 1)
    lab.check("promotion records where it came from",
              client.get_model_version(MODEL, "1").tags.get("promoted_from") == "none", "promoted_from=none")

    blocked = run(script, "promote", "3")
    lab.check("an underfitted candidate is blocked", blocked.returncode == 1, f"exit {blocked.returncode}")
    lab.check("the block explains itself with numbers", any(ch.isdigit() for ch in blocked.stdout),
              blocked.stdout.strip().splitlines()[-1][:80] if blocked.stdout else "no output")
    lab.equal("the alias did not move", int(client.get_model_version_by_alias(MODEL, "champion").version), 1)

    zone_blocked = run(script, "promote", "4")
    lab.check("a zone regression is blocked", zone_blocked.returncode == 1, f"exit {zone_blocked.returncode}")
    lab.check("the zone block names the zone", "Z01" in zone_blocked.stdout, zone_blocked.stdout.strip()[:80])

    promoted = run(script, "promote", "2")
    lab.check("a passing candidate is promoted", promoted.returncode == 0, f"exit {promoted.returncode}")
    lab.equal("champion alias points at v2",
              int(client.get_model_version_by_alias(MODEL, "champion").version), 2)
    lab.equal("v2 remembers it replaced v1", client.get_model_version(MODEL, "2").tags.get("promoted_from"), "1")

    rolled = run(script, "rollback")
    lab.check("rollback succeeds without being told the target", rolled.returncode == 0,
              (rolled.stdout + rolled.stderr).strip().splitlines()[-1])
    lab.equal("champion alias is back on v1",
              int(client.get_model_version_by_alias(MODEL, "champion").version), 1)
    lab.check("the rolled-back version is tagged", "rollback_at" in client.get_model_version(MODEL, "1").tags,
              str(sorted(client.get_model_version(MODEL, "1").tags)))

    history = ROOT / "artifacts/history.json"
    shown = run(script, "show", "--json", str(history))
    lab.check("show writes a history file", shown.returncode == 0 and history.exists(), "artifacts/history.json")
    if history.exists():
        report = json.loads(history.read_text(encoding="utf-8"))
        lab.equal("history champion matches the registry", report.get("champion"), 1)
        lab.equal("history lists every version", len(report.get("versions", [])), 4)
        two = next(v for v in report["versions"] if v["version"] == 2)
        lab.equal("history records the promotion chain", two.get("promoted_from"), "1")

    return lab.finish()


if __name__ == "__main__":
    raise SystemExit(main())
