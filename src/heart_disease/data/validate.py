import io

import numpy as np
import pandas as pd

from heart_disease.features.schema import BOUNDS, CATEGORIES, FEATURES, NULLABLE


def parse_and_clean(text):
    # Reject bad width before pandas can silently create a shifted row index.
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines or any(len(line.split(",")) != 14 for line in lines):
        raise ValueError("Source must have 14 columns on every nonempty row")
    df = pd.read_csv(
        io.StringIO("\n".join(lines)),
        header=None,
        names=FEATURES + ["num"],
        na_values=["?"],
        keep_default_na=False,
        skipinitialspace=True,
    )
    df = df.apply(pd.to_numeric, errors="raise")
    reasons = {}
    invalid = pd.Series(False, index=df.index)
    for name in FEATURES + ["num"]:
        bad = df[name].notna() & ~np.isfinite(df[name])
        if name not in NULLABLE:
            bad |= df[name].isna()
        if name in CATEGORIES:
            bad |= df[name].notna() & ~df[name].isin(CATEGORIES[name])
        elif name == "num":
            bad |= ~df[name].isin([0, 1, 2, 3, 4])
        else:
            low, high = BOUNDS[name]
            bad |= df[name].notna() & ((df[name] < low) | (df[name] > high))
            if name in ["trestbps", "chol", "thalach"]:
                bad |= df[name] == 0
            if name == "age":
                bad |= df[name].notna() & (df[name] % 1 != 0)
        reasons[name] = int(bad.sum())
        invalid |= bad
    valid = df.loc[~invalid].copy()
    valid["target"] = (valid.pop("num") > 0).astype(int)
    groups = valid.groupby(FEATURES, dropna=False)["target"].transform("nunique")
    conflict = groups > 1
    conflicting_rows = int(conflict.sum())
    valid = valid.loc[~conflict]
    duplicates = int(valid.duplicated().sum())
    clean = valid.drop_duplicates().reset_index(drop=True)
    report = {
        "source_rows": len(df),
        "invalid_rows": int(invalid.sum()),
        "invalid_field_counts": reasons,
        "conflicting_rows": conflicting_rows,
        "duplicate_rows_removed": duplicates,
        "cleaned_rows": len(clean),
        "missing_by_feature": {c: int(clean[c].isna().sum()) for c in FEATURES},
        "target_counts": {str(k): int(v) for k, v in clean.target.value_counts().items()},
    }
    assert len(df) == report["invalid_rows"] + conflicting_rows + duplicates + len(clean)
    return clean, report
