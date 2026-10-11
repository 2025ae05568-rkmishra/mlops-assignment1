import numpy as np
import pandas as pd
import pytest
from sklearn.exceptions import NotFittedError
from sklearn.linear_model import LogisticRegression

from heart_disease.features.preprocessing import pipeline
from heart_disease.features.schema import FEATURES
from heart_disease.models.select import select


def test_transformations_fit_only_training_data():
    rows = [
        [40, 1, 2, 120, 200, 0, 0, 150, 0, 1, 2, 0, 3],
        [60, 0, 4, 140, 300, 1, 2, 130, 1, 2, 3, np.nan, 7],
    ]
    train = pd.DataFrame(rows, columns=FEATURES)
    model = pipeline(LogisticRegression()).fit(train, [0, 1])
    numeric = model.named_steps["preprocessing"].named_transformers_["numeric"]
    before = numeric.named_steps["scaler"].mean_.copy()
    validation = train.copy()
    validation["chol"] = 1000000
    model.predict_proba(validation)
    np.testing.assert_array_equal(before, numeric.named_steps["scaler"].mean_)
    assert before[2] == 250
    with pytest.raises(NotFittedError):
        pipeline(LogisticRegression()).predict_proba(train)


def test_selection_tie_prefers_linear():
    linear = {"family": "logistic_regression", "mean_roc_auc": 0.90}
    forest = {"family": "random_forest", "mean_roc_auc": 0.905}
    assert select([linear, forest])[0] == linear
    assert select([linear, {**forest, "mean_roc_auc": 0.95}])[0]["family"] == "random_forest"
