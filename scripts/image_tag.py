"""Derive a local release tag from the selected model and serving inputs."""

from pathlib import Path

from heart_disease.common.io import digest, read_json, sha256

manifest = Path("artifacts/model/current/manifest.json")
if not manifest.exists():
    print("untrained")
else:
    model = read_json(manifest)["model_version"]
    paths = sorted(Path("src").rglob("*.py")) + [Path("Dockerfile"), Path("requirements.txt")]
    serving = digest({str(p): sha256(p) for p in paths})[:10]
    print(f"{model}-{serving}")
