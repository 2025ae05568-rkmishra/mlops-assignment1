# Implementation decisions

- 2026-10-11: User explicitly selected original UCI processed Cleveland and overrode the PDF feature-count wording. Use 13 predictors, original source category codes, binary target `int(num > 0)`.
- Python 3.11 is the design runtime. Use a repository-local virtual environment and checked-in resolved requirements; no project packages in the system Python.
- Train/test split 80/20, stratified, seed 42; five shared training-only CV folds. Selection uses CV ROC-AUC, with a 0.01 simplicity tie rule favoring Logistic Regression and a fixed 0.5 threshold.
- Local Minikube is the initial deployment target. No cloud resources will be provisioned without actual account and budget configuration.
- Retain the supplied design and assignment PDF unchanged except for documented implementation reconciliation in the design.

- 2026-10-18: The selected submission deployment is the external BITS Rocky Linux 9 AMD64 VM running Minikube/Traefik. GitHub Actions produces the verified release; private reviewer access uses the VM desktop or SSH forwarding to Traefik. GKE is outside the submission path. Final reports use a single captured BITS release; prior workstation evidence remains historical.
