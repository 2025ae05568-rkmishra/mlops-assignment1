import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from heart_disease.api.main import create_app
from heart_disease.api.schemas import PredictionRequest

SAMPLE = json.loads(Path("tests/fixtures/valid_request.json").read_text())


@pytest.mark.parametrize(
    "field,value",
    [
        ("cp", 0),
        ("ca", 4),
        ("thal", 0),
        ("age", True),
        ("sex", True),
        ("age", "52"),
        ("chol", "210"),
        ("chol", float("nan")),
        ("slope", 0),
    ],
)
def test_schema_rejects_invalid_inputs(field, value):
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        PredictionRequest(**{**SAMPLE, field: value})


def test_missing_bundle_unready_and_errors_sanitized(tmp_path):
    with TestClient(create_app(tmp_path / "missing")) as client:
        assert client.get("/health").status_code == 200
        unready = client.get("/ready")
        assert unready.status_code == 503
        assert unready.json()["error"] == "model_unavailable"
        assert unready.json()["request_id"]
        schema = client.get("/openapi.json").json()
        assert schema["paths"]["/predict"]["post"]["responses"]["422"]["content"][
            "application/json"
        ]["schema"]["$ref"].endswith("/ErrorResponse")
        assert client.post("/predict", json=SAMPLE).status_code == 503
        response = client.post("/predict", json={**SAMPLE, "chol": "sensitive-invalid-value"})
        assert response.status_code == 422
        assert "sensitive-invalid-value" not in response.text
        assert client.post("/predict", content=b"x" * 17000).status_code == 413
