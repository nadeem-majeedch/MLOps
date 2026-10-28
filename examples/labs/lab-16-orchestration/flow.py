"""Lab 16 starter: three tasks in a row, and a schedule nobody can trust.

    python make_data.py
    python flow.py --date 2026-09-20
    python flow.py --backfill 2026-09-18:2026-09-20

What is missing is what makes a scheduled job operable:

1. **Retries with backoff.** A transient failure (a locked file, a dropped
   connection) kills the whole night. `FLAKY_ATTEMPTS=n` makes the transform
   task fail n times before succeeding, so you can test this without breaking
   anything.
2. **A state file per date.** Without one, "did last night run?" is answered by
   looking at file timestamps, and "run it again" silently duplicates work.
3. **Idempotency.** Running a completed date must report `skipped`, not retrain
   and overwrite the artifacts that were reviewed.
4. **A backfill that is safe to repeat.** Filling three missing days twice must
   produce three runs, not six.

State contract, one file per date at `.state/<date>.json`:

    {"date": "2026-09-20", "status": "succeeded" | "failed",
     "attempts": [{"n": 1, "error": str | null, "wait_s": float}, ...],
     "outputs": {"features": "...", "metrics": "..."}, "rows": int}
"""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

DATA = Path("data/sessions.csv")
STATE = Path(".state")
RUNS = Path("runs")
FEATURES = ["hours", "prior_score", "sleep_hours", "study_ratio"]
TARGET = "score"
MAX_ATTEMPTS = int(os.environ.get("MAX_ATTEMPTS", "3"))


class TransientError(RuntimeError):
    """A failure that a retry may fix."""


def state_path(day: str) -> Path:
    return STATE / f"{day}.json"


def load_state(day: str) -> dict | None:
    path = state_path(day)
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def extract(day: str) -> pd.DataFrame:
    frame = pd.read_csv(DATA, parse_dates=["session_date"])
    subset = frame[frame["session_date"].dt.strftime("%Y-%m-%d") == day]
    if subset.empty:
        raise ValueError(f"no sessions for {day}")
    return subset.reset_index(drop=True)


def transform(frame: pd.DataFrame, failures_path: Path) -> pd.DataFrame:
    """Feature build. Fails transiently while the counter says it should."""
    budget = int(os.environ.get("FLAKY_ATTEMPTS", "0"))
    seen = int(failures_path.read_text(encoding="utf-8")) if failures_path.exists() else 0
    if seen < budget:
        failures_path.parent.mkdir(parents=True, exist_ok=True)
        failures_path.write_text(str(seen + 1), encoding="utf-8")
        raise TransientError(f"staging table locked (simulated failure {seen + 1} of {budget})")
    out = frame.copy()
    out["study_ratio"] = out["hours"] / out["prior_score"].clip(lower=1)
    return out


def train(frame: pd.DataFrame, day: str) -> dict:
    run_dir = RUNS / day
    run_dir.mkdir(parents=True, exist_ok=True)
    features_path = run_dir / "features.csv"
    frame[FEATURES + [TARGET, "session_id"]].to_csv(features_path, index=False)

    model = LinearRegression().fit(frame[FEATURES], frame[TARGET])
    mae = mean_absolute_error(frame[TARGET], model.predict(frame[FEATURES]))
    metrics = {"date": day, "rows": int(len(frame)), "mae": round(float(mae), 4)}
    metrics_path = run_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    return {"features": str(features_path), "metrics": str(metrics_path), "rows": len(frame)}


def run(day: str, force: bool = False) -> dict:
    """One date, one attempt, no memory of what happened before."""
    STATE.mkdir(exist_ok=True)
    started = time.perf_counter()
    attempts = [{"n": 1, "error": None, "wait_s": 0.0}]
    try:
        frame = extract(day)
        featured = transform(frame, STATE / f"{day}.failures")
        outputs = train(featured, day)
        status = "succeeded"
    except Exception as error:  # noqa: BLE001 - recorded in state
        attempts[-1]["error"] = f"{type(error).__name__}: {error}"
        status = "failed"
        outputs = {}

    state = {"date": day, "status": status, "attempts": attempts, "outputs": outputs,
             "elapsed_s": round(time.perf_counter() - started, 3)}
    state_path(day).write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    print(f"{day}: {status} in {state['elapsed_s']}s")
    return state


def backfill(start: str, end: str, force: bool = False) -> int:
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    days = [(first + timedelta(days=offset)).isoformat() for offset in range((last - first).days + 1)]
    results = [run(day, force=force) for day in days]
    succeeded = sum(result["status"] == "succeeded" for result in results)
    print(f"backfill {start}..{end}: {succeeded}/{len(days)} succeeded")
    return 0 if succeeded == len(days) else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date")
    parser.add_argument("--backfill", help="START:END")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.backfill:
        start, _, end = args.backfill.partition(":")
        return backfill(start, end or start, force=args.force)
    if args.date:
        return 0 if run(args.date, force=args.force)["status"] == "succeeded" else 1
    parser.error("pass --date or --backfill")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
