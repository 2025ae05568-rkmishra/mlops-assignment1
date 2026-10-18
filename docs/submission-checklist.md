# Submission checklist: BITS VM target

The existing local experiment and workstation evidence are historical. Check the BITS items only after observing the actual outputs. Repository preparation does not certify marks or individual understanding.

- [x] Cleaned dataset, pinned source/download code, EDA notebook/scripts and required figures exist.
- [x] Two model families, training-only CV, model selection and MLflow tracking are implemented.
- [x] Complete preprocessing/model packaging, locked requirements, tests, Dockerfile and CI/release workflows exist.
- [x] Kubernetes/Ingress manifests, request logging and private monitoring dashboard exist.
- [x] BITS release evidence capture, private access workflow and evidence-driven ten-page report generator are implemented.
- [ ] Commit/push the submission fixes to https://github.com/2025ae05568-rkmishra/mlops-assignment1.
- [ ] Execute bootstrap and successful release/deployment on the BITS VM; preserve the selected release run, commit, image/model identity and archive checksum.
- [ ] Verify successful inference and invalid-input rejection through Traefik Ingress, with the selected model version.
- [ ] Verify all requested API replicas are ready and current pod scrape targets are UP; capture nonempty graphs and request logs.
- [ ] Keep VM access processes available and test the documented reviewer access path.
- [ ] Add fresh ci.png, mlflow.png, deployment.png and monitoring.png in the selected evidence directory's screenshots/ folder.
- [ ] Add actual tested reviewer-access.md without credentials or placeholders.
- [ ] Record the overall pipeline, verify playback/sharing permissions, and update docs/video-link.md.
- [ ] Build the final report with the recording link and selected evidence; inspect all ten pages.
- [ ] Export/retain the release artifact, evidence directory and submission-manifest.json; include the final report and screenshot folder in the submission repository.
- [ ] Complete individual originality, understanding and assistance-disclosure review in docs/originality.md.
- [ ] Verify the evaluator can access the repository, report, recording and documented API access path.

Follow [deployment-bits.md](deployment-bits.md). GKE, public hosting, automatic rollback and a production-grade infrastructure overhaul are not required for this chosen assignment path.
