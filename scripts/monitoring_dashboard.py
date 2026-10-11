import argparse
import json
import time
from pathlib import Path

import httpx
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

parser = argparse.ArgumentParser()
parser.add_argument("--prometheus", default="http://127.0.0.1:9090")
parser.add_argument("--port", type=int, default=8090)
args = parser.parse_args()
config = json.loads(Path("deploy/monitoring/dashboard.json").read_text())
app = FastAPI(title=config["title"])


@app.get("/api/snapshot")
def snapshot():
    now = time.time()
    panels = []
    with httpx.Client(base_url=args.prometheus, timeout=10) as client:
        targets = client.get("/api/v1/targets")
        targets.raise_for_status()
        for panel in config["panels"]:
            response = client.get(
                "/api/v1/query_range",
                params={
                    "query": panel["query"],
                    "start": now - config["window_seconds"],
                    "end": now,
                    "step": config["step_seconds"],
                },
            )
            response.raise_for_status()
            values = response.json()
            if values["status"] != "success":
                raise RuntimeError("Prometheus query failed")
            panels.append({**panel, "series": values["data"]["result"]})
    return {
        "captured_at": now,
        "panels": panels,
        "targets": [
            {"health": t["health"], "pod": t.get("labels", {}).get("pod", "unknown")}
            for t in targets.json()["data"]["activeTargets"]
        ],
    }


@app.get("/", response_class=HTMLResponse)
def index():
    return Path("deploy/monitoring/dashboard.html").read_text()


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=args.port)
