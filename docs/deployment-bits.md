# BITS VM submission workflow

The selected target is the Rocky Linux 9 AMD64 BITS VM, running Minikube with Docker and Traefik Ingress. GitHub Actions trains, tests and builds the image. No public URL is required for this private Kubernetes deployment; submit working access instructions and actual endpoint evidence.

## 1. Prepare and deploy on BITS

Docker and Minikube must already be installed and usable by your regular account. The bootstrap checks these prerequisites, installs Python 3.11, supporting RPMs and kubectl, creates the Python environment and starts a four-CPU/6-GiB Minikube profile. The VM needs additional resources for its OS and Docker. A package-install failure or insufficient capacity must be resolved on the VM before continuing.

After these changes have been committed and pushed, run on BITS:

```bash
git clone https://github.com/2025ae05568-rkmishra/mlops-assignment1.git
cd mlops-assignment1
git switch main
git pull --ff-only
bash scripts/bootstrap_rocky9.sh --skip-installed
gh auth login --hostname github.com --web
bash scripts/run_lab_deployment.sh
```

The runner requires a clean checkout matching pushed main. It waits for a successful release workflow, verifies its image archive, loads a uniquely tagged release image, checks model version through Ingress, generates synthetic traffic and verifies all current API replicas are scraped by Prometheus. It captures resources, request logs, CI test/Docker proof, metrics and release identifiers together. It does not claim your screenshots, recording or individual review are complete.

```bash
# Selected self-contained evidence directory:
cat reports/evidence/runtime/latest-submission.txt
# Reuse a successful release on a replacement VM at the same commit:
bash scripts/run_lab_deployment.sh --reuse-run RUN_ID
```

Keep the downloaded release artifact and selected evidence directory. Both are ignored runtime outputs; export them before switching VMs. Downloaded tracking database/artifacts are available in the release directory printed by the runner.

## 2. Keep reviewer access running

Run in a persistent VM terminal:

```bash
bash scripts/open_vm_access.sh
```

This opens a localhost Traefik Ingress forward on 8081, internal Prometheus forward on 9090, dashboard on 8090 and the selected release's MLflow view on 5000. It rebases a disposable copy of the exported MLflow database to the downloaded artifacts without modifying the release export. It checks API/dashboard/MLflow readiness and stops its access processes when interrupted. Keep this terminal open throughout the demonstration.

On the BITS VM desktop, open:

- Dashboard: http://127.0.0.1:8090
- MLflow: http://127.0.0.1:5000

For workstation access, use your actual BITS SSH destination (and VPN/jump host if required):

```bash
ssh -N -L 8081:127.0.0.1:8081 -L 8090:127.0.0.1:8090 -L 5000:127.0.0.1:5000 USER@VM
```

Then, from a workstation checkout with the Python environment installed:

```bash
.venv/bin/python scripts/smoke_api.py --url http://127.0.0.1:8081 --host heart-disease.test
```

Alternatively, on the VM or tunneled workstation, verify readiness with:

```bash
curl --fail -H 'Host: heart-disease.test' http://127.0.0.1:8081/ready
curl --fail -H 'Host: heart-disease.test' -H 'Content-Type: application/json' \
  --data-binary @tests/fixtures/valid_request.json http://127.0.0.1:8081/predict
```

Opening 127.0.0.1:8081 in a browser without the Host header does not match the Ingress host rule. For browser API docs, map heart-disease.test to 127.0.0.1 on the viewing machine, then use http://heart-disease.test:8081/docs. Do not expose Prometheus, MLflow or Kubernetes administration ports publicly.

If SSH access is unavailable to the evaluator, document the authorized BITS desktop/VPN access process or arrange a permitted review session. A recording alone does not replace the required usable access instructions. Never include credentials in the repository, report, screenshots or recording.

## 3. Capture the required screenshots and video

Find the directory printed by `cat reports/evidence/runtime/latest-submission.txt`. Put fresh PNG screenshots from this exact release in its `screenshots/` subdirectory:

| Filename | What the screenshot must show |
|---|---|
| ci.png | Successful release workflow for the captured commit/run, verification steps and artifact |
| mlflow.png | Selected model run matching manifest.json, parameters, metrics and artifacts |
| deployment.png | BITS pods/Service/Ingress, two ready replicas and valid/invalid prediction responses |
| monitoring.png | Nonempty dashboard graphs and both current pod targets UP |

Generate traffic during capture in a second VM terminal:

```bash
.venv/bin/python scripts/generate_traffic.py --duration 60
kubectl --context mlops-assignment -n mlops-assignment get pods,svc,ingress
kubectl --context mlops-assignment -n mlops-assignment logs -l app=heart-disease-api --prefix --tail=20
```

Add `reviewer-access.md` inside the same evidence directory. Write the actual tested access method, authorized destination or BITS desktop procedure, required VPN/jump host, ports, Host header, the successful check and model version, and how the access processes remain available. Do not leave USER@VM or other placeholders and do not include passwords/private keys. Keep this note concise (approximately 100 words) for the ten-page report.

Record the pipeline using [video-script.md](video-script.md). Show real execution and explain your own choices. Upload the video to a location the evaluator can open, check playback and permissions, and put its HTTPS link in [video-link.md](video-link.md).

## 4. Build and inspect the ten-page final report

```bash
make report VIDEO_URL='https://your-reviewer-accessible-recording-link'
# Or select an exported evidence directory explicitly:
make report EVIDENCE_DIR='/path/to/exported/evidence' VIDEO_URL='https://your-recording-link'
```

The report reads only the selected release's metrics, figures and VM evidence. It refuses mismatched versions, missing replicas/scrape targets, unsuccessful test proof, missing screenshots, missing access instructions or a missing recording link. It writes `output/pdf/2025ae05568-mlops-final-report.pdf` only after producing exactly ten pages. The evidence directory receives `submission-manifest.json` with the report, screenshot and access-note hashes. The checks validate evidence consistency; you must still verify screenshot content, video access and your individual understanding.

For layout review before BITS execution, `make report-draft` creates a visibly marked draft using historical experiment results. It does not create a final submission report. The earlier workstation report is retained under `output/pdf/historical/` as historical evidence.

Open every page of the final PDF and check all screenshots, text, identifiers, links and page count. Export the entire evidence directory (including screenshots), final PDF and release artifact before shutting down. Include the final PDF and screenshot folder in the submitted GitHub repository, preserve the captured release commit separately from any later submission-document commit, and complete [submission-checklist.md](submission-checklist.md).
