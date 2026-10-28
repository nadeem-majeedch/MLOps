"""A minimal orchestrator: dependencies, retries with backoff, run state.

Not a replacement for Airflow or Prefect. It exists to make the concepts
visible: a logical run date, a task graph, attempt accounting, idempotency.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = ROOT / ".orchestrator"
RUNS_DIR = ROOT / "runs"


@dataclass
class Task:
    name: str
    module: str
    deps: list[str] = field(default_factory=list)
    retries: int = 0
    backoff_s: float = 1.0


TASKS = [
    Task("validate", "raviride_eta.data", deps=[], retries=0),
    Task("prepare", "raviride_eta.prepare", deps=["validate"], retries=1),
    Task("featurise", "raviride_eta.featurise", deps=["prepare"], retries=1),
    Task("train", "raviride_eta.train", deps=["featurise"], retries=2),
    Task("evaluate", "raviride_eta.evaluate", deps=["train"], retries=1),
]
BY_NAME = {task.name: task for task in TASKS}


class Transient(RuntimeError):
    """A failure worth retrying."""


def state_path(run_date: str) -> Path:
    return STATE_DIR / f"{run_date}.json"


def load_state(run_date: str) -> dict:
    path = state_path(run_date)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"run_date": run_date, "tasks": {}, "status": "running"}


def save_state(run_date: str, state: dict) -> None:
    STATE_DIR.mkdir(exist_ok=True)
    state_path(run_date).write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def command_for(task: Task) -> list[str]:
    if task.name == "validate":
        return [sys.executable, "-m", task.module, "data/raw/trips.csv"]
    return [sys.executable, "-m", task.module]


def run_task(task: Task, run_date: str, state: dict, inject: str | None, inject_times: int) -> None:
    record = state["tasks"].setdefault(task.name, {"status": "pending", "attempts": 0})
    if record["status"] == "success":
        print(f"[{run_date}] {task.name}: already succeeded, skipping")
        return

    for attempt in range(1, task.retries + 2):
        record["attempts"] = attempt
        started = time.perf_counter()
        try:
            if inject == task.name and attempt <= inject_times:
                raise Transient(f"simulated transient failure (attempt {attempt} of {inject_times})")
            result = subprocess.run(
                command_for(task), cwd=ROOT, capture_output=True, text=True,
                env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
            )
            if result.returncode != 0:
                raise Transient(result.stderr.strip().splitlines()[-1] if result.stderr else "non-zero exit")
            elapsed = round(time.perf_counter() - started, 2)
            record.update(
                status="success",
                duration_s=elapsed,
                finished_at=datetime.now(UTC).isoformat(timespec="seconds"),
            )
            print(f"[{run_date}] {task.name}: success on attempt {attempt} in {elapsed}s")
            save_state(run_date, state)
            return
        except Transient as exc:
            elapsed = round(time.perf_counter() - started, 2)
            record.update(status="retrying", last_error=str(exc), duration_s=elapsed)
            if attempt > task.retries:
                record["status"] = "failed"
                save_state(run_date, state)
                print(f"[{run_date}] {task.name}: FAILED after {attempt} attempts: {exc}")
                raise
            delay = task.backoff_s * (2 ** (attempt - 1))
            print(f"[{run_date}] {task.name}: attempt {attempt} failed ({exc}); retrying in {delay}s")
            save_state(run_date, state)
            time.sleep(delay)


def run(run_date: str, inject: str | None, inject_times: int) -> int:
    state = load_state(run_date)
    if state.get("status") == "success" and (RUNS_DIR / run_date / "metrics.json").exists():
        print(f"[{run_date}] run already complete and outputs present; nothing to do (idempotent)")
        return 0

    for task in TASKS:
        for dep in task.deps:
            dep_status = state["tasks"].get(dep, {}).get("status")
            if dep_status != "success":
                print(f"[{run_date}] {task.name}: blocked, upstream {dep} is {dep_status or 'pending'}")
                state["status"] = "failed"
                save_state(run_date, state)
                return 1
        try:
            run_task(task, run_date, state, inject, inject_times)
        except Transient:
            state["status"] = "failed"
            save_state(run_date, state)
            return 1

    out = RUNS_DIR / run_date
    out.mkdir(parents=True, exist_ok=True)
    (out / "metrics.json").write_text((ROOT / "metrics.json").read_text(encoding="utf-8"), encoding="utf-8")
    state["status"] = "success"
    state["finished_at"] = datetime.now(UTC).isoformat(timespec="seconds")
    save_state(run_date, state)
    print(f"[{run_date}] run complete -> {out.relative_to(ROOT)}/metrics.json")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=datetime.now(UTC).date().isoformat())
    parser.add_argument("--inject", help="task name that should fail transiently")
    parser.add_argument("--inject-times", type=int, default=1)
    parser.add_argument("--status", metavar="DATE", help="print the recorded state for a run date")
    args = parser.parse_args()

    if args.status:
        print(json.dumps(load_state(args.status), indent=2))
        return 0
    return run(args.date, args.inject, args.inject_times)


if __name__ == "__main__":
    raise SystemExit(main())
