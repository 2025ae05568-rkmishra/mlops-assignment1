import json
from pathlib import Path

import pytest

from heart_disease.submission import junit_count, validate


def put(root, name, value):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


@pytest.fixture
def evidence(tmp_path):
    put(tmp_path, "release.json", {"commit": "abc", "image": "api:run-1", "image_id": "sha256:abc"})
    put(tmp_path, "manifest.json", {"commit": "abc", "model_version": "selected"})
    put(
        tmp_path,
        "api.json",
        {
            "ready": {"model_version": "selected"},
            "version": {"model_version": "selected", "commit": "abc"},
            "prediction": {"model_version": "selected"},
            "invalid_status": 422,
            "metrics_status": 404,
        },
    )
    put(
        tmp_path,
        "deployment.txt",
        {
            "spec": {"replicas": 2, "template": {"spec": {"containers": [{"image": "api:run-1"}]}}},
            "status": {"availableReplicas": 2},
        },
    )
    put(
        tmp_path,
        "pods.txt",
        {
            "items": [
                {
                    "metadata": {"name": name},
                    "spec": {"containers": [{"image": "api:run-1"}]},
                    "status": {"conditions": [{"type": "Ready", "status": "True"}]},
                }
                for name in ("pod-a", "pod-b")
            ]
        },
    )
    put(
        tmp_path,
        "monitoring.json",
        {"targets": [{"pod": name, "health": "up"} for name in ("pod-a", "pod-b")]},
    )
    put(tmp_path, "ci/docker-smoke.json", {"model_version": "selected", "image_id": "sha256:abc"})
    for name in ("unit", "integration"):
        (tmp_path / f"ci/{name}-tests.xml").write_text(
            '<testsuites><testsuite tests="2" failures="0" errors="0" skipped="0"/></testsuites>'
        )
    return tmp_path


def test_consistent_release_evidence_accepted(evidence):
    assert validate(evidence)[3] == {"unit": 2, "integration": 2}


@pytest.mark.parametrize(
    "file,key,value",
    [
        ("manifest.json", "commit", "another-commit"),
        ("manifest.json", "model_version", "stale-model"),
        ("api.json", "metrics_status", 200),
        ("api.json", "invalid_status", 200),
        ("monitoring.json", "targets", [{"pod": "old-pod", "health": "up"}]),
        ("ci/docker-smoke.json", "model_version", "other-model"),
        ("ci/docker-smoke.json", "image_id", "sha256:another"),
    ],
)
def test_stale_or_incomplete_evidence_rejected(evidence, file, key, value):
    data = json.loads((evidence / file).read_text())
    data[key] = value
    put(evidence, file, data)
    with pytest.raises(ValueError):
        validate(evidence)


def test_partial_rollout_rejected(evidence):
    data = json.loads((evidence / "deployment.txt").read_text())
    data["status"]["availableReplicas"] = 1
    put(evidence, "deployment.txt", data)
    with pytest.raises(ValueError, match="replicas"):
        validate(evidence)


@pytest.mark.parametrize(
    "attributes", ['tests="0"', 'tests="2" failures="1"', 'tests="2" skipped="1"']
)
def test_empty_failed_or_skipped_test_proof_rejected(tmp_path, attributes):
    path = Path(tmp_path) / "tests.xml"
    path.write_text(f"<testsuites><testsuite {attributes}/></testsuites>")
    with pytest.raises(ValueError):
        junit_count(path)
