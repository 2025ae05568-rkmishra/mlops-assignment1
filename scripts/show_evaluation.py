from heart_disease.common.io import read_json
from heart_disease.models.package import load

_, manifest = load("artifacts/model/current")
print(
    f"Existing held-out evaluation for {manifest['model_version']} (no refit or test-driven tuning)"
)
print(read_json("artifacts/model/current/metrics.json"))
