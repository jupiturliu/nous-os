"""Contract test for second-vertical entry criterion #5.

'Public demo can be reproduced from README / getting-started commands.'

This guards against documentation drift: every ``python3 <path>`` and
``python3 -m <module>`` command documented in README.md and
docs/getting-started.md must point to an existing, importable target.
The lightweight no-external-deps command (``run_nous_heartbeat.py``) is
also invoked end-to-end to confirm the dashboard snapshot pipeline still
produces output the documented workflow promises.
"""

from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
GETTING_STARTED = ROOT / "docs" / "getting-started.md"

PYTHON_SCRIPT_RE = re.compile(r"python3?\s+(examples/[\w/.-]+\.py|scripts/[\w/.-]+\.py)")
PYTHON_MODULE_RE = re.compile(r"python3?\s+-m\s+([\w.]+)")


def _extract_script_paths(doc_text: str) -> set[str]:
    return set(PYTHON_SCRIPT_RE.findall(doc_text))


def _extract_module_names(doc_text: str) -> set[str]:
    return set(PYTHON_MODULE_RE.findall(doc_text))


class DocumentedCommandsExistTests(unittest.TestCase):
    """Every documented quickstart command must point to a real target."""

    def setUp(self) -> None:
        self.docs = {
            "README.md": README.read_text(encoding="utf-8"),
            "docs/getting-started.md": GETTING_STARTED.read_text(encoding="utf-8"),
        }

    def test_documented_script_paths_resolve_to_existing_files(self) -> None:
        missing: list[tuple[str, str]] = []
        for doc_name, text in self.docs.items():
            for rel in _extract_script_paths(text):
                target = ROOT / rel
                if not target.is_file():
                    missing.append((doc_name, rel))
        self.assertEqual(missing, [], f"documented scripts missing on disk: {missing}")

    def test_documented_python_modules_are_importable(self) -> None:
        # Only assert modules that ship with stdlib or this repo — third-party
        # modules documented for sibling repos are out of scope here.
        known_local_modules = {"unittest", "http.server"}
        unresolved: list[tuple[str, str]] = []
        for doc_name, text in self.docs.items():
            for module in _extract_module_names(text):
                if module in known_local_modules:
                    continue
                # Anything else documented as ``python3 -m`` should at least
                # exist as a runnable module — fail loudly when documentation
                # references something this repo cannot ship.
                try:
                    __import__(module)
                except ImportError as exc:
                    unresolved.append((doc_name, f"{module}: {exc}"))
        self.assertEqual(unresolved, [], f"documented modules not importable: {unresolved}")


class HeartbeatScriptIsRunnableTests(unittest.TestCase):
    """``run_nous_heartbeat.py`` is the documented public-release smoke entry.

    Documentation promises this command works from this repo alone. Invoke
    it as a subprocess (matching the documented invocation), confirm exit
    code 0, and confirm it produces the dashboard snapshot the docs
    advertise.
    """

    def test_run_nous_heartbeat_exits_zero_and_writes_snapshot(self) -> None:
        snapshot_path = ROOT / "examples" / "runtime" / "dashboard-data.json"
        original_mtime = snapshot_path.stat().st_mtime if snapshot_path.exists() else 0

        result = subprocess.run(
            [sys.executable, "scripts/run_nous_heartbeat.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )

        self.assertEqual(
            result.returncode, 0,
            f"run_nous_heartbeat.py exited {result.returncode}; stderr={result.stderr[-1000:]}",
        )
        self.assertTrue(snapshot_path.exists(), "dashboard snapshot was not produced")
        self.assertGreater(
            snapshot_path.stat().st_mtime, original_mtime,
            "dashboard snapshot mtime did not advance — script may have skipped writing",
        )


if __name__ == "__main__":
    unittest.main()
