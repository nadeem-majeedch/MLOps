"""Acceptance check for Lab 16.

    python check_lab16.py

Retry once, exhaust retries once, replay a completed date, and backfill twice.
The state files are the evidence; stdout is not.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "_shared"))

from labkit import Lab  # noqa: E402


def run(*args: str, env_extra: dict | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ, **(env_extra or {}))
    return subprocess.run([sys.executable, "flow.py", *args], cwd=ROOT, capture_output=True, text=True, env=env)


def state(day: str) -> dict:
    path = ROOT / f".state/{day}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def main() -> int:
    lab = Lab("L16", "Orchestrate a repeatable nightly run")

    shutil.rmtree(ROOT / ".state", ignore_errors=True)
    shutil.rmtree(ROOT / "runs", ignore_errors=True)

    flaky = run("--date", "2026-09-20", env_extra={"FLAKY_ATTEMPTS": "1", "MAX_ATTEMPTS": "3"})
    lab.check("a transient failure is retried and succeeds", flaky.returncode == 0, flaky.stdout.strip()[-80:])
    first = state("2026-09-20")
    lab.equal("the run is recorded as succeeded", first.get("status"), "succeeded")
    lab.equal("two attempts were recorded", len(first.get("attempts", [])), 2)
    if len(first.get("attempts", [])) == 2:
        lab.check("the first attempt recorded the transient error", first["attempts"][0].get("error"),
                  str(first["attempts"][0]))
        lab.check("the retry waited before running", first["attempts"][0].get("wait_s", 0) > 0,
                  str(first["attempts"][0].get("wait_s")))
        lab.check("the second attempt succeeded without waiting", first["attempts"][1].get("wait_s") == 0,
                  str(first["attempts"][1].get("wait_s")))

    metrics_path = ROOT / "runs/2026-09-20/metrics.json"
    before = digest(metrics_path) if metrics_path.exists() else ""
    finished_before = first.get("finished_at")
    replay = run("--date", "2026-09-20", env_extra={"FLAKY_ATTEMPTS": "0"})
    lab.check("replaying a completed date exits 0", replay.returncode == 0, f"exit {replay.returncode}")
    lab.check("a completed date is skipped, not retrained", "skipped" in replay.stdout.lower(), replay.stdout.strip()[:80])
    lab.check("the reviewed artifact was not overwritten", digest(metrics_path) == before and before != "",
              f"{before} -> {digest(metrics_path)}")

    exhausted = run("--date", "2026-09-21", env_extra={"FLAKY_ATTEMPTS": "9", "MAX_ATTEMPTS": "3"})
    lab.equal("exhausting the retries exits 1", exhausted.returncode, 1)
    failed = state("2026-09-21")
    lab.equal("the run is recorded as failed", failed.get("status"), "failed")
    lab.equal("exactly three attempts were made", len(failed.get("attempts", [])), 3)
    waits = [attempt.get("wait_s", 0) for attempt in failed.get("attempts", [])][:2]
    lab.check("backoff grows between attempts", len(waits) == 2 and waits[1] > waits[0],
              f"waits {waits}")

    forced = run("--date", "2026-09-20", "--force", env_extra={"FLAKY_ATTEMPTS": "0"})
    lab.check("--force reruns a completed date", forced.returncode == 0 and "skipped" not in forced.stdout.lower(),
              forced.stdout.strip()[:80])
    forced_state = state("2026-09-20")
    lab.equal("the forced run restarted the attempt count", len(forced_state.get("attempts", [])), 1)
    lab.check("the forced run produced fresh evidence",
              forced_state.get("finished_at") not in (None, finished_before),
              f"{finished_before} -> {forced_state.get('finished_at')}")

    backfill = run("--backfill", "2026-09-18:2026-09-19", env_extra={"FLAKY_ATTEMPTS": "0"})
    lab.check("a backfill fills the missing dates", backfill.returncode == 0, backfill.stdout.strip()[-80:])
    lab.equal("both backfilled dates are complete",
              [state("2026-09-18").get("status"), state("2026-09-19").get("status")],
              ["succeeded", "succeeded"])

    day_hash = digest(ROOT / "runs/2026-09-18/metrics.json")
    again = run("--backfill", "2026-09-18:2026-09-19", env_extra={"FLAKY_ATTEMPTS": "0"})
    lab.check("a repeated backfill exits 0", again.returncode == 0, f"exit {again.returncode}")
    lab.check("a repeated backfill duplicates no work", digest(ROOT / "runs/2026-09-18/metrics.json") == day_hash,
              "metrics unchanged")
    lab.check("the repeated backfill says it skipped", again.stdout.lower().count("skipped") >= 2,
              again.stdout.strip()[:100])

    return lab.finish()


if __name__ == "__main__":
    raise SystemExit(main())
