# Current submission target: BITS VM

The workstation verification below is historical. BITS execution and final submission are pending until the [BITS checklist](submission-checklist.md) is completed. The new workflow captures one selected release and builds the report from its actual VM evidence.

# Implementation progress

The design is ready for implementation with the user-approved Cleveland schema: 13 predictors and binary target derived from `num > 0`. Design coverage is distinct from measured implementation success.

| Stage | Status | Exit evidence |
|---|---|---|
| 0 — Environment and source decisions | Verified | Python 3.11.17, locked requirements, pip check, docs/environment.md |
| 1 — Data foundation and EDA | Verified | 303 cleaned rows, 242/61 split, source hash, required plots |
| 2 — Training and MLflow | Verified | 25 candidate configurations; selected Logistic Regression; CV AUC 0.9110, test AUC 0.9654 |
| 3 — Packaging and API | Verified | Checksummed MLflow CloudPickle pipeline; 19 unit + 2 integration tests pass |
| 4 — Containers and automation | Verified locally and remotely | GitHub Actions run 38159803218 passed including AMD64 Docker smoke; current local image deployed |
| 5 — Local Kubernetes and monitoring | Verified | Reverified 12 Oct 2026 | Latest expected image, two ready API replicas, Ingress valid/invalid predictions, two scrape targets UP, external metrics blocked |
| 6 — Conditional GKE | Not selected | Requires account/budget configuration |
| 7 — Final report and video | Report generated; video pending | Ten-page PDF generated and visually verified; student review and recording remain |

## Verification notes

- Initial MLflow default serializer rejected numpy.dtype during model export. The failure was retained in MLflow. Explicit CloudPickle fixed the trusted local export; checksum verification runs before model deserialization. Fixed splits/search/selection were rerun without test-driven changes; repeated held-out metrics are reproducibility evidence, not independent validation.
- GitHub main and the checkout matched commit e1710cb at verification. CI run 38159803218 succeeded. Its artifact ZIP digest matches GitHub and all model bundle checksums pass. CI and local model version IDs differ but test metrics match. CI dirty=true is retained because generated tracked files changed during training; the source hash accompanies the commit.
- Initial server dry-run on an absent namespace cannot validate dependent resources because dry-run does not persist namespaces; the actual rollout creates the namespace before validation.

- Local Traefik controller Service uses HTTP 8081 / HTTPS 8443 so its LoadBalancer tunnel is unprivileged. The actual request path remains controller -> Ingress rules -> API Service -> ready pods.

- Re-enabling the Helm-managed Traefik addon after changing its Service ports caused duplicate-port validation on upgrade. The deployment script now installs the addon only when its Deployment is absent, preserving the already verified controller and making application redeployment repeatable.

## Final report

The historical `output/pdf/historical/2025ae05568-workstation-report.pdf` contains exactly ten pages. The BITS final report is generated only after current evidence and the recording are supplied. Evidence details are in `reports/evidence/final-verification.json`. The student confirmed that the video has not yet been recorded.
