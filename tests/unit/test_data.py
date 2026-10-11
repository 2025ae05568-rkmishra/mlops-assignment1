import numpy as np
import pandas as pd
import pytest

from heart_disease.data.split import make_splits
from heart_disease.data.validate import parse_and_clean
from heart_disease.features.schema import FEATURES

ROW = "63,1,1,145,233,1,2,150,0,2.3,3,?,6,0"


def test_cleaning_missing_duplicates_and_conflicts():
    clean, report = parse_and_clean(ROW + "\n" + ROW)
    assert len(clean) == 1 and np.isnan(clean.ca.iloc[0])
    assert report["duplicate_rows_removed"] == 1
    clean, report = parse_and_clean(ROW + "\n" + ROW[:-1] + "1")
    assert clean.empty and report["conflicting_rows"] == 2


@pytest.mark.parametrize("text", [ROW + ",99", "age,sex", ROW.replace("233", "bad")])
def test_malformed_source_rejected(text):
    with pytest.raises(ValueError):
        parse_and_clean(text)


def test_unknown_codes_and_missing_target_quarantined():
    _, report = parse_and_clean(ROW.replace("63,1,1,", "63,1,0,") + "\n" + ROW[:-1] + "?")
    assert report["invalid_rows"] == 2
    assert report["cleaned_rows"] == 0


def test_disjoint_repeatable_split():
    data = pd.DataFrame(
        [
            {
                **dict(
                    zip(FEATURES, [i + 20, 1, 2, 120, 200, 0, 0, 160, 0, 1, 2, 0, 3], strict=True)
                ),
                "target": i % 2,
            }
            for i in range(60)
        ]
    )
    a, b = make_splits(data), make_splits(data)
    assert a == b
    assert set(a["train_indices"]).isdisjoint(a["test_indices"])
    assert len(a["cv_assignments"]) == len(a["train_indices"])
    assert {x["fold"] for x in a["cv_assignments"]} == set(range(5))


def test_cached_acquisition_verifies_checksum_without_network(tmp_path, monkeypatch):
    from heart_disease.common.io import sha256, write_json
    from heart_disease.data.acquire import acquire

    monkeypatch.chdir(tmp_path)
    (tmp_path / "config.yaml").write_text("source_member: processed.cleveland.data\n")
    raw = tmp_path / "data/raw/processed.cleveland.data"
    raw.parent.mkdir(parents=True)
    raw.write_text(ROW)
    write_json("data/manifests/source-lock.json", {"member_sha256": sha256(raw)})
    assert acquire("config.yaml") == raw.relative_to(tmp_path)
    raw.write_text(ROW + "altered")
    with pytest.raises(ValueError, match="checksum"):
        acquire("config.yaml")
