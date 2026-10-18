# Selected BITS submission evidence

This self-contained snapshot was imported from `bits-evidence.tgz`, captured on 18 October 2026, and validated offline. The original archive remains unchanged in Downloads; its SHA-256 and import notes are in [import.json](import.json). The archived `figures/monitoring-final.png` was a byte-identical historical Mac screenshot carried into the release; it has been removed from this curated snapshot. Actual BITS monitoring evidence is `monitoring.json` and `screenshots/monitoring.png`.

| Identity | Selected release |
|---|---|
| Workflow | [39107510102](https://github.com/2025ae05568-rkmishra/mlops-assignment1/actions/runs/39107510102) |
| Source commit | ae005d121706927a0d7956126c87bf5c85ada6c0 |
| Model | 8bb3330d56912ab6edad-54110720 |
| Final MLflow run | 541107209c2845829a2b02c184605a0d |
| Release tests | 31 unit + 2 integration; zero failures, errors or skips |
| Runtime | Two ready API pods; both Prometheus targets UP |
| API | Valid prediction 0; invalid input 422; Ingress /metrics 404 |

The release/model commits, served versions, deployed image tag, isolated Docker image identity, replica readiness and current scrape targets passed `heart_disease.submission.validate`. CI counts refer to this captured release, not later documentation changes.

Final requirement audit: [final-audit.json](final-audit.json) records the isolated pipeline verification, 36 passing tests, matched metrics, report checks and remaining delivery steps.

## Files and report mapping

| Evidence | Purpose / report pages |
|---|---|
| `data/`, `figures/` | Pinned source, cleaning, split and EDA; page 3 |
| `metrics/`, `manifest.json` | Candidate CV, selected settings, held-out results and lineage; pages 1, 4-6 |
| `ci/` | JUnit test results and isolated Docker serving proof; pages 6-7 |
| `release.json`, `lab-deployment.log` | Release identity, image/archive hashes and successful VM deployment; pages 7-8 |
| `deployment.txt`, `pods.txt`, `nodes.txt`, `resources.txt`, `api.json` | Kubernetes and verified Ingress behavior; page 8 |
| `monitoring.json`, `api-logs.txt` | Captured monitoring series, current targets and structured request logs; page 9 |
| `reviewer-access.md` | Demonstrated private BITS desktop access; pages 2 and 8 |
| `screenshots/` | Curated real screenshots and original recording frames; pages 4, 7-9 |
| `submission-manifest.json` | Report, screenshot, local video and access-note hashes |

`release.json` is preserved verbatim, including the capture script's default SSH access label. Actual demonstrated access was through the BITS remote desktop. The report and access note describe that method; an independent evaluator login was not tested. The manifest also preserves `dirty=true` and source/config/data hashes.

The automated 30-second capture recorded 57 HTTP 200 and 57 HTTP 422 responses. The later manual 60-second run recorded 111 of each. The dashboard screenshot follows that later run, so its rates are not presented as simultaneous with the earlier JSON snapshot. Expected 422s deliberately exercise input validation.

## Screenshot selection

Only cropping and lossless PNG conversion were used. No results, labels or statuses were edited. Exact source names, hashes and crop coordinates are in [screenshots/selection.json](screenshots/selection.json). The original files in Documents were retained.

| Selected file | Source and reason |
|---|---|
| `mlflow.png` | `mlflow-bits.png`: final model parameters, held-out metrics and run identity; used on page 4 |
| `ci.png` | Original screen recording at 02:00: successful release job and Docker smoke response; page 7 |
| `ci-artifact.png` | Original screen recording at 11:00: downloadable release artifact; page 7 |
| `deployment.png` | 2:25:14 PM screenshot: successful deployment and valid/invalid Ingress output; page 8 |
| `monitoring.png` | 2:03:17 PM screenshot: four populated panels and both current targets UP; page 9 |
| `api-smoke.png` | 1:55:46 PM screenshot: separate valid/invalid and 60-second traffic evidence; supporting evidence |
| `kubernetes.png` | 4:18:02 PM screenshot: ready pods, Services and Ingress; original retained including earlier command typo; supporting evidence |
| `mlflow-artifacts.png` | 2:14:54 PM screenshot: serving bundle tree and model manifest; supporting evidence |

Excluded from the report: the MLflow home page (2:03:33), crowded comparison view (2:05:58), and duplicate artifact views (2:13:48, 2:14:21, 2:14:33, 2:14:41, 2:15:00, 2:15:12). Native release plots and machine-readable manifests provide clearer evidence. The iMovie view (3:41:43), file manager (4:14:17), and repeated access terminal (4:17:11) add no distinct assignment evidence and were also omitted.

## Report reproduction

From the project root, with development requirements installed:

```bash
make report EVIDENCE_DIR=reports/evidence/bits VIDEO_FILE="$HOME/Documents/2025ae05568-mlops.mp4"
```

Submit the MP4 separately with the coursework. A hosted video link is optional. Rebuilding the report needs neither live VM access nor training, the Docker image archive, the virtual environment from the VM, or a running MLflow server. Keep the original release available through its GitHub Actions artifact for deployment reproduction.
