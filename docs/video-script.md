# Student demonstration: BITS deployment

The assignment requires a short recording, with no specified duration. Show actual execution and explain your choices in your own words. Keep the private access terminal running using `bash scripts/open_vm_access.sh`. Use the release identifiers in the selected evidence directory; do not combine old workstation footage with new BITS claims.

1. Open the submission repository and identify the selected commit, release workflow and model version. Explain the educational task and the original 13-predictor Cleveland schema.
2. Show the cleaned data/source manifests and training-only EDA plots. Explain missing values, original category codes, the binary target and leakage prevention.
3. Open the release's MLflow UI at localhost:5000. Compare Logistic Regression and Random Forest CV results, explain the search and selection rule, and distinguish held-out evaluation from tuning.
4. Open the successful release workflow. Show lint/tests/training and isolated AMD64 Docker serving proof. Explain how a failed command blocks later promotion and where logs/artifacts are retained.
5. On the BITS VM, show `kubectl --context mlops-assignment -n mlops-assignment get pods,svc,ingress`. Explain Traefik, the ClusterIP Service, readiness and the two replicas on one node.
6. Run `.venv/bin/python scripts/smoke_api.py --url http://127.0.0.1:8081 --host heart-disease.test`. Explain the prediction, probability, confidence and model version, plus invalid-input rejection. Show `/metrics` returns 404 through Ingress. Explain the actual private reviewer access path.
7. Run `.venv/bin/python scripts/generate_traffic.py --duration 60` while showing the dashboard at localhost:8090. Show both pod targets UP and changing graphs. Show sanitized request logs and explain why invalid demo requests appear as errors.
8. Show the final ten-page report and summarize limitations: small historical dataset, no clinical validation, single VM and ephemeral monitoring history. Explain your own decisions and assistance disclosure.

Avoid passwords, tokens, private keys and unrelated personal content. Check recording playback and sharing permissions from a reviewer-accessible account. Add the recording link to docs/video-link.md and pass it to `make report VIDEO_URL='https://...'`.
