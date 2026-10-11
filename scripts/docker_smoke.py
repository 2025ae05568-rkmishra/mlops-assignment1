import argparse
import json
import subprocess
import time
from pathlib import Path

import httpx

from heart_disease.common.io import now, write_json
from heart_disease.models.package import verify

parser = argparse.ArgumentParser()
parser.add_argument("--image", default="heart-disease-api:local")
args = parser.parse_args()
manifest = verify("artifacts/model/current")
cid = subprocess.check_output(
    [
        "docker",
        "run",
        "--detach",
        "--read-only",
        "--tmpfs",
        "/tmp:rw,noexec,nosuid,size=128m",
        "--publish",
        "127.0.0.1::8000",
        args.image,
    ],
    text=True,
).strip()
try:
    info = json.loads(subprocess.check_output(["docker", "inspect", cid], text=True))[0]
    port = info["NetworkSettings"]["Ports"]["8000/tcp"][0]["HostPort"]
    sample = json.loads(Path("tests/fixtures/valid_request.json").read_text())
    with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=5) as client:
        for _ in range(120):
            try:
                if client.get("/ready").status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            time.sleep(1)
        else:
            raise RuntimeError("Container never became ready")
        result = client.post("/predict", json=sample)
        result.raise_for_status()
        output = result.json()
        assert output["model_version"] == manifest["model_version"]
        assert client.post("/predict", json={**sample, "cp": 0}).status_code == 422
        assert info["Config"]["User"] == "10001"
        evidence = {
            "captured_at": now(),
            "image_id": info["Image"],
            "user": info["Config"]["User"],
            "model_version": manifest["model_version"],
            "valid_response": output,
            "invalid_status": 422,
            "read_only_root": True,
        }
        write_json("reports/evidence/docker-smoke.json", evidence)
        print(json.dumps(evidence, indent=2))
finally:
    logs = subprocess.check_output(["docker", "logs", cid], stderr=subprocess.STDOUT, text=True)
    Path("reports/evidence/runtime").mkdir(parents=True, exist_ok=True)
    Path("reports/evidence/runtime/docker.log").write_text(logs)
    subprocess.run(["docker", "stop", cid], check=True, capture_output=True)
    subprocess.run(["docker", "rm", cid], check=True, capture_output=True)
