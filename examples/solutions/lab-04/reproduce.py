"""Reference solution for Lab 04."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

FEATURES = ["hours", "prior_score", "sleep_hours"]
TARGET = "score"
SEED = 42


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_manifest(manifest: dict, data_path: Path) -> None:
    if not data_path.exists():
        raise SystemExit(f"missing data file: {data_path}")
    actual = sha256_of(data_path)
    if actual != manifest["sha256"]:
        # A message passed to SystemExit becomes the exit code (1) in some
        # paths; print it and choose the code explicitly.
        print(
            f"hash mismatch: {data_path} is {actual[:16]}..., "
            f"manifest {manifest['tag']} expects {manifest['sha256'][:16]}...",
            file=sys.stderr,
        )
        raise SystemExit(2)


def train_and_record(manifest: dict, data_path: Path) -> dict:
    frame = pd.read_csv(data_path)
    train, test = train_test_split(frame, test_size=0.25, random_state=SEED)
    model = RandomForestRegressor(n_estimators=120, max_depth=8, random_state=SEED)
    model.fit(train[FEATURES], train[TARGET])
    predictions = model.predict(test[FEATURES])
    return {
        "tag": manifest["tag"],
        "sha256": manifest["sha256"],
        "rows": int(len(frame)),
        "seed": SEED,
        "mae": round(float(mean_absolute_error(test[TARGET], predictions)), 6),
        "predictions_sha256": hashlib.sha256(predictions.round(6).tobytes()).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Reproduce a run from a manifest")
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    data_path = Path(manifest["path"])
    verify_manifest(manifest, data_path)
    record = train_and_record(manifest, data_path)

    runs = Path("runs")
    runs.mkdir(exist_ok=True)
    out = runs / f"{manifest['tag']}-{manifest['sha256'][:8]}.json"
    out.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))
    print(f"run record: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
