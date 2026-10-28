"""Acceptance check for Lab 04.

    python check_lab04.py [--reproduce reproduce.py]

Builds two versions of one dataset, reproduces the first twice, then edits the
bytes underneath the first version and expects a refusal.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "_shared"))

from labkit import Lab  # noqa: E402


def run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reproduce", default="reproduce.py")
    args = parser.parse_args()
    lab = Lab("L04", "Version a dataset and reproduce a run")

    drop = ROOT / "data/versioned_drop.csv"
    drop.parent.mkdir(exist_ok=True)
    shutil.copyfile(ROOT / "data/sessions.csv", drop)
    shutil.rmtree(ROOT / "data/manifests", ignore_errors=True)
    shutil.rmtree(ROOT / "runs", ignore_errors=True)

    first = run(["version_data.py", "--data", str(drop), "--tag", "v1"])
    manifest_path = ROOT / "data/manifests/v1.json"
    lab.check("version_data.py writes a manifest", first.returncode == 0 and manifest_path.exists(),
              (first.stderr.strip().splitlines() or ["no stderr"])[-1])
    if not manifest_path.exists():
        return lab.finish()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    lab.equal("manifest hash is the hash of the bytes", manifest.get("sha256"), sha(drop))
    lab.equal("manifest records the row count", manifest.get("rows"), 480)
    lab.check("manifest records column types", isinstance(manifest.get("columns"), dict) and len(manifest["columns"]) == 6,
              f"{len(manifest.get('columns', {}))} columns")

    runs = []
    for attempt in (1, 2):
        proc = run([args.reproduce, "--manifest", "data/manifests/v1.json"])
        record_path = ROOT / f"runs/v1-{manifest['sha256'][:8]}.json"
        ok = proc.returncode == 0 and record_path.exists()
        lab.check(f"reproduction {attempt} trains from v1", ok,
                  (proc.stderr.strip().splitlines() or ["no stderr"])[-1])
        if record_path.exists():
            runs.append(json.loads(record_path.read_text(encoding="utf-8")))

    if len(runs) == 2:
        lab.equal("two reproductions report the same mae", runs[0].get("mae"), runs[1].get("mae"))
        lab.equal("two reproductions report the same predictions hash",
                  runs[0].get("predictions_sha256"), runs[1].get("predictions_sha256"))
        lab.equal("run record names the dataset hash", runs[0].get("sha256"), manifest["sha256"])
    else:
        lab.fail("two run records to compare", f"found {len(runs)}")

    with drop.open("a", encoding="utf-8") as handle:
        handle.write("S9001,A,3.5,64.0,7.1,71.2\n")
    second = run(["version_data.py", "--data", str(drop), "--tag", "v2"])
    v2_path = ROOT / "data/manifests/v2.json"
    lab.check("a second tag records different content", second.returncode == 0 and v2_path.exists(), "v2 manifest")
    if v2_path.exists():
        v2 = json.loads(v2_path.read_text(encoding="utf-8"))
        lab.check("v1 and v2 hashes differ", v2["sha256"] != manifest["sha256"],
                  f"v2 {v2['sha256'][:12]}... vs v1 {manifest['sha256'][:12]}...")
        lab.equal("v2 row count reflects the appended row", v2.get("rows"), 481)

    refused = run([args.reproduce, "--manifest", "data/manifests/v1.json"])
    message = (refused.stdout + refused.stderr).lower()
    lab.equal("stale manifest is refused with exit 2", refused.returncode, 2)
    lab.check("refusal names the mismatch", "hash mismatch" in message, message.strip().splitlines()[-1][:80] if message else "no output")
    lab.check("no run record was written for the stale manifest",
              not (ROOT / f"runs/v2-{manifest['sha256'][:8]}.json").exists(), "checked")

    shutil.copyfile(ROOT / "data/sessions.csv", drop)
    return lab.finish()


if __name__ == "__main__":
    raise SystemExit(main())
