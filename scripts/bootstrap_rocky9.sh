#!/usr/bin/env bash
set -Eeuo pipefail

profile=mlops-assignment
skip_installed=0
prometheus_only=0
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'EOF'
Usage: bash scripts/bootstrap_rocky9.sh [OPTIONS]

Default: install/check host prerequisites, start/check the project Minikube
profile, install a matching kubectl, and deploy/verify Prometheus in-cluster.

Options:
  --skip-installed   Do not reinstall packages and tools already present.
  --prometheus-only  Skip all host installs and Minikube startup. Apply only
                     the repository's Prometheus resources to an existing
                     mlops-assignment cluster.
  -h, --help         Show this help.
EOF
}

while (($#)); do
  case "$1" in
    --skip-installed) skip_installed=1; shift ;;
    --prometheus-only) prometheus_only=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
done

log_dir="${HOME}/mlops-bootstrap-logs"
mkdir -p "$log_dir"
log_file="${log_dir}/bootstrap-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$log_file") 2>&1

tmp_dir=""

on_exit() {
  local status=$?
  if [[ -n "$tmp_dir" && -d "$tmp_dir" ]]; then
    rm -rf "$tmp_dir"
  fi
  return "$status"
}

on_error() {
  local status=$?
  trap - ERR
  printf 'ERROR: command failed at line %s (exit %s): %s\n' \
    "$1" "$status" "$2"
  if command -v kubectl >/dev/null && kubectl --context "$profile" get nodes >/dev/null 2>&1; then
    set +e
    printf '\n== Kubernetes troubleshooting snapshot ==\n'
    kubectl --context "$profile" get nodes -o wide
    kubectl --context "$profile" -n mlops-assignment get pods,svc -o wide
    kubectl --context "$profile" -n mlops-assignment get events --sort-by=.lastTimestamp
    kubectl --context "$profile" -n mlops-assignment logs \
      deployment/prometheus --all-containers --tail=100
    set -e
  fi
  printf 'See the full log: %s\n' "$log_file"
  exit "$status"
}
trap on_exit EXIT
trap 'on_error "$LINENO" "$BASH_COMMAND"' ERR

printf 'Rocky Linux 9 MLOps setup started: %s\n' "$(date --iso-8601=seconds)"
printf 'Log file: %s\n' "$log_file"
if ((skip_installed)); then
  printf 'Installed software will be detected and left unchanged where compatible.\n'
fi

if [[ ! -r /etc/os-release ]]; then
  printf 'ERROR: cannot identify the operating system (/etc/os-release is missing).' >&2
  exit 1
fi
# shellcheck disable=SC1091
source /etc/os-release
if [[ "${ID:-}" != rocky || "${VERSION_ID:-}" != 9.* ]]; then
  printf 'ERROR: this script supports Rocky Linux 9 only; detected %s %s.\n' \
    "${ID:-unknown}" "${VERSION_ID:-unknown}" >&2
  exit 1
fi

if [[ "$(id -u)" -eq 0 ]]; then
  printf 'ERROR: run this script as your regular user, not with sudo; it uses sudo only for system installs.\n' >&2
  exit 1
fi

install_prometheus() {
  local context="$profile"
  printf '\n== Deploy Prometheus from this repository ==\n'
  command -v kubectl >/dev/null || {
    printf 'ERROR: kubectl is required for Prometheus deployment.\n' >&2
    exit 1
  }
  kubectl --context "$context" get nodes
  kubectl --context "$context" apply -f "$repo_root/deploy/k8s/base/namespace.yaml"
  kubectl --context "$context" -n mlops-assignment \
    apply -f "$repo_root/deploy/monitoring/prometheus.yaml"
  kubectl --context "$context" -n mlops-assignment \
    rollout status deployment/prometheus --timeout=300s
  kubectl --context "$context" -n mlops-assignment \
    get deployment/prometheus -o wide
  kubectl --context "$context" -n mlops-assignment get pods,svc -o wide
  printf 'Prometheus is ready in namespace mlops-assignment.\n'
}

if ((prometheus_only)); then
  printf 'Prometheus-only mode: no host packages will be installed and Minikube will not be started.\n'
  install_prometheus
  printf 'Prometheus-only setup complete. Log: %s\n' "$log_file"
  exit 0
fi

command -v sudo >/dev/null || {
  printf 'ERROR: sudo is required to install system packages and kubectl.\n' >&2
  exit 1
}
sudo -v

install_rpms() {
  local -a packages=("$@")
  local -a missing=()
  local package
  for package in "${packages[@]}"; do
    if ((skip_installed)) && rpm -q "$package" >/dev/null 2>&1; then
      printf 'Already installed; skipping RPM: %s\n' "$package"
    else
      missing+=("$package")
    fi
  done
  if ((${#missing[@]})); then
    printf 'Installing RPMs:'
    printf ' %s' "${missing[@]}"
    printf '\n'
    sudo dnf install -y "${missing[@]}"
  fi
}

printf '\n== Install/check host prerequisites ==\n'
install_rpms python3.11 python3.11-pip git make curl ca-certificates

if command -v gh >/dev/null; then
  printf 'GitHub CLI already present: '
  gh --version | head -n 1
elif ((skip_installed)); then
  printf 'GitHub CLI is missing; installing it because it is required for the release workflow.\n'
  install_rpms 'dnf-command(config-manager)'
  if [[ ! -f /etc/yum.repos.d/gh-cli.repo ]]; then
    sudo dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo
  fi
  install_rpms gh
else
  printf 'Installing GitHub CLI repository and package.\n'
  install_rpms 'dnf-command(config-manager)'
  if [[ ! -f /etc/yum.repos.d/gh-cli.repo ]]; then
    sudo dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo
  fi
  install_rpms gh
fi

for tool in docker minikube curl sha256sum python3; do
  command -v "$tool" >/dev/null || {
    printf 'ERROR: required command is missing: %s\n' "$tool" >&2
    exit 1
  }
done

printf '\n== Verify Python 3.11 virtual environment support ==\n'
python3.11 --version
python3.11 -m pip --version
tmp_dir="$(mktemp -d)"
python3.11 -m venv "$tmp_dir/python-check"
"$tmp_dir/python-check/bin/python" --version

printf '\n== Check Docker access ==\n'
docker info --format 'Docker architecture={{.Architecture}} CPUs={{.NCPU}} memory={{.MemTotal}} bytes'

printf '\n== Start or check Minikube profile %s ==\n' "$profile"
minikube -p "$profile" start --driver=docker --cpus=4 --memory=6144
minikube -p "$profile" status

printf '\n== Install or verify kubectl matching the running cluster ==\n'
server_version="$(
  minikube -p "$profile" kubectl -- version -o json |
    python3 -c 'import json, sys; print(json.load(sys.stdin)["serverVersion"]["gitVersion"])'
)"
if [[ ! "$server_version" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  printf 'ERROR: could not parse Kubernetes server version: %s\n' "$server_version" >&2
  exit 1
fi

case "$(uname -m)" in
  x86_64) kubectl_arch=amd64 ;;
  aarch64) kubectl_arch=arm64 ;;
  *)
    printf 'ERROR: unsupported host architecture: %s\n' "$(uname -m)" >&2
    exit 1
    ;;
esac
printf 'Kubernetes server: %s; kubectl architecture: %s\n' "$server_version" "$kubectl_arch"
if [[ "$kubectl_arch" != amd64 ]]; then
  printf 'WARNING: the GitHub release image is AMD64; image compatibility must be confirmed before deployment.\n'
fi

client_version=""
if command -v kubectl >/dev/null; then
  client_version="$(kubectl version --client -o json |
    python3 -c 'import json, sys; print(json.load(sys.stdin)["clientVersion"]["gitVersion"])')"
fi
if [[ "$client_version" == "$server_version" ]]; then
  printf 'kubectl %s already installed; skipping download.\n' "$client_version"
else
  if [[ -n "$client_version" ]]; then
    printf 'Replacing kubectl %s with cluster-matched %s.\n' "$client_version" "$server_version"
  fi
  download_url="https://dl.k8s.io/release/${server_version}/bin/linux/${kubectl_arch}"
  curl --fail --location --retry 3 --output "$tmp_dir/kubectl" "$download_url/kubectl"
  curl --fail --location --retry 3 --output "$tmp_dir/kubectl.sha256" "$download_url/kubectl.sha256"
  (
    cd "$tmp_dir"
    printf '%s  kubectl\n' "$(tr -d '[:space:]' < kubectl.sha256)" | sha256sum --check
  )
  sudo install -o root -g root -m 0755 "$tmp_dir/kubectl" /usr/local/bin/kubectl
fi

printf '\n== Verify Python, kubectl, and cluster readiness ==\n'
python3.11 --version
kubectl version --client --output=yaml
kubectl --context "$profile" get nodes -o wide

printf '\n== Install and verify in-cluster Prometheus ==\n'
install_prometheus

printf '\n== Install project, dashboard, and report dependencies ==\n'
make -C "$repo_root" setup

printf '\nSetup complete. The application image has not been built or deployed.\n'
printf 'The assignment video must be recorded manually using the VM desktop recorder or a workstation screen recorder.\n'
printf 'Keep this log for troubleshooting: %s\n' "$log_file"
