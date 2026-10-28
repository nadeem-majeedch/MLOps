"""Stamp a dataset with a content hash and a version tag.

    python version_data.py --data data/sessions.csv --tag v1
    python version_data.py --data data/sessions.csv --tag v2

A version is not a filename and not a date. It is the SHA-256 of the bytes that
were actually read, plus the shape and column types that were actually seen.
Two files with the same tag and different hashes mean someone edited data in
place, which is the failure this lab is about.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

MANIFEST_DIR = Path("data/manifests")


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def describe(path: Path) -> dict:
    """Everything a later run needs in order to prove it read the same data."""
    frame = pd.read_csv(path)
    return {
        "sha256": sha256_of(path),
        "bytes": path.stat().st_size,
        "rows": int(len(frame)),
        "columns": {name: str(dtype) for name, dtype in frame.dtypes.items()},
        "null_counts": {name: int(count) for name, count in frame.isna().sum().items()},
    }


def write_manifest(data: Path, tag: str) -> Path:
    payload = {
        "tag": tag,
        "path": str(data),
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        **describe(data),
    }
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    out = MANIFEST_DIR / f"{tag}.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--tag", required=True)
    args = parser.parse_args()

    out = write_manifest(args.data, args.tag)
    payload = json.loads(out.read_text(encoding="utf-8"))
    print(f"{args.tag}: {payload['rows']} rows sha256={payload['sha256'][:16]}... -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
