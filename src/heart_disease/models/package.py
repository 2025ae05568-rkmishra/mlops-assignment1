import argparse
import shutil
from pathlib import Path

import mlflow.sklearn

from heart_disease.common.io import digest, read_json, sha256, write_json
from heart_disease.features.schema import feature_schema

REQUIRED = {
    "manifest.json",
    "metrics.json",
    "feature-schema.json",
    "model-card.md",
    "model/MLmodel",
}


def write_checksums(bundle):
    bundle = Path(bundle)
    entries = {
        str(p.relative_to(bundle)): sha256(p)
        for p in sorted(bundle.rglob("*"))
        if p.is_file() and p.name != "checksums.sha256"
    }
    (bundle / "checksums.sha256").write_text(
        "".join(f"{h}  {name}\n" for name, h in entries.items())
    )
    return entries


def verify(bundle):
    bundle = Path(bundle)
    checksum_file = bundle / "checksums.sha256"
    if not checksum_file.is_file():
        raise ValueError("Bundle checksum manifest missing")
    expected = {}
    for line in checksum_file.read_text().splitlines():
        checksum, name = line.split("  ", 1)
        target = (bundle / name).resolve()
        if not target.is_relative_to(bundle.resolve()) or name in expected:
            raise ValueError("Invalid checksum manifest path")
        expected[name] = checksum
        if not target.is_file() or sha256(target) != checksum:
            raise ValueError("Bundle checksum verification failed")
    actual = {
        str(p.relative_to(bundle))
        for p in bundle.rglob("*")
        if p.is_file() and p.name != "checksums.sha256"
    }
    if actual != set(expected) or not REQUIRED <= actual:
        raise ValueError("Bundle files missing or unexpected")
    if digest(read_json(bundle / "feature-schema.json")) != digest(feature_schema()):
        raise ValueError("Feature schema mismatch")
    manifest = read_json(bundle / "manifest.json")
    model_files = {k: v for k, v in expected.items() if k.startswith("model/")}
    if manifest["model_hash"] != digest(model_files):
        raise ValueError("Model directory hash mismatch")
    if manifest["classes"] != [0, 1] or manifest["positive_label"] != 1:
        raise ValueError("Class metadata mismatch")
    if not 0 <= manifest["threshold"] <= 1:
        raise ValueError("Invalid threshold")
    return manifest


def load(bundle):
    manifest = verify(bundle)
    model = mlflow.sklearn.load_model(str(Path(bundle) / "model"))
    if list(model.classes_) != manifest["classes"]:
        raise ValueError("Loaded classifier classes mismatch")
    if list(model.feature_names_in_) != feature_schema()["features"]:
        raise ValueError("Loaded classifier feature schema mismatch")
    return model, manifest


def promote(bundle, current="artifacts/model/current"):
    load(bundle)
    current = Path(current)
    if current.exists():
        shutil.rmtree(current)
    shutil.copytree(bundle, current)
    write_json("artifacts/release.json", {"bundle": str(bundle), "model": verify(bundle)})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", default="artifacts/model/current")
    args = parser.parse_args()
    _, manifest = load(args.bundle)
    print(f"Verified {manifest['model_version']}")
