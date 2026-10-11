from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from heart_disease.features.schema import CATEGORIES, NUMERIC


def pipeline(classifier, scale=True):
    numeric = [("imputer", SimpleImputer(strategy="median"))]
    if scale:
        numeric.append(("scaler", StandardScaler()))
    categorical = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "encoder",
                OneHotEncoder(
                    categories=list(CATEGORIES.values()),
                    handle_unknown="ignore",
                    sparse_output=False,
                ),
            ),
        ]
    )
    preprocessor = ColumnTransformer(
        [("numeric", Pipeline(numeric), NUMERIC), ("categorical", categorical, list(CATEGORIES))]
    )
    return Pipeline([("preprocessing", preprocessor), ("classifier", classifier)])
