"""Send every support ticket to the service and record what comes back.

    python probes.py
    python probes.py --base-url http://127.0.0.1:8010    # against a live server

Writes `artifacts/probes.json`: one entry per probe with the status code, a
short response excerpt, and the exception type when the server raised. Run it
before forming an opinion; this file is the evidence, not the ticket text.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fastapi.testclient import TestClient

import service

VALID = {"hours": 4.5, "prior_score": 62, "sleep_hours": 7}

PROBES = [
    {"id": "p01", "method": "POST", "path": "/predict", "payload": VALID},
    {"id": "p02", "method": "POST", "path": "/predict", "payload": {**VALID, "hours": -2}},
    {"id": "p03", "method": "POST", "path": "/predict", "payload": {**VALID, "prior_score": 150}},
    {"id": "p04", "method": "POST", "path": "/predict", "payload": {"hours": 4.5, "prior_score": 62}},
    {"id": "p05", "method": "POST", "path": "/predict", "payload": {**VALID, "score": 90}},
    {"id": "p06", "method": "POST", "path": "/predict", "payload": {**VALID, "prior_score": 0}},
    {"id": "p07", "method": "GET", "path": "/predict"},
    {"id": "p08", "method": "GET", "path": "/prediction"},
    {"id": "p09", "method": "POST", "path": "/predict", "payload": {}},
    {"id": "p10", "method": "POST", "path": "/predict", "payload": {**VALID, "hours": None}},
]


def excerpt(response) -> str:
    try:
        body = response.json()
    except Exception:  # noqa: BLE001 - the body may not be JSON
        return response.text[:120]
    if isinstance(body, dict) and "detail" in body:
        detail = body["detail"]
        if isinstance(detail, list) and detail:
            first = detail[0]
            return f"{first.get('type', '')}: {first.get('loc', '')}"
        return str(detail)[:120]
    return json.dumps(body)[:120]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", help="probe a running server instead of the in-process app")
    parser.add_argument("--out", type=Path, default=Path("artifacts/probes.json"))
    args = parser.parse_args()

    results = []
    if args.base_url:
        import httpx

        client = httpx.Client(base_url=args.base_url, timeout=10)
        send = lambda method, path, payload: client.request(method, path, json=payload)  # noqa: E731
    else:
        client = TestClient(service.app, raise_server_exceptions=False)
        client.__enter__()
        send = lambda method, path, payload: client.request(method, path, json=payload)  # noqa: E731

    try:
        for probe in PROBES:
            response = send(probe["method"], probe["path"], probe.get("payload"))
            results.append(
                {
                    "id": probe["id"],
                    "request": f"{probe['method']} {probe['path']}",
                    "status": response.status_code,
                    "response": excerpt(response),
                }
            )
    finally:
        if not args.base_url:
            client.__exit__(None, None, None)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"{'id':<5}{'request':<22}{'status':<7}response")
    for row in results:
        print(f"{row['id']:<5}{row['request']:<22}{row['status']:<7}{row['response']}")
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
