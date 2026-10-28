"""Lab 04 starter: reproduce a run from a manifest, or refuse to.

    python reproduce.py --manifest data/manifests/v1.json

The script must:

1. Read the manifest and the dataset it names.
2. Refuse to train if the dataset hash differs from the manifest, with exit
   code 2 and the words "hash mismatch" in the message. Training on data that
   is not the data you claim is worse than not training.
3. Otherwise train the same model as the project (random forest, seed 42) and
   write `runs/<tag>-<short sha>.json` containing at least: tag, sha256,
   rows, mae, seed, and a hash of the predictions.
4. Print the run record path.

The functions below are the shape of the answer. Fill them in.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

FEATURES = ["hours", "prior_score", "sleep_hours"]
TARGET = "score"


def verify_manifest(manifest: dict, data_path: Path) -> None:
    """Raise SystemExit(2) with "hash mismatch" when the bytes differ."""
    raise NotImplementedError("verify_manifest")


def train_and_record(manifest: dict, data_path: Path) -> dict:
    """Train, evaluate, and return the run record. Do not write files here."""
    raise NotImplementedError("train_and_record")


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
