"""Lab 08 starter: a gate that only checks the average.

    python gate.py --candidate candidates/deeper_v2.json \
                   --champion candidates/baseline_v1.json
    python gate.py --candidate candidates/shallow_v3.json \
                   --champion candidates/baseline_v1.json --json artifacts/shallow.json

Exit code 0 means promote, 1 means block. A block must say which rule failed
and by how much: "MAE too high" sends the candidate's owner nowhere.

Verdict contract:

    {"candidate": str, "decision": "pass" | "block",
     "reasons": [{"rule": str, "detail": str}, ...]}

Rule ids: absolute_ceiling, overall_regression, p95_ceiling, zone_limit,
dropped_zone, missing_slice.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

POLICY = Path("policy.yaml")


def gate(candidate: dict, champion: dict, policy: dict) -> list[dict]:
    reasons: list[dict] = []
    metrics = candidate["metrics"]
    base = champion["metrics"]

    if metrics["mae"] > policy["overall_ceiling"]:
        reasons.append(
            {
                "rule": "absolute_ceiling",
                "detail": f"mae {metrics['mae']:.3f} exceeds ceiling {policy['overall_ceiling']:.3f}",
            }
        )

    allowed = round(base["mae"] * (1 + policy["max_regression"]), 4)
    if metrics["mae"] > allowed:
        reasons.append(
            {
                "rule": "overall_regression",
                "detail": f"mae {metrics['mae']:.3f} vs champion {base['mae']:.3f}, allowed {allowed:.3f}",
            }
        )

    # TODO 1: p95_ceiling -- the 95th percentile absolute error against its own
    #         ceiling. Name the rule "p95_ceiling".
    # TODO 2: zone_limit -- for each zone in policy["zone_limits"], fail when the
    #         candidate is worse than the champion by more than the tolerance.
    #         Report the zone, both values, and the allowance.
    # TODO 3: dropped_zone -- when policy["forbid_dropped_zones"] is true and
    #         the candidate lists any dropped zone, fail and name them.
    # TODO 4: missing_slice -- every zone in policy["required_slices"] must be
    #         present in the candidate's zone report.

    return reasons


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--champion", type=Path, required=True)
    parser.add_argument("--policy", type=Path, default=POLICY)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()

    policy = yaml.safe_load(args.policy.read_text(encoding="utf-8"))
    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
    champion = json.loads(args.champion.read_text(encoding="utf-8"))

    reasons = gate(candidate, champion, policy)
    verdict = {
        "candidate": candidate.get("candidate", args.candidate.stem),
        "decision": "block" if reasons else "pass",
        "reasons": reasons,
    }
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(verdict, indent=2) + "\n", encoding="utf-8")

    print(f"{verdict['decision'].upper()} {verdict['candidate']}")
    for reason in reasons:
        print(f"  - {reason['rule']}: {reason['detail']}")
    return 0 if verdict["decision"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
