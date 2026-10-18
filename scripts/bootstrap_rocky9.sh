#!/usr/bin/env bash
set -Eeuo pipefail

profile=mlops-assignment
log_dir="${HOME}/mlops-bootstrap-logs"
mkdir -p "$log_dir"
log_file="${log_dir}/bootstrap-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$log_file") 2>&1

on_error() {
  local status=$?
  printf 'ERROR: command failed at line %s (exit %s): %s\n' \
    "$1" "$status" "$2"
  printf 'See the full log: %s\n' "$log_file"
  exit "$status"
}
trap 'on_error "$LINENO" "$BASH_COMMAND"' ERR

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

printf 'Rocky Linux 9 MLOps preflight started: %s\n' "$(date --iso-8601=seconds)"
printf 'Log file: %s\n' "$log_file"

if [[ ! -r /etc/os-release ]]; then
  printf 'ERROR: cannot identify the operating system (/etc/os-release is missing).\n' >&2
  exit 1
fi
# shellcheck disable=SC1091
source /etc/os-release
if [[ "${ID:-}" != rocky || "${VERSION_ID%%.*}" != 9 ]]; then
  printf 'ERROR: this script supports Rocky Linux 9 only; detected %s %s.\n' \
    "${ID:-unknown}" "${VERSION_ID:-unknown}" >&2
  exit 1
fi

if [[ "$(id -u)" -eq 0 ]]; then
  printf 'ERROR: run this script as your regular user, not with sudo; it uses sudo only for system installs.\n' >&2
  exit 1
fi
command -v sudo >/dev/null || {
  printf 'ERROR: sudo is required to install system packages and kubectl.\n' >&2
  exit 1
}
sudo -v

for tool in docker minikube curl sha256sum python3; do
  command -v "$tool" >/dev/null || {
    printf 'ERROR: required command is missing: %s\n' "$tool" >&2
    exit 1
  }
done

printf '\n== Install Python 3.11 and setup tools ==\n'
sudo dnf install -y python3.11 python3.11-pip git make curl ca-certificates
python3.11 --version
python3.11 -m pip --version
python3.11 -m venv "$tmp_dir/python-check"
"$tmp_dir/python-check/bin/python" --version

printf '\n== Check Docker access ==\n'
docker info --format 'Docker architecture={{.Architecture}} CPUs={{.NCPU}} memory={{.MemTotal}} bytes'

printf '\n== Start or check Minikube profile %s ==\n' "$profile"
minikube -p "$profile" start --driver=docker --cpus=4 --memory=6144
minikube -p "$profile" status

printf '\n== Install kubectl matching the running cluster ==\n'
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
  printf 'WARNING: the GitHub release image is AMD64; do not load it on this host without confirming image compatibility.\n'
fi

download_url="https://dl.k8s.io/release/${server_version}/bin/linux/${kubectl_arch}"
curl --fail --location --retry 3 --output "$tmp_dir/kubectl" "$download_url/kubectl"
curl --fail --location --retry 3 --output "$tmp_dir/kubectl.sha256" "$download_url/kubectl.sha256"
(
  cd "$tmp_dir"
  printf '%s  kubectl\n' "$(tr -d '[:space:]' < kubectl.sha256)" | sha256sum --check
)
sudo install -o root -g root -m 0755 "$tmp_dir/kubectl" /usr/local/bin/kubectl

printf '\n== Verify Python, kubectl, and cluster readiness ==\n'
python3.11 --version
kubectl version --client --output=yaml
kubectl --context "$profile" get nodes -o wide
printf '\nPreflight complete. The application image has not been built or deployed.\n'
printf 'Keep this log if anything needs troubleshooting: %s\n' "$log_file"
