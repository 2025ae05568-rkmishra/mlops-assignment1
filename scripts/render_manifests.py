"""Render the local overlay with the exact release image before applying."""

import argparse
import subprocess
import sys

import yaml

parser = argparse.ArgumentParser()
parser.add_argument("--image", required=True)
args = parser.parse_args()
rendered = subprocess.check_output(
    ["kubectl", "kustomize", "deploy/k8s/overlays/minikube"], text=True
)
resources = list(yaml.safe_load_all(rendered))
for resource in resources:
    if resource["kind"] == "Deployment" and resource["metadata"]["name"] == "heart-disease-api":
        resource["spec"]["template"]["spec"]["containers"][0]["image"] = args.image
yaml.safe_dump_all(resources, sys.stdout, sort_keys=False)
