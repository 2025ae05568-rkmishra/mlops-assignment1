"""Capture actual BITS deployment evidence for the report."""

import argparse
import shutil
import subprocess
import time
from pathlib import Path

import httpx

from heart_disease.common.io import now, read_json, sha256, write_json
from heart_disease.models.package import verify
from heart_disease.submission import validate


def capture(args):
    source, out = Path(args.release_root).resolve(), Path(args.output).resolve()
    if out.exists():
        raise ValueError("Use a new evidence directory for each capture")
    manifest = verify(source / "artifacts/model/current")
    if read_json(source / "reports/metrics/final.json") != read_json(
        source / "artifacts/model/current/metrics.json"
    ):
        raise ValueError("Release report metrics differ from the verified model bundle")
    out.mkdir(parents=True)
    for folder in ("metrics", "figures"):
        shutil.copytree(source / "reports" / folder, out / folder)
    shutil.copytree(source / "data/manifests", out / "data")
    (out / "ci").mkdir()
    for name in ("unit-tests.xml", "integration-tests.xml", "docker-smoke.json"):
        shutil.copy2(source / "reports/evidence" / name, out / "ci" / name)
    (out / "screenshots").mkdir()
    write_json(out / "manifest.json", manifest)
    write_json(
        out / "release.json",
        {
            "captured_at": now(),
            "repository": args.repository,
            "commit": manifest["commit"],
            "run_id": args.run_id,
            "attempt": args.attempt,
            "image": args.image,
            "image_id": subprocess.check_output(
                ["docker", "image", "inspect", args.image, "--format", "{{.Id}}"], text=True
            ).strip(),
            "archive_sha256": sha256(source / "artifacts/heart-disease-api.tar.gz"),
            "release_root": str(source),
            "access_mode": "Private BITS VM; localhost forwarding to Traefik Ingress",
        },
    )
    sample = read_json("tests/fixtures/valid_request.json")
    with httpx.Client(
        base_url=args.url, headers={"Host": "heart-disease.test"}, timeout=15
    ) as client:
        ready = client.get("/ready")
        ready.raise_for_status()
        version = client.get("/version")
        version.raise_for_status()
        end = time.monotonic() + args.traffic_seconds
        counts = {"200": 0, "422": 0}
        while True:
            prediction = client.post("/predict", json=sample)
            prediction.raise_for_status()
            invalid = client.post("/predict", json={**sample, "cp": 0})
            if invalid.status_code != 422:
                raise ValueError("Invalid request was not rejected")
            counts["200"] += 1
            counts["422"] += 1
            if time.monotonic() >= end:
                break
            time.sleep(0.5)
        write_json(
            out / "api.json",
            {
                "captured_at": now(),
                "url": args.url,
                "host": "heart-disease.test",
                "ready": ready.json(),
                "version": version.json(),
                "prediction": prediction.json(),
                "invalid_status": invalid.status_code,
                "metrics_status": client.get("/metrics").status_code,
                "traffic_counts": counts,
                "traffic_seconds": args.traffic_seconds,
            },
        )
    config = read_json("deploy/monitoring/dashboard.json")
    with httpx.Client(base_url=args.prometheus, timeout=15) as client:
        targets = client.get("/api/v1/targets")
        targets.raise_for_status()
        panels = []
        for panel in config["panels"]:
            response = client.get(
                "/api/v1/query_range",
                params={
                    "query": panel["query"],
                    "start": time.time() - config["window_seconds"],
                    "end": time.time(),
                    "step": config["step_seconds"],
                },
            )
            response.raise_for_status()
            data = response.json()
            if data["status"] != "success":
                raise ValueError("Prometheus query failed")
            panels.append({**panel, "series": data["data"]["result"]})
        write_json(
            out / "monitoring.json",
            {
                "captured_at": now(),
                "panels": panels,
                "targets": [
                    {"pod": t.get("labels", {}).get("pod", "unknown"), "health": t["health"]}
                    for t in targets.json()["data"]["activeTargets"]
                ],
            },
        )
    subprocess.run(
        [".venv/bin/python", "scripts/collect_evidence.py", "--output", str(out)], check=True
    )
    validate(out)
    Path("reports/evidence/runtime/latest-submission.txt").write_text(str(out) + "\n")
    print(f"Verified BITS evidence: {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("release-root", "output", "repository", "run-id", "attempt", "image"):
        parser.add_argument(f"--{name}", required=True)
    parser.add_argument("--url", default="http://127.0.0.1:8081")
    parser.add_argument("--prometheus", default="http://127.0.0.1:9090")
    parser.add_argument("--traffic-seconds", type=int, default=30)
    capture(parser.parse_args())
