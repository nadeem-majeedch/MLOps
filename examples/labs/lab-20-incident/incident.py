"""Generate the evidence for the 2026-10-18 incident.

    python incident.py

Writes `incident/`:
    metrics_hourly.csv   requests, errors, p95 latency, delayed mae, by hour
    alerts.json          what fired, when, and what it said
    deploys.json         which version served which window, and how it was released
    app.log              a slice of the service log around the change
    tickets.json         what users reported

The numbers are consistent with each other. Your report has to be too: this
exercise is judged on whether the timeline, the impact figure and the root
cause agree with these files.
"""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path("incident")

HOURLY = [
    # hour, requests, errors, p95_ms, mae
    ("2026-10-18T00:00", 1180, 0, 182, 2.61),
    ("2026-10-18T01:00", 1150, 0, 178, 2.58),
    ("2026-10-18T02:00", 1200, 240, 910, None),
    ("2026-10-18T03:00", 1210, 300, 1240, None),
    ("2026-10-18T04:00", 1190, 120, 420, 4.92),
    ("2026-10-18T05:00", 1160, 0, 190, 2.64),
    ("2026-10-18T06:00", 1140, 0, 185, 2.60),
]

ALERTS = [
    {"at": "2026-10-18T02:12", "name": "latency_p95_high", "value": 910, "threshold": 800,
     "severity": "warning", "state": "firing"},
    {"at": "2026-10-18T02:18", "name": "http_5xx_rate_high", "value": 0.20, "threshold": 0.02,
     "severity": "critical", "state": "firing"},
    {"at": "2026-10-18T03:05", "name": "feature_drift_psi", "value": 0.31, "threshold": 0.25,
     "severity": "warning", "state": "firing"},
    {"at": "2026-10-18T04:24", "name": "http_5xx_rate_high", "value": 0.001, "threshold": 0.02,
     "severity": "critical", "state": "resolved"},
]

DEPLOYS = [
    {"version": "v4", "from": "2026-10-15T01:40", "to": "2026-10-18T02:00", "release": "normal",
     "gate": "passed", "alias": "champion"},
    {"version": "v5", "from": "2026-10-18T02:00", "to": "2026-10-18T04:20", "release": "hotfix",
     "gate": "overridden", "override_reason": "fix long-session accuracy before the Monday rush",
     "alias": "champion (revoked)"},
]

TICKETS = [
    {"at": "2026-10-18T02:31", "channel": "support", "text": "The app says 'estimate unavailable' for every trip since about 2am."},
    {"at": "2026-10-18T02:47", "channel": "phone", "text": "Dispatch is timing out. Are you down?"},
    {"at": "2026-10-18T04:35", "channel": "support", "text": "Working again now. What happened?"},
]

LOG = """\
2026-10-18T01:58:41Z INFO  service starting version=v5 model=session-score/5
2026-10-18T01:58:42Z WARN  feature schema requires ['traffic_index'] but request schema does not provide it
2026-10-18T02:00:03Z INFO  POST /predict 200 41ms
2026-10-18T02:00:04Z ERROR POST /predict 500 KeyError: 'traffic_index'  (request_id=r0042101)
2026-10-18T02:00:04Z ERROR POST /predict 500 KeyError: 'traffic_index'  (request_id=r0042102)
2026-10-18T02:00:07Z ERROR POST /predict 500 KeyError: 'traffic_index'  (request_id=r0042130)
2026-10-18T02:07:12Z WARN  error budget burn rate 41x, window 5m
2026-10-18T02:12:00Z ALERT latency_p95_high value=910 threshold=800
2026-10-18T02:18:00Z ALERT http_5xx_rate_high value=0.20 threshold=0.02
2026-10-18T02:22:51Z INFO  on-call acknowledged page (minutes since page: 11)
2026-10-18T02:41:09Z INFO  inspecting model versions; alias champion -> v5
2026-10-18T02:58:30Z WARN  hypothesis: feature mismatch, checking training metadata
2026-10-18T03:20:44Z INFO  rollback rehearsal requires release approval
2026-10-18T03:52:10Z INFO  approval received from release owner
2026-10-18T04:20:00Z INFO  alias champion -> v4 (rolled back from v5)
2026-10-18T04:21:30Z INFO  POST /predict 200 39ms
2026-10-18T04:24:00Z INFO  error rate 0.001, alert resolved
"""


def main() -> None:
    OUT.mkdir(exist_ok=True)
    header = "hour,requests,errors,p95_ms,mae\n"
    rows = [f"{hour},{requests},{errors},{p95},{'' if mae is None else mae}" for hour, requests, errors, p95, mae in HOURLY]
    (OUT / "metrics_hourly.csv").write_text(header + "\n".join(rows) + "\n", encoding="utf-8")
    (OUT / "alerts.json").write_text(json.dumps(ALERTS, indent=2) + "\n", encoding="utf-8")
    (OUT / "deploys.json").write_text(json.dumps(DEPLOYS, indent=2) + "\n", encoding="utf-8")
    (OUT / "tickets.json").write_text(json.dumps(TICKETS, indent=2) + "\n", encoding="utf-8")
    (OUT / "app.log").write_text(LOG, encoding="utf-8")

    failed = sum(row[2] for row in HOURLY)
    print(f"wrote evidence to {OUT}/")
    print(f"failed requests on the day: {failed}")
    print("first alert 02:12, rollback 04:20, error rate back to baseline 04:24")


if __name__ == "__main__":
    main()
