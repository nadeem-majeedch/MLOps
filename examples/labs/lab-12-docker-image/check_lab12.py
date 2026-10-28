"""Acceptance check for Lab 12.

    python check_lab12.py [--dockerfile Dockerfile] [--ignore .dockerignore]

Static audit plus a Compose sanity check. A real build is attempted only when
Docker is installed; otherwise the check reports the limitation instead of
pretending the image is verified.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "_shared"))
sys.path.insert(0, str(ROOT))

from labkit import Lab  # noqa: E402

import audit_image  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dockerfile", default="Dockerfile")
    parser.add_argument("--ignore", default=".dockerignore")
    parser.add_argument("--build", action="store_true", help="build the image when Docker is installed")
    args = parser.parse_args()
    lab = Lab("L12", "Package the service as a container")

    dockerfile = ROOT / args.dockerfile
    if not lab.check("Dockerfile exists", dockerfile.exists(), str(dockerfile)):
        return lab.finish()

    findings = audit_image.audit(dockerfile, ROOT / args.ignore, ROOT / "requirements.txt")
    for finding in findings:
        lab.check(finding.check, finding.ok, finding.detail)

    compose_path = ROOT / "compose.yaml"
    if lab.check("compose.yaml exists", compose_path.exists(), "compose.yaml"):
        compose = yaml.safe_load(compose_path.read_text(encoding="utf-8")) or {}
        api = (compose.get("services") or {}).get("api", {})
        lab.equal("compose builds the local directory", api.get("build"), ".")
        lab.check("compose publishes port 8000", "8000:8000" in (api.get("ports") or []), str(api.get("ports")))
        lab.check("compose passes a model path through the environment",
                  "MODEL_PATH" in (api.get("environment") or {}), str(api.get("environment")))

    docker = shutil.which("docker")
    if docker is None:
        print("\n  [SKIP] image build: Docker is not installed on this machine.")
        print("         Verify on a machine with Docker: docs/labs/lab-12-docker-image.md, Part 3.")
    elif args.build:
        built = subprocess.run([docker, "build", "-t", "session-score:local", "."],
                               cwd=ROOT, capture_output=True, text=True)
        lab.check("docker build succeeds", built.returncode == 0, built.stderr.strip()[-160:] or "ok")
        if built.returncode == 0:
            size = subprocess.run([docker, "image", "inspect", "session-score:local", "--format", "{{.Size}}"],
                                  capture_output=True, text=True)
            if size.returncode == 0:
                print(f"  image size: {int(size.stdout.strip()) / 1e6:.0f} MB")
    else:
        print("\n  [SKIP] image build: pass --build to run it (Docker is installed).")

    return lab.finish()


if __name__ == "__main__":
    raise SystemExit(main())
