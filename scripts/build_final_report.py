"""Build a ten-page report from one BITS release; refuse incomplete final evidence."""

import argparse
import html
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

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

from heart_disease.common.io import read_json, sha256, write_json
from heart_disease.submission import validate

ROOT = Path(__file__).resolve().parents[1]


class Architecture(Flowable):
    def __init__(self):
        super().__init__()
        self.width, self.height = 490, 200

    def draw(self):
        c = self.canv
        boxes = [
            (0, 140, "Pinned UCI data", "Clean CSV + fixed split"),
            (168, 140, "CV and MLflow", "Training partition only"),
            (336, 140, "GitHub Actions", "Tests + Docker proof"),
            (336, 70, "Release artifact", "Verified AMD64 image"),
            (168, 70, "BITS VM / Minikube", "Traefik -> API pods"),
            (0, 70, "Reviewer client", "SSH + Ingress requests"),
            (168, 0, "Prometheus", "Per-pod metrics + logs"),
            (336, 0, "Private dashboard", "Rate, errors, p95, ready"),
        ]
        for x, y, title, sub in boxes:
            c.setFillColor(colors.HexColor("#eef6f8"))
            c.setStrokeColor(colors.HexColor("#167d8d"))
            c.roundRect(x, y, 154, 50, 5, fill=1)
            c.setFillColor(colors.HexColor("#102a43"))
            c.setFont("Helvetica-Bold", 9)
            c.drawCentredString(x + 77, y + 30, title)
            c.setFont("Helvetica", 8)
            c.drawCentredString(x + 77, y + 14, sub)
        for points in [
            (154, 165, 168, 165),
            (322, 165, 336, 165),
            (413, 140, 413, 120),
            (336, 95, 322, 95),
            (154, 95, 168, 95),
            (245, 70, 245, 50),
            (322, 25, 336, 25),
        ]:
            c.line(*points)


def build(args):
    draft = args.draft
    evidence = Path(args.evidence_dir).resolve() if args.evidence_dir else None
    pointer = ROOT / "reports/evidence/runtime/latest-submission.txt"
    if evidence is None and pointer.exists() and not draft:
        evidence = Path(pointer.read_text().strip())
    if evidence:
        release, manifest, api, counts = validate(evidence)
        metrics = read_json(evidence / "metrics/final.json")
        candidates = read_json(evidence / "metrics/cv-comparison.json")
        cleaning = read_json(evidence / "data/cleaning.json")
        figures = evidence / "figures"
    elif draft:
        release = {
            "repository": "2025ae05568-rkmishra/mlops-assignment1",
            "commit": "BITS release pending",
            "run_id": "pending",
            "captured_at": "pending",
            "image": "pending",
            "image_id": "pending",
        }
        manifest = read_json(ROOT / "docs/model-manifest.json")
        metrics = read_json(ROOT / "reports/metrics/final.json")
        candidates = read_json(ROOT / "reports/metrics/cv-comparison.json")
        cleaning = read_json(ROOT / "data/manifests/cleaning.json")
        figures = ROOT / "reports/figures"
        api, counts = None, None
    else:
        raise ValueError(
            "No BITS evidence. Run scripts/run_lab_deployment.sh on the VM first; use --draft only for layout review."
        )
    screenshots = evidence / "screenshots" if evidence else None
    access_file = evidence / "reviewer-access.md" if evidence else None
    access = (
        access_file.read_text()
        if access_file and access_file.exists()
        else "Pending: add tested reviewer access instructions to reviewer-access.md in the evidence directory."
    )
    if not draft:
        missing = [
            name
            for name in ("ci", "mlflow", "deployment", "monitoring")
            if not (screenshots / f"{name}.png").is_file()
        ]
        if missing:
            raise ValueError(f"Capture current-release screenshots first: {', '.join(missing)}")
        for name in ("ci", "mlflow", "deployment", "monitoring"):
            with PILImage.open(screenshots / f"{name}.png") as im:
                im.verify()
        if not args.video_url or not args.video_url.startswith("https://"):
            raise ValueError("Supply --video-url with the reviewer-accessible HTTPS recording link")
        if not access_file.is_file() or any(
            token in access for token in ("USER@VM", "REPLACE", "pending", "Pending")
        ):
            raise ValueError(
                "Add tested, non-placeholder reviewer-access.md to the evidence directory"
            )
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="BodyX",
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            spaceAfter=9,
            textColor=colors.HexColor("#243448"),
        )
    )
    styles.add(
        ParagraphStyle(name="SmallX", fontName="Helvetica", fontSize=8, leading=11, spaceAfter=7)
    )
    styles.add(
        ParagraphStyle(
            name="HeadX",
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            spaceAfter=15,
            textColor=colors.HexColor("#102a43"),
        )
    )
    story = []

    def esc(value):
        return html.escape(str(value))

    def p(value, style="BodyX"):
        story.append(Paragraph(str(value), styles[style]))

    def page(n, title):
        if n > 1:
            story.append(PageBreak())
        p(f"{n:02d} / BITS AIMLCZG523 - Assignment 1", "SmallX")
        p(title, "HeadX")
        if draft:
            p(
                "DRAFT - BITS execution, screenshots, access and recording must be verified before submission.",
                "SmallX",
            )

    def table(rows, widths=(200, 290)):
        t = Table(
            [[Paragraph(esc(v), styles["SmallX"]) for v in row] for row in rows], colWidths=widths
        )
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e4f1f3")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#d7e2ea")),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(t)
        story.append(Spacer(1, 10))

    def image(path, caption, maxh=250):
        if path and path.is_file():
            with PILImage.open(path) as im:
                w, h = im.size
            scale = min(490 / w, maxh / h)
            story.append(Image(str(path), width=w * scale, height=h * scale))
            p(caption, "SmallX")
        elif draft:
            p("Screenshot pending: " + caption, "SmallX")
        else:
            raise ValueError(f"Required figure missing: {path}")

    def screenshot(name, caption, maxh=300):
        image(screenshots / f"{name}.png" if screenshots else None, caption, maxh)

    cv, test = metrics["selected_cv"], metrics["test"]
    repo_url = "https://github.com/" + release["repository"]
    run_url = repo_url + "/actions/runs/" + str(release["run_id"])
    page(1, "Heart disease prediction: data to BITS deployment")
    p(
        "<b>Student ID: 2025AE05568</b><br/>"
        + datetime.now(ZoneInfo("Asia/Kolkata")).strftime("Prepared: %d %B %Y (IST)")
    )
    p(
        "An educational classifier based on original UCI Cleveland data. The workflow combines deterministic data validation, training-only cross-validation, MLflow tracking, a packaged preprocessing/model pipeline, GitHub automation, Docker serving and monitored Kubernetes deployment on the BITS VM."
    )
    table(
        [
            ["Measure", "Selected experiment"],
            ["Data split", f"{metrics['train_n']} training / {metrics['test_n']} held-out rows"],
            ["Selected family", cv["family"]],
            ["Hyperparameters", json.dumps(cv["params"])],
            ["Mean CV ROC-AUC", f"{cv['mean_roc_auc']:.4f} +/- {cv['std_roc_auc']:.4f}"],
            ["Held-out accuracy / ROC-AUC", f"{test['accuracy']:.4f} / {test['roc_auc']:.4f}"],
            ["BITS verification", release["captured_at"]],
        ]
    )
    p(
        '<b>Repository:</b> <link href="'
        + esc(repo_url)
        + '">'
        + esc(repo_url)
        + "</link>"
        + "<br/><b>Release commit:</b> "
        + esc(release["commit"]),
        "SmallX",
    )
    p(
        "The actual dataset has 13 predictors plus the diagnosis target; the student explicitly selected this schema despite the PDF's feature-count wording. Scores are educational model estimates, not clinically validated risk."
    )
    if draft and not evidence:
        p(
            "Metrics in this draft come from the historical experiment in the repository. They are not proof of a BITS deployment."
        )

    page(2, "Architecture and environment")
    story.append(Architecture())
    p(
        "The build runs in GitHub Actions on AMD64. The BITS VM downloads the successful release artifact, checks the archive checksum, loads the image into Minikube and verifies predictions through Traefik Ingress. Training and image rebuilding are not needed on the VM."
    )
    p(
        "The reviewer access path is workstation SSH forwarding to the VM's localhost Traefik port. Host heart-disease.test selects the Ingress rule. Prometheus and the dashboard stay private. No public API URL or managed-cloud deployment is claimed."
    )
    table(
        [
            ["Boundary", "Implementation"],
            ["Training", "Python 3.11; locked requirements; scikit-learn and MLflow"],
            ["Serving", "FastAPI/Uvicorn; one worker per pod; verified baked-in model"],
            ["Deployment", "Rocky Linux 9 x86_64; Docker driver; Minikube and Traefik"],
            ["Capacity", "Two API replicas on one node; no node-level fault tolerance"],
            ["Monitoring", "Per-pod Prometheus scraping; private four-panel dashboard"],
        ]
    )

    page(3, "Data provenance, cleaning and exploratory analysis")
    p(
        "Source: Janosi et al. (1989), Heart Disease, UCI Machine Learning Repository, DOI 10.24432/C52P4X, CC BY 4.0. Source archive and Cleveland member hashes are pinned. The binary target is int(num > 0); source category codes are retained."
    )
    p(
        f"Observed cleaning: {cleaning['source_rows']} source rows; {cleaning['cleaned_rows']} retained; {cleaning['invalid_rows']} invalid; {cleaning['duplicate_rows_removed']} duplicates removed; {cleaning['conflicting_rows']} conflicting rows. Missing values by feature: {esc(json.dumps({k: v for k, v in cleaning['missing_by_feature'].items() if v}))}. Imputation is fitted within training folds."
    )
    image(figures / "class_balance.png", "Training-partition class balance.", 100)
    image(figures / "histograms.png", "Training-only continuous-feature distributions.", 175)
    image(
        figures / "correlation_heatmap.png",
        "Training-only correlation heatmap; associations are descriptive, not causal.",
        150,
    )

    page(4, "Feature engineering, model comparison and tracking")
    p(
        "A fixed stratified 80/20 split and five shared training-only folds use seed 42. Numeric features use median imputation and scaling for Logistic Regression. Categorical features use mode imputation and one-hot encoding. Random Forest omits scaling. The entire fitted pipeline is shared with inference."
    )
    p(
        f"The search evaluates {len(candidates)} configurations: DummyClassifier, Logistic Regression and Random Forest. Selection uses mean CV ROC-AUC, preferring Logistic Regression when within 0.01 of the best. Threshold 0.5 is fixed; held-out performance does not select the model."
    )
    best = [
        next(r for r in candidates if r["family"] == "dummy"),
        cv,
        max(
            (r for r in candidates if r["family"] == "random_forest"),
            key=lambda r: r["mean_roc_auc"],
        ),
    ]
    table(
        [["Family", "CV accuracy / precision / recall / AUC"]]
        + [
            [
                r["family"],
                " / ".join(
                    f"{r['mean_' + k]:.4f}" for k in ("accuracy", "precision", "recall", "roc_auc")
                ),
            ]
            for r in best
        ]
    )
    screenshot(
        "mlflow", "Selected release's MLflow run: parameters, metrics, lineage and artifacts.", 260
    )
    p(
        "Each candidate has a child run with fold metrics, aggregates, parameters and plots. The selected refit exports a full serving bundle. Training-only folds prevent preprocessing leakage."
    )

    page(5, "Held-out results and limitations")
    p(
        f"After selection, the complete pipeline is fitted on {metrics['train_n']} training rows and evaluated on {metrics['test_n']} held-out rows. Repeated fixed-split results are reproducibility evidence, not independent validation."
    )
    table([["Held-out metric", "Value"]] + [[k, f"{v:.6f}"] for k, v in test.items()])
    image(
        figures / "confusion_matrix.png",
        "Held-out confusion matrix at the configured threshold.",
        170,
    )
    image(
        figures / "roc_curve.png",
        "Held-out ROC curve; ranking quality is distinct from calibrated risk.",
        145,
    )
    p(
        "The small historical cohort limits generalizability. There is no external-cohort validation or prospective clinical evaluation. Class-weighted probabilities are not calibrated clinical risk.",
        "SmallX",
    )

    page(6, "Packaging, API and isolated container verification")
    p(
        "The serving bundle contains fitted preprocessing and classifier, feature schema, metrics, model card, manifest and checksums. Startup verifies integrity, classes and feature order before readiness. The image contains the bundle and does not depend on MLflow availability at inference time."
    )
    table(
        [
            ["Endpoint / response", "Contract"],
            ["POST /predict", "All 13 fields required; ca and thal allow explicit null"],
            [
                "Prediction",
                "Binary label, positive-class probability and returned-class confidence",
            ],
            ["Version", "Model/schema version and request ID accompany the prediction"],
            ["Validation", "Unknown codes, extra/missing fields and invalid types return 422"],
            [
                "Availability",
                "/health liveness; /ready verified model; unavailable model returns 503",
            ],
            ["Boundaries", "16 KiB request limit; sanitized JSON logs; /metrics internal only"],
        ]
    )
    p(
        "Docker runs as UID 10001 with read-only root and writable /tmp. The release workflow builds and tests the AMD64 container with synthetic valid/invalid input, verifies the served model version, and saves isolated-serving evidence."
    )
    p(
        "<b>Model version:</b> "
        + esc(manifest["model_version"])
        + "<br/><b>Image:</b> "
        + esc(release["image"])
        + "<br/><b>Image identity:</b> "
        + esc(release["image_id"]),
        "SmallX",
    )
    if api:
        result = api["prediction"]
        p(
            f"Captured Ingress result: prediction {result['prediction']}, positive-class probability {result['positive_class_probability']:.6f}, confidence {result['confidence']:.6f}; invalid status {api['invalid_status']}; external metrics status {api['metrics_status']}."
        )
    else:
        p("BITS API and container-to-deployment identity evidence pending.")

    page(7, "CI automation and release provenance")
    p(
        "GitHub Actions runs lint, unit tests, data preparation, EDA, model comparison/training, packaging, integration tests and Docker smoke tests. Pipefail prevents failed checks from being masked by tee. Artifact upload runs with if: always() to preserve available failure diagnostics."
    )
    p(
        '<b>Workflow run:</b> <link href="' + esc(run_url) + '">' + esc(run_url) + "</link>",
        "SmallX",
    )
    p(
        f"Verified release test counts: {counts['unit']} unit and {counts['integration']} integration tests, zero failures/errors/skips."
        if counts
        else "BITS release test evidence pending; do not substitute historical CI results."
    )
    screenshot(
        "ci",
        "Successful selected release workflow with training, tests, Docker proof and artifact export.",
        330,
    )
    p(
        "The VM verifies the downloaded image archive checksum before loading. Release commit, run/attempt, model version, archive hash, image identity and actual pod resources are retained together. The deployment verifies that responses identify the selected release."
    )
    if "archive_sha256" in release:
        p("<b>Archive SHA-256:</b> " + esc(release["archive_sha256"]), "SmallX")

    page(8, "BITS Kubernetes deployment and access")
    p(
        "The application uses a Deployment with two replicas, startup/readiness/liveness probes, resource requests/limits and a ClusterIP Service. Traefik interprets Exact-path Ingress rules for prediction, health, readiness, version and API docs; /metrics is excluded."
    )
    screenshot(
        "deployment",
        "BITS VM resources and successful valid/invalid requests through Traefik Ingress.",
        300,
    )
    p("Reviewer access instructions (tested by the student):")
    p(esc(access).replace("\n", "<br/>"), "SmallX")
    p(
        "The forwarding process must remain running during review. The port-forward to Traefik exercises Ingress rules; it does not claim a publicly reachable LoadBalancer. A direct API Service port-forward is not used as Ingress proof."
    )

    page(9, "Monitoring and request logging")
    p(
        "Prometheus discovers each API pod using namespace-scoped read-only RBAC and scrapes every five seconds. The private dashboard shows prediction request rate, 4xx/5xx rate, model inference p95 and ready model replicas. No online accuracy or drift measurement is claimed."
    )
    screenshot(
        "monitoring",
        "Actual BITS dashboard after synthetic traffic, with both current pod targets UP.",
        330,
    )
    if api:
        p(
            "Captured synthetic traffic: "
            + esc(json.dumps(api["traffic_counts"]))
            + f" over {api['traffic_seconds']} seconds. Expected invalid requests deliberately contribute to the 4xx series."
        )
    p(
        "Structured logs retain request ID, route, status, duration and model version without raw health values. Captured logs are included in api-logs.txt. Metric labels are bounded. Inference p95 measures model computation rather than network latency."
    )
    p(
        "Prometheus retains up to 24 hours / 256 MB using ephemeral storage. Export the evidence directory before stopping or replacing the VM. Two API replicas on the same node do not protect against VM failure."
    )

    page(10, "Reproduction, deliverables and individual review")
    p(
        "On BITS: clone the repository, use Python 3.11 and locked requirements, run bash scripts/bootstrap_rocky9.sh --skip-installed, authenticate GitHub CLI, then run bash scripts/run_lab_deployment.sh. On a replacement VM, use --reuse-run RUN_ID at the same commit. Docker and Minikube must already be available to the regular user."
    )
    p(
        "Run bash scripts/open_vm_access.sh in a persistent VM terminal. Open the dashboard on the VM desktop, generate synthetic requests, and capture the selected release's CI, MLflow, deployment and monitoring screenshots. Record the overall pipeline and verify reviewer permissions. Build the final report with make report VIDEO_URL=https://... after adding screenshots and tested reviewer-access.md to the captured evidence directory."
    )
    table(
        [
            ["Deliverable", "Repository location"],
            [
                "Data / EDA / training / inference",
                "data/processed/cleaned.csv; src/; notebooks/; reports/figures",
            ],
            ["Environment / tests / CI", "requirements*.txt; tests/; .github/workflows/"],
            ["Container / deployment / monitoring", "Dockerfile; deploy/; scripts/"],
            [
                "Evidence / report / access",
                "Selected evidence directory; output/pdf; docs/deployment-bits.md",
            ],
        ]
    )
    p(
        '<b>Video:</b> <link href="' + esc(args.video_url) + '">' + esc(args.video_url) + "</link>"
        if args.video_url
        else "Video: pending student recording",
        "SmallX",
    )
    p(
        "<b>Sources:</b> UCI Heart Disease, https://doi.org/10.24432/C52P4X (CC BY 4.0); repository and selected workflow linked above. This work was developed with Codex assistance. The student must review, understand, personalize and disclose assistance according to course rules. The report does not certify independent understanding or guarantee marks.",
        "SmallX",
    )

    def footer(canvas, doc):
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#475569"))
        canvas.drawString(
            48,
            26,
            "2025AE05568 | "
            + ("DRAFT - not submission ready" if draft else "BITS release evidence"),
        )
        canvas.drawRightString(A4[0] - 48, 26, f"{doc.page} / 10")

    out = Path(
        args.output
        or ROOT
        / "output/pdf"
        / ("2025ae05568-mlops-draft-report.pdf" if draft else "2025ae05568-mlops-final-report.pdf")
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    temporary = out.with_suffix(".building.pdf")
    doc = SimpleDocTemplate(
        str(temporary),
        pagesize=A4,
        rightMargin=48,
        leftMargin=48,
        topMargin=42,
        bottomMargin=52,
        title="MLOps Assignment 1 - BITS deployment",
        author="2025AE05568",
    )
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    if doc.page != 10:
        temporary.unlink()
        raise ValueError(f"Report layout produced {doc.page} pages; expected exactly 10")
    temporary.replace(out)
    if not draft:
        write_json(
            evidence / "submission-manifest.json",
            {
                "report_sha256": sha256(out),
                "pages": doc.page,
                "release": release,
                "video_url": args.video_url,
                "screenshots": {p.name: sha256(p) for p in screenshots.glob("*.png")},
                "access_sha256": sha256(access_file),
            },
        )
    print(out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir")
    parser.add_argument("--video-url")
    parser.add_argument("--draft", action="store_true")
    parser.add_argument("--output")
    try:
        build(parser.parse_args())
    except (ValueError, FileNotFoundError, KeyError) as exc:
        parser.exit(1, f"Report not ready: {exc}\n")
