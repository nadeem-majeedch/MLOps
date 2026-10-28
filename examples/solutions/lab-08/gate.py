"""Reference solution for Lab 08: five rules, each with a number in the message."""

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

    p95_ceiling = policy.get("p95_ceiling")
    if p95_ceiling is not None and metrics.get("p95_abs_error", 0) > p95_ceiling:
        reasons.append(
            {
                "rule": "p95_ceiling",
                "detail": f"p95 {metrics['p95_abs_error']:.3f} exceeds ceiling {p95_ceiling:.3f}",
            }
        )

    candidate_zones = metrics.get("zones", {})
    if policy.get("forbid_dropped_zones") and candidate.get("dropped_zones"):
        reasons.append(
            {
                "rule": "dropped_zone",
                "detail": "training data excludes production zones: " + ", ".join(candidate["dropped_zones"]),
            }
        )

    missing = [zone for zone in policy.get("required_slices", []) if zone not in candidate_zones]
    if missing:
        reasons.append(
            {"rule": "missing_slice", "detail": "no evaluation for required slices: " + ", ".join(missing)}
        )

    for zone, limit in policy.get("zone_limits", {}).items():
        if zone not in candidate_zones or zone not in base.get("zones", {}):
            continue
        allowed_zone = round(base["zones"][zone]["mae"] * (1 + limit), 4)
        actual = candidate_zones[zone]["mae"]
        if actual > allowed_zone:
            reasons.append(
                {
                    "rule": "zone_limit",
                    "detail": (
                        f"{zone} mae {actual:.3f} vs champion {base['zones'][zone]['mae']:.3f} "
                        f"by more than {limit:.0%} (allowed {allowed_zone:.3f})"
                    ),
                }
            )

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
