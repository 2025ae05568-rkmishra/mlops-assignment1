# Heart Disease Prediction — MLOps Assignment 1

Educational binary classification using original UCI processed Cleveland: 13 predictors, target `int(num > 0)`. The user explicitly selected this real schema over the assignment's feature-count wording. This model is not clinically validated and must not guide diagnosis or treatment.

## Start from a clean checkout

Install Python 3.11, Git, Docker Desktop, kubectl and Minikube. On macOS: `brew install python@3.11 minikube` (Docker Desktop installed separately). Start Docker Desktop before container or cluster commands. Linux CI uses the same Python requirements.

```bash
make setup
make data
make eda
make train
make package
make test
```

The first source has already been checksum-pinned in `data/manifests/source-lock.json`. `make data` downloads the UCI archive when the raw cache is absent, checks both archive and member SHA-256, writes the cleaned CSV and deterministic split manifest, and refuses changed upstream data. Network access is needed for installation/acquisition. Do not regenerate the source lock silently.

Run the API and exercise synthetic JSON:

```bash
make serve
# In another terminal:
make smoke
```

API documentation: http://127.0.0.1:8000/docs. Predictions include class, positive-class probability, confidence assigned to the returned class, threshold and actual model/schema version. All 13 fields are required; only `ca` and `thal` may explicitly be null. Original category codes are enforced; invalid inputs return sanitized HTTP 422 responses.

## Training and experiment tracking

Preprocessing uses median imputation for numeric features, mode imputation/one-hot encoding for categories and scaling for Logistic Regression. All fitted transformations are inside the CV pipeline. An 80/20 stratified split and five shared training-only folds use seed 42. Compare DummyClassifier, six Logistic Regression configurations and eighteen Random Forest configurations. Select mean CV ROC-AUC with a 0.01 simplicity rule favoring Logistic Regression; threshold is fixed at 0.5. See `configs/training.yaml`.

`reports/metrics/` contains measured comparison and final metrics. `reports/figures/` contains required EDA and evaluation plots. `notebooks/01_eda.ipynb` calls the shared implementation. The selected full MLflow pipeline is saved under an immutable `artifacts/model/<version>/`; `current/` is a verified serving copy. Checksums, schema, class order and feature names are checked before readiness. Only load locally trusted bundles.

```bash
make mlflow
# Open http://127.0.0.1:5000
make evaluate
```

MLflow tracks every executed candidate configuration, fold metrics, lineage, artifacts and plots in `mlflow.db`/`mlruns/`. `make evaluate` displays the saved held-out evaluation rather than tuning or retraining on test results. Verified identical training inputs reuse the experiment cache. Rebuilding after a packaging failure is a reproducibility check; it is not independent validation.

## Docker and local Kubernetes

On a Rocky Linux 9 lab VM, clone the repository and run `bash scripts/bootstrap_rocky9.sh` as your regular user first. It installs Python 3.11, kubectl and GitHub CLI, starts/checks the `mlops-assignment` Minikube profile, and saves a timestamped troubleshooting log in `~/mlops-bootstrap-logs/`. It does not train, build, or deploy the assignment image.

After authenticating GitHub CLI with `gh auth login --hostname github.com --web`, the end-to-end lab runner triggers the release build on GitHub Actions, downloads and verifies its image, deploys it to Minikube, smoke-tests Ingress, and collects evidence:

```bash
bash scripts/run_lab_deployment.sh
```

For another VM, check out the same commit and reuse the successful release artifact instead of rebuilding:

```bash
bash scripts/run_lab_deployment.sh --reuse-run RUN_ID
```

See [local access instructions](docs/deployment-minikube.md) for requirements, logs, and manual steps.

```bash
make docker-build
make docker-smoke
minikube start -p mlops-assignment --driver=docker --cpus=4 --memory=6144
make deploy-minikube
```

The image bakes in the exact verified pipeline, runs as UID 10001 and supports a read-only root with writable `/tmp`. Two replicas expose only the documented public routes through Traefik Ingress; `/metrics` stays internal. Follow [local access instructions](docs/deployment-minikube.md), including the persistent tunnel. A local tunnel is not a public Internet URL.

```bash
# Keep these separate terminals running:
minikube -p mlops-assignment tunnel
kubectl --context mlops-assignment -n mlops-assignment port-forward svc/prometheus 9090:9090
make dashboard
```

Dashboard: http://127.0.0.1:8090. Prometheus: http://127.0.0.1:9090. The dashboard shows request/error rate, inference p95 and verified model replicas; Prometheus scrapes each pod separately. Logs omit raw features, bodies and credentials. History is ephemeral and limited to 24 hours; export evidence before teardown.

## Automation, evidence and current scope

`make verify` runs lint, data/EDA/training, package checks, unit and integration tests. `.github/workflows/ci.yml` performs these and isolated Docker testing; `release.yml` exports a tested image archive and checksum for scripted local deployment. Official actions are pinned to resolved SHAs. Failures block subsequent steps; `if: always()` preserves available artifacts/logs. The existing origin is https://github.com/rmishra3261/2025ae05568-mlops. Remote workflow execution requires the implementation to be committed and pushed; local checks are not claimed as GitHub runs. Release archives are architecture-specific (GitHub Ubuntu is AMD64); build locally for the ARM64 Minikube cluster.

Use `make evidence` to collect runtime versions/resources/logs and release linkage. Generated model/MLflow files stay ignored and must be exported for durable submission. See [progress](docs/progress.md), [submission checklist](docs/submission-checklist.md) and the supplied architecture design. GKE is conditional and has not been provisioned. A student-reviewed 10-page report, screenshot selection and overall-pipeline recording remain separate submission work.

Stop without deleting evidence: `minikube stop -p mlops-assignment`. Stop the tunnel and port-forward processes too. After preserving needed artifacts, `minikube delete -p mlops-assignment` removes this project's local cluster.

Dataset attribution: Janosi, A., Steinbrunn, W., Pfisterer, M., & Detrano, R. (1989). Heart Disease. UCI Machine Learning Repository. https://doi.org/10.24432/C52P4X. CC BY 4.0. [Data provenance](data/README.md).

The local controller LoadBalancer exposes HTTP on 8081 and HTTPS on 8443 to allow unprivileged service tunneling. `scripts/configure_traefik_ports.py` preserves the controller target ports. Minikube may also attempt a separate privileged Ingress tunnel on ports 80/443; application access uses the controller Service tunnel on 8081 and does not depend on that additional tunnel.

Default image tags combine the immutable selected model version with a serving-code/dependency/Dockerfile hash. Deployment renders this exact tag before applying manifests; no mutable local tag is used by default. Uvicorn access logging is disabled to prevent arbitrary URL/query values entering logs; bounded structured request logging remains active.
