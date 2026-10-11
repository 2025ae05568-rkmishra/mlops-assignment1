# Verified requirements and implementation evidence

## 2. Verified rubric and submission traceability — 50 marks

| ID | Assignment area [R] | Marks | PDF page | Implementation and required evidence |
|---|---|---:|---:|---|
| R1 | Data acquisition and EDA | 5 | 1 | UCI download script/instructions; missing-value handling and encoding; histograms, correlation heatmap and class-balance plot; cleaned dataset and provenance |
| R2 | Feature engineering and model development | 8 | 1 | Scaling/encoding; at least two classifiers; documented tuning/selection; CV accuracy, precision, recall and ROC-AUC |
| R3 | Experiment tracking | 5 | 1 | MLflow or equivalent; parameters, metrics, artifacts and plots for every experiment run |
| R4 | Model packaging and reproducibility | 7 | 1 | Reusable final model; clean requirements.txt or Conda environment; complete preprocessing pipeline/transformers; clean-environment reload |
| R5 | CI/CD and automated testing | 8 | 2 | Data/model unit tests; GitHub Actions or Jenkins with lint, unit-test and model-training steps; logs/artifacts for every workflow run, including failures |
| R6 | Containerization | 5 | 2 | Dockerized API; /predict accepts JSON and returns prediction plus confidence; local container build/run with sample input |
| R7 | Production deployment | 7 | 2 | Public cloud or local Kubernetes; manifest or Helm chart; LoadBalancer or Ingress; verified endpoint and deployment screenshots |
| R8 | Monitoring and logging | 3 | 2 | API request logging; demonstrated Prometheus + Grafana or API metrics/logs dashboard |
| R9 | Documentation and reporting | 2 | 2 | Setup/install, EDA/modeling choices, experiment summary, architecture diagram, CI/CD/deployment screenshots and repository link |
| | **Total** | **50** | | |

[R] Page 2 additionally requires the GitHub repository to contain code, Dockerfile(s), requirements.txt/env.yml, cleaned dataset and download script/instructions, EDA/training/inference notebooks or scripts, unit-test folder, workflow YAML/Jenkinsfile, deployment manifests/Helm charts, a screenshot folder and the final 10-page DOC/DOCX/PDF report. Submit the public API URL when applicable, otherwise local access instructions, and a short overall-pipeline video. Section 19.5 maps each deliverable to a concrete path.

[R] Page 3 requires all scripts to execute from a clean setup using the requirements file, isolated model serving with Docker build/test proof, and a pipeline that fails on code/test errors with clear logs. It also requires independent work, individual understanding and originality; see Section 19.6.

Local Kubernetes is fully permitted. The PDF does not require a paid cloud deployment, a public URL for a local deployment, both LoadBalancer and Ingress, or fully automated deployment to a laptop cluster. This design retains both Ingress and a controller LoadBalancer for the local demonstration as a decision, not an extra rubric requirement. Render remains supplemental to the selected Kubernetes implementation.

**Source reconciliation result:** All nine categories and weights match the PDF. The 10-page report and permitted formats are confirmed. The user explicitly selected the actual Cleveland schema and instructed that the PDF's “14+ features” wording be ignored for this decision (Section 6.1). This is a recorded override, not an unresolved blocker. Requirements not stated in this PDF remain unspecified.


Implementation artifacts and actual status: see [progress](progress.md), [submission checklist](submission-checklist.md), `reports/evidence/` and `reports/metrics/`. Remote CI and final submission remain pending.
