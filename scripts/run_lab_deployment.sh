#!/usr/bin/env bash
set -Eeuo pipefail

repo=2025ae05568-rkmishra/mlops-assignment1
profile=mlops-assignment
branch=main
reuse_run_id=""
root="$(git rev-parse --show-toplevel)"
cd "$root"

usage() {
  cat <<'EOF'
Usage: bash scripts/run_lab_deployment.sh [--reuse-run RUN_ID]

By default, trigger the GitHub Actions release workflow for the current main
commit, wait for it to succeed, download and verify its image, deploy it to
Minikube, test the Ingress, and collect evidence.

Use --reuse-run RUN_ID to download and deploy an already successful release
run for the current main commit instead of starting another build.
EOF
}

while (($#)); do
  case "$1" in
    --reuse-run)
      (($# >= 2)) || { usage >&2; exit 2; }
      reuse_run_id="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      usage >&2
      exit 2
      ;;
  esac
done

log_dir="$root/reports/evidence/runtime"
mkdir -p "$log_dir"
log_file="$log_dir/lab-deployment-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$log_file") 2>&1

port_forward_pid=""
prometheus_pid=""
port_forward_log="$log_dir/traefik-port-forward-$(date +%Y%m%d-%H%M%S).log"

cleanup() {
  if [[ -n "$prometheus_pid" ]]; then
    kill "$prometheus_pid" 2>/dev/null || true
    wait "$prometheus_pid" 2>/dev/null || true
  fi
  if [[ -n "$port_forward_pid" ]] && kill -0 "$port_forward_pid" 2>/dev/null; then
    kill "$port_forward_pid" 2>/dev/null || true
    wait "$port_forward_pid" 2>/dev/null || true
  fi
}

collect_diagnostics() {
  set +e
  if ! command -v kubectl >/dev/null || ! kubectl --context "$profile" get nodes >/dev/null 2>&1; then
    printf '\nCluster diagnostics unavailable for context %s.\n' "$profile"
    return
  fi
  printf '\n== Automatic failure diagnostics ==\n'
  kubectl --context "$profile" get nodes -o wide
  kubectl --context "$profile" -n mlops-assignment get pods,svc,ingress -o wide
  kubectl --context "$profile" -n kube-system get pods,svc -o wide
  kubectl --context "$profile" -n mlops-assignment get events --sort-by=.lastTimestamp
  kubectl --context "$profile" -n mlops-assignment logs \
    -l app=heart-disease-api --all-containers --prefix --tail=100
  kubectl --context "$profile" -n kube-system logs \
    deployment/traefik --all-containers --prefix --tail=100
}

on_error() {
  local status=$?
  trap - ERR
  printf '\nERROR: command failed at line %s (exit %s): %s\n' \
    "$1" "$status" "$2"
  collect_diagnostics
  printf '\nFull run log: %s\n' "$log_file"
  printf 'Traefik port-forward log (if started): %s\n' "$port_forward_log"
  exit "$status"
}

trap cleanup EXIT
trap 'on_error "$LINENO" "$BASH_COMMAND"' ERR

step() {
  local label="$1"
  shift
  local started status elapsed
  started="$(date +%s)"
  printf '\n==> %s\n' "$label"
  printf 'Command:'
  printf ' %q' "$@"
  printf '\n'
  if "$@"; then
    status=0
  else
    status=$?
  fi
  elapsed=$(( $(date +%s) - started ))
  printf '<== %s: %s (exit %s, %ss)\n' \
    "$label" "$([[ $status -eq 0 ]] && printf OK || printf FAILED)" "$status" "$elapsed"
  return "$status"
}

printf 'Lab deployment started: %s\n' "$(date --iso-8601=seconds)"
printf 'Repository: %s\nCommit: %s\n' "$repo" "$(git rev-parse HEAD)"
printf 'Log: %s\n' "$log_file"

for tool in gh git docker minikube kubectl make python3.11 curl sha256sum; do
  command -v "$tool" >/dev/null || {
    printf 'ERROR: missing prerequisite: %s. Run scripts/bootstrap_rocky9.sh first.\n' "$tool" >&2
    exit 1
  }
done

if [[ "$(uname -m)" != x86_64 ]]; then
  printf 'ERROR: the GitHub release is AMD64; this runner requires an x86_64 VM.\n' >&2
  exit 1
fi
[[ "$(git branch --show-current)" == "$branch" ]] || {
  printf 'ERROR: check out %s before running this script.\n' "$branch" >&2
  exit 1
}
[[ -z "$(git status --porcelain)" ]] || {
  printf 'ERROR: working tree is not clean. Commit or stash changes before deploying.\n' >&2
  git status --short
  exit 1
}
case "$(git remote get-url origin)" in
  *"$repo"*) ;;
  *)
    printf 'ERROR: origin must point to https://github.com/%s.git.\n' "$repo" >&2
    exit 1
    ;;
esac

step "Verify GitHub CLI authentication" gh auth status --hostname github.com
remote_sha="$(gh api "repos/${repo}/commits/${branch}" --jq .sha)"
commit_sha="$(git rev-parse HEAD)"
[[ "$commit_sha" == "$remote_sha" ]] || {
  printf 'ERROR: local HEAD %s is not origin/%s (%s). Pull the latest pushed commit first.\n' \
    "$commit_sha" "$branch" "$remote_sha" >&2
  exit 1
}
printf 'Verified clean %s checkout matches GitHub commit %s.\n' "$branch" "$commit_sha"

step "Check Docker daemon" docker info --format 'architecture={{.Architecture}} CPUs={{.NCPU}} memory={{.MemTotal}} bytes'
step "Start or check Minikube profile" \
  minikube -p "$profile" start --driver=docker --cpus=4 --memory=6144
step "Check Minikube profile status" minikube -p "$profile" status
step "Check Kubernetes nodes" kubectl --context "$profile" get nodes -o wide
node_arch="$(kubectl --context "$profile" get nodes -o jsonpath='{.items[0].status.nodeInfo.architecture}')"
[[ "$node_arch" == amd64 ]] || {
  printf 'ERROR: Minikube node architecture is %s; the release image is amd64.\n' "$node_arch" >&2
  exit 1
}

if [[ -n "$reuse_run_id" ]]; then
  run_id="$reuse_run_id"
  [[ "$run_id" =~ ^[0-9]+$ ]] || {
    printf 'ERROR: GitHub Actions run ID must be numeric.\n' >&2
    exit 2
  }
  printf '\nReusing successful release workflow run %s.\n' "$run_id"
else
  dispatch_started="$(date +%s)"
  step "Trigger GitHub release build" \
    gh workflow run release.yml --repo "$repo" --ref "$branch"
  printf 'Waiting for the release run to appear in GitHub Actions...\n'
  run_id=""
  for attempt in {1..24}; do
    run_id="$(
      gh run list --repo "$repo" --workflow release.yml --branch "$branch" \
        --event workflow_dispatch --limit 20 \
        --json databaseId,headSha,createdAt |
        python3 -c '
import datetime, json, sys
started = int(sys.argv[1])
runs = json.load(sys.stdin)
for run in runs:
    created = datetime.datetime.fromisoformat(run["createdAt"].replace("Z", "+00:00"))
    if run["headSha"] == sys.argv[2] and int(created.timestamp()) >= started:
        print(run["databaseId"])
        break
' "$dispatch_started" "$commit_sha"
    )"
    [[ -n "$run_id" ]] && break
    sleep 5
  done
  [[ -n "$run_id" ]] || {
    printf 'ERROR: could not find the newly dispatched release run for commit %s.\n' "$commit_sha" >&2
    exit 1
  }
  printf 'Release workflow run ID: %s\n' "$run_id"
  step "Wait for GitHub release build and smoke test" \
    gh run watch "$run_id" --repo "$repo" --exit-status
fi

run_json="$(gh run view "$run_id" --repo "$repo" \
  --json headSha,status,conclusion,attempt)"
read -r run_sha run_status run_conclusion run_attempt \
  < <(python3 -c '
import json, sys
run = json.load(sys.stdin)
print(run["headSha"], run["status"], run["conclusion"],
      run["attempt"])
' <<< "$run_json")
workflow_name="$(gh run view "$run_id" --repo "$repo" --json workflowName --jq .workflowName)"
[[ "$run_sha" == "$commit_sha" ]] || {
  printf 'ERROR: release run %s is for %s, not this checkout %s.\n' \
    "$run_id" "$run_sha" "$commit_sha" >&2
  exit 1
}
[[ "$run_status" == completed && "$run_conclusion" == success ]] || {
  printf 'ERROR: release run %s status=%s conclusion=%s.\n' \
    "$run_id" "$run_status" "$run_conclusion" >&2
  exit 1
}
[[ "$workflow_name" == "Package verified local-deployment release" ]] || {
  printf 'ERROR: run %s is not the expected release workflow (%s).\n' \
    "$run_id" "$workflow_name" >&2
  exit 1
}

release_dir="$root/artifacts/lab-release-${run_id}-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$release_dir"
artifact_name="release-${commit_sha}-${run_attempt}"
step "Download GitHub release artifact ${artifact_name}" \
  gh run download "$run_id" --repo "$repo" --name "$artifact_name" --dir "$release_dir"

archive_path="$(find "$release_dir" -type f -path '*/artifacts/heart-disease-api.tar.gz' -print -quit)"
[[ -n "$archive_path" ]] || {
  printf 'ERROR: release artifact does not contain artifacts/heart-disease-api.tar.gz.\n' >&2
  find "$release_dir" -maxdepth 4 -type f -print
  exit 1
}
artifact_root="${archive_path%/artifacts/heart-disease-api.tar.gz}"
checksum_path="$artifact_root/artifacts/heart-disease-api.tar.gz.sha256"
[[ -f "$checksum_path" ]] || {
  printf 'ERROR: release image checksum is missing: %s\n' "$checksum_path" >&2
  exit 1
}
step "Verify release archive checksum" \
  bash -c 'cd "$1" && sha256sum -c artifacts/heart-disease-api.tar.gz.sha256' \
  _ "$artifact_root"
step "Load release image into Docker" docker load -i "$archive_path"
image="heart-disease-api:${commit_sha}"
release_image="heart-disease-api:${commit_sha}-${run_id}-${run_attempt}"
step "Give the verified release a unique deployment tag" docker tag "$image" "$release_image"
image="$release_image"
step "Verify loaded image" docker image inspect "$image" --format '{{.Id}} {{.Os}}/{{.Architecture}}'

bundle_manifest="$(find "$artifact_root" -type f -path '*/artifacts/model/current/manifest.json' -print -quit)"
[[ -n "$bundle_manifest" ]] || {
  printf 'ERROR: release artifact is missing artifacts/model/current/manifest.json.\n' >&2
  exit 1
}
bundle_dir="${bundle_manifest%/manifest.json}"
mkdir -p "$root/artifacts/model/current"
cp -a "$bundle_dir/." "$root/artifacts/model/current/"

step "Install project dependencies" make setup
step "Deploy verified image to Minikube" make deploy-minikube "IMAGE=$image"

step "Verify application rollout" \
  kubectl --context "$profile" -n mlops-assignment \
  rollout status deployment/heart-disease-api --timeout=300s
step "Verify app resources" \
  kubectl --context "$profile" -n mlops-assignment get pods,svc,ingress -o wide
step "Verify Traefik service" \
  kubectl --context "$profile" -n kube-system get svc traefik -o wide

printf '\n== Start temporary local Ingress port-forward ==\n'
kubectl --context "$profile" -n kube-system \
  port-forward --address 127.0.0.1 svc/traefik 8081:8081 \
  >"$port_forward_log" 2>&1 &
port_forward_pid=$!
ready=0
for attempt in {1..30}; do
  if ! kill -0 "$port_forward_pid" 2>/dev/null; then
    printf 'ERROR: port-forward exited. See %s\n' "$port_forward_log" >&2
    cat "$port_forward_log"
    exit 1
  fi
  if curl --silent --fail --max-time 2 \
    -H 'Host: heart-disease.test' http://127.0.0.1:8081/ready >/dev/null; then
    ready=1
    break
  fi
  sleep 2
done
[[ "$ready" -eq 1 ]] || {
  printf 'ERROR: app did not become reachable through Ingress on 127.0.0.1:8081.\n' >&2
  cat "$port_forward_log"
  exit 1
}
printf 'Ingress /ready succeeded through Traefik.\n'

expected_version="$("$root/.venv/bin/python" -c 'import json; print(json.load(open("artifacts/model/current/manifest.json"))["model_version"])')"
step "Smoke-test valid and invalid API requests through Ingress" \
  "$root/.venv/bin/python" scripts/smoke_api.py \
  --url http://127.0.0.1:8081 --host heart-disease.test --requests 20 \
  --expected-version "$expected_version"
metrics_status="$(
  curl --silent --output /dev/null --write-out '%{http_code}' \
    -H 'Host: heart-disease.test' http://127.0.0.1:8081/metrics
)"
[[ "$metrics_status" == 404 ]] || {
  printf 'ERROR: expected /metrics to be blocked by Ingress (404), got %s.\n' "$metrics_status" >&2
  exit 1
}
printf 'Ingress /metrics check: correctly blocked (HTTP %s).\n' "$metrics_status"
printf '\n== Capture selected-release submission evidence ==\n'
kubectl --context "$profile" -n mlops-assignment \
  port-forward --address 127.0.0.1 svc/prometheus 9090:9090 \
  >"$log_dir/prometheus-forward.log" 2>&1 &
prometheus_pid=$!
prometheus_ready=0
for attempt in {1..30}; do
  kill -0 "$prometheus_pid" 2>/dev/null || { cat "$log_dir/prometheus-forward.log"; exit 1; }
  if curl --silent --fail --max-time 2 http://127.0.0.1:9090/-/ready >/dev/null; then
    prometheus_ready=1
    break
  fi
  sleep 2
done
[[ "$prometheus_ready" -eq 1 ]] || { printf 'ERROR: Prometheus forwarding failed.\n' >&2; exit 1; }
evidence_dir="$log_dir/submission-${run_id}-${run_attempt}-$(date +%Y%m%d-%H%M%S)"
step "Capture and validate BITS evidence, model identity and monitoring" \
  "$root/.venv/bin/python" scripts/capture_submission.py \
  --release-root "$artifact_root" --output "$evidence_dir" \
  --repository "$repo" --run-id "$run_id" --attempt "$run_attempt" --image "$image"
cleanup
port_forward_pid=""
prometheus_pid=""

printf '\nDeployment completed successfully.\n'
printf 'Repository commit: %s\nRelease workflow run: %s\n' "$commit_sha" "$run_id"
printf 'Workflow: https://github.com/%s/actions/runs/%s\n' "$repo" "$run_id"
printf 'Image: %s\nLog: %s\n' "$image" "$log_file"
printf 'Downloaded release artifact: %s\n' "$release_dir"
printf 'Submission evidence: %s\n' "$evidence_dir"
printf 'For reviewer access and screenshots, run: bash scripts/open_vm_access.sh\n'
printf 'Then follow README.md to record the video and build the final report.\n'
printf 'To repeat on another VM, use a clean main checkout at %s while remote main still matches, then run:\n' "$commit_sha"
printf '  bash scripts/run_lab_deployment.sh --reuse-run %s\n' "$run_id"
printf 'If main has advanced, deploy a new release with bash scripts/run_lab_deployment.sh.\n'
