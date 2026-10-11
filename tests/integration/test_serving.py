import json
import shutil
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from heart_disease.api.main import create_app
from heart_disease.features.schema import FEATURES
from heart_disease.models.evaluate import probabilities
from heart_disease.models.package import load

pytestmark = pytest.mark.integration
BUNDLE = Path("artifacts/model/current")
SAMPLE = json.loads(Path("tests/fixtures/valid_request.json").read_text())


def test_selected_model_api_parity_and_metrics():
    model, manifest = load(BUNDLE)
    records = pd.read_csv("data/processed/cleaned.csv").iloc[:30][FEATURES]
    with TestClient(create_app(BUNDLE)) as client:
        classes = set()
        for _, record in records.iterrows():
            payload = {
                k: None
                if pd.isna(v)
                else float(v)
                if k in ["trestbps", "chol", "thalach", "oldpeak"]
                else int(v)
                for k, v in record.items()
            }
            result = client.post("/predict", json=dict(reversed(list(payload.items()))))
            assert result.status_code == 200
            out = result.json()
            direct = float(
                probabilities(model, pd.DataFrame([payload], columns=FEATURES).astype(float))[0]
            )
            assert out["positive_class_probability"] == pytest.approx(direct, abs=1e-12)
            assert out["confidence"] == pytest.approx(direct if out["prediction"] else 1 - direct)
            assert out["model_version"] == manifest["model_version"]
            classes.add(out["prediction"])
        assert classes == {0, 1}
        assert "model_predictions_total" in client.get("/metrics").text
        assert client.post("/predict", json={**SAMPLE, "unexpected": 1}).status_code == 422
        assert (
            client.post("/predict", json={k: v for k, v in SAMPLE.items() if k != "ca"}).status_code
            == 422
        )


def test_corrupted_bundle_never_ready(tmp_path):
    dest = tmp_path / "bundle"
    shutil.copytree(BUNDLE, dest)
    (dest / "model" / "model.pkl").write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="checksum"):
        load(dest)
    with TestClient(create_app(dest)) as client:
        assert client.get("/ready").status_code == 503
