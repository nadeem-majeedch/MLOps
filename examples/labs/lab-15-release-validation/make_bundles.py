"""Build two release bundles.

    python make_bundles.py

`release/clean/` is a complete, honest bundle.
`release/tempting/` is the one that gets past a metrics-only check: the MAE is
good, the artifact is real, and three other things are wrong.

A bundle is four files:

    candidate.json   metrics and metadata
    model.joblib     the artifact
    tests.json       the test report from CI
    checksums.txt    sha256 of every file in the bundle except itself
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.dummy import DummyRegressor

METRICS = {
    "mae": 2.74,
    "p95_abs_error": 8.12,
    "zones": {"Z01": 1.88, "Z05": 3.02, "Z07": 5.1, "Z08": 5.4},
}


def checksums(bundle: Path) -> None:
    lines = []
    for path in sorted(bundle.iterdir()):
        if path.name == "checksums.txt":
            continue
        lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}")
    (bundle / "checksums.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build(bundle: Path, metadata: dict, tests: dict) -> None:
    bundle.mkdir(parents=True, exist_ok=True)
    features = pd.DataFrame({"hours": [4.0, 5.0], "prior_score": [60.0, 70.0], "sleep_hours": [7.0, 6.5]})
    model = DummyRegressor(strategy="constant", constant=METRICS["mae"]).fit(features, [70.0, 75.0])
    joblib.dump(model, bundle / "model.joblib")
    (bundle / "candidate.json").write_text(
        json.dumps({"metrics": METRICS, "metadata": metadata}, indent=2) + "\n", encoding="utf-8"
    )
    (bundle / "tests.json").write_text(json.dumps(tests, indent=2) + "\n", encoding="utf-8")
    checksums(bundle)


def main() -> None:
    root = Path("release")
    good_meta = {
        "candidate": "session-etl-v7",
        "git_commit": "4c9e1ab",
        "data_hash": "7b3ad0d92b721cf4",
        "trained_at": "2026-10-02T09:30:00Z",
        "owner": "ml-platform",
        "approval": "reviewed by two engineers",
    }
    build(root / "clean", good_meta, {"total": 34, "passed": 34, "failed": 0, "skipped": 0, "duration_s": 51.2})

    tempting_meta = {"candidate": "session-etl-v8", "git_commit": "e11f2c9", "data_hash": "7b3ad0d92b721cf4",
                     "trained_at": "2026-10-04T22:05:00Z"}
    tempting = root / "tempting"
    build(tempting, tempting_meta, {"total": 34, "passed": 0, "failed": 0, "skipped": 34, "duration_s": 4.1})
    # Then lie about the artifact: the hash in checksums.txt no longer matches.
    with (tempting / "model.joblib").open("ab") as handle:
        handle.write(b"\n# rebuilt after the checksum was written\n")

    print(json.dumps({"clean": str(root / "clean"), "tempting": str(root / "tempting")}, indent=2))
    print("clean: mae 2.74, all 34 tests passed, every field present")
    print("tempting: mae 2.74, 34 tests skipped, no owner, artifact hash changed after packaging")


if __name__ == "__main__":
    main()
