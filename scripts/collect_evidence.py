import subprocess
from pathlib import Path

from heart_disease.common.io import now, read_json, write_json

out = Path("reports/evidence/runtime")
out.mkdir(parents=True, exist_ok=True)
for name, command in {
    "resources": [
        "kubectl",
        "--context",
        "mlops-assignment",
        "-n",
        "mlops-assignment",
        "get",
        "pods,svc,ingress",
        "-o",
        "wide",
    ],
    "nodes": ["kubectl", "--context", "mlops-assignment", "get", "nodes", "-o", "wide"],
    "deployment": [
        "kubectl",
        "--context",
        "mlops-assignment",
        "-n",
        "mlops-assignment",
        "get",
        "deployment/heart-disease-api",
        "-o",
        "json",
    ],
    "pods": [
        "kubectl",
        "--context",
        "mlops-assignment",
        "-n",
        "mlops-assignment",
        "get",
        "pods",
        "-l",
        "app=heart-disease-api",
        "-o",
        "json",
    ],
    "api-logs": [
        "kubectl",
        "--context",
        "mlops-assignment",
        "-n",
        "mlops-assignment",
        "logs",
        "-l",
        "app=heart-disease-api",
        "--prefix",
        "--tail=100",
    ],
}.items():
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    (out / f"{name}.txt").write_text(result.stdout)
write_json(
    "reports/evidence/index.json",
    {
        "captured_at": now(),
        "model": read_json("artifacts/model/current/manifest.json"),
        "runtime_directory": str(out),
    },
)
print(out)
