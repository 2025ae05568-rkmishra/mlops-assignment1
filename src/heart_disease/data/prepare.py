import argparse
from pathlib import Path

from heart_disease.common.io import config, sha256, write_json
from heart_disease.data.acquire import acquire
from heart_disease.data.split import make_splits
from heart_disease.data.validate import parse_and_clean
from heart_disease.features.schema import feature_schema


def prepare(config_path="configs/data.yaml"):
    cfg = config(config_path)
    raw = acquire(config_path)
    df, cleaning = parse_and_clean(raw.read_text())
    dest = Path("data/processed/cleaned.csv")
    dest.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(dest, index=False)
    # Persist splits against exactly the CSV representation used for training.
    import pandas as pd

    df = pd.read_csv(dest)
    split = make_splits(df, cfg["seed"], cfg["test_size"], cfg["folds"])
    split["processed_sha256"] = sha256(dest)
    write_json("data/manifests/split.json", split)
    write_json(
        "data/manifests/cleaning.json",
        {**cleaning, "raw_sha256": sha256(raw), "processed_sha256": sha256(dest)},
    )
    write_json("data/manifests/feature-schema.json", feature_schema())
    print(
        f"Prepared {len(df)} rows; train={len(split['train_indices'])}, test={len(split['test_indices'])}"
    )
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/data.yaml")
    prepare(parser.parse_args().config)
