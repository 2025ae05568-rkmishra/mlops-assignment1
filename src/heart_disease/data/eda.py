import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from heart_disease.common.io import read_json, sha256
from heart_disease.features.schema import CATEGORIES, NUMERIC


def eda(output="reports/figures"):
    df = pd.read_csv("data/processed/cleaned.csv")
    split = read_json("data/manifests/split.json")
    if sha256("data/processed/cleaned.csv") != split["processed_sha256"]:
        raise ValueError("EDA dataset differs from persisted split")
    train = df.iloc[split["train_indices"]]
    dest = Path(output)
    dest.mkdir(parents=True, exist_ok=True)
    label = f"Training partition n={len(train)}; data {split['processed_sha256'][:12]}"
    sns.set_theme(style="whitegrid")
    units = {
        "age": "years",
        "trestbps": "mm Hg",
        "chol": "mg/dL",
        "thalach": "beats/min",
        "oldpeak": "ST depression",
    }
    fig, axes = plt.subplots(2, 3, figsize=(12, 7))
    for col, ax in zip(NUMERIC, axes.flat, strict=False):
        sns.histplot(train[col], bins=16, ax=ax)
        ax.set_xlabel(f"{col} ({units[col]})")
    axes.flat[-1].set_visible(False)
    fig.suptitle(label)
    fig.tight_layout()
    fig.savefig(dest / "histograms.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 6))
    sns.heatmap(
        train[NUMERIC + ["target"]].corr(),
        annot=True,
        fmt=".2f",
        vmin=-1,
        vmax=1,
        cmap="vlag",
        ax=ax,
    )
    ax.set_title("Pearson correlation: numeric features and binary target\n" + label)
    fig.tight_layout()
    fig.savefig(dest / "correlation_heatmap.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.countplot(data=train, x="target", ax=ax)
    ax.set_xticks([0, 1], ["Absent (0)", "Present (1)"])
    ax.set_title("Class balance — " + label)
    fig.tight_layout()
    fig.savefig(dest / "class_balance.png", dpi=160)
    plt.close(fig)
    fig, axes = plt.subplots(2, 4, figsize=(14, 7))
    for col, ax in zip(CATEGORIES, axes.flat, strict=True):
        sns.countplot(data=train, x=col, ax=ax)
    fig.suptitle("Original source category codes — " + label)
    fig.tight_layout()
    fig.savefig(dest / "categories.png", dpi=160)
    plt.close(fig)
    train.isna().sum().to_csv(dest / "missingness.csv", header=["missing_count"])
    print(f"EDA exported to {dest}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="reports/figures")
    eda(parser.parse_args().output)
