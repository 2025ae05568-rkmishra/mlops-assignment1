# Verified local environment

Python 3.11.17; Darwin arm64. Dependencies resolved in requirements.txt and requirements-dev.txt.

- numpy: 2.4.6
- pandas: 2.3.3
- scikit-learn: 1.9.1
- mlflow: 3.17.0
- fastapi: 0.143.0
- uvicorn: 0.54.0
- pytest: 9.1.1
- ruff: 0.17.0

Docker Desktop engine 29.7.2; Minikube 1.39.0; local Kubernetes 1.37.0. System Python 3.9 is not used for the project. The container base is Python 3.11.17 slim pinned to a multi-platform digest in Dockerfile. Prometheus 3.15.0 is digest-pinned. Architecture portability must be verified by actual container tests.
