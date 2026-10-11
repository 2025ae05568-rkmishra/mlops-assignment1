"""Prove the CI shell's pipefail keeps failed tests from promoting a release."""

import subprocess
import tempfile
from pathlib import Path

from heart_disease.common.io import now, write_json

with tempfile.TemporaryDirectory(prefix="mlops-failure-") as temporary:
    root = Path(temporary)
    test = root / "test_intentional_failure.py"
    test.write_text(
        'def test_intentional_failure():\n    assert False, "intentional release-gate failure"\n'
    )
    sentinel = root / "should-not-run"
    logs = Path("reports/evidence/runtime/intentional-failure.log")
    logs.parent.mkdir(parents=True, exist_ok=True)
    import shlex

    command = f"set -euo pipefail\n.venv/bin/python -m pytest {shlex.quote(str(test))} 2>&1 | tee {shlex.quote(str(logs))}\ntouch {shlex.quote(str(sentinel))}"
    result = subprocess.run(["bash", "-c", command], capture_output=True, text=True)
    assert result.returncode == 1
    assert not sentinel.exists()
    assert "intentional release-gate failure" in logs.read_text()
    write_json(
        "reports/evidence/failure-gate.json",
        {
            "captured_at": now(),
            "test_exit_code": result.returncode,
            "downstream_step_blocked": True,
            "diagnostic_log_retained": True,
            "scope": "local verification of the CI shell failure semantics; not a remote GitHub Actions run",
        },
    )
    print("Intentional test failure produced exit 1, retained diagnostics and blocked promotion.")
