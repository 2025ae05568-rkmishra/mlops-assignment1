"""Serve a disposable, rebased copy of the selected GitHub release's MLflow DB."""

import os
import shutil
import sqlite3
from pathlib import Path

from heart_disease.common.io import read_json


def rebase_database(source, destination, artifacts):
    """Only change the copied export's local artifact URI prefixes."""
    shutil.copy2(source, destination)
    with sqlite3.connect(destination) as db:
        for table, key, column in (
            ("experiments", "experiment_id", "artifact_location"),
            ("runs", "run_uuid", "artifact_uri"),
        ):
            for identity, uri in db.execute(f"SELECT {key}, {column} FROM {table}").fetchall():
                if uri and "/mlruns/" in uri:
                    tail = uri.split("/mlruns/", 1)[1]
                    target = (Path(artifacts) / tail).resolve()
                    if not target.is_relative_to(Path(artifacts).resolve()):
                        raise ValueError("Invalid exported artifact path")
                    db.execute(
                        f"UPDATE {table} SET {column} = ? WHERE {key} = ?",
                        (target.as_uri(), identity),
                    )


if __name__ == "__main__":
    pointer = Path("reports/evidence/runtime/latest-submission.txt")
    if not pointer.exists():
        raise SystemExit("Run the BITS deployment first; no selected-release evidence exists.")
    evidence = Path(pointer.read_text().strip())
    source = Path(read_json(evidence / "release.json")["release_root"])
    destination = evidence / "mlflow-view.db"
    rebase_database(source / "mlflow.db", destination, source / "mlruns")
    command = [
        ".venv/bin/mlflow",
        "server",
        "--backend-store-uri",
        f"sqlite:///{destination.resolve()}",
        "--host",
        "127.0.0.1",
        "--port",
        "5000",
    ]
    os.execv(command[0], command)
