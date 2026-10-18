# Selected BITS submission evidence

This folder contains the execution evidence supporting the final ten-page report. Data provenance, cleaning, schema and split manifests are kept once in [data/manifests](../../../data/manifests/).

| Identity | Selected release |
|---|---|
| Workflow | [39107510102](https://github.com/2025ae05568-rkmishra/mlops-assignment1/actions/runs/39107510102) |
| Source commit | ae005d121706927a0d7956126c87bf5c85ada6c0 |
| Model | 8bb3330d56912ab6edad-54110720 |
| Final MLflow run | 541107209c2845829a2b02c184605a0d |
| Release tests | 31 unit + 2 integration; zero failures, errors or skips |
| Runtime | Two ready API pods; both Prometheus targets UP |
| API | Valid prediction 0; invalid input 422; Ingress /metrics 404 |

## Evidence locations

| Evidence | Purpose |
|---|---|
| `figures/` | Required EDA charts and held-out confusion matrix/ROC curve |
| `metrics/`, `manifest.json` | Candidate cross-validation, selected settings, held-out results and model lineage |
| `ci/` | JUnit results and isolated Docker serving proof for the recorded release |
| `release.json`, `lab-deployment.log` | Release identity, hashes and successful VM deployment |
| `deployment.txt`, `pods.txt`, `nodes.txt`, `resources.txt`, `api.json` | Kubernetes readiness, environment and verified Ingress behavior |
| `monitoring.json`, `api-logs.txt` | Monitoring series, current targets and structured request logs |
| `reviewer-access.md` | Demonstrated private BITS desktop access |
| `screenshots/` | CI job/artifact, MLflow metrics/artifacts, deployment/API checks and populated monitoring |

Release/model commits, served versions, image identities, replica readiness and scrape targets pass `heart_disease.submission.validate`. Counts above describe the captured release, not subsequent code changes.

The automated 30-second capture recorded 57 HTTP 200 and 57 HTTP 422 responses. The later manual 60-second run recorded 111 of each; the dashboard screenshot follows that later run. Expected 422s exercise input validation. Screenshots were cropped for readability without editing results or statuses.

The original `release.json` retains the capture script's SSH access label. Actual demonstrated access was through the BITS remote desktop, as documented in the access note. Separate evaluator account permissions were not tested. The model manifest preserves `dirty=true` and source/config/data hashes.

## Report and video

The [completed ten-page report](../../../output/pdf/2025ae05568-mlops-final-report.pdf) is provided as a PDF. Submit the existing `2025ae05568-mlops.mp4` separately with the coursework. The original model bundle, MLflow artifacts and container archive are available in the selected GitHub Actions release artifact for deployment reproduction.
