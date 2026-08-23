"""Deep Module for Software Change Spec lifecycle, gates, and verification."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

import yaml

from nous_os.core import EvidenceEvent, EventStore, RuntimePaths


CHANGE_ID = re.compile(r"^[0-9]{4}-[a-z0-9]+(?:-[a-z0-9]+)*$")
TRAILER = re.compile(r"^Spec-Ref:\s*(\S+)\s*$", re.MULTILINE)
PACKAGE_FILES = ("manifest.yaml", "spec.yaml", "implementation.yaml")
ALLOWED_CHECK_KINDS = {"unittest", "harness", "profiles", "contracts", "site"}
ZERO_SHA = "0" * 40


@dataclass(frozen=True)
class ChangePackage:
    root: Path
    change_id: str
    manifest: dict[str, Any]
    spec: dict[str, Any]
    implementation: dict[str, Any]
    approval: dict[str, Any] | None
    verification: dict[str, Any] | None
    revision_hashes: dict[str, str] | None = None
    revision_approval_hash: str | None = None

    @property
    def directory(self) -> Path:
        return self.root / "specs" / "changes" / self.change_id

    @property
    def hashes(self) -> dict[str, str]:
        if self.revision_hashes is not None:
            return self.revision_hashes
        return {
            "spec_sha256": _sha256(self.directory / "spec.yaml"),
            "implementation_sha256": _sha256(self.directory / "implementation.yaml"),
        }


def initialize_change(root: Path, change_id: str, title: str) -> Path:
    """Create a strict draft package; callers edit requirements before approval."""
    _require_change_id(change_id)
    if not title.strip():
        raise ValueError("title must not be empty")
    directory = root / "specs" / "changes" / change_id
    if directory.exists():
        raise ValueError(f"change already exists: {change_id}")
    directory.mkdir(parents=True)
    today = date.today().isoformat()
    _write_yaml(directory / "manifest.yaml", {
        "schema_version": 1, "change_id": change_id, "title": title.strip(),
        "owners": [], "status": "draft", "created_at": today, "supersedes": [],
    })
    _write_yaml(directory / "spec.yaml", {
        "schema_version": 1, "change_id": change_id, "intent": "",
        "requirements": [], "constraints": [], "acceptance_criteria": [],
        "out_of_scope": [], "assumptions": [], "risks": [],
        "authority": {"human_decisions": [], "automated_decisions": []},
    })
    _write_yaml(directory / "implementation.yaml", {
        "schema_version": 1, "change_id": change_id, "affected_paths": [],
        "requirement_mapping": [], "checks": [], "compatibility": [],
        "migration": [], "rollback": [], "residual_risks": [],
    })
    return directory


def validate_change(root: Path, change_id: str, *, require_approval: bool = False,
                    require_verification: bool = False) -> dict[str, Any]:
    package = _load_package(root, change_id)
    issues = _validate_package(package, require_approval=require_approval,
                               require_verification=require_verification)
    return {"ok": not issues, "change_id": change_id, "issues": issues,
            "status": _derived_status(package, issues)}


def approve_change(root: Path, change_id: str, *, approver: str, reason: str,
                   channel: str = "local", reference: str | None = None,
                   runtime_home: str | Path | None = None) -> dict[str, Any]:
    """Record explicit human approval against immutable Spec/Plan hashes."""
    if channel not in {"local", "pull-request"}:
        raise ValueError("approval channel must be local or pull-request")
    if not approver.strip() or not reason.strip():
        raise ValueError("approval requires a real approver and reason")
    if channel == "pull-request" and not reference:
        raise ValueError("pull-request approval requires --reference")
    _require_clean(root)
    package = _load_package(root, change_id)
    issues = _validate_package(package, require_approval=False)
    if issues:
        raise ValueError("invalid change package: " + "; ".join(issues))
    if package.approval:
        raise ValueError(f"change already approved: {change_id}")
    head = _git(root, "rev-parse", "HEAD")
    for filename in PACKAGE_FILES:
        tracked = _git(root, "show", f"HEAD:specs/changes/{change_id}/{filename}", check=False)
        if tracked is None:
            raise ValueError("Spec and Implementation Plan must be committed before approval")
    approval = {
        "schema_version": 1,
        "change_id": change_id,
        "channel": channel,
        "approver": approver.strip(),
        "approved_at": _now(),
        "reason": reason.strip(),
        "reference": reference,
        "spec_commit": head,
        "hashes": package.hashes,
    }
    _write_json(package.directory / "approval.json", approval)
    manifest = dict(package.manifest)
    manifest["status"] = "approved"
    _write_yaml(package.directory / "manifest.yaml", manifest)
    store = EventStore(RuntimePaths.resolve(runtime_home))
    artifact = store.write_artifact("spec-approval", approval, change_id)
    store.append(EvidenceEvent(
        event_type="spec.approved", run_id=f"spec-{change_id}", profile="development",
        producer="software-change-spec", payload={"change_id": change_id, "channel": channel,
        "approver": approver.strip()}, evidence_refs=(artifact,), privacy="internal",
    ))
    return approval


def status_change(root: Path, change_id: str) -> dict[str, Any]:
    package = _load_package(root, change_id)
    issues = _validate_package(package)
    commits = _implementation_commits(root, change_id, package)
    return {
        "change_id": change_id,
        "declared_status": package.manifest.get("status"),
        "derived_status": _derived_status(package, issues, commits),
        "valid": not issues,
        "approved": package.approval is not None and not _approval_issues(package),
        "implementation_commits": commits,
        "verified": bool(package.verification and package.verification.get("verdict") == "pass"),
        "issues": issues,
    }


def verify_change(root: Path, change_id: str, *, runtime_home: str | Path | None = None) -> dict[str, Any]:
    """Run only declared safe checks and write tracked plus runtime verification evidence."""
    _require_clean(root)
    package = _load_package(root, change_id)
    issues = _validate_package(package, require_approval=True)
    if issues:
        raise ValueError("invalid approved change: " + "; ".join(issues))
    commits = _implementation_commits(root, change_id, package)
    if not commits:
        raise ValueError("no committed implementation found for change")
    head = _git(root, "rev-parse", "HEAD")
    if commits[-1] != head:
        raise ValueError("verification must run on the clean latest implementation commit")
    changed_paths = _implementation_paths(root, commits)
    coverage = _path_coverage_issues(changed_paths, package.implementation["affected_paths"])
    if coverage:
        raise ValueError("implementation path coverage failed: " + "; ".join(coverage))

    results = [_run_check(root, check, runtime_home) for check in package.implementation["checks"]]
    verdict = "pass" if all(result["outcome"] == "pass" for result in results) else "fail"
    report = {
        "schema_version": 1,
        "change_id": change_id,
        "implementation_commit": head,
        "generated_at": _now(),
        "changed_paths": changed_paths,
        "checks": results,
        "residual_risks": package.implementation["residual_risks"],
        "hashes": {**package.hashes, "approval_sha256": _sha256(package.directory / "approval.json")},
        "verdict": verdict,
    }
    _write_json(package.directory / "verification.json", report)
    store = EventStore(RuntimePaths.resolve(runtime_home))
    artifact = store.write_artifact("spec-verification", report, f"{change_id}-{head[:12]}")
    store.append(EvidenceEvent(
        event_type="spec.verification-recorded", run_id=f"spec-{change_id}-{head[:12]}",
        profile="development", producer="software-change-spec",
        payload={"change_id": change_id, "implementation_commit": head, "verdict": verdict},
        evidence_refs=(artifact,), privacy="internal",
    ))
    return report


def gate_staged(root: Path, message_file: Path) -> dict[str, Any]:
    """Enforce temporal approval and planned-path coverage for the staged commit."""
    paths = _lines(_git(root, "diff", "--cached", "--name-only", "--diff-filter=ACMRD"))
    if not paths:
        return {"ok": True, "kind": "empty", "issues": []}
    policy = _load_policy(root)
    protected = [path for path in paths if _is_protected(path, policy)]
    non_spec = [path for path in paths if not _is_spec_path(path)]
    spec_ids = sorted({path.split("/", 3)[2] for path in paths if path.startswith("specs/changes/") and len(path.split("/")) > 3})
    if not non_spec and spec_ids:
        issues: list[str] = []
        for change_id in spec_ids:
            try:
                issues.extend(_validate_package(_load_package(root, change_id)))
            except (FileNotFoundError, ValueError) as error:
                issues.append(str(error))
        return {"ok": not issues, "kind": "spec-artifact", "issues": _unique(issues)}
    if not protected:
        return {"ok": True, "kind": "exempt", "issues": []}
    message = message_file.read_text(encoding="utf-8")
    refs = sorted(set(TRAILER.findall(message)))
    issues: list[str] = []
    if len(refs) != 1:
        issues.append("protected commit requires exactly one Spec-Ref: <change-id> trailer")
        return {"ok": False, "kind": "implementation", "issues": issues}
    change_id = refs[0]
    try:
        _require_change_id(change_id)
        package = _load_package_at(root, change_id, "HEAD")
    except (FileNotFoundError, ValueError) as error:
        return {"ok": False, "kind": "implementation", "issues": [
            f"approval must exist in parent history; same-commit approval is forbidden ({error})"
        ]}
    issues.extend(_validate_package(package, require_approval=True))
    if spec_ids:
        issues.append("approved Spec artifacts cannot change in an implementation commit")
    issues.extend(_path_coverage_issues(non_spec, package.implementation.get("affected_paths", [])))
    return {"ok": not issues, "kind": "implementation", "change_id": change_id, "issues": _unique(issues)}


def gate_range(root: Path, revision_range: str, *, require_remote_approval: bool = False) -> dict[str, Any]:
    """Validate every introduced commit and require final passing evidence for implementations."""
    commits = _lines(_git(root, "rev-list", "--reverse", revision_range))
    policy = _load_policy(root)
    issues: list[str] = []
    implemented: dict[str, str] = {}
    for commit in commits:
        paths = _lines(_git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", commit))
        protected = [path for path in paths if _is_protected(path, policy)]
        if not protected:
            continue
        message = _git(root, "show", "-s", "--format=%B", commit)
        refs = sorted(set(TRAILER.findall(message)))
        if len(refs) != 1:
            issues.append(f"{commit[:12]} requires exactly one Spec-Ref trailer")
            continue
        change_id = refs[0]
        parent = f"{commit}^"
        try:
            package = _load_package_at(root, change_id, parent)
        except (FileNotFoundError, ValueError) as error:
            issues.append(f"{commit[:12]}: {error}")
            continue
        package_issues = _validate_package(package, require_approval=True)
        issues.extend(f"{commit[:12]}: {issue}" for issue in package_issues)
        non_spec = [path for path in paths if not _is_spec_path(path)]
        issues.extend(f"{commit[:12]}: {issue}" for issue in
                      _path_coverage_issues(non_spec, package.implementation.get("affected_paths", [])))
        implemented[change_id] = commit
        if require_remote_approval and package.approval and package.approval.get("channel") == "pull-request":
            issues.extend(f"{commit[:12]}: {issue}" for issue in _remote_approval_issues(package.approval))

    head = _git(root, "rev-parse", revision_range.rsplit("..", 1)[-1])
    for change_id, implementation_commit in implemented.items():
        try:
            package = _load_package_at(root, change_id, head)
        except (FileNotFoundError, ValueError) as error:
            issues.append(str(error))
            continue
        report = package.verification
        if not report:
            issues.append(f"{change_id}: missing verification.json at range head")
        else:
            issues.extend(f"{change_id}: {issue}" for issue in _verification_issues(package))
            if report.get("verdict") != "pass":
                issues.append(f"{change_id}: verification verdict must be pass")
            if report.get("implementation_commit") != implementation_commit:
                issues.append(f"{change_id}: verification report does not match latest implementation commit")
    return {"ok": not issues, "range": revision_range, "commits": len(commits),
            "implemented_changes": sorted(implemented), "issues": _unique(issues)}


def _load_package(root: Path, change_id: str) -> ChangePackage:
    _require_change_id(change_id)
    directory = root / "specs" / "changes" / change_id
    if not directory.is_dir():
        raise FileNotFoundError(f"change package not found: {change_id}")
    return ChangePackage(
        root=root, change_id=change_id,
        manifest=_load_yaml(directory / "manifest.yaml"),
        spec=_load_yaml(directory / "spec.yaml"),
        implementation=_load_yaml(directory / "implementation.yaml"),
        approval=_load_json_optional(directory / "approval.json"),
        verification=_load_json_optional(directory / "verification.json"),
    )


def _load_package_at(root: Path, change_id: str, revision: str) -> ChangePackage:
    _require_change_id(change_id)
    prefix = f"specs/changes/{change_id}/"
    def content(filename: str, required: bool = True) -> str | None:
        value = _git_raw(root, "show", f"{revision}:{prefix}{filename}", check=False)
        if value is None and required:
            raise FileNotFoundError(f"{filename} for {change_id} not found in parent history")
        return value
    manifest_text, spec_text, implementation_text = (content(name) for name in PACKAGE_FILES)
    approval_text = content("approval.json", False)
    verification_text = content("verification.json", False)
    package = ChangePackage(
        root=root, change_id=change_id,
        manifest=_parse_yaml(manifest_text or "", "manifest.yaml"),
        spec=_parse_yaml(spec_text or "", "spec.yaml"),
        implementation=_parse_yaml(implementation_text or "", "implementation.yaml"),
        approval=_parse_json(approval_text, "approval.json") if approval_text is not None else None,
        verification=_parse_json(verification_text, "verification.json") if verification_text is not None else None,
        revision_hashes={
            "spec_sha256": hashlib.sha256((spec_text or "").encode()).hexdigest(),
            "implementation_sha256": hashlib.sha256((implementation_text or "").encode()).hexdigest(),
        },
        revision_approval_hash=hashlib.sha256(approval_text.encode()).hexdigest() if approval_text is not None else None,
    )
    return package


def _package_hashes(package: ChangePackage) -> dict[str, str]:
    return package.hashes


def _validate_package(package: ChangePackage, *, require_approval: bool = False,
                      require_verification: bool = False) -> list[str]:
    issues: list[str] = []
    issues.extend(_shape(package.manifest, "manifest", {
        "schema_version", "change_id", "title", "owners", "status", "created_at", "supersedes"}))
    issues.extend(_shape(package.spec, "spec", {
        "schema_version", "change_id", "intent", "requirements", "constraints", "acceptance_criteria",
        "out_of_scope", "assumptions", "risks", "authority"}))
    issues.extend(_shape(package.implementation, "implementation", {
        "schema_version", "change_id", "affected_paths", "requirement_mapping", "checks", "compatibility",
        "migration", "rollback", "residual_risks"}))
    for name, document in (("manifest", package.manifest), ("spec", package.spec),
                           ("implementation", package.implementation)):
        if document.get("schema_version") != 1:
            issues.append(f"{name}.schema_version must equal 1")
        if document.get("change_id") != package.change_id:
            issues.append(f"{name}.change_id must equal directory name")

    if package.manifest.get("status") not in {"draft", "approved", "retired"}:
        issues.append("manifest.status must be draft, approved, or retired")
    for field in ("owners", "supersedes"):
        issues.extend(_string_list_issues(package.manifest.get(field), f"manifest.{field}"))
    if not isinstance(package.manifest.get("created_at"), (str, date)):
        issues.append("manifest.created_at must be an ISO date")
    if not _text(package.manifest.get("title")):
        issues.append("manifest.title must not be empty")

    for field in ("constraints", "out_of_scope", "assumptions", "risks"):
        issues.extend(_string_list_issues(package.spec.get(field), f"spec.{field}"))
    if not _text(package.spec.get("intent")):
        issues.append("spec.intent must not be empty")
    requirements = package.spec.get("requirements")
    requirement_ids, nested = _id_text_items(requirements, "spec.requirements")
    issues.extend(nested)
    criteria = package.spec.get("acceptance_criteria")
    criterion_ids: list[str] = []
    if not isinstance(criteria, list) or not criteria:
        issues.append("spec.acceptance_criteria must be a non-empty list")
    else:
        for index, item in enumerate(criteria):
            label = f"spec.acceptance_criteria[{index}]"
            issues.extend(_shape(item, label, {"id", "text", "checks"}))
            if isinstance(item, dict):
                criterion_ids.append(item.get("id"))
                if not _text(item.get("id")) or not _text(item.get("text")):
                    issues.append(f"{label} requires non-empty id and text")
                issues.extend(_string_list_issues(item.get("checks"), f"{label}.checks", nonempty=True))
    issues.extend(_duplicates(criterion_ids, "acceptance criterion"))
    authority = package.spec.get("authority")
    issues.extend(_shape(authority, "spec.authority", {"human_decisions", "automated_decisions"}))
    if isinstance(authority, dict):
        issues.extend(_string_list_issues(authority.get("human_decisions"), "spec.authority.human_decisions"))
        issues.extend(_string_list_issues(authority.get("automated_decisions"), "spec.authority.automated_decisions"))

    affected_paths = package.implementation.get("affected_paths")
    issues.extend(_string_list_issues(affected_paths, "implementation.affected_paths", nonempty=True))
    if isinstance(affected_paths, list):
        for path in affected_paths:
            if isinstance(path, str) and not _safe_repo_path(path):
                issues.append(f"unsafe or unsupported affected path: {path!r}")
        issues.extend(_duplicates(affected_paths, "affected path"))
    checks = package.implementation.get("checks")
    check_ids: list[str] = []
    if not isinstance(checks, list) or not checks:
        issues.append("implementation.checks must be a non-empty list")
    else:
        for index, check in enumerate(checks):
            label = f"implementation.checks[{index}]"
            if not isinstance(check, dict):
                issues.append(f"{label} must be an object")
                continue
            allowed = {"id", "kind", "target"} if check.get("kind") == "unittest" else {"id", "kind"}
            issues.extend(_shape(check, label, allowed))
            check_ids.append(check.get("id"))
            if not _text(check.get("id")):
                issues.append(f"{label}.id must not be empty")
            if check.get("kind") not in ALLOWED_CHECK_KINDS:
                issues.append(f"{label}.kind is not allowed")
            if check.get("kind") == "unittest" and not _safe_unittest_target(check.get("target")):
                issues.append(f"{label}.target is not a safe unittest target")
    issues.extend(_duplicates(check_ids, "check"))
    check_set = set(value for value in check_ids if isinstance(value, str))
    if isinstance(criteria, list):
        for item in criteria:
            if isinstance(item, dict) and isinstance(item.get("checks"), list):
                for check_id in item["checks"]:
                    if check_id not in check_set:
                        issues.append(f"acceptance criterion {item.get('id')} references unknown check {check_id}")

    mappings = package.implementation.get("requirement_mapping")
    mapped: set[str] = set()
    if not isinstance(mappings, list) or not mappings:
        issues.append("implementation.requirement_mapping must be a non-empty list")
    else:
        for index, mapping in enumerate(mappings):
            label = f"implementation.requirement_mapping[{index}]"
            issues.extend(_shape(mapping, label, {"requirement_id", "paths"}))
            if isinstance(mapping, dict):
                requirement_id = mapping.get("requirement_id")
                if requirement_id not in requirement_ids:
                    issues.append(f"{label} references unknown requirement {requirement_id}")
                else:
                    mapped.add(requirement_id)
                issues.extend(_string_list_issues(mapping.get("paths"), f"{label}.paths", nonempty=True))
                if isinstance(mapping.get("paths"), list):
                    for path in mapping["paths"]:
                        if path not in (affected_paths or []):
                            issues.append(f"{label} references undeclared affected path {path}")
    for requirement_id in requirement_ids:
        if requirement_id not in mapped:
            issues.append(f"requirement {requirement_id} has no implementation mapping")
    for field in ("compatibility", "migration", "rollback", "residual_risks"):
        issues.extend(_string_list_issues(package.implementation.get(field), f"implementation.{field}"))

    if package.approval:
        issues.extend(_approval_issues(package))
    elif require_approval:
        issues.append("approval.json is required")
    if package.verification:
        issues.extend(_verification_issues(package))
    elif require_verification:
        issues.append("verification.json is required")
    return _unique(issues)


def _approval_issues(package: ChangePackage) -> list[str]:
    approval = package.approval
    if not approval:
        return []
    issues = _shape(approval, "approval", {
        "schema_version", "change_id", "channel", "approver", "approved_at", "reason",
        "reference", "spec_commit", "hashes"})
    if approval.get("schema_version") != 1 or approval.get("change_id") != package.change_id:
        issues.append("approval identity or schema version mismatch")
    if approval.get("channel") not in {"local", "pull-request"}:
        issues.append("approval.channel must be local or pull-request")
    for field in ("approver", "approved_at", "reason", "spec_commit"):
        if not _text(approval.get(field)):
            issues.append(f"approval.{field} must not be empty")
    if approval.get("channel") == "pull-request" and not _text(approval.get("reference")):
        issues.append("pull-request approval requires reference")
    hashes = approval.get("hashes")
    issues.extend(_shape(hashes, "approval.hashes", {"spec_sha256", "implementation_sha256"}))
    if isinstance(hashes, dict) and hashes != _package_hashes(package):
        issues.append("approval hashes do not match current Spec and Implementation Plan")
    if package.manifest.get("status") not in {"approved", "retired"}:
        issues.append("approved package manifest must be approved or retired")
    return issues


def _verification_issues(package: ChangePackage) -> list[str]:
    report = package.verification
    if not report:
        return []
    issues = _shape(report, "verification", {
        "schema_version", "change_id", "implementation_commit", "generated_at", "changed_paths",
        "checks", "residual_risks", "hashes", "verdict"})
    if report.get("schema_version") != 1 or report.get("change_id") != package.change_id:
        issues.append("verification identity or schema version mismatch")
    for field in ("implementation_commit", "generated_at"):
        if not _text(report.get(field)):
            issues.append(f"verification.{field} must not be empty")
    if _text(report.get("implementation_commit")) and not re.fullmatch(r"[0-9a-f]{40}", report["implementation_commit"]):
        issues.append("verification.implementation_commit must be a full Git SHA")
    if report.get("verdict") not in {"pass", "fail", "inconclusive"}:
        issues.append("verification.verdict is invalid")
    issues.extend(_string_list_issues(report.get("changed_paths"), "verification.changed_paths", nonempty=True))
    if isinstance(report.get("changed_paths"), list):
        for path in report["changed_paths"]:
            if not _safe_repo_path(path):
                issues.append(f"unsafe verification changed path: {path!r}")
    issues.extend(_string_list_issues(report.get("residual_risks"), "verification.residual_risks"))
    results = report.get("checks")
    if not isinstance(results, list) or not results:
        issues.append("verification.checks must be a non-empty list")
    else:
        declared_ids = {item.get("id") for item in package.implementation.get("checks", []) if isinstance(item, dict)}
        result_ids = []
        for index, item in enumerate(results):
            label = f"verification.checks[{index}]"
            issues.extend(_shape(item, label, {"id", "kind", "outcome", "duration_seconds", "output"}))
            if not isinstance(item, dict):
                continue
            result_ids.append(item.get("id"))
            if item.get("id") not in declared_ids:
                issues.append(f"{label} references undeclared check {item.get('id')}")
            if item.get("kind") not in ALLOWED_CHECK_KINDS:
                issues.append(f"{label}.kind is not allowed")
            if item.get("outcome") not in {"pass", "fail", "inconclusive"}:
                issues.append(f"{label}.outcome is invalid")
            if not isinstance(item.get("duration_seconds"), (int, float)) or item.get("duration_seconds", -1) < 0:
                issues.append(f"{label}.duration_seconds must be non-negative")
            if not isinstance(item.get("output"), str):
                issues.append(f"{label}.output must be a string")
        issues.extend(_duplicates(result_ids, "verification check"))
        if set(result_ids) != declared_ids:
            issues.append("verification checks do not exactly match the Implementation Plan")
        if report.get("verdict") == "pass" and any(
            not isinstance(item, dict) or item.get("outcome") != "pass" for item in results
        ):
            issues.append("passing verification contains a non-passing check")
    hashes = report.get("hashes")
    expected = {**_package_hashes(package)}
    if package.approval:
        expected["approval_sha256"] = package.revision_approval_hash or _sha256(package.directory / "approval.json")
    if isinstance(hashes, dict):
        for key, value in expected.items():
            if hashes.get(key) != value:
                issues.append(f"verification hash mismatch: {key}")
    else:
        issues.append("verification.hashes must be an object")
    return issues


def _run_check(root: Path, check: dict[str, Any], runtime_home: str | Path | None) -> dict[str, Any]:
    kind, check_id = check["kind"], check["id"]
    if kind == "unittest":
        target = check["target"]
        args = [sys.executable, "-m", "unittest"]
        args += ["discover", "-s", target.split(":", 1)[1], "-v"] if target.startswith("discover:") else [target, "-v"]
    elif kind == "profiles":
        return _run_profiles_check(root, check_id, runtime_home)
    else:
        command = {"harness": ["validate", "harness"], "contracts": ["validate", "contracts"],
                   "site": ["site", "stage"]}[kind]
        args = [sys.executable, "-m", "nous_os", *command]
        if kind == "site":
            with tempfile.TemporaryDirectory(prefix=".nous-os-spec-site-", dir=root) as temporary:
                return _execute_check(root, check_id, kind, [*args, "--destination", temporary], runtime_home)
    return _execute_check(root, check_id, kind, args, runtime_home)


def _run_profiles_check(root: Path, check_id: str, runtime_home: str | Path | None) -> dict[str, Any]:
    started = time.monotonic()
    outputs: list[str] = []
    outcome = "pass"
    for profile in sorted((root / "config" / "profiles").glob("*.yaml")):
        result = _execute(root, [sys.executable, "-m", "nous_os", "validate", "profile", "--profile", str(profile)], runtime_home)
        outputs.append(result.stdout + result.stderr)
        if result.returncode:
            outcome = "fail"
    return {"id": check_id, "kind": "profiles", "outcome": outcome,
            "duration_seconds": round(time.monotonic() - started, 3), "output": _truncate("".join(outputs))}


def _execute_check(root: Path, check_id: str, kind: str, args: list[str], runtime_home: str | Path | None) -> dict[str, Any]:
    started = time.monotonic()
    result = _execute(root, args, runtime_home)
    return {"id": check_id, "kind": kind, "outcome": "pass" if result.returncode == 0 else "fail",
            "duration_seconds": round(time.monotonic() - started, 3),
            "output": _truncate(result.stdout + result.stderr)}


def _execute(root: Path, args: list[str], runtime_home: str | Path | None) -> subprocess.CompletedProcess[str]:
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(root / "src")
    if runtime_home:
        environment["NOUS_OS_HOME"] = str(runtime_home)
    return subprocess.run(args, cwd=root, env=environment, text=True, capture_output=True, check=False)


def _implementation_commits(root: Path, change_id: str, package: ChangePackage) -> list[str]:
    if not package.approval:
        return []
    approval_path = f"specs/changes/{change_id}/approval.json"
    added = _lines(_git(root, "log", "--diff-filter=A", "--format=%H", "--", approval_path))
    if not added:
        return []
    approval_commit = added[-1]
    commits = _lines(_git(root, "rev-list", "--reverse", f"{approval_commit}..HEAD"))
    policy = _load_policy(root)
    implementation_commits = []
    for commit in commits:
        if change_id not in TRAILER.findall(_git(root, "show", "-s", "--format=%B", commit)):
            continue
        paths = _lines(_git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", commit))
        if any(_is_protected(path, policy) for path in paths):
            implementation_commits.append(commit)
    return implementation_commits


def _implementation_paths(root: Path, commits: Iterable[str]) -> list[str]:
    paths: set[str] = set()
    for commit in commits:
        paths.update(_lines(_git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", commit)))
    return sorted(path for path in paths if not _is_spec_path(path))


def _path_coverage_issues(paths: Iterable[str], planned: Iterable[str]) -> list[str]:
    declared = list(planned)
    return [f"changed path is outside Implementation Plan: {path}" for path in paths
            if not any(path == item or (item.endswith("/") and path.startswith(item)) for item in declared)]


def _load_policy(root: Path) -> dict[str, Any]:
    policy = _load_yaml(root / "config" / "spec-policy.yaml")
    issues = _shape(policy, "spec-policy", {"schema_version", "protected_paths", "exempt_paths"})
    if policy.get("schema_version") != 1:
        issues.append("spec-policy.schema_version must equal 1")
    for field in ("protected_paths", "exempt_paths"):
        issues.extend(_string_list_issues(policy.get(field), f"spec-policy.{field}"))
        for path in policy.get(field, []):
            if not _safe_repo_path(path):
                issues.append(f"unsafe policy path: {path}")
    if issues:
        raise ValueError("invalid spec policy: " + "; ".join(issues))
    return policy


def _is_protected(path: str, policy: dict[str, Any]) -> bool:
    protected = _matches_any(path, policy["protected_paths"])
    exempt = _matches_any(path, policy["exempt_paths"])
    return protected or (not exempt and path in {"AGENTS.md", "CONTEXT.md"})


def _matches_any(path: str, patterns: Iterable[str]) -> bool:
    return any(path == pattern or (pattern.endswith("/") and path.startswith(pattern)) for pattern in patterns)


def _is_spec_path(path: str) -> bool:
    return path.startswith("specs/changes/")


def _remote_approval_issues(approval: dict[str, Any]) -> list[str]:
    reference = approval.get("reference", "")
    match = re.fullmatch(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", reference)
    if not match:
        return ["pull-request approval reference must be a GitHub PR URL"]
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return ["GITHUB_TOKEN is required for remote approval validation"]
    owner, repo, number = match.groups()
    headers = {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}",
               "X-GitHub-Api-Version": "2022-11-28"}
    try:
        pull = _github_json(f"https://api.github.com/repos/{owner}/{repo}/pulls/{number}", headers)
        reviews = _github_json(f"https://api.github.com/repos/{owner}/{repo}/pulls/{number}/reviews", headers)
    except (urllib.error.URLError, ValueError) as error:
        return [f"GitHub approval lookup failed: {error}"]
    issues = []
    if not pull.get("merged_at"):
        issues.append("approval pull request is not merged")
    approver = approval.get("approver")
    if not any(review.get("state") == "APPROVED" and review.get("user", {}).get("login") == approver for review in reviews):
        issues.append("approval pull request lacks matching APPROVED reviewer")
    return issues


def _github_json(url: str, headers: dict[str, str]) -> Any:
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def _derived_status(package: ChangePackage, issues: list[str], commits: list[str] | None = None) -> str:
    if package.manifest.get("status") == "retired":
        return "retired"
    if package.verification and package.verification.get("verdict") == "pass" and not issues:
        return "verified"
    if commits:
        return "implemented"
    if package.approval and not _approval_issues(package):
        return "approved"
    return "draft"


def _safe_repo_path(value: Any) -> bool:
    if not isinstance(value, str) or not value or "*" in value or "?" in value or "\\" in value:
        return False
    stripped = value[:-1] if value.endswith("/") else value
    path = PurePosixPath(stripped)
    return not path.is_absolute() and ".." not in path.parts and "." not in path.parts and bool(path.parts)


def _safe_unittest_target(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    if value.startswith("discover:"):
        return _safe_repo_path(value.split(":", 1)[1])
    return bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+", value))


def _shape(value: Any, label: str, required: set[str]) -> list[str]:
    if not isinstance(value, dict):
        return [f"{label} must be an object"]
    missing, unknown = required - set(value), set(value) - required
    issues = []
    if missing:
        issues.append(f"{label} missing fields: {', '.join(sorted(missing))}")
    if unknown:
        issues.append(f"{label} unknown fields: {', '.join(sorted(unknown))}")
    return issues


def _id_text_items(value: Any, label: str) -> tuple[list[str], list[str]]:
    ids: list[str] = []
    issues: list[str] = []
    if not isinstance(value, list) or not value:
        return ids, [f"{label} must be a non-empty list"]
    for index, item in enumerate(value):
        item_label = f"{label}[{index}]"
        issues.extend(_shape(item, item_label, {"id", "text"}))
        if isinstance(item, dict):
            ids.append(item.get("id"))
            if not _text(item.get("id")) or not _text(item.get("text")):
                issues.append(f"{item_label} requires non-empty id and text")
    issues.extend(_duplicates(ids, "requirement"))
    return [item for item in ids if isinstance(item, str)], issues


def _string_list_issues(value: Any, label: str, *, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or (nonempty and not value):
        return [f"{label} must be {'a non-empty' if nonempty else 'an'} list"]
    if any(not _text(item) for item in value):
        return [f"{label} must contain only non-empty strings"]
    return []


def _duplicates(values: Iterable[Any], label: str) -> list[str]:
    seen, duplicates = set(), set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return [f"duplicate {label} id: {value}" for value in sorted(str(item) for item in duplicates)]


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _require_change_id(change_id: str) -> None:
    if not CHANGE_ID.fullmatch(change_id):
        raise ValueError(f"invalid change id: {change_id!r}")


def _require_clean(root: Path) -> None:
    if _git(root, "status", "--porcelain"):
        raise ValueError("working tree must be clean")


def _git(root: Path, *args: str, check: bool = True) -> str | None:
    result = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)
    if result.returncode:
        if check:
            raise ValueError(result.stderr.strip() or f"git {' '.join(args)} failed")
        return None
    return result.stdout.rstrip("\n")


def _git_raw(root: Path, *args: str, check: bool = True) -> str | None:
    result = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)
    if result.returncode:
        if check:
            raise ValueError(result.stderr.strip() or f"git {' '.join(args)} failed")
        return None
    return result.stdout


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"required file not found: {path}")
    return _parse_yaml(path.read_text(encoding="utf-8"), path.name)


def _parse_yaml(text: str, label: str) -> dict[str, Any]:
    try:
        value = yaml.safe_load(text)
    except yaml.YAMLError as error:
        raise ValueError(f"invalid YAML in {label}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{label} must contain a mapping")
    return value


def _load_json_optional(path: Path) -> dict[str, Any] | None:
    return _parse_json(path.read_text(encoding="utf-8"), path.name) if path.is_file() else None


def _parse_json(text: str, label: str) -> dict[str, Any]:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON in {label}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{label} must contain an object")
    return value


def _write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _lines(value: str | None) -> list[str]:
    return [line for line in (value or "").splitlines() if line]


def _unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _truncate(value: str, limit: int = 12000) -> str:
    return value if len(value) <= limit else value[-limit:]
