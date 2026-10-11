"""Generate bounded synthetic traffic for the local monitoring demonstration."""

import argparse
import json
import time
from pathlib import Path

import httpx

from heart_disease.common.io import now, write_json

parser = argparse.ArgumentParser()
parser.add_argument("--url", default="http://127.0.0.1:8081")
parser.add_argument("--duration", type=int, default=60)
args = parser.parse_args()
sample = json.loads(Path("tests/fixtures/valid_request.json").read_text())
counts = {"200": 0, "422": 0}
with httpx.Client(base_url=args.url, headers={"Host": "heart-disease.test"}, timeout=10) as client:
    end = time.monotonic() + args.duration
    while time.monotonic() < end:
        for payload, expected in [(sample, 200), ({**sample, "cp": 0}, 422)]:
            result = client.post("/predict", json=payload)
            assert result.status_code == expected
            counts[str(expected)] += 1
        time.sleep(0.5)
write_json(
    "reports/evidence/synthetic-traffic.json",
    {"captured_at": now(), "counts": counts, "duration_seconds": args.duration},
)
print(counts)
