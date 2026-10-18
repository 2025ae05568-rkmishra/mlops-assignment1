#!/usr/bin/env bash
# Keep private Ingress, dashboard and release experiment views available on BITS.
set -Eeuo pipefail
cd "$(git rev-parse --show-toplevel)"
context=mlops-assignment
log_dir=reports/evidence/runtime/access
mkdir -p "$log_dir"
pids=()
cleanup() {
  for pid in "${pids[@]}"; do kill "$pid" 2>/dev/null || true; done
  for pid in "${pids[@]}"; do wait "$pid" 2>/dev/null || true; done
}
trap cleanup EXIT
trap 'exit 130' INT TERM
kubectl --context "$context" -n kube-system port-forward --address 127.0.0.1 \
  svc/traefik 8081:8081 >"$log_dir/traefik.log" 2>&1 &
pids+=("$!")
kubectl --context "$context" -n mlops-assignment port-forward --address 127.0.0.1 \
  svc/prometheus 9090:9090 >"$log_dir/prometheus.log" 2>&1 &
pids+=("$!")
.venv/bin/python scripts/monitoring_dashboard.py >"$log_dir/dashboard.log" 2>&1 &
pids+=("$!")
.venv/bin/python scripts/serve_release_mlflow.py >"$log_dir/mlflow.log" 2>&1 &
pids+=("$!")
ready=0
for attempt in {1..60}; do
  for pid in "${pids[@]}"; do
    kill -0 "$pid" 2>/dev/null || { printf 'Access process failed. Inspect %s/*.log\n' "$log_dir" >&2; exit 1; }
  done
  if curl -fsS --max-time 2 -H 'Host: heart-disease.test' http://127.0.0.1:8081/ready >/dev/null 2>&1 && \
     curl -fsS --max-time 2 http://127.0.0.1:8090/api/snapshot >/dev/null 2>&1 && \
     curl -fsS --max-time 2 http://127.0.0.1:5000/health >/dev/null 2>&1; then
    ready=1
    break
  fi
  sleep 2
done
[[ "$ready" -eq 1 ]] || { printf 'Access startup timed out; inspect %s/*.log\n' "$log_dir" >&2; exit 1; }
.venv/bin/python scripts/smoke_api.py --url http://127.0.0.1:8081 --host heart-disease.test
printf '\nPrivate access is ready. Keep this terminal running. Ctrl-C stops these access processes.\n'
printf 'VM desktop: dashboard http://127.0.0.1:8090 ; MLflow http://127.0.0.1:5000\n'
printf 'Workstation: ssh -N -L 8081:127.0.0.1:8081 -L 8090:127.0.0.1:8090 -L 5000:127.0.0.1:5000 USER@VM\n'
printf 'Use Host: heart-disease.test for API requests; see README.md.\n'
while true; do
  for pid in "${pids[@]}"; do
    kill -0 "$pid" 2>/dev/null || { printf 'Access process exited; inspect %s/*.log\n' "$log_dir" >&2; exit 1; }
  done
  sleep 5
done
