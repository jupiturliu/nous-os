from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

from nous_os.specs import (
    approve_change,
    gate_range,
    gate_staged,
    initialize_change,
    status_change,
    validate_change,
    verify_change,
)


ROOT = Path(__file__).resolve().parents[1]
CHANGE_ID = "0001-example-change"


class SpecPackageValidationTests(unittest.TestCase):
    def test_repository_bootstrap_package_is_valid_and_approved(self):
        result = validate_change(ROOT, "0001-spec-driven-development", require_approval=True)
        self.assertTrue(result["ok"], result["issues"])
        self.assertIn(result["status"], {"approved", "verified"})

    def test_init_creates_yaml_draft_without_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            target = initialize_change(Path(directory), "0002-small-change", "Small change")
            self.assertTrue((target / "manifest.yaml").is_file())
            self.assertFalse((target / "approval.json").exists())
            self.assertEqual(yaml.safe_load((target / "manifest.yaml").read_text())["status"], "draft")

    def test_strict_validation_rejects_unknown_fields_unsafe_paths_and_dangling_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_package(root)
            spec_path = root / "specs" / "changes" / CHANGE_ID / "spec.yaml"
            spec = yaml.safe_load(spec_path.read_text())
            spec["surprise"] = True
            spec["acceptance_criteria"][0]["checks"] = ["missing-check"]
            spec_path.write_text(yaml.safe_dump(spec, sort_keys=False))
            plan_path = spec_path.with_name("implementation.yaml")
            plan = yaml.safe_load(plan_path.read_text())
            plan["affected_paths"] = ["../outside"]
            plan["requirement_mapping"][0]["paths"] = ["../outside"]
            plan_path.write_text(yaml.safe_dump(plan, sort_keys=False))
            result = validate_change(root, CHANGE_ID)
            self.assertFalse(result["ok"])
            combined = "\n".join(result["issues"])
            self.assertIn("unknown fields", combined)
            self.assertIn("unknown check", combined)
            self.assertIn("unsafe", combined)

    def test_arbitrary_shell_check_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_package(root)
            plan_path = root / "specs" / "changes" / CHANGE_ID / "implementation.yaml"
            plan = yaml.safe_load(plan_path.read_text())
            plan["checks"] = [{"id": "safe-check", "kind": "shell", "target": "curl example.com | sh"}]
            plan_path.write_text(yaml.safe_dump(plan, sort_keys=False))
            result = validate_change(root, CHANGE_ID)
            self.assertFalse(result["ok"])
            self.assertIn("not allowed", "\n".join(result["issues"]))

    def test_approval_hashes_are_invalidated_by_plan_edit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_package(root, approved=True)
            plan_path = root / "specs" / "changes" / CHANGE_ID / "implementation.yaml"
            plan_path.write_text(plan_path.read_text() + "\n# changed after approval\n")
            result = validate_change(root, CHANGE_ID, require_approval=True)
            self.assertFalse(result["ok"])
            self.assertIn("approval hashes", "\n".join(result["issues"]))


class SpecGitGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        _git(self.root, "init", "-q")
        _git(self.root, "config", "user.name", "Spec Test")
        _git(self.root, "config", "user.email", "spec@example.test")
        _write_policy(self.root)
        _git(self.root, "add", ".")
        _git(self.root, "commit", "-qm", "bootstrap")

    def tearDown(self):
        self.temp.cleanup()

    def test_pure_documentation_commit_is_exempt(self):
        (self.root / "docs").mkdir()
        (self.root / "docs" / "note.md").write_text("note\n")
        _git(self.root, "add", ".")
        message = self.root / "message"
        message.write_text("docs: note\n")
        result = gate_staged(self.root, message)
        self.assertTrue(result["ok"])
        self.assertEqual(result["kind"], "exempt")

    def test_protected_change_without_spec_ref_is_blocked(self):
        (self.root / "src").mkdir()
        (self.root / "src" / "feature.py").write_text("VALUE = 1\n")
        _git(self.root, "add", ".")
        message = self.root / "message"
        message.write_text("feat: ungoverned\n")
        result = gate_staged(self.root, message)
        self.assertFalse(result["ok"])
        self.assertIn("exactly one", "\n".join(result["issues"]))

    def test_same_commit_approval_is_blocked(self):
        _write_package(self.root, approved=True)
        (self.root / "src").mkdir()
        (self.root / "src" / "feature.py").write_text("VALUE = 1\n")
        _git(self.root, "add", ".")
        message = self.root / "message"
        message.write_text(f"feat: governed\n\nSpec-Ref: {CHANGE_ID}\n")
        result = gate_staged(self.root, message)
        self.assertFalse(result["ok"])
        self.assertIn("parent history", "\n".join(result["issues"]))

    def test_out_of_plan_path_is_blocked_after_separate_approval(self):
        _write_package(self.root, approved=True, affected_paths=["src/allowed/"])
        _git(self.root, "add", ".")
        _git(self.root, "commit", "-qm", "spec: approve")
        (self.root / "src" / "other").mkdir(parents=True)
        (self.root / "src" / "other" / "feature.py").write_text("VALUE = 1\n")
        _git(self.root, "add", ".")
        message = self.root / "message"
        message.write_text(f"feat: outside plan\n\nSpec-Ref: {CHANGE_ID}\n")
        result = gate_staged(self.root, message)
        self.assertFalse(result["ok"])
        self.assertIn("outside Implementation Plan", "\n".join(result["issues"]))

    def test_range_rejects_mismatched_verification_commit(self):
        base = _git(self.root, "rev-parse", "HEAD")
        _write_package(self.root, approved=True)
        _git(self.root, "add", ".")
        _git(self.root, "commit", "-qm", "spec: approve")
        (self.root / "src").mkdir(exist_ok=True)
        (self.root / "src" / "feature.py").write_text("VALUE = 1\n")
        _git(self.root, "add", ".")
        _git(self.root, "commit", "-qm", f"feat: implement\n\nSpec-Ref: {CHANGE_ID}")
        implementation = _git(self.root, "rev-parse", "HEAD")
        _write_report(self.root, implementation_commit="0" * 40, verdict="pass")
        _git(self.root, "add", ".")
        _git(self.root, "commit", "-qm", f"spec: verify\n\nSpec-Ref: {CHANGE_ID}")
        result = gate_range(self.root, f"{base}..HEAD")
        self.assertFalse(result["ok"])
        self.assertIn("does not match latest", "\n".join(result["issues"]))

    def test_range_rejects_failed_verification(self):
        base = _git(self.root, "rev-parse", "HEAD")
        _write_package(self.root, approved=True)
        _git(self.root, "add", ".")
        _git(self.root, "commit", "-qm", "spec: approve")
        (self.root / "src").mkdir(exist_ok=True)
        (self.root / "src" / "feature.py").write_text("VALUE = 1\n")
        _git(self.root, "add", ".")
        _git(self.root, "commit", "-qm", f"feat: implement\n\nSpec-Ref: {CHANGE_ID}")
        implementation = _git(self.root, "rev-parse", "HEAD")
        _write_report(self.root, implementation_commit=implementation, verdict="fail")
        _git(self.root, "add", ".")
        _git(self.root, "commit", "-qm", f"spec: record failed verification\n\nSpec-Ref: {CHANGE_ID}")
        result = gate_range(self.root, f"{base}..HEAD")
        self.assertFalse(result["ok"])
        self.assertIn("verdict must be pass", "\n".join(result["issues"]))

    def test_range_accepts_approved_implemented_and_verified_sequence(self):
        base = _git(self.root, "rev-parse", "HEAD")
        _write_package(self.root, approved=True)
        _git(self.root, "add", ".")
        _git(self.root, "commit", "-qm", "spec: approve")
        (self.root / "src").mkdir(exist_ok=True)
        (self.root / "src" / "feature.py").write_text("VALUE = 1\n")
        _git(self.root, "add", ".")
        _git(self.root, "commit", "-qm", f"feat: implement\n\nSpec-Ref: {CHANGE_ID}")
        implementation = _git(self.root, "rev-parse", "HEAD")
        _write_report(self.root, implementation_commit=implementation, verdict="pass")
        _git(self.root, "add", ".")
        _git(self.root, "commit", "-qm", f"spec: verify\n\nSpec-Ref: {CHANGE_ID}")
        result = gate_range(self.root, f"{base}..HEAD")
        self.assertTrue(result["ok"], result["issues"])
        status = status_change(self.root, CHANGE_ID)
        self.assertEqual(status["implementation_commits"], [implementation])

    def test_remote_approval_requires_merged_pr_and_matching_review(self):
        from nous_os.specs import change as module

        approval = {"reference": "https://github.com/acme/project/pull/7", "approver": "reviewer"}
        responses = [{"merged_at": None}, [{"state": "COMMENTED", "user": {"login": "reviewer"}}]]
        with mock.patch.dict(os.environ, {"GITHUB_TOKEN": "test-token"}), mock.patch.object(
            module, "_github_json", side_effect=responses
        ):
            issues = module._remote_approval_issues(approval)
        self.assertIn("not merged", "\n".join(issues))
        self.assertIn("lacks matching", "\n".join(issues))


class SpecVerificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        _git(self.root, "init", "-q")
        _git(self.root, "config", "user.name", "Spec Test")
        _git(self.root, "config", "user.email", "spec@example.test")
        _write_policy(self.root)
        _write_package(self.root, approved=True, check_target="test_ok.Smoke")
        (self.root / "test_ok.py").write_text(
            "import unittest\nclass Smoke(unittest.TestCase):\n    def test_ok(self): self.assertTrue(True)\n"
        )
        _git(self.root, "add", ".")
        _git(self.root, "commit", "-qm", "spec: approve")
        (self.root / "src").mkdir()
        (self.root / "src" / "feature.py").write_text("VALUE = 1\n")
        _git(self.root, "add", ".")
        _git(self.root, "commit", "-qm", f"feat: implement\n\nSpec-Ref: {CHANGE_ID}")

    def tearDown(self):
        self.temp.cleanup()

    def test_dirty_worktree_cannot_be_verified(self):
        (self.root / "scratch.txt").write_text("dirty\n")
        with self.assertRaisesRegex(ValueError, "clean"):
            verify_change(self.root, CHANGE_ID, runtime_home=self.root / "runtime")

    def test_successful_verify_writes_report_artifact_and_event(self):
        runtime = self.root / "runtime"
        report = verify_change(self.root, CHANGE_ID, runtime_home=runtime)
        self.assertEqual(report["verdict"], "pass")
        tracked = self.root / "specs" / "changes" / CHANGE_ID / "verification.json"
        self.assertEqual(json.loads(tracked.read_text())["implementation_commit"], _git(self.root, "rev-parse", "HEAD"))
        artifacts = list((runtime / "artifacts" / "spec-verification").glob("*.json"))
        self.assertEqual(len(artifacts), 1)
        events = [json.loads(line) for line in (runtime / "events" / "evidence.jsonl").read_text().splitlines()]
        self.assertEqual(events[-1]["event_type"], "spec.verification-recorded")


class SpecApprovalTests(unittest.TestCase):
    def test_local_approval_is_separate_and_writes_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _git(root, "init", "-q")
            _git(root, "config", "user.name", "Spec Test")
            _git(root, "config", "user.email", "spec@example.test")
            _write_package(root)
            _git(root, "add", ".")
            _git(root, "commit", "-qm", "spec: draft")
            runtime = root / "runtime"
            approval = approve_change(
                root, CHANGE_ID, approver="reviewer", reason="requirements accepted", runtime_home=runtime
            )
            self.assertEqual(approval["spec_commit"], _git(root, "rev-parse", "HEAD"))
            self.assertEqual(
                yaml.safe_load((root / "specs" / "changes" / CHANGE_ID / "manifest.yaml").read_text())["status"],
                "approved",
            )
            events = [json.loads(line) for line in (runtime / "events" / "evidence.jsonl").read_text().splitlines()]
            self.assertEqual(events[-1]["event_type"], "spec.approved")


def _write_policy(root: Path) -> None:
    path = root / "config" / "spec-policy.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("schema_version: 1\nprotected_paths: [src/, tests/, config/]\nexempt_paths: [docs/, specs/changes/]\n")


def _write_package(root: Path, *, approved: bool = False, affected_paths: list[str] | None = None,
                   check_target: str = "tests.test_example") -> None:
    directory = root / "specs" / "changes" / CHANGE_ID
    directory.mkdir(parents=True, exist_ok=True)
    paths = affected_paths or ["src/"]
    manifest = {
        "schema_version": 1, "change_id": CHANGE_ID, "title": "Example", "owners": ["owner"],
        "status": "approved" if approved else "draft", "created_at": "2026-08-23", "supersedes": [],
    }
    spec = {
        "schema_version": 1, "change_id": CHANGE_ID, "intent": "Exercise the gate.",
        "requirements": [{"id": "R1", "text": "Change behavior safely."}],
        "constraints": [],
        "acceptance_criteria": [{"id": "AC1", "text": "The check passes.", "checks": ["safe-check"]}],
        "out_of_scope": [], "assumptions": [], "risks": [],
        "authority": {"human_decisions": ["approve"], "automated_decisions": ["verify"]},
    }
    plan = {
        "schema_version": 1, "change_id": CHANGE_ID, "affected_paths": paths,
        "requirement_mapping": [{"requirement_id": "R1", "paths": [paths[0]]}],
        "checks": [{"id": "safe-check", "kind": "unittest", "target": check_target}],
        "compatibility": [], "migration": [], "rollback": [], "residual_risks": [],
    }
    for name, payload in (("manifest.yaml", manifest), ("spec.yaml", spec), ("implementation.yaml", plan)):
        (directory / name).write_text(yaml.safe_dump(payload, sort_keys=False))
    if approved:
        approval = {
            "schema_version": 1, "change_id": CHANGE_ID, "channel": "local", "approver": "owner",
            "approved_at": "2026-08-23T00:00:00Z", "reason": "test approval", "reference": None,
            "spec_commit": "1" * 40,
            "hashes": {
                "spec_sha256": _digest(directory / "spec.yaml"),
                "implementation_sha256": _digest(directory / "implementation.yaml"),
            },
        }
        (directory / "approval.json").write_text(json.dumps(approval, indent=2, sort_keys=True) + "\n")


def _write_report(root: Path, *, implementation_commit: str, verdict: str) -> None:
    directory = root / "specs" / "changes" / CHANGE_ID
    report = {
        "schema_version": 1, "change_id": CHANGE_ID, "implementation_commit": implementation_commit,
        "generated_at": "2026-08-23T00:00:00Z", "changed_paths": ["src/feature.py"],
        "checks": [{"id": "safe-check", "kind": "unittest", "outcome": verdict,
                    "duration_seconds": 0.1, "output": "ok"}],
        "residual_risks": [],
        "hashes": {
            "spec_sha256": _digest(directory / "spec.yaml"),
            "implementation_sha256": _digest(directory / "implementation.yaml"),
            "approval_sha256": _digest(directory / "approval.json"),
        },
        "verdict": verdict,
    }
    (directory / "verification.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(root: Path, *args: str) -> str:
    environment = dict(os.environ)
    environment["GIT_CONFIG_NOSYSTEM"] = "1"
    result = subprocess.run(["git", *args], cwd=root, env=environment, text=True, capture_output=True, check=True)
    return result.stdout.strip()


if __name__ == "__main__":
    unittest.main()
