#!/usr/bin/env bash
set -euo pipefail
image="${1:-heart-disease-api:$(.venv/bin/python scripts/image_tag.py)}"
context=mlops-assignment
minikube status -p "$context"
if ! kubectl --context "$context" -n kube-system get deployment traefik >/dev/null 2>&1; then
  minikube -p "$context" addons enable traefik
fi
kubectl --context "$context" get ingressclass traefik
.venv/bin/python scripts/configure_traefik_ports.py
minikube -p "$context" image load "$image"
.venv/bin/python scripts/render_manifests.py --image "$image" | kubectl --context "$context" apply -f -
kubectl --context "$context" -n mlops-assignment rollout status deployment/heart-disease-api --timeout=300s
kubectl --context "$context" -n mlops-assignment apply -f deploy/monitoring/prometheus.yaml
kubectl --context "$context" -n mlops-assignment rollout status deployment/prometheus --timeout=300s
kubectl --context "$context" -n mlops-assignment get pods,svc,ingress
printf 'Run in separate terminals: minikube -p mlops-assignment tunnel; kubectl --context mlops-assignment -n mlops-assignment port-forward svc/prometheus 9090:9090\n'
