# Local Kubernetes access

Requirements: Docker running, Minikube, Python 3.11, kubectl, GitHub CLI (`gh`), and an AMD64 VM for the GitHub release image. On Rocky Linux 9, clone the repository and run `bash scripts/bootstrap_rocky9.sh` as your regular user before deploying. It installs Python 3.11 and supporting tools, GitHub CLI, starts/checks the dedicated Minikube profile, installs the kubectl version matching the running cluster, and writes a timestamped diagnostic log under `~/mlops-bootstrap-logs/`. Authenticate GitHub CLI with an account that can run Actions and download this repo's workflow artifacts (`gh auth login --hostname github.com --web`). This preflight does not build or deploy the assignment image. If it fails, preserve the printed log path and inspect the log before retrying.

Use explicit `--context mlops-assignment` to avoid mutating other clusters. The bootstrap uses `minikube start -p mlops-assignment --driver=docker --cpus=4 --memory=6144`; after preparing and loading a verified image, run `make deploy-minikube`.

For an automated build-through-deployment on a clean checkout of pushed `main`, authenticate `gh` and run `bash scripts/run_lab_deployment.sh`. It starts the `Package verified local-deployment release` GitHub workflow, waits for its AMD64 image build and smoke test, downloads and checksum-verifies the image, loads it, deploys to Minikube, tests prediction and invalid-input routes through Traefik, checks `/metrics` stays private, and collects evidence. Logs are saved in `reports/evidence/runtime/`. On a replacement VM, check out the same commit and use the prior successful run ID with `bash scripts/run_lab_deployment.sh --reuse-run RUN_ID` to avoid rebuilding. The release artifact is retained by GitHub Actions for 90 days.

The script enables Traefik, verifies its IngressClass, loads the provided image, applies the overlay, waits for application rollout, applies internal Prometheus and waits for its rollout. Use unique model/version image tags for subsequent releases; avoid reusing `local` with unchanged pods.

```bash
# Separate persistent terminal:
minikube -p mlops-assignment tunnel
# Discover the real assigned address:
kubectl --context mlops-assignment -n kube-system get svc traefik
# Substitute the observed address; for this macOS Docker run it may be 127.0.0.1:
.venv/bin/python scripts/smoke_api.py --url http://127.0.0.1:8081 --host heart-disease.test --requests 100
```

No hosts-file change is necessary when using the Host header. For interactive docs use hostname mapping only after verifying the actual address. Readiness alone does not prove Ingress: test /predict through the controller route. `/metrics` must return 404 through Ingress while remaining accessible to internal Prometheus.

```bash
kubectl --context mlops-assignment -n mlops-assignment port-forward svc/prometheus 9090:9090
make dashboard
make evidence
```

Dashboard is http://127.0.0.1:8090. Capture nonempty graphs after enough traffic and at least two scrapes. Check both pod targets are UP. A direct API Service port-forward is for diagnosis only; it does not count as Ingress evidence.

If rollout fails: inspect pods/events/logs and resource limits. If image cannot execute: verify architecture. If Ingress gives 404: inspect Host and IngressClass. If 503: inspect ready endpoints, model-load logs and service ports. Keep the tunnel and Docker running while reviewing. Stop cluster/tunnel after evidence export to release host resources.

The local controller LoadBalancer exposes HTTP on 8081 and HTTPS on 8443 to allow unprivileged service tunneling. `scripts/configure_traefik_ports.py` preserves the controller target ports. Minikube may also attempt a separate privileged Ingress tunnel on ports 80/443; application access uses the controller Service tunnel on 8081 and does not depend on that additional tunnel.

The application deploy script installs Traefik only if absent. Repeated addon enable/upgrade against the patched Service may attempt duplicate ports; before a deliberate controller upgrade restore its web/websecure Service ports to 80/443, upgrade, then run the local port configuration script again. Application releases do not reinstall the controller.
