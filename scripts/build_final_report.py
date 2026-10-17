"""Build the ten-page assignment report from verified CI and local evidence.
Run with the bundled document Python runtime (ReportLab and Pillow).
"""

import csv
import json
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Flowable,
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/pdf/2025ae05568-mlops-final-report.pdf"
CI = ROOT / "tmp/pdfs/ci-artifact"
V = json.loads((ROOT / "reports/evidence/final-verification.json").read_text())
M = json.loads((CI / "reports/metrics/final.json").read_text())
C = V["ci_manifest"]
L = V["local_manifest"]
rows = list(csv.DictReader((CI / "reports/metrics/cv-comparison.csv").open()))
rf = max(
    (r for r in rows if r["family"] == "random_forest"), key=lambda r: float(r["mean_roc_auc"])
)
styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="BodyX",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        spaceAfter=8,
        textColor=colors.HexColor("#243448"),
    )
)
styles.add(
    ParagraphStyle(
        name="SmallX",
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        spaceAfter=6,
        textColor=colors.HexColor("#475569"),
    )
)
styles.add(
    ParagraphStyle(
        name="TitleX",
        fontName="Helvetica-Bold",
        fontSize=28,
        leading=32,
        spaceAfter=18,
        textColor=colors.HexColor("#102a43"),
    )
)
styles.add(
    ParagraphStyle(
        name="HeadX",
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        spaceAfter=12,
        textColor=colors.HexColor("#102a43"),
    )
)
styles.add(
    ParagraphStyle(
        name="SubX",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        spaceBefore=7,
        spaceAfter=6,
        textColor=colors.HexColor("#167d8d"),
    )
)
styles.add(ParagraphStyle(name="CellX", fontName="Helvetica", fontSize=9, leading=12))
story = []


def p(s, style="BodyX"):
    story.append(Paragraph(s, styles[style]))


def h(s):
    p(s, "SubX")


def page(n, title):
    if n > 1:
        story.append(PageBreak())
    p(f"{n:02d} / MLOps Assignment 1", "SmallX")
    p(title, "HeadX")


def table(data, widths):
    cells = [[Paragraph(escape(str(c)), styles["CellX"]) for c in row] for row in data]
    t = Table(cells, colWidths=widths, hAlign="LEFT")
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e4f1f3")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.HexColor("#167d8d")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f8fb")]),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 9))


def image(path, maxh, caption, width=499):
    path = ROOT / path
    w, ht = PILImage.open(path).size
    scale = min(width / w, maxh / ht)
    story.append(Image(str(path), width=w * scale, height=ht * scale, hAlign="CENTER"))
    p(caption, "SmallX")


class Architecture(Flowable):
    def __init__(self):
        super().__init__()
        self.width = 499
        self.height = 215

    def draw(self):
        c = self.canv
        labels = [
            (0, 155, "UCI Cleveland", "Pinned raw checksum"),
            (172, 155, "Data validation", "CSV + split manifests"),
            (344, 155, "CV and MLflow", "25 configs; train only"),
            (344, 78, "Verified model bundle", "Preprocessing + classifier"),
            (172, 78, "Docker / FastAPI", "Strict schema + confidence"),
            (0, 78, "Minikube / Traefik", "Ingress -> two API replicas"),
            (0, 0, "Synthetic client", "Valid and invalid requests"),
            (172, 0, "Prometheus", "Private per-pod scrape"),
            (344, 0, "Local dashboard", "Four operational panels"),
        ]
        for x, y, title, sub in labels:
            c.setFillColor(colors.HexColor("#eef6f8"))
            c.setStrokeColor(colors.HexColor("#167d8d"))
            c.roundRect(x, y, 155, 53, 6, fill=1)
            c.setFillColor(colors.HexColor("#102a43"))
            c.setFont("Helvetica-Bold", 9)
            c.drawCentredString(x + 77, y + 32, title)
            c.setFont("Helvetica", 8)
            c.drawCentredString(x + 77, y + 15, sub)
        c.setStrokeColor(colors.HexColor("#167d8d"))
        for x1, y1, x2, y2 in [
            (155, 182, 172, 182),
            (327, 182, 344, 182),
            (421, 155, 421, 131),
            (344, 105, 327, 105),
            (172, 105, 155, 105),
            (77, 53, 77, 78),
            (249, 78, 249, 53),
            (327, 27, 344, 27),
        ]:
            c.line(x1, y1, x2, y2)


page(1, "Reproducible heart disease classification")
p("From source data to monitored inference", "TitleX")
p(
    "<b>BITS AIMLCZG523 - MLOps Assignment 1</b><br/>Student ID: 2025AE05568<br/>Prepared: 12 October 2026 (India Standard Time)"
)
h("Project outcome")
p(
    "This implementation turns the original UCI processed Cleveland dataset into a reproducible educational classification service. A checksummed dataset, persisted split, training-only cross-validation, MLflow experiment records, complete serving pipeline, CI checks and a monitored local Kubernetes deployment form one traceable workflow."
)
table(
    [
        ["Verified measure", "Result"],
        ["Dataset / partition", "303 rows; 242 training and 61 held out"],
        ["Selected classifier", "Logistic Regression; C=0.1; balanced class weights"],
        ["Selected mean CV ROC-AUC", "0.9110 (standard deviation 0.0305)"],
        ["Held-out accuracy / ROC-AUC", "0.8852 / 0.9654"],
        ["Automated verification", "19 unit tests + 2 integration tests; GitHub CI successful"],
        ["Live serving", "2 ready API replicas; valid prediction and invalid-input rejection"],
    ],
    [195, 304],
)
h("Scope and evidence boundary")
p(
    "The approved source schema contains 13 predictors and a binary target derived from num &gt; 0. Deployment uses Minikube and Traefik on the local workstation. Cloud provisioning was not selected. CI independently rebuilds and tests an AMD64 image; the local ARM64 deployment uses its own verified model bundle."
)
p(
    "The demonstration video has not yet been recorded, as confirmed by the student. This report documents completed technical work; recording and student review remain final submission tasks. The model has no clinical validation.",
    "SmallX",
)
p(
    '<b>Repository:</b> <link href="https://github.com/rmishra3261/2025ae05568-mlops" color="#167d8d">github.com/rmishra3261/2025ae05568-mlops</link><br/><b>Verified commit:</b> e1710cb008e52dac1c6916fd325be4eb06c06821',
    "SmallX",
)

page(2, "Architecture and reproducibility contract")
story.append(Architecture())
p(
    "Figure 1. Implemented data, training, serving and monitoring path. GitHub Actions automates the data-to-container verification path; local deployment loads the built image into Minikube.",
    "SmallX",
)
h("One bundle across training and serving")
p(
    "The saved scikit-learn pipeline contains the fitted imputers, category encoder, numeric scaler and classifier. FastAPI loads it once at startup rather than reproducing preprocessing in request handlers. A manifest records source, cleaned data, split, configuration, code and model hashes plus class order and threshold. Checksums are verified before trusted CloudPickle deserialization; a damaged or incompatible bundle never becomes ready."
)
h("Persistent evidence and controlled promotion")
p(
    "Raw acquisition is pinned by source-lock.json. Cleaning and split manifests record row accounting and membership. Each candidate uses the same five validation folds. The chosen estimator is refitted on the complete training partition, evaluated on the fixed held-out partition and written to an immutable version directory before promotion to current. The cleaned CSV remains free of learned transformations."
)
table(
    [
        ["Component", "Responsibility"],
        ["src/heart_disease/data", "Acquisition, validation, splitting and training-partition EDA"],
        [
            "features and models",
            "Fold-local transformations, CV, selection, evaluation and packaging",
        ],
        ["api", "Validated prediction contract, readiness, metrics and sanitized logs"],
        [
            ".github/workflows",
            "Lint, tests, training, packaging, Docker build and retained evidence",
        ],
        [
            "deploy and scripts",
            "Kubernetes manifests, Traefik access, monitoring and evidence capture",
        ],
    ],
    [180, 319],
)
p(
    "The image tag combines model version with a source/build-input hash. Two replicas improve process availability, but both run on one node; this does not establish node-level fault tolerance. Monitoring history is ephemeral.",
    "SmallX",
)

page(3, "Dataset provenance and quality controls")
p(
    "The source is processed.cleveland.data from the UCI Heart Disease archive. The citation is Janosi, Steinbrunn, Pfisterer and Detrano (1989), DOI 10.24432/C52P4X; the dataset is distributed under CC BY 4.0. The cleaned adaptation names fields, normalizes missing tokens and maps original diagnosis values 1-4 to target 1, retaining 0 as target 0."
)
table(
    [
        ["Predictor(s)", "Meaning / source representation"],
        ["age; trestbps; chol", "Age in years; resting pressure in mm Hg; cholesterol in mg/dL"],
        ["thalach; oldpeak", "Maximum heart rate; ST depression relative to rest"],
        ["sex; fbs; exang", "Source binary codes: sex, fasting sugar >120 mg/dL, exercise angina"],
        [
            "cp; restecg; slope",
            "Categories: chest pain 1-4; resting ECG 0-2; exercise ST slope 1-3",
        ],
        ["ca; thal", "Vessel count code 0-3; thal codes 3/6/7; explicit missingness allowed"],
    ],
    [185, 314],
)
h("Observed cleaning outcome")
p(
    "All 303 source rows were retained. There were no invalid rows, exact duplicates or conflicting feature groups requiring removal. Four ca values and two thal values are missing. Full-dataset target counts are 164 negative and 139 positive. Missing values remain in the cleaned CSV and are imputed only during model fitting."
)
h("Deterministic validation")
p(
    "The raw parser requires the expected 14 columns, converts numeric values and checks field domains. Malformed rows are accounted for in a quarantine report rather than silently repaired. Duplicate and conflicting feature groups are checked before splitting. Source encodings are preserved: category codes are not relabeled into a different dataset convention."
)
h("Dataset fingerprints")
p(
    "Raw SHA-256:<br/>a74b7efa387bc9d108d7d0115d831fe9b414b29ae7124f331b622b4efa0427c8<br/>Cleaned SHA-256:<br/>e81973d3356c231ed8903aab16f5faa72d9679eb8ef6dc98a602b25df3f5d23d",
    "SmallX",
)
p(
    "The same fingerprints occur in the supplied CI artifact and local model lineage. The persisted stratified 80/20 split uses seed 42, yielding 242 training and 61 held-out records. The source schema decision follows the actual Cleveland dataset selected by the student.",
    "SmallX",
)
p(
    '<link href="https://archive.ics.uci.edu/dataset/45/heart+disease" color="#167d8d">Source: UCI Heart Disease dataset</link> | <link href="https://doi.org/10.24432/C52P4X" color="#167d8d">Dataset DOI</link>',
    "SmallX",
)

image(
    "reports/figures/class_balance.png",
    170,
    "Training-partition class balance. Full-dataset counts above are provenance only; exploratory analysis uses training records.",
)

page(4, "Exploratory analysis and leakage prevention")
p(
    "Exploratory plots use the training partition only (n=242). Holding out test records before EDA avoids using their distribution to choose preprocessing, hyperparameters or the decision threshold. The notebook invokes the same preparation and plotting modules used by the pipeline."
)
image(
    "reports/figures/histograms.png",
    220,
    "Figure 2. Training-only distributions of continuous predictors. Different numeric scales motivate scaling for the linear model.",
)
image(
    "reports/figures/correlation_heatmap.png",
    230,
    "Figure 3. Training-partition correlation heatmap. Correlation is descriptive and does not establish causation; integer category encodings require cautious interpretation.",
)
h("Preprocessing fitted inside each fold")
p(
    "Numeric features use median imputation and StandardScaler for Logistic Regression. Categorical features use most-frequent imputation and one-hot encoding with explicit source categories. Random Forest omits numeric scaling. Each validation fold is transformed using statistics learned from its training fold; integration tests check the complete pipeline rather than a separate hand-written feature transformation."
)

page(5, "Model search, selection and MLflow tracking")
p(
    "The experiment contains 25 candidate configurations: one majority-class dummy baseline, six Logistic Regression settings and eighteen Random Forest settings. Every candidate uses the same five persisted stratified folds and seed 42. Accuracy, precision, recall, F1, ROC-AUC and average precision are logged as fold results and aggregates."
)
table(
    [
        ["Family", "Configured search"],
        ["Dummy", "Majority-class reference (one configuration)"],
        ["Logistic Regression", "C in {0.1, 1, 10}; class_weight in {None, balanced}"],
        [
            "Random Forest",
            "200 trees; depth in {None, 4, 8}; leaf minimum in {1, 3, 5}; class_weight in {None, balanced}",
        ],
    ],
    [155, 344],
)
table(
    [
        ["Training CV comparison", "Accuracy", "Precision", "Recall", "ROC-AUC"],
        ["Dummy baseline", "0.5413", "0.0000", "0.0000", "0.5000"],
        ["Selected Logistic Regression", "0.8267", "0.8379", "0.7850", "0.9110"],
        [
            "Best Random Forest by AUC",
            f"{float(rf['mean_accuracy']):.4f}",
            f"{float(rf['mean_precision']):.4f}",
            f"{float(rf['mean_recall']):.4f}",
            f"{float(rf['mean_roc_auc']):.4f}",
        ],
    ],
    [187, 78, 78, 78, 78],
)
p(
    "Selection ranks mean training-only CV ROC-AUC and prefers the best Logistic Regression if it is within 0.01 of the global best. The chosen model is C=0.1 with balanced class weights, mean AUC 0.9110 and fold standard deviation 0.0305. Threshold 0.5 is fixed in configuration and was not tuned on held-out records."
)
image(
    "reports/evidence/screenshots/mlflow/selected-model.png",
    210,
    "Figure 4. Captured local MLflow selected-model run. CI produces a separate run with the same measured evaluation results.",
)
p(
    "MLflow parent and child runs retain candidate parameters, fold metrics, lineage and plots. The final serving-bundle artifact contains the complete pipeline. Failed local serializer runs were retained; explicit CloudPickle resolved the export issue. Repeated fixed-split evaluations are reproducibility evidence, not independent validation.",
    "SmallX",
)

page(6, "Held-out evaluation and interpretation")
p(
    "After model selection, the chosen pipeline is refitted on 242 training records and evaluated on 61 untouched held-out records. The selected-model evaluation is identical in the local and CI artifacts. Test metrics did not determine the search grid, preprocessing or selection rule."
)
table(
    [
        ["Held-out metric", "Measured value"],
        ["Accuracy", "0.885246"],
        ["Precision / Recall", "0.838710 / 0.928571"],
        ["F1", "0.881356"],
        ["ROC-AUC / Average precision", "0.965368 / 0.962246"],
    ],
    [250, 249],
)
image(
    "reports/figures/confusion_matrix.png",
    215,
    "Figure 5. Held-out confusion matrix at threshold 0.5: TN=28, FP=5, FN=2, TP=26 (61 records).",
)
image(
    "reports/figures/roc_curve.png",
    205,
    "Figure 6. Held-out ROC curve for the selected pipeline. AUC summarizes ranking across thresholds, whereas the confusion matrix uses the configured operating point.",
)
p(
    "The historical cohort and small held-out sample limit generalizability. Class-weighted outputs are not calibrated clinical risk. No external cohort, prospective validation, subgroup fairness conclusion or production drift detection is claimed. High held-out AUC is an observed experiment result, not evidence of deployment safety.",
    "SmallX",
)

page(7, "Serving contract, packaging and container proof")
p(
    "POST /predict requires all 13 named fields. ca and thal may be explicit null. Unknown category codes, missing or extra keys, numeric strings, Boolean substitutions and nonfinite values are rejected. Bodies larger than 16 KiB return 413. JSON field order does not affect the prediction."
)
table(
    [
        ["Response field", "Semantics"],
        ["prediction; threshold", "Binary prediction at configured threshold 0.5"],
        ["positive_class_probability", "Pipeline probability for class 1"],
        ["confidence", "p for prediction 1; 1-p for prediction 0"],
        ["model_version; schema_version", "Verified serving lineage and contract identity"],
        ["request_id", "Correlation ID for sanitized request/error logs"],
    ],
    [198, 301],
)
h("Verified live request")
p(
    "A synthetic request through Traefik returned prediction 0, positive-class probability 0.225527 and confidence 0.774473. Five additional valid requests succeeded during final verification; a synthetic cp=0 request returned 422. /metrics returned 404 through the external Ingress, while Prometheus scraped the internal pod endpoints."
)
h("Model lifecycle and availability")
p(
    "/health is a process liveness check. /ready requires a loaded checksum-verified bundle with expected schema, features and classes. /version exposes serving identity. Invalid requests produce sanitized error messages; unavailable models return 503, and unexpected exceptions return a generic 500 with a request ID. One worker per pod keeps metrics aggregation simple; inference uses a bounded threadpool."
)
h("Container isolation")
p(
    "The Docker image bakes in the selected model and locked runtime requirements. It runs as UID 10001 with a read-only root filesystem and writable temporary mount. The CI artifact records an isolated AMD64 Docker smoke test with valid prediction, invalid-input rejection, non-root user and read-only root enabled. The local deployment uses the ARM64 build and Kubernetes probes."
)
p(
    "<b>CI model:</b> "
    + C["model_version"]
    + "<br/><b>Local deployed model:</b> "
    + L["model_version"]
    + "<br/><b>Local image:</b> heart-disease-api:"
    + L["model_version"]
    + "-769ef0ea30",
    "SmallX",
)
p(
    "Distinct versions reflect independent training runs, not a single promoted image. The verified test metrics agree; the synthetic prediction probabilities agree to floating-point precision. CI manifest dirty=true is retained honestly: generated tracked outputs changed during training, so the source hash accompanies the commit SHA.",
    "SmallX",
)

page(8, "GitHub automation and artifact verification")
p(
    "GitHub Actions run 38159803218 completed successfully for commit e1710cb on main. Steps installed the locked environment, passed lint and 19 unit tests, acquired data and trained models, verified packaging and two integration tests, rendered Kubernetes manifests, built the AMD64 image and passed its isolated serving test. Evidence upload executes with if: always() to retain available diagnostics even when a prior step fails."
)
image(
    "reports/evidence/screenshots/ci-final.png",
    340,
    "Figure 7. Actual GitHub Actions success summary and published artifact digest; this is remote CI evidence, separate from the local deployment.",
)
h("Supplied ZIP verified against published digest")
p(
    "Artifact: pipeline-38159803218-1.zip. The GitHub page and downloaded ZIP agree on SHA-256:<br/>f5d839f4c6ff305e879ef7af1a8724d410b405d09f21acf12d58c3365d3a34ef",
    "SmallX",
)
p(
    "ZIP CRC verification passed. Every path in the current model checksum list matched the corresponding archived file. JUnit evidence reports 19 unit and 2 integration tests with zero failures, errors or skips. The archive contains metrics, manifests, plots, logs, MLflow database/artifacts and the serving bundle. No artifact model was deserialized merely to inspect its metadata."
)
p(
    "A retained local deliberate-failure test proves exit code 1, preserved diagnostics and a blocked downstream step under pipefail. It is not presented as a failed remote GitHub run. GitHub reported a Node action-runtime deprecation warning; the run still passed. Maintaining pinned action versions is future upkeep.",
    "SmallX",
)
p(
    '<link href="https://github.com/rmishra3261/2025ae05568-mlops/actions/runs/38159803218" color="#167d8d">Evidence: successful workflow run and downloadable artifact</link>',
    "SmallX",
)

page(9, "Kubernetes deployment and operational monitoring")
p(
    "Final verification on 12 October 2026 found the Minikube host, kubelet and API server running with a configured context. The heart-disease-api Deployment had two available replicas on the latest expected image. Prometheus had one ready replica. Traefik routes host heart-disease.test to the ClusterIP API Service; its local controller uses HTTP port 8081 through the Minikube tunnel."
)
image(
    "reports/figures/monitoring-final.png",
    270,
    "Figure 8. Charts rendered from the final live dashboard API snapshot (IST). Both current API pods are UP. The actual UI screenshot is retained in reports/evidence/screenshots/monitoring/dashboard-final.png.",
)
table(
    [
        ["Operational evidence", "Final observation"],
        ["API replicas / Prometheus", "2/2 available / 1/1 available"],
        ["Scrape targets", "Both current API pods report UP"],
        [
            "Synthetic traffic demonstration",
            "30 seconds; 58 valid responses and 58 expected 422 responses",
        ],
        ["Ingress boundaries", "/predict succeeds; external /metrics returns 404"],
    ],
    [210, 289],
)
p(
    "Prometheus discovers and scrapes each API pod every five seconds. The dashboard reads private Prometheus through localhost:9090 and serves on localhost:8090. Its error panel includes 4xx and 5xx, so deliberately invalid demo requests raise that series. Inference p95 measures model computation, not end-to-end network latency.",
    "SmallX",
)
p(
    "Bounded route/status metric labels avoid request-specific cardinality. JSON logs omit raw request values. Prometheus retention is 24 hours / 256 MB in ephemeral storage; export evidence before shutdown. Readiness proves artifact loading, not ongoing predictive accuracy.",
    "SmallX",
)

page(10, "Reproduction, coverage and submission status")
h("Reproduction sequence")
p(
    "Use Python 3.11, Docker Desktop, kubectl and Minikube. In the repository, run make setup, then make verify. This installs pinned packages and executes lint, source preparation, training, packaging and tests. Next run make docker-build, make docker-smoke and make deploy-minikube. Keep minikube -p mlops-assignment tunnel running; port-forward svc/prometheus on 9090 and run make dashboard in separate terminals. Use scripts/smoke_api.py with URL http://127.0.0.1:8081 and Host heart-disease.test, then run make evidence."
)
p(
    "To inspect the supplied CI evidence, extract the ZIP separately from local artifacts. Preserve its directory structure, manifests and checksums. CI and local versions must not be relabeled as the same release. For a Docker restart, recover the profile and run minikube update-context -p mlops-assignment before verifying the node and application rollout."
)
table(
    [
        ["Assignment area", "Completion / evidence"],
        ["Data and EDA", "Cleaned CSV, provenance, split and required plots verified"],
        ["Models and tracking", "Two model families, CV comparison, metrics and MLflow artifacts"],
        [
            "Reproducibility and CI",
            "Locked environment, full model pipeline, 21 tests, successful remote CI",
        ],
        [
            "Container and deployment",
            "AMD64 CI smoke; local image, two ready replicas and Ingress prediction",
        ],
        ["Monitoring", "Private per-pod scrape, four-panel dashboard and sanitized request logs"],
        ["Written report", "This ten-page report; student review required before submission"],
        [
            "Video and individual review",
            "Video not yet recorded; student understanding/disclosure review pending",
        ],
    ],
    [183, 316],
)
h("Sources and attribution")
p(
    "Dataset: Janosi et al. (1989), Heart Disease, UCI, DOI 10.24432/C52P4X, CC BY 4.0. Implementation evidence: repository commit e1710cb; Actions run 38159803218; supplied ZIP and final local verification records. Project documentation records Codex assistance. The student must understand, review and disclose that assistance according to course rules; this report does not assert an independent review already occurred.",
    "SmallX",
)
p(
    '<link href="https://github.com/rmishra3261/2025ae05568-mlops" color="#167d8d">Repository</link> | <link href="https://github.com/rmishra3261/2025ae05568-mlops/actions/runs/38159803218" color="#167d8d">CI evidence</link> | <link href="https://archive.ics.uci.edu/dataset/45/heart+disease" color="#167d8d">UCI source</link><br/>Demonstration video: pending recording. Outline: docs/video-script.md.',
    "SmallX",
)


def footer(c, doc):
    c.saveState()
    w, ht = A4
    c.setStrokeColor(colors.HexColor("#d7e2ea"))
    c.line(48, 39, w - 48, 39)
    c.setFillColor(colors.HexColor("#475569"))
    c.setFont("Helvetica", 8)
    c.drawString(48, 26, "2025AE05568 | Heart disease classification | Verified 12 Oct 2026")
    c.drawRightString(w - 48, 26, f"{doc.page} / 10")
    c.restoreState()


OUT.parent.mkdir(parents=True, exist_ok=True)
doc = SimpleDocTemplate(
    str(OUT),
    pagesize=A4,
    rightMargin=48,
    leftMargin=48,
    topMargin=42,
    bottomMargin=52,
    title="MLOps Assignment 1 - Heart Disease Classification",
    author="2025AE05568",
    subject="Verified implementation, evaluation and deployment report",
)
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT)
