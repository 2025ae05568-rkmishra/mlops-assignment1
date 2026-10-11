"""Use unprivileged local controller ports while preserving the chart's target ports."""

import json
import subprocess

command = ["kubectl", "--context", "mlops-assignment", "-n", "kube-system"]
service = json.loads(
    subprocess.check_output([*command, "get", "svc", "traefik", "-o", "json"], text=True)
)
ports = service["spec"]["ports"]
for port in ports:
    if port["name"] == "web":
        port["port"] = 8081
    elif port["name"] == "websecure":
        port["port"] = 8443
assert any(p["name"] == "web" and p["port"] == 8081 for p in ports)
subprocess.run(
    [
        *command,
        "patch",
        "svc",
        "traefik",
        "--type=merge",
        "-p",
        json.dumps({"spec": {"ports": ports}}),
    ],
    check=True,
)
