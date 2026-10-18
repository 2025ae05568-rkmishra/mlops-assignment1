# Heart Disease Prediction — MLOps Assignment 1

This repository contains an end-to-end MLOps assignment using the UCI processed Cleveland heart-disease dataset. The implementation uses its actual 13 predictor fields and derives a binary target as `int(num > 0)`, following the student's selected schema rather than the assignment PDF's "14+ features" wording. This model is educational, has not been clinically validated, and must not guide diagnosis or treatment.

Repository: <https://github.com/2025ae05568-rkmishra/mlops-assignment1>

## Fast path: deploy on a Rocky Linux 9 BITS lab VM

The GitHub release workflow builds and smoke-tests the AMD64 application image. The VM downloads that image and runs it in Minikube; it does not need to train or build the model locally.

### Before starting

Use a Rocky Linux 9 **x86_64/AMD64** VM with:

- Docker running and usable by your account.
- Minikube installed; enough VM resources for a 4-CPU, 6-GiB Minikube profile.
- Network access to GitHub Actions artifacts, Python package downloads, and container registries.
- An account with `sudo` access for the bootstrap, plus GitHub access to dispatch workflows and download artifacts.
- A desktop/browser on either the VM or your workstation for reviewing the dashboard and recording the video. Video recording is manual; it is not a Kubernetes component.

### Run in this order

1. **Clone the new repository and enter it.**

   ```bash
   git clone https://github.com/2025ae05568-rkmishra/mlops-assignment1.git
   cd mlops-assignment1
   git switch main
   git pull --ff-only
   ```

   Run the scripts from this checkout. They require a clean worktree on the pushed `main` commit. If you make documentation or code changes, commit and push them before running the end-to-end deployment script.

2. **Prepare the VM, Python environment, Minikube, and Prometheus.**

   ```bash
   bash scripts/bootstrap_rocky9.sh --skip-installed
   ```

   Run as your regular user, **not** with `sudo`. This installs missing host tools (including Python 3.11, `kubectl`, and GitHub CLI), starts/checks the `mlops-assignment` Minikube profile, installs a `kubectl` client matching the cluster, applies and waits for the in-cluster Prometheus deployment, and runs `make setup` to install the locked Python, dashboard, and report dependencies. It does **not** build or deploy the assignment application image. The timestamped log is in `~/mlops-bootstrap-logs/`.

   If only Prometheus needs applying to an already-running cluster, use this instead:

   ```bash
   bash scripts/bootstrap_rocky9.sh --prometheus-only
   ```

   This mode installs no host software, does not start Minikube, and does not set up the Python environment. It is optional: the deployment script also applies Prometheus.

3. **Authenticate GitHub CLI.**

   ```bash
   gh auth login --hostname github.com --web
   gh auth status --hostname github.com
   ```

   Complete browser sign-in with an account that can run Actions and download artifacts for this repository.

4. **Build on GitHub Actions, then deploy and test on the VM.**

   ```bash
   bash scripts/run_lab_deployment.sh
   ```

   This one command checks the checkout and cluster, dispatches the **Package verified local-deployment release** workflow on GitHub, waits for its training/tests/image smoke test to succeed, downloads and checksum-verifies its image artifact, loads the image into Docker, deploys the API and Prometheus to Minikube, exercises valid and invalid API requests through Traefik Ingress, checks that `/metrics` is not publicly routed, and collects deployment evidence. It prints the workflow run ID and link when complete. Detailed logs and captured runtime evidence are under `reports/evidence/runtime/`.

   For a replacement VM, clone/check out the **same commit** and reuse the successful **release workflow** run ID:

   ```bash
   bash scripts/run_lab_deployment.sh --reuse-run RUN_ID
   ```

   This downloads the existing artifact instead of starting a new build. GitHub retains release artifacts for 90 days. Do not use a CI run ID as the release run ID.

5. **Check the result.**

   ```bash
   minikube -p mlops-assignment status
   kubectl --context mlops-assignment -n mlops-assignment get pods,svc,ingress
   kubectl --context mlops-assignment -n mlops-assignment get deployment/prometheus
   ```

   Wait for two API replicas and Prometheus to be ready. The runner already tests prediction via Ingress. For manual access and troubleshooting, see [Minikube deployment and access](docs/deployment-minikube.md).

### View the monitoring dashboard

Prometheus runs **inside Minikube**; do not install Grafana separately. The project includes a Python dashboard that reads Prometheus metrics.

1. In a VM terminal, forward Prometheus:

   ```bash
   kubectl --context mlops-assignment -n mlops-assignment \
     port-forward svc/prometheus 9090:9090
   ```

2. In another VM terminal, start the dashboard:

   ```bash
   make dashboard
   ```

3. Open `http://127.0.0.1:8090` on the VM. To view it from your workstation, keep the dashboard and port-forward running, then create an SSH tunnel from the workstation:

   ```bash
   ssh -L 8090:127.0.0.1:8090 -L 9090:127.0.0.1:9090 USER@VM
   ```

   Open `http://127.0.0.1:8090` on the workstation. Generate requests and allow at least two Prometheus scrapes for useful graphs. Metrics history is ephemeral; save screenshots and evidence before stopping Minikube.

## Run the data, training, and test pipeline

Use Python 3.11 and the repository's locked requirements:

```bash
make setup
make verify
```

`make verify` runs lint, data acquisition, EDA, model comparison/training, model packaging, and unit/integration tests. To run individual stages:

```bash
make data
make eda
make train
make evaluate
make package
make test
```

The dataset archive and its member are SHA-256 pinned in `data/manifests/source-lock.json`. `make data` downloads the source if it is not cached, verifies its hashes, creates the cleaned dataset and deterministic split manifest, and fails if the upstream data changes. Do not silently regenerate the source lock.

Preprocessing is part of the fitted cross-validation pipeline: median imputation for numeric features, mode imputation and one-hot encoding for categorical features, and scaling for Logistic Regression. A stratified 80/20 split and five shared training-only folds use seed 42. The search compares a DummyClassifier, six Logistic Regression configurations, and eighteen Random Forest configurations; model selection uses mean CV ROC-AUC with a 0.01 simplicity rule favoring Logistic Regression. The 0.5 threshold is fixed. Held-out test results do not drive tuning. See [training configuration](configs/training.yaml), [model card](docs/model-card.md), `reports/metrics/`, and `reports/figures/`.

MLflow records candidate parameters, metrics, artifacts, plots, and lineage in `mlflow.db` and `mlruns/`. The selected full preprocessing/model pipeline is packaged with checksums and schema information under `artifacts/model/`; those generated model and tracking files are git-ignored and should be exported when needed for durable evidence.

To browse the local experiment runs, start MLflow and open its URL:

```bash
make mlflow
# Open http://127.0.0.1:5000
```

## Local development (macOS or Linux)

Install Python 3.11, Git, Docker, kubectl, and Minikube first (on macOS, install Docker Desktop separately and start it). Then run the pipeline commands above. To deploy a locally built image to Minikube instead of using the BITS lab release flow:

```bash
make docker-build
make docker-smoke
minikube start -p mlops-assignment --driver=docker --cpus=4 --memory=6144
make deploy-minikube
```

For the deployed local API's Traefik route, Prometheus access, and dashboard, follow [Minikube deployment and access](docs/deployment-minikube.md). `make docker-build` packages the current local model, so train/package first if no verified model bundle is present.

## API and Docker

The FastAPI service loads the verified packaged pipeline; requests do not trigger training. To run locally after packaging:

```bash
make serve
```

In another terminal:

```bash
make smoke
```

API docs: <http://127.0.0.1:8000/docs>. `POST /predict` accepts the synthetic request in `tests/fixtures/valid_request.json` and returns the class, positive-class probability, confidence for the returned class, threshold, and model/schema versions. All 13 fields are required; only `ca` and `thal` may explicitly be null. Invalid input receives a sanitized HTTP 422 response. See [API contract](docs/api.md).

Build and test an isolated container after packaging:

```bash
make docker-build
make docker-smoke
```

The Docker image contains the selected model and runs as UID 10001 with a read-only root filesystem and writable `/tmp`. The GitHub workflows also verify the model, tests, container build, and container smoke test.

## Assignment deliverables and evidence

The assignment PDF asks for each item below. Paths point to the implementation/evidence in this repository:

| Requirement | Implementation / evidence |
|---|---|
| Data acquisition, cleaning, missing-value handling, EDA visualizations | `src/heart_disease/data/`, `data/README.md`, `data/processed/cleaned.csv`, `data/manifests/`, `notebooks/01_eda.ipynb`, `reports/figures/` |
| Feature engineering, at least two classifiers, tuning and CV metrics | `src/heart_disease/models/`, `configs/training.yaml`, `reports/metrics/`, `docs/model-card.md` |
| Experiment tracking | `make mlflow`, `mlflow.db`, `mlruns/` |
| Reusable model and clean requirements | `artifacts/model/` (generated), `requirements.txt`, `requirements-dev.txt` |
| Unit tests and automated CI with logs/artifacts | `tests/`, `.github/workflows/ci.yml`, `.github/workflows/release.yml`, GitHub Actions run artifacts |
| JSON prediction API and isolated container proof | `src/heart_disease/api/`, `Dockerfile`, `tests/fixtures/valid_request.json`, `make docker-smoke` |
| Kubernetes deployment, Ingress, endpoint proof | `deploy/k8s/`, `scripts/deploy_minikube.sh`, `scripts/run_lab_deployment.sh`, `reports/evidence/` |
| Request logging and monitoring/dashboard | `src/heart_disease/api/`, `deploy/monitoring/`, `scripts/monitoring_dashboard.py`, `reports/evidence/screenshots/monitoring/` |
| Setup, modeling, architecture, deployment and report | This README, `docs/architecture.md`, other `docs/`, `output/pdf/2025ae05568-mlops-final-report.pdf` |
| Local API access instructions and short pipeline video | [Minikube access instructions](docs/deployment-minikube.md), [recording outline](docs/video-script.md), [video link placeholder](docs/video-link.md) |

The assignment permits **local Kubernetes** and local access instructions when the API is not public; paid cloud deployment and a public URL are not required for this chosen path. The overall architecture is in [docs/architecture.md](docs/architecture.md), progress and measured evidence in [docs/progress.md](docs/progress.md), and the remaining student/submission checks in [docs/submission-checklist.md](docs/submission-checklist.md).

The included report is ten pages, but **review it before submission**. Its current PDF and report generator contain links and run details for the previous GitHub repository; they are not updated automatically by this deployment flow. Update the report source with the new repository URL and the exact CI/release evidence you verified, then rebuild with `make report` when the required verification evidence, screenshots, and extracted CI artifact are available. The video must be recorded by the student: demonstrate the actual pipeline, identify the repository and model version, explain data/EDA and model selection, show CI and container verification, inspect Kubernetes/Ingress, exercise valid and invalid requests, show monitoring/logs, and explain design choices. Do not present unrun steps as completed work; independently review the PDF and follow academic integrity requirements.

## GitHub Actions

- **Verify ML pipeline** (`.github/workflows/ci.yml`) runs on pushes/PRs and can be manually dispatched. It performs linting, tests, data/EDA/training, packaging, and an AMD64 Docker build/smoke test. Run failures stop later steps; available diagnostics/artifacts are retained.
- **Package verified local-deployment release** (`.github/workflows/release.yml`) is manually dispatched by `scripts/run_lab_deployment.sh`. It verifies/trains/tests, builds and smoke-tests the serving image, then publishes the image archive, checksum, model bundle, and diagnostics as a downloadable artifact.

The deployment runner requires the local checkout to be clean and exactly match pushed `main`. Push changes before invoking it. A successful CI run is not the same as a release run: use the release workflow ID with `--reuse-run`.

## Stop and preserve work

Save runtime logs, screenshots, report, and any untracked model/evidence files to persistent storage before switching VMs or deleting the cluster. Then stop Minikube:

```bash
minikube stop -p mlops-assignment
```

Stop any port-forward, dashboard, or tunnel terminals separately. `minikube delete -p mlops-assignment` deletes this project's cluster and should only be used after preserving needed evidence. A Minikube cluster and local Docker images are VM-local; GitHub code and unexpired release artifacts can be fetched again on a replacement VM.

## Data attribution

Janosi, A., Steinbrunn, W., Pfisterer, M., & Detrano, R. (1989). *Heart Disease*. UCI Machine Learning Repository. <https://doi.org/10.24432/C52P4X>. Licensed under CC BY 4.0. See [data provenance](data/README.md).
