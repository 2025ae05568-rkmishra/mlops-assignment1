import numpy as np
from sklearn.model_selection import StratifiedKFold, train_test_split

from heart_disease.common.io import digest
from heart_disease.features.schema import FEATURES


def record_ids(df):
    return [
        digest({c: None if np.isnan(row[c]) else float(row[c]) for c in FEATURES})
        for _, row in df.iterrows()
    ]


def make_splits(df, seed=42, test_size=0.2, folds=5):
    ids = record_ids(df)
    if len(set(ids)) != len(ids):
        raise ValueError("Feature groups must be unique before splitting")
    train, test = train_test_split(
        np.arange(len(df)), test_size=test_size, stratify=df.target, random_state=seed
    )
    train, test = sorted(train.tolist()), sorted(test.tolist())
    y = df.iloc[train].target.to_numpy()
    if min(np.bincount(y)) < folds:
        raise ValueError("Not enough training examples per class for CV")
    cv = StratifiedKFold(folds, shuffle=True, random_state=seed)
    assignments = []
    for fold, (_, valid) in enumerate(cv.split(np.zeros(len(y)), y)):
        assignments += [{"record_id": ids[train[i]], "fold": fold} for i in valid]
    return {
        "seed": seed,
        "test_size": test_size,
        "folds": folds,
        "record_ids": ids,
        "train_indices": train,
        "test_indices": test,
        "cv_assignments": assignments,
    }
