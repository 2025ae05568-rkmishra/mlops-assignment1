"""Exercise controller installation/reuse without a real cluster or host changes."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

SCRIPT = Path("scripts/deploy_minikube.sh").resolve()


@pytest.mark.parametrize("existing", [False, True])
def test_deployment_installs_or_reuses_controller_without_addon(tmp_path, existing):
    fakebin = tmp_path / "bin"
    fakebin.mkdir()
    log = tmp_path / "commands.log"
    kubectl = fakebin / "kubectl"
    kubectl.write_text("""#!/bin/sh
printf 'kubectl %s\\n' "$*" >> "$TEST_LOG"
case "$*" in
  *'get deployment traefik'*) test "$TEST_EXISTING" = yes; exit $? ;;
esac
exit 0
""")
    minikube = fakebin / "minikube"
    minikube.write_text("""#!/bin/sh
printf 'minikube %s\\n' "$*" >> "$TEST_LOG"
case "$*" in *addons*) exit 99 ;; esac
exit 0
""")
    python = tmp_path / ".venv/bin/python"
    python.parent.mkdir(parents=True)
    python.write_text("""#!/bin/sh
case "$*" in *render_manifests*) printf '{}\\n' ;; esac
exit 0
""")
    for program in (kubectl, minikube, python):
        program.chmod(0o755)
    env = {
        **os.environ,
        "PATH": str(fakebin) + os.pathsep + os.environ["PATH"],
        "TEST_LOG": str(log),
        "TEST_EXISTING": "yes" if existing else "no",
    }
    subprocess.run(
        ["bash", str(SCRIPT), "api:verified-release"],
        cwd=tmp_path,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    commands = log.read_text()
    assert "addons" not in commands
    assert ("apply -f deploy/traefik/controller.yaml" in commands) == (not existing)
    assert "rollout status deployment/traefik --timeout=300s" in commands
    assert "image load api:verified-release" in commands


def test_direct_controller_matches_existing_ingress_and_forwarding():
    resources = list(yaml.safe_load_all(Path("deploy/traefik/controller.yaml").read_text()))
    by_kind = {r["kind"]: r for r in resources}
    deployment = by_kind["Deployment"]
    assert deployment["metadata"] == {"name": "traefik", "namespace": "kube-system"}
    spec = deployment["spec"]["template"]["spec"]
    args = spec["containers"][0]["args"]
    assert "--providers.kubernetesingress=true" in args
    assert "--providers.kubernetesingress.namespaces=mlops-assignment" in args
    assert "--providers.kubernetesingress.ingressclass=traefik" in args
    assert by_kind["IngressClass"]["metadata"]["name"] == "traefik"
    service = by_kind["Service"]
    assert service["spec"]["selector"] == deployment["spec"]["selector"]["matchLabels"]
    port = service["spec"]["ports"][0]
    assert port == {"name": "web", "port": 8081, "targetPort": "web"}
    assert any(
        p["name"] == "web" and p["containerPort"] == 8000 for p in spec["containers"][0]["ports"]
    )
    assert not any(r["kind"] == "CustomResourceDefinition" for r in resources)


@pytest.mark.parametrize("rollout_fails", [False, True])
def test_prometheus_bootstrap_uses_valid_queries_and_stops_on_failed_rollout(
    tmp_path, rollout_fails
):
    source = Path("scripts/bootstrap_rocky9.sh").read_text()
    start = source.index("install_prometheus() {\n")
    end = source.index("\n}\n", start) + 3
    function = source[start:end]
    fakebin = tmp_path / "bin"
    fakebin.mkdir()
    log = tmp_path / "commands.jsonl"
    kubectl = fakebin / "kubectl"
    kubectl.write_text(
        f"#!{sys.executable}\n"
        "import json, os, sys\n"
        "args = sys.argv[1:]\n"
        "with open(os.environ['TEST_LOG'], 'a') as output:\n"
        "    output.write(json.dumps(args) + '\\n')\n"
        "if any('/' in arg and ',' in arg for arg in args):\n"
        "    sys.exit(2)  # kubectl cannot mix TYPE/NAME with resource types.\n"
        "if 'rollout' in args and os.environ['TEST_ROLLOUT_FAIL'] == 'yes':\n"
        "    sys.exit(1)\n"
    )
    kubectl.chmod(0o755)
    result = subprocess.run(
        ["bash", "-c", "set -euo pipefail\n" + function + "\ninstall_prometheus\n"],
        env={
            **os.environ,
            "PATH": str(fakebin) + os.pathsep + os.environ["PATH"],
            "profile": "mlops-assignment",
            "repo_root": str(Path.cwd()),
            "TEST_LOG": str(log),
            "TEST_ROLLOUT_FAIL": "yes" if rollout_fails else "no",
        },
        capture_output=True,
        text=True,
    )
    commands = [json.loads(line) for line in log.read_text().splitlines()]
    if rollout_fails:
        assert result.returncode != 0
        assert "Prometheus is ready" not in result.stdout
        assert "rollout" in commands[-1]
    else:
        assert result.returncode == 0, result.stderr
        queries = [args[args.index("get") + 1] for args in commands if "get" in args]
        assert queries == ["nodes", "deployment/prometheus", "pods,svc"]
        assert "Prometheus is ready" in result.stdout
