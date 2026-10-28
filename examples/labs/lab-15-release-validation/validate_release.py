"""Lab 15 starter: a release check that only reads the headline number.

    python make_bundles.py
    python validate_release.py --bundle release/tempting

Run it. It says PASS. The bundle is not shippable: the artifact was modified
after its checksum was recorded, every test was skipped, and no owner is named.
A metrics-only gate cannot see any of that, and a green tick from it is worse
than no tick, because someone will trust it.

Your job is to make the gate fail closed. A bundle that omits evidence must be
rejected, not treated as compliant.

Reason ids to report:

    artifact_hash     checksums.txt disagrees with the files on disk
    artifact_loads    the artifact cannot be loaded, or predicts nonsense
    tests_evidence    tests did not run, or any failed
    missing_metadata  a required field is absent or empty
    metric_ceiling    mae above the absolute ceiling
    zone_limit        a monitored zone above its ceiling

Output contract (`--json`):

    {"bundle": str, "decision": "pass" | "block",
     "reasons": [{"rule": str, "detail": str}]}
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

POLICY = {"overall_ceiling": 3.20, "p95_ceiling": 9.60, "zone_ceilings": {"Z08": 6.05}}

REQUIRED_METADATA = ["candidate", "git_commit", "data_hash", "trained_at", "owner"]
MIN_TESTS = 20


def validate(bundle: Path) -> list[dict]:
    reasons: list[dict] = []
    candidate = json.loads((bundle / "candidate.json").read_text(encoding="utf-8"))
    metrics = candidate["metrics"]

    if metrics["mae"] > POLICY["overall_ceiling"]:
        reasons.append({"rule": "metric_ceiling", "detail": f"mae {metrics['mae']} exceeds {POLICY['overall_ceiling']}"})

    # TODO 1: artifact_hash -- recompute sha256 of every file named in
    #         checksums.txt and report any mismatch. A missing checksums file is
    #         also a block.
    # TODO 2: artifact_loads -- load model.joblib and make one prediction.
    #         A non-finite result is a failure, not a warning.
    # TODO 3: tests_evidence -- tests.json must exist, report at least MIN_TESTS
    #         executed tests, and have failed == 0. Skipping everything is not
    #         passing.
    # TODO 4: missing_metadata -- every field in REQUIRED_METADATA must be a
    #         non-empty string.
    # TODO 5: zone_limit -- each zone in POLICY["zone_ceilings"] must be present
    #         in metrics["zones"] and at or below its ceiling.

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
    verdict = {
        "bundle": str(args.bundle),
        "decision": "block" if reasons else "pass",
        "reasons": reasons,
    }
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(verdict, indent=2) + "\n", encoding="utf-8")

    print(f"{verdict['decision'].upper()} {args.bundle}")
    for reason in reasons:
        print(f"  - {reason['rule']}: {reason['detail']}")
    return 0 if verdict["decision"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
