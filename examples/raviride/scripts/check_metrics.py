"""Fail when a candidate's metrics regress beyond the agreed tolerance.

Exit codes: 0 within tolerance, 1 regression, 2 missing or unreadable input.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def overall_mae(document: dict) -> float:
    return float(document.get("overall", document)["mae"])


def zone_mae(document: dict, zone: str) -> float | None:
    slices = document.get("slices", {})
    value = slices.get("zones", {}).get(zone, {}).get("mae")
    return float(value) if value is not None else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--current", required=True)
    parser.add_argument("--tolerance", type=float, default=0.05)
    parser.add_argument("--zone", default="Z08")
    parser.add_argument("--zone-tolerance", type=float, default=0.15)
    args = parser.parse_args()

    try:
        baseline = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
        current = json.loads(Path(args.current).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"could not read metrics: {exc}")
        return 2

    failures: list[str] = []
    base_mae = overall_mae(baseline)
    cur_mae = overall_mae(current)
    allowed = round(base_mae * (1 + args.tolerance), 4)
    status = "PASS" if cur_mae <= allowed else "FAIL"
    print(
        f"{status} overall mae {cur_mae:.4f} "
        f"(baseline {base_mae:.4f}, allowed {allowed:.4f}, tolerance {args.tolerance:.0%})"
    )
    if cur_mae > allowed:
        failures.append(f"overall mae {cur_mae:.4f} exceeds {allowed:.4f}")

    base_zone = zone_mae(baseline, args.zone)
    cur_zone = zone_mae(current, args.zone)
    if base_zone is not None and cur_zone is not None:
        zone_allowed = round(base_zone * (1 + args.zone_tolerance), 4)
        status = "PASS" if cur_zone <= zone_allowed else "FAIL"
        print(
            f"{status} {args.zone} mae {cur_zone:.4f} "
            f"(baseline {base_zone:.4f}, allowed {zone_allowed:.4f}, "
            f"tolerance {args.zone_tolerance:.0%})"
        )
        if cur_zone > zone_allowed:
            failures.append(f"{args.zone} mae {cur_zone:.4f} exceeds {zone_allowed:.4f}")

    if failures:
        print("model regression:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("model is within tolerance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
