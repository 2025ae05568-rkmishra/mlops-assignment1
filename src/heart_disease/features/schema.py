FEATURES = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
]
NUMERIC = ["age", "trestbps", "chol", "thalach", "oldpeak"]
CATEGORIES = {
    "sex": [0, 1],
    "cp": [1, 2, 3, 4],
    "fbs": [0, 1],
    "restecg": [0, 1, 2],
    "exang": [0, 1],
    "slope": [1, 2, 3],
    "ca": [0, 1, 2, 3],
    "thal": [3, 6, 7],
}
NULLABLE = {"ca", "thal"}
BOUNDS = {
    "age": (1, 120),
    "trestbps": (0, 350),
    "chol": (0, 1000),
    "thalach": (0, 300),
    "oldpeak": (-10, 20),
}
SCHEMA_VERSION = "1.0"


def feature_schema():
    return {
        "version": SCHEMA_VERSION,
        "features": FEATURES,
        "numeric": NUMERIC,
        "categories": CATEGORIES,
        "nullable": sorted(NULLABLE),
        "bounds": BOUNDS,
        "target": "int(num > 0)",
        "positive_label": 1,
    }
