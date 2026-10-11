import argparse
import json
from pathlib import Path

import httpx

parser = argparse.ArgumentParser()
parser.add_argument("--url", default="http://127.0.0.1:8000")
parser.add_argument("--host")
parser.add_argument("--requests", type=int, default=1)
parser.add_argument("--expected-version")
args = parser.parse_args()
headers = {"Host": args.host} if args.host else {}
sample = json.loads(Path("tests/fixtures/valid_request.json").read_text())
with httpx.Client(base_url=args.url, headers=headers, timeout=30) as client:
    client.get("/ready").raise_for_status()
    for _ in range(args.requests):
        response = client.post("/predict", json=sample)
        response.raise_for_status()
        output = response.json()
        assert 0 <= output["confidence"] <= 1
        if args.expected_version:
            assert output["model_version"] == args.expected_version
    invalid = client.post("/predict", json={**sample, "cp": 0})
    assert invalid.status_code == 422
    print(json.dumps({"valid": output, "invalid_status": invalid.status_code}, indent=2))
