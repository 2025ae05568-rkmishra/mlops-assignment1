import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import yaml


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def read_json(path):
    return json.loads(Path(path).read_text())


def config(path):
    return yaml.safe_load(Path(path).read_text())


def now():
    return datetime.now(timezone.utc).isoformat()


def code_identity():
    paths = sorted(Path("src").rglob("*.py"))
    code_hash = digest({str(p): sha256(p) for p in paths})
    result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
    status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    return {
        "commit": result.stdout.strip() if result.returncode == 0 else "uncommitted",
        "dirty": bool(status.stdout.strip()),
        "code_hash": code_hash,
    }
