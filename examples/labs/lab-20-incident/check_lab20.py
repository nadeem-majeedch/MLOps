"""Acceptance check for Lab 20.

    python check_lab20.py [--incident incident.json] [--postmortem postmortem.md]

Every claim in the report is compared with the evidence pack: the impact
figure, the timestamps, the version restored, and the mechanism.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "_shared"))

from labkit import Lab  # noqa: E402

SECTIONS = ["Summary", "Impact", "Timeline", "Root cause", "Detection", "Response", "Prevention", "Lessons"]


def section_body(text: str, heading: str) -> str:
    marker = f"## {heading}"
    if marker not in text:
        return ""
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--incident", default="incident.json")
    parser.add_argument("--postmortem", default="postmortem.md")
    args = parser.parse_args()
    lab = Lab("L20", "Run the incident review end to end")

    made = subprocess.run([sys.executable, "incident.py"], cwd=ROOT, capture_output=True, text=True)
    lab.check("the evidence pack is generated", made.returncode == 0, (made.stderr.strip().splitlines() or [""])[-1])

    import pandas as pd

    metrics = pd.read_csv(ROOT / "incident/metrics_hourly.csv")
    expected_failures = int(metrics["errors"].sum())

    path = ROOT / args.incident
    if not lab.check("incident.json exists", path.exists(), str(path)):
        return lab.finish()
    record = json.loads(path.read_text(encoding="utf-8"))

    lab.check("severity is stated", str(record.get("severity", "")).upper() in {"SEV1", "SEV2", "SEV3", "CRITICAL", "HIGH"},
              str(record.get("severity")))
    lab.equal("detection time is the first page", record.get("detected_at"), "2026-10-18T02:12")
    lab.equal("mitigation time is the alias change", record.get("mitigated_at"), "2026-10-18T04:20")

    try:
        started = datetime.fromisoformat(record["detected_at"])
        ended = datetime.fromisoformat(record["mitigated_at"])
        minutes = int((ended - started).total_seconds() // 60)
    except Exception:  # noqa: BLE001 - already checked the strings
        minutes = -1
    lab.equal("the reported mttr matches its own timestamps", record.get("mttr_minutes"), minutes)
    lab.check("the mttr is over two hours", 120 <= minutes <= 140, f"{minutes} minutes")

    impact = record.get("impact", {})
    lab.equal("failed requests match the metrics", impact.get("failed_requests"), expected_failures)

    cause = str(record.get("root_cause", "")).lower()
    lab.check("the root cause names the missing feature",
              "traffic_index" in cause or ("schema" in cause and "feature" in cause), cause[:110])

    factors = " ".join(str(item).lower() for item in record.get("contributing_factors", []))
    lab.check("the gate override is a contributing factor",
              any(word in factors for word in ("override", "gate", "bypass", "skipped")), factors[:110])
    lab.check("the release shape is a contributing factor",
              any(word in factors for word in ("canary", "100%", "rollout", "all traffic", "approval", "response")),
              factors[:110])
    lab.check("at least three contributing factors are named", len(record.get("contributing_factors", [])) >= 3,
              str(len(record.get("contributing_factors", []))))

    action = record.get("immediate_action", {})
    lab.equal("the immediate action is a rollback", action.get("action"), "rollback")
    lab.equal("the previous version is restored", action.get("target_version"), "v4")
    lab.check("recovery is verified with a signal", bool(action.get("verified_by")) and
              any(word in str(action["verified_by"]).lower() for word in ("5xx", "error", "latency", "alert")),
              str(action.get("verified_by"))[:90])

    timeline = record.get("timeline", [])
    lab.check("the timeline has at least eight entries", len(timeline) >= 8, f"{len(timeline)} entries")
    if timeline:
        stamps = [row.get("at", "") for row in timeline]
        lab.check("the timeline is in order", stamps == sorted(stamps), f"{stamps[:2]} ... {stamps[-1:]}")
        joined = " ".join(str(row.get("event", "")) for row in timeline).lower()
        for moment in ("alert", "rollback", "resolved"):
            lab.check(f"the timeline includes {moment}", moment in joined, "checked event text")

    prevention = " ".join(str(item).lower() for item in record.get("prevention", []))
    lab.check("at least three preventive changes are listed", len(record.get("prevention", [])) >= 3,
              str(len(record.get("prevention", []))))
    lab.check("prevention is verifiable, not aspirational",
              sum(1 for word in ("test", "canary", "gate", "alert", "block", "drill") if word in prevention) >= 3,
              prevention[:110])

    post_path = ROOT / args.postmortem
    if not lab.check("the postmortem exists", post_path.exists(), str(post_path)):
        return lab.finish()
    post = post_path.read_text(encoding="utf-8")
    for heading in SECTIONS:
        body = section_body(post, heading).strip()
        lab.check(f"the postmortem has a filled '{heading}' section", len(body) > 80 and "TODO" not in body,
                  f"{len(body)} characters")
    lab.check("the postmortem is explicitly blameless", "blameless" in post.lower(), "stated")
    lab.check("no individual is blamed", not re.search(r"(?i)\b(careless|to blame|fault of|mistake by)\b", post),
              "searched for blaming language")
    timeline_body = section_body(post, "Timeline")
    stamps_found = len(re.findall(r"\b\d{2}:\d{2}", timeline_body))
    lab.check("the written timeline carries at least eight timestamps", stamps_found >= 8, f"{stamps_found} timestamps")

    return lab.finish()


if __name__ == "__main__":
    raise SystemExit(main())
