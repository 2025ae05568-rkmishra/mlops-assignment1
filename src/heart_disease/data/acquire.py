import argparse
import hashlib
import io
import urllib.request
import zipfile
from pathlib import Path

from heart_disease.common.io import config, now, read_json, sha256, write_json


def acquire(config_path="configs/data.yaml", initialize=False):
    cfg = config(config_path)
    raw = Path("data/raw") / cfg["source_member"]
    lock_path = Path("data/manifests/source-lock.json")
    lock = read_json(lock_path) if lock_path.exists() else None
    if lock and raw.exists():
        if sha256(raw) != lock["member_sha256"]:
            raise ValueError("Cached source checksum mismatch; refusing changed data")
        return raw
    if lock is None and not initialize:
        raise ValueError("Source lock missing; initial acquisition requires --initialize-source")
    with urllib.request.urlopen(cfg["source_url"], timeout=60) as response:
        archive = response.read(2_000_001)
    if len(archive) > 2_000_000:
        raise ValueError("Unexpected source download size")
    archive_hash = hashlib.sha256(archive).hexdigest()
    if lock and archive_hash != lock["archive_sha256"]:
        raise ValueError("Upstream archive checksum mismatch")
    with zipfile.ZipFile(io.BytesIO(archive)) as zf:
        content = zf.read(cfg["source_member"])
    member_hash = hashlib.sha256(content).hexdigest()
    if lock and member_hash != lock["member_sha256"]:
        raise ValueError("Source member checksum mismatch")
    raw.parent.mkdir(parents=True, exist_ok=True)
    raw.write_bytes(content)
    if lock is None:
        write_json(
            lock_path,
            {
                **cfg,
                "retrieved_at": now(),
                "archive_sha256": archive_hash,
                "member_sha256": member_hash,
                "byte_count": len(content),
            },
        )
    return raw


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/data.yaml")
    parser.add_argument("--initialize-source", action="store_true")
    args = parser.parse_args()
    print(acquire(args.config, args.initialize_source))
