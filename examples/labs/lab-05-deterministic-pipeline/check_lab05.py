"""Acceptance check for Lab 05.

    python check_lab05.py [--pipeline pipeline.py]

Runs the same pipeline under two hash seeds, then twice more with --reuse to
see whether unchanged stages are skipped, then once with a changed parameter.
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

MANIFEST = ROOT / "artifacts/manifest.json"


def run(script: Path, *args: str, hashseed: str = "0") -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONHASHSEED=hashseed)
    return subprocess.run([sys.executable, str(script), *args], cwd=ROOT, capture_output=True, text=True, env=env)


def manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def statuses(payload: dict) -> list[str]:
    return [stage.get("status") for stage in payload.get("stages", [])]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pipeline", default="pipeline.py")
    args = parser.parse_args()
    lab = Lab("L05", "Deterministic pipeline with a stage cache")
    script = (ROOT / args.pipeline).resolve()

    for path in (MANIFEST, ROOT / ".cache"):
        if path.is_dir():
            for child in path.iterdir():
                child.unlink()
        elif path.exists():
            path.unlink()

    first = run(script)
    lab.check("pipeline runs", first.returncode == 0 and MANIFEST.exists(),
              (first.stderr.strip().splitlines() or ["no stderr"])[-1])
    if not MANIFEST.exists():
        return lab.finish()
    one = manifest()

    second = run(script, hashseed="1")
    two = manifest()
    lab.check("a second run exits 0", second.returncode == 0, f"exit {second.returncode}")
    lab.equal("metrics are identical under a different hash seed", two["metrics"].get("mae"), one["metrics"].get("mae"))
    lab.equal("predictions are identical", two["metrics"].get("predictions_sha256"),
              one["metrics"].get("predictions_sha256"))
    lab.equal("the review sample is identical", two["metrics"].get("review"), one["metrics"].get("review"))
    lab.equal("feature order is identical", two.get("features"), one.get("features"))
    lab.check("every stage computed on a cold run", statuses(one) == ["computed"] * 3, str(statuses(one)))
    lab.check("stage keys are non-empty", all(s.get("key") for s in one["stages"]), str([s.get("key") for s in one["stages"]]))

    run(script, "--reuse")
    warm = manifest()
    lab.check("an unchanged rerun reuses every stage", statuses(warm) == ["hit"] * 3, str(statuses(warm)))

    run(script, "--reuse", "--trees", "60")
    partial = manifest()
    lab.equal("changing the trees parameter recomputes only train", statuses(partial), ["hit", "hit", "computed"])
    lab.check("the changed run reports different metrics", partial["metrics"].get("mae") != one["metrics"].get("mae"),
              f"{partial['metrics'].get('mae')} vs {one['metrics'].get('mae')}")
    train_key = partial["stages"][2].get("key")
    lab.check("the train cache key changes with the parameter", train_key != one["stages"][2].get("key"), "keys differ")

    return lab.finish()


if __name__ == "__main__":
    raise SystemExit(main())
