"""Validate that submission evidence describes the selected BITS release."""

import xml.etree.ElementTree as ET
from pathlib import Path

from heart_disease.common.io import read_json


def junit_count(path):
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    totals = {
        key: sum(int(s.get(key, 0)) for s in suites)
        for key in ("tests", "failures", "errors", "skipped")
    }
    if not totals["tests"] or any(totals[k] for k in ("failures", "errors", "skipped")):
        raise ValueError(f"Incomplete or unsuccessful test evidence: {path}")
    return totals["tests"]


def validate(evidence):
    evidence = Path(evidence)
    release = read_json(evidence / "release.json")
    manifest = read_json(evidence / "manifest.json")
    if manifest["commit"] != release["commit"]:
        raise ValueError("Release and model commits differ")
    api = read_json(evidence / "api.json")
    for response in (api["ready"], api["version"], api["prediction"]):
        if response["model_version"] != manifest["model_version"]:
            raise ValueError("Served model differs from selected release")
    if api["version"]["commit"] != release["commit"]:
        raise ValueError("Served commit differs from selected release")
    if api["invalid_status"] != 422 or api["metrics_status"] != 404:
        raise ValueError("API validation or Ingress boundary check failed")
    deployment = read_json(evidence / "deployment.txt")
    wanted = deployment["spec"]["replicas"]
    if deployment["status"].get("availableReplicas", 0) != wanted:
        raise ValueError("Not all requested API replicas are available")
    template = deployment["spec"]["template"]["spec"]["containers"][0]
    if template["image"] != release["image"]:
        raise ValueError("Deployment image differs from selected release")
    pods = read_json(evidence / "pods.txt")["items"]
    current = [p for p in pods if not p["metadata"].get("deletionTimestamp")]
    ready = {
        p["metadata"]["name"]
        for p in current
        if any(
            c["type"] == "Ready" and c["status"] == "True"
            for c in p.get("status", {}).get("conditions", [])
        )
    }
    if len(ready) != wanted:
        raise ValueError("API pod readiness evidence is incomplete")
    if any(p["spec"]["containers"][0]["image"] != release["image"] for p in current):
        raise ValueError("Running pod image differs from selected release")
    targets = read_json(evidence / "monitoring.json")["targets"]
    up = {t["pod"] for t in targets if t["health"] == "up"}
    if not ready <= up:
        raise ValueError("Current API pods are not all scraped successfully")
    docker = read_json(evidence / "ci/docker-smoke.json")
    if docker["model_version"] != manifest["model_version"]:
        raise ValueError("Docker proof describes another model")
    if docker["image_id"] != release["image_id"]:
        raise ValueError("Docker proof describes another image")
    counts = {
        name: junit_count(evidence / f"ci/{name}-tests.xml") for name in ("unit", "integration")
    }
    return release, manifest, api, counts
