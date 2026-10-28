"""Acceptance check for Lab 10.

    python check_lab10.py [--app app:app]

Starts the service with Uvicorn, exercises it over HTTP, then restarts it with
no artifact to check that liveness and readiness are different questions.
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "_shared"))

from labkit import Lab  # noqa: E402

VALID = {"hours": 4.5, "prior_score": 62, "sleep_hours": 7}
INVALID = [
    ("hours above the range", {"hours": 40, "prior_score": 62, "sleep_hours": 7}, "hours"),
    ("prior score above 100", {"hours": 4, "prior_score": 140, "sleep_hours": 7}, "prior_score"),
    ("missing field", {"hours": 4, "sleep_hours": 7}, "prior_score"),
    ("wrong type", {"hours": "four", "prior_score": 62, "sleep_hours": 7}, "hours"),
    ("extra field", {**VALID, "score": 88}, "score"),
]


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def start(port: int, env_extra: dict) -> subprocess.Popen:
    env = dict(os.environ, **(env_extra or {}))
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", str(port),
         "--log-level", "warning"],
        cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env,
    )
    return proc


def wait_for(url: str, timeout: float = 25.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                return response.status == 200
        except Exception:  # noqa: BLE001 - the server may not be listening yet
            time.sleep(0.3)
    return False


def call(url: str, payload: dict | None = None) -> tuple[int, dict | str]:
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(url, data=data, headers={"content-type": "application/json"},
                                     method="POST" if payload is not None else "GET")
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            body = response.read().decode()
            try:
                return response.status, json.loads(body)
            except json.JSONDecodeError:
                return response.status, body[:200]
    except urllib.error.HTTPError as error:
        body = error.read().decode()
        try:
            return error.code, json.loads(body)
        except json.JSONDecodeError:
            return error.code, body[:200]


def stop(proc: subprocess.Popen) -> None:
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", default="app:app")
    args = parser.parse_args()
    lab = Lab("L10", "Serve a model behind a validated contract")

    trained = subprocess.run([sys.executable, "make_model.py"], cwd=ROOT, capture_output=True, text=True)
    lab.check("the artifact is trained", trained.returncode == 0,
              (trained.stderr.strip().splitlines() or [""])[-1])
    meta = json.loads((ROOT / "models/meta.json").read_text(encoding="utf-8")) if (ROOT / "models/meta.json").exists() else {}
    lab.check("the artifact has a version", bool(meta.get("version")), str(meta.get("version")))

    port = free_port()
    server = start(port, {})
    base = f"http://127.0.0.1:{port}"
    try:
        lab.check("the service starts and answers /health", wait_for(base + "/health"), f"port {port}")
        if not wait_for(base + "/health"):
            return lab.finish()

        status, body = call(base + "/ready")
        lab.equal("/ready returns 200 with the loaded version", (status, body.get("model_version") if isinstance(body, dict) else None),
                  (200, meta.get("version")))
        status, body = call(base + "/model-info")
        lab.check("/model-info reports the artifact metadata", status == 200 and isinstance(body, dict)
                  and body.get("version") == meta.get("version"), str(body)[:80])

        status, body = call(base + "/predict", VALID)
        lab.check("a valid request returns 200", status == 200, f"status {status}")
        lab.check("the response carries a prediction and a version",
                  isinstance(body, dict) and isinstance(body.get("prediction"), (int, float))
                  and body.get("model_version") == meta.get("version"), str(body)[:100])

        repeated = [call(base + "/predict", VALID)[1]["prediction"] for _ in range(3)]
        lab.check("the same request returns the same answer", len(set(repeated)) == 1, str(repeated))

        for name, payload, field in INVALID:
            status, body = call(base + "/predict", payload)
            detail = json.dumps(body)[:150] if not isinstance(body, str) else body
            lab.equal(f"{name} is rejected with 422", status, 422)
            lab.check(f"{name} names {field}", field in detail, detail)

        status, _ = call(base + "/docs")
        lab.check("/docs is served", status == 200, f"status {status}")
        status, schema = call(base + "/openapi.json")
        paths = schema.get("paths", {}) if isinstance(schema, dict) else {}
        lab.check("OpenAPI lists the three endpoints",
                  {"/predict", "/ready", "/model-info"} <= set(paths), str(sorted(paths)))
    finally:
        stop(server)

    missing_port = free_port()
    missing = start(missing_port, {"MODEL_PATH": "models/does-not-exist.joblib"})
    missing_base = f"http://127.0.0.1:{missing_port}"
    try:
        lab.check("the service still starts without an artifact", wait_for(missing_base + "/health"),
                  "liveness must not depend on the model")
        if wait_for(missing_base + "/health"):
            status, _ = call(missing_base + "/ready")
            lab.equal("/ready reports 503 without an artifact", status, 503)
            status, body = call(missing_base + "/predict", VALID)
            lab.equal("/predict reports 503 without an artifact", status, 503)
            lab.check("the 503 message is readable", isinstance(body, dict) and "detail" in body, str(body)[:80])
    finally:
        stop(missing)

    return lab.finish()


if __name__ == "__main__":
    raise SystemExit(main())
