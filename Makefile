.DEFAULT_GOAL := help
PYTHON ?= python3.11
PY := .venv/bin/python
IMAGE ?= heart-disease-api:$(shell $(PY) scripts/image_tag.py)
API_URL ?= http://127.0.0.1:8000
export MPLCONFIGDIR := /tmp/mlops-matplotlib
export OMP_NUM_THREADS := 1
export OPENBLAS_NUM_THREADS := 1
export MLFLOW_DISABLE_AGENT_HINT := 1

.PHONY: help setup data eda train evaluate package lint unit integration test verify serve mlflow docker-build docker-smoke deploy-minikube smoke dashboard evidence report
help:
	@echo "setup -> data -> eda -> train -> package -> test -> docker-build -> docker-smoke -> deploy-minikube"
setup:
	$(PYTHON) -m venv .venv
	$(PY) -m pip install -r requirements-dev.txt
	$(PY) -m pip install --no-deps --no-build-isolation -e .
data:
	$(PY) -m heart_disease.data.prepare
eda: data
	$(PY) -m heart_disease.data.eda
train: eda
	$(PY) -m heart_disease.models.train
evaluate:
	$(PY) scripts/show_evaluation.py
package:
	$(PY) -m heart_disease.models.package
lint:
	.venv/bin/ruff check src tests scripts
	.venv/bin/ruff format --check src tests scripts
unit:
	$(PY) -m pytest tests/unit --junitxml=reports/evidence/unit-tests.xml
integration:
	$(PY) -m pytest tests/integration --junitxml=reports/evidence/integration-tests.xml
test: unit integration
verify: lint train package test
serve:
	.venv/bin/uvicorn heart_disease.api.main:app --host 127.0.0.1 --port 8000 --no-access-log
mlflow:
	.venv/bin/mlflow server --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1 --port 5000
docker-build: package
	docker build -t $(IMAGE) .
docker-smoke:
	$(PY) scripts/docker_smoke.py --image $(IMAGE)
deploy-minikube:
	bash scripts/deploy_minikube.sh $(IMAGE)
smoke:
	$(PY) scripts/smoke_api.py --url $(API_URL)
dashboard:
	$(PY) scripts/monitoring_dashboard.py
evidence:
	$(PY) scripts/collect_evidence.py
report:
	$(PY) scripts/build_final_report.py
