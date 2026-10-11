import argparse
import importlib.metadata
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from mlflow.models import infer_signature
from sklearn.base import clone
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import ConfusionMatrixDisplay, PrecisionRecallDisplay, RocCurveDisplay
from sklearn.model_selection import ParameterGrid

from heart_disease.common.io import (
    code_identity,
    config,
    digest,
    now,
    read_json,
    sha256,
    write_json,
)
from heart_disease.features.preprocessing import pipeline
from heart_disease.features.schema import FEATURES, SCHEMA_VERSION, feature_schema
from heart_disease.models.evaluate import metrics, probabilities
from heart_disease.models.package import load, promote, write_checksums
from heart_disease.models.select import select


def candidates(cfg):
    yield "dummy", {}, pipeline(DummyClassifier(strategy="prior"))
    for params in ParameterGrid(cfg["logistic_regression"]):
        yield (
            "logistic_regression",
            params,
            pipeline(LogisticRegression(**params, max_iter=2000, random_state=cfg["seed"])),
        )
    for params in ParameterGrid(cfg["random_forest"]):
        yield (
            "random_forest",
            params,
            pipeline(
                RandomForestClassifier(**params, n_jobs=1, random_state=cfg["seed"]), scale=False
            ),
        )


def train(config_path="configs/training.yaml", tracking_uri="sqlite:///mlflow.db"):
    cfg = config(config_path)
    split = read_json("data/manifests/split.json")
    dataset_hash = sha256("data/processed/cleaned.csv")
    if (
        dataset_hash != split["processed_sha256"]
        or cfg["folds"] != split["folds"]
        or cfg["seed"] != split["seed"]
    ):
        raise ValueError("Dataset or CV config differs from split manifest")
    df = pd.read_csv("data/processed/cleaned.csv")
    X = df.iloc[split["train_indices"]][FEATURES].reset_index(drop=True)
    y = df.iloc[split["train_indices"]].target.reset_index(drop=True)
    identity = code_identity()
    versions = {
        name: importlib.metadata.version(name)
        for name in ["scikit-learn", "numpy", "pandas", "mlflow"]
    }
    lineage = {
        **identity,
        "config_hash": sha256(config_path),
        "dataset_hash": dataset_hash,
        "raw_hash": read_json("data/manifests/source-lock.json")["member_sha256"],
        "split_hash": sha256("data/manifests/split.json"),
        "versions": versions,
        "schema_version": SCHEMA_VERSION,
        "threshold": cfg["threshold"],
    }
    # A verified identical experiment is reused; held-out results are not new validation.
    experiment_id = digest(lineage)[:20]
    cache = Path("artifacts/experiments") / f"{experiment_id}.json"
    if cache.exists():
        previous = read_json(cache)
        load(previous["bundle"])
        promote(previous["bundle"])
        print(f"Reused verified experiment {experiment_id}; no new held-out evaluation")
        return previous
    fold_by_id = {a["record_id"]: a["fold"] for a in split["cv_assignments"]}
    fold_ids = np.array([fold_by_id[split["record_ids"][i]] for i in split["train_indices"]])
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("heart-disease-assignment-1")
    Path("reports/metrics").mkdir(parents=True, exist_ok=True)
    Path("artifacts/model").mkdir(parents=True, exist_ok=True)
    results, estimators = [], {}
    with mlflow.start_run(run_name=f"comparison-{experiment_id}") as parent:
        mlflow.log_dict(lineage, "lineage.json")
        for index, (family, params, estimator) in enumerate(candidates(cfg)):
            start = time.monotonic()
            with mlflow.start_run(run_name=f"{family}-{index}", nested=True) as run:
                mlflow.log_params(
                    {
                        "family": family,
                        "seed": cfg["seed"],
                        "schema_version": SCHEMA_VERSION,
                        "threshold": cfg["threshold"],
                        **params,
                    }
                )
                mlflow.log_dict(lineage, "lineage.json")
                mlflow.log_dict(feature_schema(), "feature-schema.json")
                mlflow.log_dict(read_json("data/manifests/cleaning.json"), "cleaning.json")
                oof, fold_metrics = np.zeros(len(y)), []
                for fold in range(cfg["folds"]):
                    tr, va = np.flatnonzero(fold_ids != fold), np.flatnonzero(fold_ids == fold)
                    fitted = clone(estimator).fit(X.iloc[tr], y.iloc[tr])
                    scores = probabilities(fitted, X.iloc[va])
                    oof[va] = scores
                    values = metrics(y.iloc[va], scores, cfg["threshold"])
                    fold_metrics.append(values)
                    mlflow.log_metrics({f"fold_{k}": v for k, v in values.items()}, step=fold)
                aggregates = {
                    f"{stat}_{key}": float(fn([m[key] for m in fold_metrics]))
                    for key in fold_metrics[0]
                    for stat, fn in [("mean", np.mean), ("std", np.std)]
                }
                mlflow.log_metrics({**aggregates, "duration_seconds": time.monotonic() - start})
                mlflow.log_dict(fold_metrics, "fold-metrics.json")
                mlflow.log_dict(infer_signature(X, oof).to_dict(), "signature.json")
                mlflow.log_dict(
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
                        "ca": None,
                        "thal": 3,
                    },
                    "synthetic-input.json",
                )
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.bar(range(cfg["folds"]), [m["roc_auc"] for m in fold_metrics])
                ax.set(
                    ylim=(0, 1),
                    xlabel="Shared CV fold",
                    ylabel="ROC-AUC",
                    title=f"{family} — training-only CV",
                )
                fig.tight_layout()
                mlflow.log_figure(fig, "cv-roc-auc.png")
                plt.close(fig)
                result = {
                    "candidate": index,
                    "family": family,
                    "params": params,
                    "run_id": run.info.run_id,
                    **aggregates,
                }
                results.append(result)
                estimators[index] = estimator
                print(
                    f"{index:02d} {family}: CV ROC-AUC={aggregates['mean_roc_auc']:.4f}", flush=True
                )
        selected, reason = select(results, cfg["tie_tolerance"])
        write_json("reports/metrics/cv-comparison.json", results)
        pd.DataFrame(results).to_csv("reports/metrics/cv-comparison.csv", index=False)
        mlflow.log_artifact("reports/metrics/cv-comparison.json")
        with mlflow.start_run(run_name="selected-final-model", nested=True) as final:
            mlflow.log_params(
                {
                    "family": selected["family"],
                    **selected["params"],
                    "seed": cfg["seed"],
                    "threshold": cfg["threshold"],
                }
            )
            mlflow.log_dict(lineage, "lineage.json")
            model = clone(estimators[selected["candidate"]]).fit(X, y)
            test = df.iloc[split["test_indices"]]
            scores = probabilities(model, test[FEATURES])
            values = metrics(test.target, scores, cfg["threshold"])
            mlflow.log_metrics(values)
            version = f"{experiment_id}-{final.info.run_id[:8]}"
            bundle = Path("artifacts/model") / version
            bundle.mkdir()
            mlflow.sklearn.save_model(
                model,
                str(bundle / "model"),
                serialization_format="cloudpickle",
                signature=infer_signature(X, probabilities(model, X)),
                pip_requirements=[
                    line.strip()
                    for line in Path("requirements.txt").read_text().splitlines()
                    if line and not line.startswith(("#", " "))
                ],
            )
            for name, display in [
                ("confusion_matrix", ConfusionMatrixDisplay.from_predictions),
                ("roc_curve", RocCurveDisplay.from_predictions),
                ("precision_recall_curve", PrecisionRecallDisplay.from_predictions),
            ]:
                fig, ax = plt.subplots(figsize=(6, 5))
                display(
                    test.target,
                    (scores >= cfg["threshold"]).astype(int)
                    if name == "confusion_matrix"
                    else scores,
                    ax=ax,
                )
                ax.set_title(f"Held-out {name.replace('_', ' ')}; n={len(test)}")
                fig.tight_layout()
                fig.savefig(f"reports/figures/{name}.png", dpi=160)
                mlflow.log_figure(fig, f"{name}.png")
                plt.close(fig)
            write_json(
                bundle / "metrics.json",
                {
                    "test": values,
                    "test_n": len(test),
                    "train_n": len(X),
                    "selected_cv": selected,
                    "selection_reason": reason,
                },
            )
            write_json(bundle / "feature-schema.json", feature_schema())
            model_files = {
                str(p.relative_to(bundle)): sha256(p)
                for p in sorted((bundle / "model").rglob("*"))
                if p.is_file()
            }
            manifest = {
                **lineage,
                "model_version": version,
                "run_id": final.info.run_id,
                "parent_run_id": parent.info.run_id,
                "model_hash": digest(model_files),
                "classes": [int(c) for c in model.classes_],
                "positive_label": 1,
                "trained_at": now(),
                "selected_family": selected["family"],
            }
            write_json(bundle / "manifest.json", manifest)
            (bundle / "model-card.md").write_text(
                f"# Model card\n\nEducational UCI Cleveland binary classifier. Not clinically validated.\n\nSelected: {selected['family']}. {reason}.\n\nTraining rows: {len(X)}; held-out rows: {len(test)}. CV selected the model; the held-out partition did not drive tuning. Threshold: {cfg['threshold']}.\n\nSmall historical cohort; scores are not calibrated clinical risk. See metrics.json and lineage manifest for measured results.\n"
            )
            write_checksums(bundle)
            mlflow.log_artifacts(str(bundle), "serving-bundle")
            # Private row-level predictions stay outside tracked evidence.
            private = Path("artifacts/evaluation")
            private.mkdir(parents=True, exist_ok=True)
            pd.DataFrame(
                {
                    "record_id": [split["record_ids"][i] for i in split["test_indices"]],
                    "target": test.target.to_numpy(),
                    "positive_probability": scores,
                }
            ).to_csv(private / f"{experiment_id}.csv", index=False)
            write_json("reports/metrics/final.json", read_json(bundle / "metrics.json"))
            write_json("docs/model-manifest.json", manifest)
            Path("docs/model-card.md").write_text((bundle / "model-card.md").read_text())
            result = {"experiment_id": experiment_id, "bundle": str(bundle), "manifest": manifest}
            write_json(cache, result)
            promote(bundle)
            print(
                f"Selected {selected['family']}; held-out ROC-AUC={values['roc_auc']:.4f}; bundle={bundle}"
            )
            return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/training.yaml")
    parser.add_argument("--tracking-uri", default="sqlite:///mlflow.db")
    args = parser.parse_args()
    train(args.config, args.tracking_uri)
