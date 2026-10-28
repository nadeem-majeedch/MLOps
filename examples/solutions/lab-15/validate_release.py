"""Reference solution for Lab 15: absence of evidence is a block."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import joblib

POLICY = {"overall_ceiling": 3.20, "p95_ceiling": 9.60, "zone_ceilings": {"Z08": 6.05}}
REQUIRED_METADATA = ["candidate", "git_commit", "data_hash", "trained_at", "owner"]
MIN_TESTS = 20
SMOKE_INPUT = [[4.0, 60.0, 7.0]]


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_checksums(bundle: Path) -> list[str]:
    manifest = bundle / "checksums.txt"
    if not manifest.exists():
        return ["checksums.txt is missing, so no file can be verified"]
    problems = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, name = line.split(maxsplit=1)
        target = bundle / name.strip()
        if not target.exists():
            problems.append(f"{name.strip()} listed but absent")
        elif sha256_of(target) != expected:
            problems.append(f"{name.strip()} hash is {sha256_of(target)[:12]}..., manifest says {expected[:12]}...")
    return problems


def validate(bundle: Path) -> list[dict]:
    reasons: list[dict] = []
    candidate_path = bundle / "candidate.json"
    if not candidate_path.exists():
        return [{"rule": "missing_metadata", "detail": "candidate.json is missing"}]
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    metrics = candidate.get("metrics", {})

    checksum_problems = verify_checksums(bundle)
    if checksum_problems:
        reasons.append({"rule": "artifact_hash", "detail": "; ".join(checksum_problems)})

    model_path = bundle / "model.joblib"
    try:
        model = joblib.load(model_path)
        value = float(model.predict(SMOKE_INPUT)[0])
        if not math.isfinite(value):
            raise ValueError(f"prediction was {value}")
    except Exception as error:  # noqa: BLE001 - every failure here is a block
        reasons.append({"rule": "artifact_loads", "detail": f"{type(error).__name__}: {error}"})

    tests_path = bundle / "tests.json"
    if not tests_path.exists():
        reasons.append({"rule": "tests_evidence", "detail": "tests.json is absent; no test result was shipped"})
    else:
        tests = json.loads(tests_path.read_text(encoding="utf-8"))
        executed = int(tests.get("passed", 0))
        if int(tests.get("failed", 0)) > 0:
            reasons.append({"rule": "tests_evidence", "detail": f"{tests['failed']} tests failed"})
        elif executed < MIN_TESTS:
            reasons.append(
                {"rule": "tests_evidence",
                 "detail": f"only {executed} tests passed (need {MIN_TESTS}); "
                           f"{tests.get('skipped', 0)} skipped"}
            )

    metadata = candidate.get("metadata", {})
    missing = [key for key in REQUIRED_METADATA if not str(metadata.get(key, "")).strip()]
    if missing:
        reasons.append({"rule": "missing_metadata", "detail": "absent or empty: " + ", ".join(missing)})

    mae = metrics.get("mae")
    if mae is None:
        reasons.append({"rule": "metric_ceiling", "detail": "no mae was reported"})
    elif mae > POLICY["overall_ceiling"]:
        reasons.append({"rule": "metric_ceiling", "detail": f"mae {mae} exceeds {POLICY['overall_ceiling']}"})

    if metrics.get("p95_abs_error", 0) > POLICY["p95_ceiling"]:
        reasons.append({"rule": "metric_ceiling",
                        "detail": f"p95 {metrics['p95_abs_error']} exceeds {POLICY['p95_ceiling']}"})

    zones = metrics.get("zones", {})
    for zone, ceiling in POLICY["zone_ceilings"].items():
        if zone not in zones:
            reasons.append({"rule": "zone_limit", "detail": f"{zone} has no evaluation in the bundle"})
        elif zones[zone] > ceiling:
            reasons.append({"rule": "zone_limit", "detail": f"{zone} mae {zones[zone]} exceeds {ceiling}"})

    return reasons


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()

    if not args.bundle.exists():
        print(f"BLOCK {args.bundle}: bundle not found")
        return 2

    reasons = validate(args.bundle)
    verdict = {"bundle": str(args.bundle), "decision": "block" if reasons else "pass", "reasons": reasons}
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(verdict, indent=2) + "\n", encoding="utf-8")

    print(f"{verdict['decision'].upper()} {args.bundle}")
    for reason in reasons:
        print(f"  - {reason['rule']}: {reason['detail']}")
    return 0 if verdict["decision"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
