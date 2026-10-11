# BITS Pilani AIMLCZG523 — MLOps Assignment 1
# Implementation Architecture and Design: Heart Disease Prediction

**Document version:** 1.3 • **Prepared / reconciled:** 11 October 2026 • **Status:** PDF-reconciled implementation specification with explicit user override selecting the actual Cleveland dataset schema

**Intended audience:** Individual student, implementation assistant, assignment reviewer.

**Purpose:** Provide a single implementation reference covering the data-to-deployment lifecycle, its engineering contracts, and the evidence required to demonstrate it. This is a design, not a claim that a model has been trained, a deployment has succeeded, or marks have been earned.

## 1. Source authority, scope, and reading instructions

### 1.1 Verified assignment source

The official `MLOps Assignment 1 Instructions.pdf` in this repository was inspected in full (three pages, including rendered pages) on 11 October 2026. Its SHA-256 is `10fc83cf093704b4c46fd02edaa2dea21236d075652ba0cd90ab255ccadf115a`. Page 1 specifies the dataset and tasks 1–4; page 2 specifies tasks 5–9 and submission deliverables; page 3 specifies production readiness and academic integrity.

The earlier conversation **Plan Assignment Deployment**, ID `6acba02e-5eb0-83ee-900b-d15ee30eff2e`, supplies implementation preferences only. It is not the authority for the assignment requirements.

The PDF explicitly requires a 10-page final report in DOC, DOCX or PDF format and a short video of the overall pipeline. It provides no exact video duration, deadline, timezone, naming convention, submission portal, or public-repository rule. Obtain any additional course instructions separately; do not invent them. The assignment expects independent work and demonstrated individual understanding (page 3).

Source precedence when implementation begins:

1. Explicit current user instructions, including the dataset override recorded in Section 6.1.
2. Official assignment PDF for coursework requirements not overridden by the user.
3. Retrieved conversation decisions, where not superseded.
4. Defaults and recommendations in this document.
5. Current official product documentation for syntax and service behavior.

If a conflict appears, update the requirements matrix and decision log; never silently reinterpret a mandatory requirement. The source requirements are verified; implementation compliance must still be demonstrated through actual artifacts and evidence. The PDF feature-count wording is explicitly overridden by the user in Section 6.1; retain that distinction in traceability rather than claiming literal compliance with that wording.

### 1.2 Requirement labels

- **[R] Verified requirement:** Confirmed against the official assignment PDF, with page references in Section 2.
- **[D] Decision:** Explicit current user direction or retained architecture decision.
- **[A] Assumption/default:** A concrete implementation choice made here because the accessible sources do not settle it.
- **[O] Optional:** Useful extension, not part of the minimum implementation.
- **[V] Verify:** Requires source, account, or runtime verification.

Unless marked [R] or [D], engineering details below are proposed defaults. Numeric performance targets are engineering goals, never observed measurements or guaranteed assignment thresholds.

### 1.3 Scope

Build a reproducible educational binary classifier for heart disease, compare at least two model families, track experiments, package the entire preprocessing-and-classifier pipeline, expose a validated REST API, test and automate releases, containerize, deploy on Kubernetes, and demonstrate monitoring and operational evidence.

This is an educational application using a public dataset. It must not claim clinical validation, diagnostic suitability, individual treatment guidance, or population-wide generalizability. No patient data collection, hospital integration, GPU training, feature store, service mesh, or automatic online learning is required.

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

## 3. Decisions and defaults

| Topic | Selected approach | Status and reason |
|---|---|---|
| Problem | Heart disease binary classification | [R] UCI Heart Disease classification mandated; exact source file not specified |
| Dataset | Original UCI processed Cleveland dataset, 13 predictors, target derived from `num` | [D] User-confirmed actual dataset schema; PDF feature-count wording explicitly overridden |
| Development | Python 3.11, virtual environment, package layout under `src/` | [A] Resolve compatible exact dependency versions once |
| Models | Logistic Regression and Random Forest plus DummyClassifier baseline | [D] First two recovered from conversation; dummy is [A] |
| Preprocessing | Scikit-learn Pipeline and ColumnTransformer | [D] Same fitted transformations at training and inference |
| Tracking/packaging | MLflow and full scikit-learn pipeline | [D] Export immutable serving bundle |
| API | FastAPI with Pydantic validation and Uvicorn | [D] JSON contract and generated OpenAPI |
| Testing/CI | Pytest, Ruff, GitHub Actions | [D] Automated verification and release evidence |
| Registry | Google Artifact Registry for GKE; GHCR or local images for fallback | [A] Registry selection must be explicit |
| Preferred deployment | GKE when usable credits and budget are confirmed | [D] Conditional, not assumed free |
| Fallback | Minikube, Traefik Ingress, controller LoadBalancer, `minikube tunnel` | [D] No cloud infrastructure charge; laptop/resources required |
| Public supplement | Render | [O] Useful public HTTPS URL; does not replace Kubernetes evidence |
| Alternative managed K8s | EKS | [O] Only if AWS is deliberately selected |
| Monitoring | Prometheus, JSON logs and an API metrics dashboard; Grafana optional | [D] Keep monitoring lightweight |
| Replicas | One during development; two for routing/rollout demonstration | [A] Both replicas on one node do not provide node fault tolerance |
| Infrastructure | Checked-in manifests with Kustomize overlays | [A] No Helm required for application |
| Training location | Local or GitHub Actions; not inside serving pods | [A] Small dataset does not require cloud training |

Do not pin “latest” in delivered dependencies or deployment images. Record tested Python, library, Docker, Minikube, Kubernetes, Traefik and cloud CLI versions in `docs/environment.md`. Resolve actual compatible versions during implementation; this design intentionally does not invent a tested lockfile.

## 4. Architecture and boundaries

### 4.1 Training and release architecture

```mermaid
flowchart LR
    A[Approved data source] --> B[Immutable raw snapshot and hash]
    B --> C[Schema checks and deterministic cleaning]
    C --> D[Fixed train and test partitions]
    D --> E[Train-only CV: preprocessing plus classifiers]
    E --> F[MLflow runs and selection evidence]
    F --> G[Refit selected pipeline on training partition]
    G --> H[One held-out evaluation]
    H --> I[Immutable model bundle]
    I --> J[Tests and Docker image]
    J --> K[Registry digest]
    K --> L[Kubernetes rollout and smoke test]
```

Cross-validation receives only the training partition. The held-out partition never supplies imputation values, scaling parameters, feature selection, hyperparameters, or decision thresholds. Release approval is separate from statistical evaluation: passing a release gate must not trigger repeated tuning on the same test set.

### 4.2 Local deployment

```text
Host client -> tunnel-reachable Traefik LoadBalancer service
            -> Traefik controller implementing Ingress rules
            -> heart-disease-api ClusterIP service -> ready API pods

Prometheus -> internal per-pod /metrics endpoints
API pods -> structured stdout logs
Local MLflow -> local tracking database and artifact directory
```

The Ingress object is configuration interpreted by the controller, not another running proxy. The app Service remains ClusterIP; expose the controller through LoadBalancer. A local tunnel endpoint is not a public Internet endpoint. Local operation depends on the laptop, container runtime, cluster and tunnel remaining active.

### 4.3 GKE deployment

```text
GitHub Actions -> tests/train/package -> Artifact Registry digest
               -> authenticated deployment job -> GKE Deployment

Client -> Google external Application Load Balancer
       -> GKE Ingress-managed backend/NEG -> ready API pods

Kubernetes Service defines the backend association.
Prometheus scrapes pods internally; logs are emitted to stdout.
```

Use native GKE Ingress for this overlay; do not deploy Traefik and a second external load balancer there by default. With container-native networking, traffic can reach pod endpoints through NEGs rather than traversing the ClusterIP virtual address. See [GKE Ingress guidance](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/load-balance-ingress).

### 4.4 Component ownership

| Component | Responsibility | Must not do |
|---|---|---|
| Data acquisition | Retrieve approved bytes; record provenance | Fetch a new unpinned dataset during inference |
| Validation/cleaning | Enforce schema and deterministic normalization | Fit statistical transformations globally |
| Training | Fit and compare candidate pipelines | Read held-out outcomes for selection |
| Packaging | Export selected pipeline plus manifest | Package an unfitted or unrelated estimator |
| API | Validate, load once, predict, report version | Train per request or silently fall back to another model |
| CI | Verify reproducibility and promote immutable outputs | Publish from untrusted pull requests |
| Deployment | Run the selected image and prove readiness | Pull mutable `latest` in a reproducible release |
| Monitoring | Measure service behavior | Claim prediction accuracy without labels |

## 5. Repository structure

```text
heart-disease-mlops/
├── README.md
├── pyproject.toml
├── requirements.in
├── requirements.txt                 # exact resolved runtime/training versions
├── requirements-dev.txt             # exact resolved testing/notebook versions
├── Makefile
├── .python-version
├── .env.example
├── .gitignore
├── .dockerignore
├── Dockerfile
├── compose.yaml                    # optional local API/Prometheus
├── configs/
│   ├── data.yaml
│   ├── training.yaml
│   └── logging.yaml
├── data/
│   ├── README.md
│   ├── raw/                        # immutable, ignored unless licensing allows commit
│   ├── processed/                  # commit cleaned.csv and its provenance; ignore other intermediates
│   └── manifests/                  # provenance, hashes, split policy
├── notebooks/01_eda.ipynb
├── src/heart_disease/
│   ├── __init__.py
│   ├── data/{acquire,validate,prepare,split}.py
│   ├── features/{schema,preprocessing}.py
│   ├── models/{train,evaluate,select,package}.py
│   ├── api/{main,schemas,service,metrics,logging}.py
│   └── common/{config,hashing}.py
├── tests/
│   ├── fixtures/
│   ├── unit/
│   ├── integration/
│   └── smoke/
├── artifacts/                      # generated model bundles; normally ignored
├── reports/
│   ├── figures/
│   ├── metrics/
│   └── evidence/                   # includes tracked screenshots/ subfolder
├── scripts/
│   ├── monitoring_dashboard.py
│   ├── smoke_api.py
│   ├── verify_bundle.py
│   ├── deploy_minikube.sh
│   ├── deploy_gke.sh
│   └── collect_evidence.sh
├── deploy/
│   ├── k8s/base/{kustomization,namespace,deployment,service,configmap}.yaml
│   ├── k8s/overlays/minikube/{kustomization,ingress}.yaml
│   ├── k8s/overlays/gke/{kustomization,ingress,backendconfig}.yaml
│   ├── monitoring/{prometheus,alerts}.yaml
│   ├── monitoring/dashboard.json
│   └── render/render.yaml
├── .github/workflows/{ci,release,deploy-gke}.yml
└── docs/
    ├── architecture.md
    ├── requirements-matrix.md
    ├── environment.md
    ├── data-card.md
    ├── model-card.md
    ├── api.md
    ├── deployment-minikube.md
    ├── deployment-gke.md
    ├── operations.md
    ├── decisions.md
    ├── report.md                    # editable report source
    ├── final-report.pdf             # required 10-page submission artifact
    ├── originality.md
    ├── submission-checklist.md
    ├── video-script.md
    └── video-link.md
```

Brace notation above denotes separate files, not literal filenames. All scripts run from the repository root, fail on errors, and accept explicit config paths. Business logic lives in importable modules; notebooks call those modules. Avoid parallel copies of preprocessing logic in notebooks and the API.

## 6. Data provenance, schema, cleaning, and leakage protection

### 6.1 Dataset choice and provenance

[D] Use original UCI processed Cleveland data as the selected implementation dataset. The UCI Heart Disease page documents the common 13-predictor classification task and original target conventions; the assignment names UCI Heart Disease but does not identify an exact source file. [UCI source](https://archive.ics.uci.edu/dataset/45/heart%2Bdisease).

[D] **Dataset decision, 11 October 2026:** The user instructed: “go ahead with the actual data set and ignore the pdf on this.” Use the original UCI `processed.cleveland.data` file with **13 predictors plus the original `num` target (14 total columns)**. Convert `num` to binary `target = int(num > 0)` for the cleaned CSV and modeling. The predictor list is `age`, `sex`, `cp`, `trestbps`, `chol`, `fbs`, `restecg`, `thalach`, `exang`, `oldpeak`, `slope`, `ca`, `thal`. The PDF's “14+ features” wording is explicitly overridden for this dataset choice. No additional predictors, substitute dataset or course clarification is required for this design. Preserve the original category codes in Section 6.2 and record this decision in `docs/decisions.md` during implementation. All other PDF requirements remain in scope.

Before acquisition, confirm the file, license and attribution requirements. Prefer the upstream dataset over an undocumented Kaggle re-export. Record source URL, retrieval UTC timestamp, exact filename, byte count, SHA-256, license, citation, parser version, and observed row/column counts in a manifest. The manifest must contain real values generated by acquisition, not placeholders presented as measurements.

Preserve raw bytes. Normalize into a separate processed artifact. Never silently mix Cleveland with other sites or enlarged/repeated versions. If a supplied CSV uses zero-based category encodings, document its mapping separately; do not apply the original UCI API contract unchanged.

### 6.2 Default raw and API feature schema

| Field | Meaning | Proposed accepted representation |
|---|---|---|
| `age` | Age in years | Integer, 1–120 |
| `sex` | Source sex code | Integer category 0 or 1; preserve source semantics |
| `cp` | Chest pain category | Original-source integer 1, 2, 3, 4 |
| `trestbps` | Resting blood pressure, mm Hg | Finite number, greater than 0 and at most 350 |
| `chol` | Serum cholesterol, mg/dL | Finite number, greater than 0 and at most 1000 |
| `fbs` | Fasting blood sugar over source threshold | Integer category 0 or 1 |
| `restecg` | Resting ECG category | Integer category 0, 1, 2 |
| `thalach` | Maximum heart rate achieved | Finite number, greater than 0 and at most 300 |
| `exang` | Exercise-induced angina code | Integer category 0 or 1 |
| `oldpeak` | Exercise ST depression relative to rest | Finite number, proposed range −10 to 20 |
| `slope` | Peak exercise ST segment slope code | Integer category 1, 2, 3 |
| `ca` | Major vessels colored by fluoroscopy | Integer category 0, 1, 2, 3, or explicit null |
| `thal` | Source test category: 3 normal, 6 fixed defect, 7 reversible defect | Integer category 3, 6, 7, or explicit null |
| `num` | Original disease target; training only | Integer 0–4; derive binary `target = int(num > 0)` |

These numeric bounds are permissive input sanity checks, not clinical reference ranges. Validate them against the approved source and document changes. Codes and field meanings must be confirmed from the chosen source data dictionary. Reject unexpected `ca=4`, `thal=0`, or `cp=0` under this contract rather than guessing that they mean missing or a different encoding.

### 6.3 Deterministic cleaning policy

1. Check expected raw column count before assigning names; ensure a headerless file is not accidentally interpreted as having a header.
2. Normalize whitespace and declared missing tokens such as `?` to null. Parse numeric fields explicitly and report conversion failures.
3. Reject/quarantine unknown categories, missing target, impossible target values and malformed rows. Emit a reason-count table. Do not silently turn parse errors into normal zeros.
4. Check missingness by feature. The default serving contract allows null only for `ca` and `thal`; if the approved dataset contains other missing features, revise training and serving contracts together.
5. Detect exact duplicate records. Keep one by deterministic source order and record removed counts. If identical feature vectors have conflicting labels, quarantine the entire conflicting group by a fixed policy and report it; do not choose the convenient label.
6. Exclude identifiers and target-derived fields from features. If patient identifiers exist, use them only for grouping/splitting, never as predictors.
7. Generate stable record/group identifiers from canonicalized source values for split auditing. Do not expose these in logs or the public API.
8. Write cleaning report, processed-data hash and source linkage. Do not modify raw data in place. Export and commit `data/processed/cleaned.csv` with named predictor columns and binary `target`, plus its provenance manifest and data dictionary. Include stable split/group metadata separately; fit statistical preprocessing only within training partitions. Keep other generated intermediates ignored. Confirm redistribution rights before committing; a license conflict must be resolved with a permitted source or course-approved alternative before submission.

Record zero removals when none occur. Never invent expected missingness or duplicate counts. Deterministic format checks may precede splitting; learned outlier thresholds and statistically estimated transformations may not.

### 6.4 Splitting and EDA

[A] Use a single stratified 80/20 train/test split, seed 42, after deterministic validation and duplicate handling. Persist split assignments with the dataset hash. If patient/site groups exist, use group-disjoint splitting and group-aware CV with class balance checks. Fail clearly when the dataset is too small for the requested folds.

Use five stratified shuffled folds, seed 42, within the training partition. Candidate models share the exact same folds. Persist fold assignments or reproducibly generate them from the saved split manifest.

Perform initial schema/count checks on the full source, but substantive target-driven EDA and design choices use the training partition. [R] Export labeled continuous-feature histograms, a correlation heatmap and a class-balance plot to `reports/figures/`, and include them in the notebook and report. Also produce missingness, categorical distributions and selected feature-target summaries. Specify heatmap columns and encoding semantics in its caption; do not infer causal relationships from correlations. Correlation among numeric codes is descriptive and does not imply causal or ordinal meaning. Label all plots with partition, sample count, units and data version. Do not inspect test performance repeatedly while changing the model.

### 6.5 Pipeline design

Continuous columns: `age`, `trestbps`, `chol`, `thalach`, `oldpeak`.

Categorical columns: `sex`, `cp`, `fbs`, `restecg`, `exang`, `slope`, `ca`, `thal`.

- Numeric pipeline: median imputation, then StandardScaler for Logistic Regression. Scaling may be omitted for Random Forest while preserving the same raw input schema.
- Categorical pipeline: most-frequent imputation, then one-hot encoding. Use explicit approved category lists and robust unknown handling internally; the external schema rejects unrecognized codes.
- Combine using ColumnTransformer, then the classifier in a single Pipeline.
- Fit that entire Pipeline inside cross-validation. No globally fit scaler, imputer, resampler, encoder, feature selector or dimensionality reduction.
- Avoid SMOTE by default. If later justified, place sampling inside each training fold using an appropriate pipeline and leave validation/test distributions untouched.

The central leakage safeguard is training transformations only on training data, including within each CV fold. See [scikit-learn pitfalls](https://scikit-learn.org/stable/common_pitfalls.html).

## 7. Model development and evaluation

### 7.1 Candidate search

| Candidate | Proposed bounded search | Purpose |
|---|---|---|
| DummyClassifier | `strategy="prior"` | Sanity baseline |
| Logistic Regression | `C` in 0.1, 1, 10; `class_weight` None or balanced; `max_iter=2000`; compatible solver | Interpretable linear baseline |
| Random Forest | `n_estimators=200`; `max_depth` None, 4, 8; `min_samples_leaf` 1, 3, 5; `class_weight` None or balanced | Nonlinear comparison |

Set random seeds explicitly and limit parallelism in CI. Record warnings, convergence failures and runtime. Do not expand the search only because the held-out score is disappointing.

[A] Primary selection metric: mean CV ROC-AUC from positive-class probabilities. Also report CV accuracy, precision, recall, F1 and ROC-AUC with mean and standard deviation; add PR-AUC/average precision for imbalance context. Define positive class as `num > 0`. Use `zero_division=0` for precision/F1 and record any degenerate cases. Accuracy alone is insufficient.

Choose the highest mean CV ROC-AUC. If candidates differ by at most 0.01, prefer Logistic Regression for simplicity; document this as a heuristic, not proof of statistical equivalence. Fix the decision rule in config before running comparisons. The default class threshold is 0.5. Any threshold tuning uses training-only out-of-fold predictions, is recorded, and precedes final test evaluation.

### 7.2 Final evaluation

Refit the selected complete pipeline on the full training partition. Evaluate once on the untouched test partition. Save metrics JSON, confusion matrix, ROC curve, precision-recall curve, prediction table keyed by private record identifier, and the selection rationale. Include sample counts and limitations caused by a small historical dataset. Optional bootstrap intervals require the resampling method and seed to be stated.

Never promise an accuracy level in advance. Candidate failure, baseline underperformance or unstable CV is a finding to explain, not a reason to fabricate successful metrics. Use model quality gates as release controls; if a gate fails, document the failure and revisit the experimental design without repeatedly optimizing against the held-out set.

### 7.3 MLflow tracking contract

Use one named experiment, `heart-disease-assignment-1`. Create a parent comparison run with candidate child runs, or one consistently structured run per candidate. Record parameters, CV metrics, artifacts and model lineage with MLflow. The tracking system supports parameter/metric/artifact history; the following exact run schema is this project's design. [MLflow tracking](https://mlflow.org/docs/latest/ml/tracking/).

[R] Apply this contract to every executed experiment run, including baseline, tuning configurations, selected model and reruns. Log each evaluated hyperparameter configuration as a run or child run; associate CV fold results and plots with that run. Failed runs retain available parameters, logs and a failure status rather than disappearing from the comparison.

Each run must include:

- Commit SHA, clean/dirty status, config hash, raw and processed dataset hashes, split manifest hash and seed.
- Candidate family, complete hyperparameters, preprocessing schema version and decision threshold.
- Fold metrics, aggregates, training duration and package versions.
- Figures, cleaning summary, feature names, CV search table and selection metadata.
- Model signature and representative non-sensitive input example.

[A] Local tracking uses an explicit SQLite database and filesystem artifact root, both ignored by Git. Bind its UI to localhost. CI stores run exports and the selected model bundle as workflow artifacts; an ephemeral runner's local database is not durable evidence unless uploaded. A remote MLflow server/registry is optional, not a serving dependency.

## 8. Packaging, versioning and reproducibility

Export the selected pipeline with `mlflow.sklearn.save_model(..., serialization_format="cloudpickle")` and use its sklearn loader for `predict_proba`. The tested MLflow 3.17 default skops export rejected a NumPy dtype; explicit CloudPickle is used only for the trusted, checksum-verified local bundle. The generic pyfunc prediction interface alone is not assumed to provide probabilities. A trusted joblib export may be supplied for diagnostics but is not a second source of truth.

Required bundle layout:

```text
artifacts/model/<model-version>/
├── model/                  # MLflow model directory and environment metadata
├── manifest.json
├── metrics.json
├── feature-schema.json
├── model-card.md
└── checksums.sha256
```

`manifest.json` includes model version, training commit, run ID, data/config/split hashes, model directory hash, class ordering, positive label, threshold, schema version, training timestamp and dependency versions. An example version format is `<commit-short>-<run-short>`; actual IDs are generated, not hand-written.

Load only trusted artifacts. Serialized Python models may execute code on load. Package verification must validate checksums, required files, expected feature schema and classifier class ordering before readiness. Read the positive-class probability by locating label `1` in `classes_`, not by assuming a column index.

Build the serving image from the verified bundle. The image includes the model so startup does not depend on a live MLflow server, external download, mutable registry alias or cloud credentials. The release manifest maps commit -> dataset hash -> MLflow run -> model hash -> image digest -> deployment evidence.

Reproducibility means identical inputs, split policy, environment and configuration can reconstruct the workflow; cross-platform floating-point results may differ slightly. Record measured differences and tolerances rather than claiming byte-for-byte reproducibility on every CPU architecture.

## 9. FastAPI contract

### 9.1 Endpoints

| Endpoint | Success behavior | Failure behavior |
|---|---|---|
| `GET /health` | 200, process liveness only | Do not tie liveness to external services |
| `GET /ready` | 200 after verified model load | 503 if model is unavailable or incompatible |
| `GET /version` | 200 with model/schema/code version | Do not expose secrets or local paths |
| `POST /predict` | 200, one prediction | 422 validation; 503 unready; sanitized 500 unexpected failure |
| `GET /metrics` | Prometheus exposition internally | Excluded from public routing |
| `GET /docs`, `/openapi.json` | Educational API documentation | Public exposure configurable |

[A] Single-record inference is mandatory for this design; batch inference is optional and must have a maximum batch size. Load the model once at application startup. Use a synchronous inference handler or a controlled threadpool so CPU work does not block the asynchronous event loop. Start with one Uvicorn worker per container and scale pods; Prometheus multi-worker aggregation is then unnecessary.

### 9.2 Request example

```json
{
  "age": 52,
  "sex": 1,
  "cp": 2,
  "trestbps": 128,
  "chol": 210,
  "fbs": 0,
  "restecg": 0,
  "thalach": 165,
  "exang": 0,
  "oldpeak": 0.8,
  "slope": 2,
  "ca": null,
  "thal": 3
}
```

This is a synthetic contract example, not a patient record or predicted result. All 13 keys are required, even where explicit null is allowed. Reject extra fields, missing keys, numeric strings, boolean substitutions for integer codes, NaN, Infinity and unknown category codes. Allow ordinary JSON integer values for continuous-number fields where appropriate. Pydantic validators must make coercion policy explicit.

### 9.3 Response contract

```text
request_id: string, generated or sanitized from a bounded incoming identifier
prediction: integer, 0 or 1
positive_class_probability: finite float in [0,1]
confidence: finite float in [0,1], probability assigned to the returned prediction
threshold: finite float in [0,1], default 0.5
model_version: nonempty string from the bundle
schema_version: string, default "1.0"
```

`prediction = int(positive_class_probability >= threshold)`. [R] Return both prediction and confidence: `confidence = positive_class_probability` for prediction 1, otherwise `1 - positive_class_probability`. Document and test both classes and threshold boundaries. With a tuned threshold, confidence need not exceed 0.5; it is the probability assigned to the returned class. The field is a model score/probability estimate, not a calibrated clinical risk unless calibration has been evaluated. Do not return a fabricated illustrative numeric prediction as evidence.

Validation responses identify invalid field names and safe error descriptions. Override default validation logging/serialization if it would echo raw health-feature values. Unexpected errors return a stable generic message and request ID; stack traces stay in restricted logs. Define a consistent error schema in OpenAPI and test it.

### 9.4 Input-to-model parity

Create a one-row DataFrame with canonical named columns. Never rely on JSON property order. Use the bundled fitted pipeline directly; do not hand-normalize inputs in the endpoint beyond schema parsing. Nulls become the same missing representation used during training. Response version must match the actual loaded artifact, not an unrelated environment variable.

## 10. Automated testing

| Layer | Required behavior to verify |
|---|---|
| Acquisition | Expected checksum accepted; changed or malformed source rejected |
| Cleaning | Missing tokens, categories, duplicates and conflicting labels handled deterministically |
| Split | No record/group overlap; seeded repeatability; both classes where required |
| Leakage | Training imputation/scaling statistics unaffected by extreme validation-only values |
| Pipeline | Unfitted access fails; full pipeline reload works; original feature schema enforced |
| Probability | Positive class selected by label; finite bounded output; threshold boundary and returned-class confidence correct |
| API | Valid request, reordered keys, null policy, extras/missing fields, invalid codes and types |
| Readiness | Missing/corrupt/wrong-schema model cannot become ready |
| Parity | In-process model and API probabilities agree within declared tolerance |
| Container | Fresh image starts as non-root; valid inference succeeds using packaged model |
| Deployment | Ingress request succeeds and identifies expected model; failed rollout is detected |
| Monitoring | Request counter advances; labels bounded; metrics scrape succeeds |

Use tiny synthetic fixtures for fast unit tests and a small fitted fixture pipeline for API tests. Release integration tests use the actual selected model. Do not make unit tests depend on public network availability. Separate slow training tests from fast tests, while ensuring release gates execute both.

[A] Target at least 80% coverage on core data/model/API modules as an engineering signal, not a PDF rubric threshold. Prioritize failure paths and leakage checks over tests that only mirror implementation. Run each test suite once per unchanged release stage; retry only when investigating a failure.

## 11. CI/CD design

### 11.1 Pull-request CI

Use a clean Python environment with locked dependencies. Run Ruff, unit tests, schema checks and fixture API tests. Render/validate Kubernetes manifests, and build a container with a fixture or approved artifact when needed. Upload test reports and coverage. Across PR, release and deployment workflows, every run must retain its commit/config identity, executed-step statuses and available logs/artifacts, including failures. Run artifact upload steps with `if: always()`; avoid publishing secrets and distinguish a skipped report from a passing check. Preserve lint output, test reports and training logs/metrics where that stage ran. Exercise an intentional failing check and confirm the workflow fails, downstream promotion is blocked and diagnostics remain accessible. Fork PRs receive no cloud credentials and do not deploy or push images.

### 11.2 Release pipeline

On a protected main-branch release or explicit workflow dispatch:

1. Check out an exact commit and install locked dependencies.
2. Acquire the approved dataset using the pinned manifest and verify its checksum. Use a controlled cached snapshot if upstream access is unavailable; never substitute another dataset silently.
3. Validate, clean, reproduce splits, compare models, track runs and package the selected pipeline.
4. Run actual-model integration/parity tests and package verification.
5. Export metrics, figures, MLflow evidence and the immutable model bundle.
6. Build one release image or a multi-architecture manifest from that bundle; smoke-test the architecture used for cloud serving.
7. Push to the registry using a commit tag and capture the immutable digest.
8. Deploy that exact digest to the selected environment.
9. Wait for rollout, verify readiness, issue a prediction through the external entry point and confirm model version.
10. Archive release identity, deployment output and monitoring evidence.

A failed stage prevents downstream promotion. Reuse artifacts between jobs by checksum. Do not retrain independently inside Docker or the deploy job: that could deploy a model different from the evaluated artifact.

### 11.3 Credentials and deployment trigger

For GKE, use GitHub OIDC with Google Workload Identity Federation and a narrowly scoped deploy identity. Restrict trust to the intended repository and protected ref/environment. Give the workflow only the permissions it needs; do not store a long-lived service-account JSON key as the default. [GitHub OIDC guide](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-google-cloud-platform).

Use protected environment deployment approval where appropriate to the account owner's workflow. Infrastructure creation and billing are separate deliberate actions; code generation does not imply permission to create chargeable resources. Once a deployment environment is authorized, routine releases should follow its documented process.

GitHub-hosted runners cannot directly access a laptop's private Minikube cluster. The fallback therefore has automated CI/build plus a scripted local deployment from the verified release artifact. State that boundary accurately. [O] A carefully secured self-hosted runner can automate local deployment, but do not install it solely to claim complete automation. The PDF requires an automated pipeline with lint, unit-test and model-training steps; this release workflow supplies them. It does not explicitly require automatic deployment into a laptop cluster. Include local deployment commands and evidence in the report.

### 11.4 Release protection and rollback

Pin third-party actions to reviewed commit SHAs, use least-privilege workflow tokens, serialize deployment jobs per environment and prevent untrusted artifact promotion. Store the previous deployment image digest. On failed smoke test, restore that digest and verify rollout; preserve failed evidence for diagnosis. Rolling back code must also roll back its baked-in model and schema.

## 12. Docker design

Use a slim, supported Python base pinned to a tested digest. Copy dependency metadata first for caching, install only needed serving packages, then copy application and verified model bundle. Training dependencies may be separated into a builder/training environment to reduce the runtime image.

Run as a non-root UID such as 10001. Listen on `0.0.0.0:8000`. Do not copy `.env`, cloud keys, raw datasets, notebooks, `.git`, MLflow databases or training caches into the image. Use stdout logging, a writable temporary directory where needed and a read-only model path. Include OCI labels for source commit and model version.

Set reasonable thread limits for BLAS/OpenMP and Random Forest inference so each pod respects its CPU limit. Kubernetes probes replace reliance on Docker HEALTHCHECK in cluster operation, although a container healthcheck may help local use.

The earlier conversation mentions a MacBook M4: treat ARM64 local compatibility as a design consideration, not a verified hardware inspection. Build native ARM64 locally; build/test AMD64 for typical GKE nodes, or publish both architectures through Buildx. Loading a local ARM64 image does not prove AMD64 compatibility.

Proposed commands after implementation:

```bash
make setup
make data
make train
make test
make package
make docker-build
make docker-smoke
```

These Make targets must be implemented; they are not commands already available in this document's output directory.

## 13. Kubernetes common manifest contract

Use namespace `mlops-assignment`. Label resources consistently with app, component, version and managed-by labels. The Deployment runs `heart-disease-api` on port 8000 and the Service exposes port 80. Base service type is ClusterIP.

[A] Initial per-pod request: 250m CPU and 256Mi memory; limit: 1 CPU and 512Mi. Measure actual model import/load and inference memory before finalizing; increase limits if justified. Use two replicas for the demonstration if capacity allows. Configure rolling updates with `maxUnavailable: 0`, `maxSurge: 1`; ensure surge capacity exists.

Use startup and readiness probes on `/ready`, liveness on `/health`. Suggested startup allowance: up to 120 seconds; readiness interval 5 seconds; liveness interval 10 seconds. Give graceful shutdown 30 seconds. Startup failure for a corrupt model must be visible, never converted into a ready dummy service.

Set `runAsNonRoot`, `allowPrivilegeEscalation: false`, dropped capabilities and read-only root filesystem where compatible. Mount a small `emptyDir` for required temporary writes. Disable automatic Kubernetes service-account token mounting for the API. Use ConfigMap for non-sensitive configuration and Secrets only for actual secrets; do not commit secret values.

Expose only `/predict`, `/health`, `/ready`, `/version`, and optionally `/docs` and `/openapi.json` in public Ingress rules. Use Exact paths where supported and appropriate. Keep `/metrics` accessible internally. A broad `/` rule would expose metrics unless explicitly blocked; do not accidentally use it in the final public manifest.

## 14. Minikube + Traefik + tunnel deployment runbook

### 14.1 Prerequisites and creation

Verify Docker/container runtime, Minikube, kubectl and available host resources. Record tool versions. Example resource allocation is 4 CPUs and 6 GB memory; reduce/increase based on the host without starving the OS.

```bash
minikube start -p mlops-assignment --driver=docker --cpus=4 --memory=6144
minikube -p mlops-assignment addons enable traefik
kubectl config use-context mlops-assignment
kubectl get nodes
kubectl get ingressclass
kubectl get svc -A
```

Use the installed Minikube release's documented Traefik addon and verify its actual controller namespace, Service name and IngressClass. Do not assume those names from an old screenshot. The official addon demonstrates a LoadBalancer Service. [Traefik addon](https://minikube.sigs.k8s.io/docs/handbook/addons/traefik/).

### 14.2 Image and manifests

Build the image for the local cluster architecture and load it:

```bash
minikube -p mlops-assignment image load heart-disease-api:local
kubectl apply -k deploy/k8s/overlays/minikube
kubectl -n mlops-assignment rollout status deployment/heart-disease-api --timeout=180s
kubectl -n mlops-assignment get pods,svc,ingress
```

The deploy script renders the local overlay with a tag derived from model version plus serving-source/dependency/Dockerfile hash and `imagePullPolicy: IfNotPresent` and an Ingress whose `ingressClassName` matches the installed Traefik class, with host `heart-disease.test`. Refresh the tag or use a unique commit tag between builds to prevent stale-image confusion.

### 14.3 Tunnel and host routing

Keep a separate terminal running:

```bash
minikube -p mlops-assignment tunnel
```

The tunnel may request administrator permission to create routes or bind privileged ports. Discover the controller Service's assigned external address with `kubectl get svc -A`. It may be localhost depending on driver/platform; do not hard-code that as a universal result. Minikube documents tunnel-based LoadBalancer access. [Accessing apps](https://minikube.sigs.k8s.io/docs/handbook/accessing/).

The implemented local controller Service exposes web on 8081 and websecure on 8443, preserving Traefik target ports. This allows its LoadBalancer service tunnel to bind unprivileged localhost ports. Minikube may independently attempt a privileged 80/443 tunnel for the Ingress object; use the working controller Service route on 8081. Install the addon only when absent; repeated Helm addon enable after patching Service ports can create duplicate-port upgrade errors. Set `INGRESS_IP` to the actual reachable address, then:

```bash
curl --fail-with-body -H 'Host: heart-disease.test' "http://${INGRESS_IP}:8081/ready"
curl --fail-with-body -H 'Host: heart-disease.test' \
  -H 'Content-Type: application/json' \
  --data-binary @tests/fixtures/valid_request.json \
  "http://${INGRESS_IP}:8081/predict"
```

For browser documentation, add a local hostname mapping only after verifying the actual IP, or use a client that supports explicit host resolution. Do not use the host header method to claim that public DNS has been configured.

### 14.4 Evidence and diagnosis

Capture node readiness, pod versions and readiness, two replicas where enabled, Deployment rollout, app ClusterIP, controller LoadBalancer external address, Ingress class/rules, active tunnel, and successful prediction through that Ingress. A port-forward-only request does not demonstrate Ingress.

If the external IP stays pending, inspect the controller Service type and tunnel output. If HTTP returns 404, inspect Host header and IngressClass. If 502/503, inspect endpoint readiness, ports and pod logs. If the image cannot execute, verify CPU architecture. Use port-forward only to isolate app problems, then return to testing the prescribed route.

Stop the cluster between sessions with `minikube stop -p mlops-assignment`; delete it after preserving evidence with `minikube delete -p mlops-assignment`. Stop the tunnel process as well.

## 15. GKE conditional preferred deployment

### 15.1 Eligibility and cost gate

GKE is preferred only when the owner confirms credits, billing status, quota and an acceptable budget. Otherwise complete Minikube first and use it as the final fallback. Do not postpone the coursework indefinitely to obtain cloud credits.

As checked on 11 October 2026, GKE lists a $0.10/hour cluster management fee and a $74.40 monthly credit per billing account for eligible Autopilot or zonal Standard management charges. This credit does not cover worker compute, networking or other resources. [GKE pricing](https://cloud.google.com/kubernetes-engine/pricing).

Google's eligible new-user trial lists $300 valid for 90 days. Availability depends on eligibility and account restrictions. An unupgraded trial stops when credits/time expire; upgrading enables billing for uncovered usage. Verify remaining credit and expiry in the actual account. [Google trial terms](https://docs.cloud.google.com/free/docs/free-cloud-features).

Budget alerts are notifications, not a guaranteed spending cap. Estimate compute, cluster fees after credits, load balancing, external addresses, disks, registry storage, logging/monitoring and egress. Set an owner-approved budget and alerts before provisioning; do not label the deployment “free forever.” Record creation time, planned teardown time and resource inventory.

### 15.2 Cluster default

[A] Start with a single-zone GKE Standard cluster, one small general-purpose node, no GPU and no autoscaling. A two-vCPU-class node with approximately 4 GB RAM is a starting capacity estimate, not a guaranteed fit. Measure allocatable resources after system pods, Prometheus and rollout surge. Two API pods on one node demonstrate pod replication but not high availability.

[A] Example region/zone: `asia-south1` / `asia-south1-a`, subject to pricing, quota and availability. Use a supported regular release channel and record the resolved Kubernetes version. Autopilot is a valid alternative if simpler operations or an actual estimate favors it; inspect admitted resource requests because minimums may change billable resources. Do not assume it is always cheaper.

### 15.3 One-time setup sequence

1. Select a dedicated project and confirm billing/credits and budget alerts.
2. Enable GKE and Artifact Registry APIs; enable identity/token exchange APIs required by the chosen OIDC configuration.
3. Create a regional Docker repository named `mlops` in Artifact Registry.
4. Create or select a least-privilege node identity able to pull that repository; do not rely on broad default project permissions.
5. Create the zonal VPC-native cluster with the approved node size and release channel. Record network, zone and resource names.
6. Configure GitHub federation and deployment IAM/RBAC scoped to the necessary resources.
7. Obtain cluster credentials and verify the active project/context before applying manifests.

Illustrative commands below require authorized cloud setup and substitution; they are a template, not executed steps:

```bash
export PROJECT_ID='replace-with-project-id'
export REGION='asia-south1'
export ZONE='asia-south1-a'
export CLUSTER='mlops-assignment'
gcloud config set project "$PROJECT_ID"
gcloud services enable container.googleapis.com artifactregistry.googleapis.com
gcloud artifacts repositories create mlops --repository-format=docker --location="$REGION"
# Create the cluster with the reviewed node identity/network settings, then:
gcloud container clusters get-credentials "$CLUSTER" --zone="$ZONE" --project="$PROJECT_ID"
kubectl config current-context
```

The implementation must provide a completed, validated cluster-create command or declarative configuration for the actual account. Do not invent a service-account email, network or billing account.

### 15.4 Image release and GKE overlay

Publish an AMD64-compatible image to `${REGION}-docker.pkg.dev/${PROJECT_ID}/mlops/heart-disease-api:<commit>` and deploy its resolved digest. Validate the model manifest before publishing.

GKE overlay requirements:

- Use native external GKE Ingress with the documented `kubernetes.io/ingress.class: gce` annotation; do not assume `ingressClassName: gce` is an equivalent substitute.
- Annotate the ClusterIP Service for Ingress NEGs using `cloud.google.com/neg: '{"ingress": true}'` where required.
- Associate a BackendConfig defining an HTTP health check on `/ready`, port 8000, and a suitable timeout.
- Route only the intended public endpoints; do not expose `/metrics` or Prometheus.
- Begin with an IP-based, synthetic-data-only demonstration if no domain is supplied. For an enduring public service, configure DNS and a managed TLS certificate, verify HTTPS, then redirect/disable plaintext HTTP appropriately.

Apply the overlay after injecting the exact image digest, wait for rollout and backend health, and inspect Ingress events/address. Load balancer readiness may lag pod readiness; poll with a bounded timeout and preserve diagnostic output on failure. Never present a pending address as a completed deployment.

```bash
kubectl apply -k deploy/k8s/overlays/gke
kubectl -n mlops-assignment rollout status deployment/heart-disease-api --timeout=300s
kubectl -n mlops-assignment get ingress
kubectl -n mlops-assignment describe ingress heart-disease-api
```

Run the same valid/invalid request and version checks through the actual external address. For host-based rules, use the corresponding hostname/Host header. Capture deployed digest, ready endpoints and actual API response.

### 15.5 Teardown and residual-resource audit

Export logs, release manifest, screenshots and monitoring evidence first. Delete the Ingress and wait for its managed networking resources to be removed before deleting the cluster. Then remove the dedicated cluster and any project-specific registry images, disks or reserved addresses that are no longer needed. Check forwarding rules, backend services, health checks, NEGs, disks, static IPs and registry storage for leftovers. Keep shared resources intact.

Deleting a namespace or scaling pods to zero does not guarantee that node or load-balancer charges stop. Confirm deletion in the project and inspect billing after its reporting delay. Retain an evidence copy of teardown, with sensitive account information redacted.

## 16. EKS comparison and optional Render

### 16.1 EKS

AWS EKS lists $0.10 per cluster-hour for standard Kubernetes support; extended support costs more. Worker compute and networking are additional. There is no equivalent recurring general-purpose free EKS control-plane allowance assumed in this design. [EKS pricing](https://aws.amazon.com/eks/pricing/).

AWS advertises up to $200 for eligible new customers, with $100 initially and additional credits earned, and a Free plan lasting up to six months. This is not confirmation that a particular account/plan can provision EKS or that all associated resources are covered. Verify service availability and credit terms before choosing it. [AWS Free Tier](https://aws.amazon.com/free/).

If EKS is selected, use ECR, an EKS cluster/node group, appropriate workload identity, AWS Load Balancer Controller and an ALB-backed Ingress. Adapt annotations and health checks; GKE's BackendConfig is not portable. Account for NAT gateways, ALBs, nodes, storage and retained resources in addition to the cluster. This is an alternate implementation path, not a requirement to build a second managed-cloud deployment.

### 16.2 Deployment decision table

| Option | Kubernetes evidence | Public access | Cost posture | Decision |
|---|---|---|---|---|
| Minikube + Traefik + tunnel | Yes | Host-local by default | No cloud bill; host resources used | Guaranteed design fallback |
| GKE | Yes | Managed external LB/Ingress | Credits conditional; otherwise billed | Preferred with confirmed budget |
| EKS | Yes | Controller-provisioned AWS LB | Promotional credits conditional; extra infrastructure charges | Alternate only |
| Render web service | Does not execute our K8s manifests | Managed public endpoint | Free plan subject to restrictions | Optional supplement |

### 16.3 Render runbook

Use the same verified model bundle and application revision. Configure a Docker web service or supported prebuilt-image flow, health check `/ready`, and listen on `0.0.0.0` at the assigned `PORT` (default 8000 locally). Keep secrets out of image layers. Record if Render rebuilds from Git rather than using the identical registry digest; do not claim digest parity without verifying it.

Render's free web services have usage limitations, spin down after inactivity and use an ephemeral filesystem. Keep the model baked into the image and do not use local files for durable tracking. Capture cold-start behavior honestly. [Render free services](https://render.com/docs/free).

Disable an independent auto-deploy path if it can deploy before required CI checks. Trigger promotion only after the approved build passes. Use synthetic demonstration requests, verify HTTPS and model version, and retain Minikube/GKE screenshots as the actual Kubernetes evidence.

## 17. Monitoring, logging and operations

### 17.1 Application metrics

Expose counters/histograms with low-cardinality labels:

- `http_requests_total{method,route,status}`.
- `http_request_duration_seconds_bucket{method,route,...}`.
- `model_predictions_total{predicted_class}`.
- `model_inference_duration_seconds_bucket`.
- `model_loaded` gauge, 1 only after successful verification.
- `model_info{model_version,schema_version}` gauge.

Use route templates, not arbitrary URLs, request IDs, feature values or exception text as labels. Count validation failures and unhandled errors. Exclude health/metrics traffic from prediction latency summaries.

### 17.2 Prometheus deployment

Deploy one small internal Prometheus instance or run it locally with explicit scrape access. In Kubernetes, discover annotated pods/endpoints and scrape each replica directly; scraping only a load-balanced Service may mix counters from different replicas. Provide required read-only discovery RBAC and a checked-in scrape configuration. A ServiceMonitor object works only when its operator is installed; do not add one without the operator.

Keep Prometheus private and use port-forward for its UI. [A] Short retention, such as 24 hours and a bounded storage size, is sufficient for the assignment; ephemeral storage is acceptable if evidence is exported before shutdown. Record that history is not durable.

Example queries, adjusted to actual implemented labels:

```promql
sum(rate(http_requests_total{route="/predict"}[5m]))
sum(rate(http_requests_total{status=~"5.."}[5m]))
histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket{route="/predict"}[5m])))
sum(model_loaded)
```

[R] Provide a checked-in API metrics dashboard definition (`deploy/monitoring/dashboard.json`) and a lightweight dashboard script (`scripts/monitoring_dashboard.py`) that queries Prometheus and displays request rate, error rate, p95 latency and model readiness in labeled panels. This is the chosen API metrics dashboard alternative to Prometheus + Grafana; raw exposition alone is insufficient evidence. Document startup, queries, time window and access instructions; keep it internal. Grafana may implement the same panels instead if chosen, with its exported dashboard checked in. Capture readable dashboard screenshots under `reports/evidence/screenshots/monitoring/` showing generated traffic, plus sanitized request logs.

Generate sufficient synthetic traffic before capturing graphs. A zero/empty rate immediately after startup is not a monitoring failure by itself. Prove the target is UP and request counters increase.

### 17.3 Structured logs

Each request log includes UTC timestamp, severity, request ID, method, route template, status, duration, model version and a sanitized error category when applicable. Never log raw request bodies, health-feature vectors, API keys, authorization headers or training rows. Document retention/access and redact account IDs/tokens in evidence.

[A] Initial operational goals: warmed single-record inference p95 under 500 ms under a modest documented test load; zero unexpected 5xx during smoke testing; startup within 120 seconds. These are targets to measure, not contractual production SLOs or observed results.

Model monitoring is limited to service behavior and optional aggregate input/prediction distribution checks. Accuracy/drift claims require suitable reference distributions and, for performance, real labels. No automatic retraining trigger is required.

## 18. Security and responsible operation

Use only public educational data and synthetic demo requests. Keep the README/model card explicit about limitations. Public demonstration endpoints should not accept real patient records.

Keep credentials in approved secret stores, use short-lived CI identity, restrict registry write rights, keep MLflow/Prometheus private, and scan dependencies/images before release. Pin inputs, verify model hashes and never load an artifact from an untrusted request URL. Apply request-size limits and bounded concurrency; configure rate limiting at the selected ingress/platform if the service is left public.

Disable permissive CORS unless a specific frontend needs it. TLS is required for a persistent public service. A brief HTTP-only cloud demonstration must be labeled as such and use only synthetic data. API-key authentication is optional for a short-lived public demo; if enabled, use a secret, exclude it from logs and document how the reviewer receives access securely. Health-check endpoints must remain usable by the load balancer.

Use dedicated cloud resources, least-privilege identities, a resource inventory and teardown ownership. Avoid exposing Kubernetes dashboards or cluster credentials in recordings. Test backup/recovery by rebuilding from the repository and immutable artifacts rather than depending on a developer's laptop state.

## 19. Documentation, report and video evidence

### 19.1 README minimum contents

Explain objective and educational limitations; source dataset and license; architecture; exact prerequisites; environment setup; acquisition/training/tracking commands; metrics generation; tests; Docker; Minikube and GKE alternatives; API examples; monitoring; troubleshooting; costs and teardown; and links to report/video/evidence.

A reviewer must be able to start from a clean checkout. Separate commands that create cost-bearing resources from local commands. Mark placeholders clearly and supply the actual release identifiers in final evidence.

### 19.2 Required 10-page final report [R]

PDF page 2 requires a 10-page final written report as DOC, DOCX or PDF. Deliver `docs/final-report.pdf` and retain `docs/report.md` as editable source. Markdown alone is not the final submission artifact. Use this structure and put longer implementation detail in the repository:

| Page | Suggested content |
|---|---|
| 1 | Problem, objectives, scope, architecture and compact setup/install instructions |
| 2 | Provenance, schema, cleaning and EDA |
| 3 | Feature engineering and leakage safeguards |
| 4 | Model comparison, CV and final metrics |
| 5 | MLflow and reproducibility |
| 6 | API and Docker |
| 7 | Tests and CI/CD |
| 8 | Kubernetes, Ingress and LoadBalancer |
| 9 | Monitoring, security and operational behavior |
| 10 | Limitations, conclusions, reproducibility links and references |

The PDF supplies no exclusions for title, references or appendices; count all pages and target exactly 10 total pages. Verify the exported PDF page count and render it for readability. Include setup/install instructions, EDA/modeling choices, experiment tracking summary, a rendered architecture diagram, CI/CD and deployment screenshots, and the repository link. Use readable captions identifying the release and the claim each screenshot supports. A report-source file or unrendered Mermaid code alone is insufficient final evidence.

### 19.3 Evidence inventory

| Evidence ID | Artifact | Required content |
|---|---|---|
| E01 | Data manifest/EDA | Committed cleaned CSV, hash, source, counts, cleaning decisions, histograms, correlation heatmap and class-balance plot |
| E02 | Model comparison | At least two model families, shared CV, metrics and selected model |
| E03 | MLflow | Run parameters, metrics and artifacts linked to commit/data |
| E04 | Package verification | Fresh reload/parity test and environment identity |
| E05 | CI | Lint/unit-test/training stages, per-run artifacts/logs, release IDs and retained failing-check diagnostics |
| E06 | API/Docker | Image identity, valid inference and invalid-request behavior |
| E07 | Kubernetes | Nodes, pods, Deployment, Service, Ingress/controller and external route |
| E08 | Monitoring | UP scrape target, API metrics dashboard screenshots under traffic and sanitized request logs |
| E09 | Submission | README, 10-page final PDF, repository/access/video links, originality record and deliverable checklist |
| E10 | Operations | Rollback or restart evidence plus cloud teardown where applicable |

Store an evidence index with capture time, environment, commit, model version, image digest, command/action, filename and rubric mapping. Screenshots from different versions must be labeled. No fabricated terminal output, successful test counts, model scores, URLs or cloud balances.

### 19.4 Demonstration video plan

[R] Submit a short recording of the overall pipeline; this PDF gives no exact duration. Keep the recording concise and ensure it demonstrates the full sequence: identify repository/release; show data provenance and EDA; compare models in MLflow; show CI and package identity; inspect Docker/Kubernetes; call `/predict` through Ingress; send invalid input; show monitoring and logs; explain fallback/cost controls and limitations.

Record a real working deployment. Show successful requests after the actual rollout; narrated design alone is not deployment evidence. Do not claim traffic hit both replicas solely because two pods exist. If demonstrating distribution, correlate repeated request IDs with pod logs without logging feature values. Verify video/report/repository permissions from a reviewer-like session before submission.

### 19.5 Concrete submission manifest [R]

| PDF page 2 deliverable | Repository path or submission reference | Acceptance |
|---|---|---|
| Code and Dockerfile(s) | `src/`, `Dockerfile` | Importable implementation; isolated local build/run proof |
| Requirements/environment | `requirements.txt`, `requirements-dev.txt` | Clean setup executes all scripts with documented runtime/dev installation |
| Cleaned dataset and acquisition | `data/processed/cleaned.csv`, `data/manifests/`, `data/README.md`, `src/heart_disease/data/acquire.py` | Tracked cleaned CSV, permitted redistribution, checksum and reproducible download instructions |
| EDA, training and inference notebooks/scripts | `notebooks/01_eda.ipynb`, `src/heart_disease/models/train.py`, `scripts/smoke_api.py` | Document runnable entry points and outputs for each |
| Unit-test folder | `tests/unit/` | Data/model unit tests; `tests/` serves the PDF's test-folder requirement |
| CI workflow | `.github/workflows/ci.yml`, `release.yml` | Automated lint, unit tests and training; every run retains logs/artifacts |
| Deployment definitions | `deploy/k8s/` | Valid manifests and verified LoadBalancer/Ingress route |
| Screenshot folder | `reports/evidence/screenshots/` | Readable EDA/tracking/CI/Docker/deployment/dashboard evidence |
| Final written report | `docs/final-report.pdf` | Exactly 10 readable pages with required content and repository link |
| API URL or local access instructions | `README.md`, `docs/deployment-minikube.md` or `docs/deployment-gke.md` | Actual public URL if deployed publicly; otherwise tested cluster/tunnel/host/curl instructions |
| Short overall-pipeline video | `docs/video-link.md` | Accessible recording link or submitted video file, tied to release identity |

Maintain `docs/submission-checklist.md` with actual paths/URLs, release identity, reviewer access checks and PDF requirement IDs. Refer to repository-relative workflow paths under `.github/workflows/` for both YAML files. Do not check off planned or nonexistent artifacts.

### 19.6 Independent work and originality [R]

PDF page 3 expects independent completion and individual understanding. Do not directly copy another student's or online source's code, notebook, visualizations, feature engineering, workflow, deployment configuration or overall pipeline. Similar implementations may trigger academic integrity review. Personalize experimentation, design decisions, monitoring and documentation through the student's own justified choices, rather than cosmetic renaming.

Maintain `docs/originality.md` describing personal experiments, alternatives considered, reasons for the chosen approach, references and any assistance used in accordance with applicable course rules. References and attribution support transparency but do not override the prohibition on direct copying. The student must review and understand every delivered component and explain preprocessing, model selection, CI failure behavior, routing and monitoring in the demonstration. This specification is a planning aid; completion and understanding require actual work and evidence.

## 20. Acceptance criteria and completion gates

### Gate A — Source and data

- [x] PDF inspected and rubric/submission requirements reconciled in this specification.
- [x] User selected original UCI processed Cleveland: 13 predictors, binary target derived from `num`; PDF feature-count wording overridden.
- [ ] Acquired source and cleaned CSV match the selected schema and target conversion.
- [ ] Approved dataset/license confirmed and source manifest contains real hashes.
- [ ] Data dictionary matches both parser and API codes.
- [ ] Cleaning report accounts for every removed/quarantined record.
- [ ] Cleaned CSV and provenance are committed with permitted redistribution.
- [ ] Histograms, correlation heatmap and class-balance plots are exported and included in the report.
- [ ] Train/test and CV partitions are deterministic and disjoint by required group.

### Gate B — Modeling and packaging

- [ ] At least Logistic Regression and Random Forest compared on identical CV folds.
- [ ] All learned preprocessing fit inside folds; leakage regression tests pass.
- [ ] Selection metric, tie rule and threshold recorded before final evaluation.
- [ ] Every experiment run has parameters, metrics, artifacts and plots, with retained failure diagnostics where applicable.
- [ ] Final held-out results are actual measured outputs, with limitations.
- [ ] Complete pipeline reloads in a clean environment and matches API predictions.

### Gate C — Software and release

- [ ] API enforces the documented request/error contract and reports actual model version.
- [ ] Ruff and meaningful automated tests pass; failures block release.
- [ ] Automated workflow includes lint, data/model unit tests and model training; each run retains logs/artifacts even on failure.
- [ ] /predict returns JSON prediction and documented returned-class confidence; both classes are verified.
- [ ] Container runs without developer-local files or training on startup.
- [ ] Model, code, data and image identities are linked by a release manifest.
- [ ] Actual target architecture image is smoke-tested; AMD64 verification is required when deploying to AMD64 cloud nodes.

### Gate D — Deployment and operations

- [ ] At least one complete Kubernetes target works: Minikube or GKE.
- [ ] Ingress/LoadBalancer external request reaches the expected model.
- [ ] Probes, resource settings and failed-rollout behavior verified.
- [ ] Prometheus scrapes real API replicas; requests produce metrics/logs and a demonstrated API metrics dashboard with screenshots.
- [ ] Cloud costs/credits and teardown are documented if cloud is used.
- [ ] Render, if included, is described as supplemental evidence.

### Gate E — Submission

- [ ] Each 50-mark rubric area maps to implementation and actual evidence.
- [ ] README works from a clean checkout.
- [ ] Final PDF contains exactly 10 readable pages and all required report content; short overall-pipeline video is accessible.
- [ ] Every Section 19.5 deliverable exists and is recorded in the submission checklist.
- [ ] Originality record is complete and the student can explain the implementation independently.
- [ ] Repository/video links are accessible to the intended reviewer.
- [ ] No secrets, fabricated measurements or unsupported clinical claims appear.

Do not mark the assignment complete until all implementation/submission gates pass under the recorded user dataset decision. Source reconciliation alone does not establish implementation success or guarantee marks.

## 21. Staged instructions for Codex

### Stage 0 — Reconcile inputs and initialize

Use the verified PDF requirements in Section 2 and the source hash in Section 1. Recheck if the PDF changes; retain the explicit user dataset override and implement the Cleveland schema in Section 6. Inspect existing repository contents and preserve user work. Confirm dataset source and choose local-first development. Create the project skeleton, decision log and environment setup. Do not create cloud resources merely to initialize the repository.

**Exit:** Requirements matrix with unresolved items identified; deterministic config files; installable package scaffold.

### Stage 1 — Build data foundation

Implement acquisition, checksum verification, parser, validation, deterministic cleaning and split manifests. Write tests for malformed data, category encodings, missing values, duplicates and overlap. Build the EDA notebook from shared functions and export figures.

**Exit:** Reproducible data command, committed cleaned CSV and provenance, required EDA plots, accepted schema and leakage-safe split.

### Stage 2 — Train and track

Implement preprocessing pipelines, shared CV, bounded candidate search, MLflow logging, selection rule and final held-out evaluation. Add the dummy baseline, model card and real comparison tables. Keep test outcomes out of tuning logic.

**Exit:** Traceable model comparison and an explicitly selected model with actual metrics.

### Stage 3 — Package and serve

Export the complete selected model, manifest and checksums. Implement FastAPI lifecycle, schemas, probability mapping, errors, health/readiness/version and metrics. Test actual-model inference parity and startup failure behavior.

**Exit:** Validated API serving the exact packaged model without an MLflow server dependency.

### Stage 4 — Containerize and automate

Implement Dockerfile, ignore rules, test commands and CI. Build on the intended architectures. Add release artifact transfer, registry publication and deployment trigger separation. Record image digests and ensure failure gates work.

**Exit:** Clean checkout can test/build; release cannot bypass required checks.

### Stage 5 — Prove local Kubernetes

Implement base manifests and Minikube overlay. Enable/verify Traefik, expose its controller through LoadBalancer/tunnel, and test requests via Ingress. Add Prometheus, the API metrics dashboard and request logging; capture traffic graphs and sanitized logs. Keep the local path documented even when cloud is selected.

**Exit:** Fully demonstrated no-cloud fallback with collected evidence.

### Stage 6 — Conditional GKE

Proceed only after account/credit/budget and deployment authorization are established. Complete actual infrastructure parameters, least-privilege identity, Artifact Registry, GKE overlay and native Ingress. Deploy the already verified release, confirm routing/health and capture evidence. If credits/quota/setup fail, retain Minikube as the completed target and explain the limitation.

**Exit:** Verified GKE deployment or explicitly documented fallback; no unfinished cloud resources left unnoticed.

### Stage 7 — Documentation and submission assembly

Generate report sections from actual artifacts, export and visually verify the 10-page final PDF, record the demonstration, audit every rubric/deliverable row and verify all links. Include the cleaned CSV, dashboard screenshots and originality record. Capture operational and teardown evidence. Ensure the final report does not present architectural intentions as completed work.

**Exit:** All verified acceptance gates pass, with a final list of limitations and measured results.

### Implementation-agent operating rules

Implement the smallest coherent stage, run its meaningful checks, and update the progress log before moving on. Use this document's defaults unless an official requirement or explicit user decision supersedes them. Ask only for genuinely unavailable facts or authorization for external/cost-bearing actions; continue independent local work meanwhile. Never invent an account identifier, observed score, dataset count or deployment success. Update this specification when implementation choices change so it remains the single reference.

## 22. Unresolved decisions and explicit defaults

| Open question | Default until resolved | Blocking scope |
|---|---|---|
| Official PDF source | Verified repository PDF; hash and pages recorded in Section 1 | Recheck only if source changes |
| Dataset file and feature count | Resolved by user: processed.cleveland.data; 13 predictors plus num, converted to binary target | Source acquisition/schema verification only |
| Existing repository/student details? | Use this repository; independent student submission; no invented contributors | Remote access and student attribution |
| Exact Python/library versions? | Python 3.11; resolve and lock compatible releases | Reproducible executable environment |
| GCP account, credits, quota and budget? | Minikube until confirmed | GKE provisioning |
| GKE mode and region? | One zonal Standard cluster; asia-south1 candidate | Account-specific cloud configuration |
| Registry visibility/access? | Private Artifact Registry for GKE; local image for fallback | Image publication/pull authentication |
| Domain and TLS? | Local `.test` host; synthetic-only short cloud IP demo | Persistent public service |
| Model quality threshold? | Report measured quality; no invented pass score | Any additional quality-based promotion rule |
| Public API authentication? | No real data; short-lived demo; optional key when left public | Persistent exposure policy |
| Report/video/deadline? | 10-page DOC/DOCX/PDF confirmed; PDF selected; short video with no exact duration; deadline unspecified | Obtain additional course instructions if applicable |
| Local deployment automation? | Automated lint/tests/training + scripted Minikube deployment; automatic laptop CD not explicitly required | Verify documented access and deployment evidence |
| Library upload capability? | Deliver downloadable Markdown in this chat's outputs | Claiming separate Library persistence |

## 23. Risks and mitigations

| Risk | Mitigation |
|---|---|
| PDF wording differs from selected dataset | Explicit user override recorded in Section 6.1; report actual 13-predictor schema accurately |
| Dataset re-export changes encodings or duplicates | Pin original bytes and enforce explicit schema |
| Inflated scores from preprocessing leakage | Fit full pipelines within folds; test disjointness/statistics |
| Small sample size creates unstable metrics | Report CV spread and held-out limitations honestly |
| Training-serving skew | One fitted pipeline and actual-model parity tests |
| Container architecture mismatch | Test native local and cloud target architectures |
| Cloud credits do not apply or expire | Complete local fallback first; budget/expiry check and teardown |
| Ingress health checks fail despite ready pods | Explicit health-check path/port and backend diagnostics |
| Local tunnel mistaken for public endpoint | Label accessibility accurately; optional public supplement |
| CI artifacts disappear before grading | Export durable release/evidence copies with identities |
| Public logs leak health inputs | No body logging, sanitized errors and screenshots |
| Cloud deletion leaves billable resources | Explicit residual-resource inventory and billing review |

## 24. Official references and verification record

External product facts were checked against the following official pages on 11 October 2026. Product behavior, pricing and eligibility can change; recheck the relevant page before provisioning. Architecture prescriptions are this document's proposed implementation, not claims that these sources require the whole design.

1. [Referenced conversation: Plan Assignment Deployment](chatgpt-conversation://6acba02e-5eb0-83ee-900b-d15ee30eff2e) — retained implementation preferences; rubric superseded by verified PDF.
2. Official `MLOps Assignment 1 Instructions.pdf` — verified three-page repository source; SHA-256 recorded in Section 1; rubric pages 1–2, readiness/integrity page 3.
3. [UCI Heart Disease](https://archive.ics.uci.edu/dataset/45/heart%2Bdisease) — proposed source and data dictionary.
4. [Scikit-learn common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html) — preprocessing consistency and leakage.
5. [MLflow experiment tracking](https://mlflow.org/docs/latest/ml/tracking/) — tracking concepts.
6. [Minikube Traefik addon](https://minikube.sigs.k8s.io/docs/handbook/addons/traefik/) — controller installation and service exposure.
7. [Minikube application access](https://minikube.sigs.k8s.io/docs/handbook/accessing/) — local LoadBalancer tunnel.
8. [GKE Ingress configuration](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/load-balance-ingress) — native load-balancer integration.
9. [GKE pricing](https://cloud.google.com/kubernetes-engine/pricing) — management credit and separate compute costs.
10. [Google Cloud trial](https://docs.cloud.google.com/free/docs/free-cloud-features) — eligibility, credit duration and billing behavior.
11. [AWS EKS pricing](https://aws.amazon.com/eks/pricing/) — cluster/support charges.
12. [AWS Free Tier](https://aws.amazon.com/free/) — promotional credit/plan terms.
13. [Render free services](https://render.com/docs/free) — restrictions and service behavior.
14. [GitHub OIDC for Google Cloud](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-google-cloud-platform) — short-lived workflow identity.

## Appendix A. Proposed command interface

The implementation must make these commands real, document their outputs, and return nonzero on failure:

| Target | Contract |
|---|---|
| `make setup` | Create/install locked development environment |
| `make data` | Acquire/verify/clean/split with manifest outputs |
| `make eda` | Generate reproducible training-partition EDA |
| `make train` | Compare candidates and track runs |
| `make evaluate` | Evaluate only an explicitly selected bundle/split under the final-evaluation policy |
| `make package` | Export and verify selected complete pipeline |
| `make lint` | Ruff checks |
| `make test` | Unit and required integration suites |
| `make serve` | Run API with explicit bundle path |
| `make docker-build` | Build tagged image from verified bundle |
| `make docker-smoke` | Run container and validate inference/readiness |
| `make deploy-minikube` | Apply local manifests to verified context |
| `make smoke` | Verify selected deployment endpoint/version |
| `make evidence` | Collect sanitized release and runtime evidence |

Do not make `make train` repeatedly consume the test set during experimentation. Track final-evaluation identity so later reruns on unchanged artifacts are reported as reproducibility checks, not independent new validation.

## Appendix B. Clean handoff instruction

> Implement the BITS Pilani AIMLCZG523 MLOps Assignment 1 project according to this architecture document. Use the verified assignment PDF and requirements matrix with the explicit user override: original UCI processed Cleveland, 13 predictors, binary target derived from num. Ignore the PDF feature-count wording for this dataset decision. Do not invent unstated requirements. Use its explicit defaults for independent engineering work. Build and verify the project in the staged order, preserve data/model/image lineage, and collect real evidence for every rubric category. Prefer GKE only after credits, budget and authorization are confirmed; otherwise complete Minikube with Traefik Ingress and a tunnel-backed LoadBalancer. Keep Render optional. Never report proposed metrics or deployment output as observed results. Maintain this specification, the decision log and acceptance checklist as implementation proceeds.


## 25. Implementation reconciliation record — 11 October 2026

The repository now implements local-first Stages 0–5. Actual evidence and remaining work are tracked in `docs/progress.md` and `docs/submission-checklist.md`; this specification does not mark remote CI or final submission complete.

- Python 3.11.17 and Minikube 1.39.0 installed; runtime/dev versions locked and checked.
- Original Cleveland source downloaded and pinned; 303 cleaned rows, 242/61 train/test split, required training-only EDA plots and notebook generated.
- 25 candidate configurations compared in MLflow. Selected Logistic Regression C=0.1 with balanced class weights; mean CV ROC-AUC 0.9110; measured 61-row held-out accuracy 0.8852 and ROC-AUC 0.9654. Packaging retry reproduced fixed experiments without tuning against the test set.
- Full model bundle verified; 19 unit and 2 selected-model integration tests pass, including leakage, source checksum, input validation, returned-class confidence, API parity and corrupt-bundle failure. API errors use the documented OpenAPI schema; inference threadpool is bounded to four slots.
- Non-root read-only ARM64 Docker serving verified. Immutable local image tags tie the selected model to serving inputs; training code identity remains in the model manifest. Default Uvicorn access logging is disabled; sanitized structured logs remain enabled.
- Two Minikube API replicas and internal Prometheus deployed; actual inference through Traefik controller LoadBalancer/Ingress verified on localhost port 8081; both scrape targets UP and metrics blocked at public Ingress. Dashboard and selected MLflow run screenshots retained.
- CI and release YAML authored with pinned actions and failure artifact retention. Local pipefail failure semantics verified. GitHub origin exists, but this checkout has no commits and remote workflow execution has not been claimed.
- Student review/originality explanation, GitHub commit/push and remote CI evidence, final 10-page PDF and video remain submission-stage work. GKE remains conditional and unprovisioned.
