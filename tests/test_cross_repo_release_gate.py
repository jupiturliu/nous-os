from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import check_cross_repo_release_gate as gate


def _init_repo(path: Path) -> None:
    path.mkdir(parents=True)
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=path, check=True)
    (path / "README.md").write_text("# Test\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=path, check=True, capture_output=True)


def test_release_gate_reports_missing_repos(tmp_path: Path) -> None:
    report = gate.build_report(tmp_path)

    assert report["ok"] is False
    assert report["repos"]["nous-os"]["exists"] is False
    assert "repository missing" in report["repos"]["nous-os"]["issues"]


def test_release_gate_detects_dirty_repo(tmp_path: Path) -> None:
    repo = tmp_path / "nous-os"
    _init_repo(repo)
    (repo / "README.md").write_text("# Test\n\nchanged\n", encoding="utf-8")

    report = gate.build_report(tmp_path)

    assert report["repos"]["nous-os"]["exists"] is True
    assert report["repos"]["nous-os"]["dirty"] is True


def test_release_gate_scans_secret_like_tokens(tmp_path: Path) -> None:
    repo = tmp_path / "nous-os"
    _init_repo(repo)
    (repo / "docs").mkdir()
    (repo / "docs" / "bad.md").write_text("api_key = abcdefghijklmnopqrstuvwxyz123456\n", encoding="utf-8")

    report = gate.build_report(tmp_path)

    assert any("secret-like token" in issue for issue in report["repos"]["nous-os"]["issues"])


def test_release_gate_allows_documented_workspace_paths(tmp_path: Path) -> None:
    repo = tmp_path / "nous-os"
    _init_repo(repo)
    (repo / "docs").mkdir()
    (repo / "docs" / "paths.md").write_text(
        "Run with --workspace /Users/liyao/nousos for the local dev workspace.\n",
        encoding="utf-8",
    )

    report = gate.build_report(tmp_path)

    assert not any("private absolute path" in issue for issue in report["repos"]["nous-os"]["issues"])


def test_release_gate_cli_json_shape(tmp_path: Path, capsys) -> None:
    code = gate.main(["--workspace", str(tmp_path), "--json"])
    out = capsys.readouterr().out
    payload = json.loads(out)

    assert code == 1
    assert "repos" in payload
    assert "nous-os" in payload["repos"]
