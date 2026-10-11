import numpy as np
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def probabilities(model, X):
    classes = list(model.classes_)
    if classes != [0, 1]:
        raise ValueError("Model must have binary classes [0, 1]")
    values = model.predict_proba(X)[:, classes.index(1)]
    if not np.isfinite(values).all() or ((values < 0) | (values > 1)).any():
        raise ValueError("Invalid model probabilities")
    return values


def metrics(y, scores, threshold=0.5):
    predictions = (np.asarray(scores) >= threshold).astype(int)
    return {
        "accuracy": float(accuracy_score(y, predictions)),
        "precision": float(precision_score(y, predictions, zero_division=0)),
        "recall": float(recall_score(y, predictions, zero_division=0)),
        "f1": float(f1_score(y, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(y, scores)),
        "average_precision": float(average_precision_score(y, scores)),
    }
