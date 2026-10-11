# Implementation progress

The design is ready for implementation with the user-approved Cleveland schema: 13 predictors and binary target derived from `num > 0`. Design coverage is distinct from measured implementation success.

| Stage | Status | Exit evidence |
|---|---|---|
| 0 — Environment and source decisions | Verified | Python 3.11.17, locked requirements, pip check, docs/environment.md |
| 1 — Data foundation and EDA | Verified | 303 cleaned rows, 242/61 split, source hash, required plots |
| 2 — Training and MLflow | Verified | 25 candidate configurations; selected Logistic Regression; CV AUC 0.9110, test AUC 0.9654 |
| 3 — Packaging and API | Verified | Checksummed MLflow CloudPickle pipeline; 19 unit + 2 integration tests pass |
| 4 — Containers and automation | Local verification complete | ARM64 image and read-only non-root smoke pass; local failure gate pass; workflow YAML authored, remote runs pending |
| 5 — Local Kubernetes and monitoring | Verified | Two ready API replicas; actual Ingress inference on 8081; two Prometheus targets UP; metrics blocked externally; dashboard captured |
| 6 — Conditional GKE | Not selected | Requires account/budget configuration |
| 7 — Final report and video | Pending | Student-reviewed final submission and recording |

## Verification notes

- Initial MLflow default serializer rejected numpy.dtype during model export. The failure was retained in MLflow. Explicit CloudPickle fixed the trusted local export; checksum verification runs before model deserialization. Fixed splits/search/selection were rerun without test-driven changes; repeated held-out metrics are reproducibility evidence, not independent validation.
- Git has no initial commit in this checkout; origin is https://github.com/rmishra3261/2025ae05568-mlops. Training records uncommitted/dirty status and a source hash; no commit SHA or GitHub run is invented.
- Initial server dry-run on an absent namespace cannot validate dependent resources because dry-run does not persist namespaces; the actual rollout creates the namespace before validation.

- Local Traefik controller Service uses HTTP 8081 / HTTPS 8443 so its LoadBalancer tunnel is unprivileged. The actual request path remains controller -> Ingress rules -> API Service -> ready pods.

- Re-enabling the Helm-managed Traefik addon after changing its Service ports caused duplicate-port validation on upgrade. The deployment script now installs the addon only when its Deployment is absent, preserving the already verified controller and making application redeployment repeatable.
