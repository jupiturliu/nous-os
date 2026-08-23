#!/usr/bin/env python3
"""Validate a minimal SpecIR v0 + VerificationReport v0 bundle.

This is deliberately a narrow contract validator. It does not claim a plan is
real-world feasible; it verifies that a feasibility claim is qualified by the
Spec's assumptions and the VerificationReport's declared evidence state.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SPEC_REQUIRED = {
    "spec_id",
    "intent",
    "goals",
    "hard_constraints",
    "acceptance_tests",
    "authority",
    "assumptions",
}
REPORT_REQUIRED = {
    "verification_id",
    "spec_ref",
    "impl_ref",
    "target_ref",
    "platform_config_ref",
    "checks",
    "counterexamples",
    "residual_risks",
    "verdict",
    "human_decision_required",
}
VALID_ASSUMPTION_STATES = {"unverified", "validated", "falsified"}
VALID_CHECK_RESULTS = {"pass", "fail", "inconclusive"}
VALID_VERDICTS = {"feasible", "conditionally_feasible", "infeasible", "insufficient_evidence"}
TARGET_REQUIRED = {"target_id", "observed_at", "provenance", "assets", "capacities", "constraints", "current_state"}
PLATFORM_CONFIG_REQUIRED = {"config_id", "version", "permissions", "enabled_features", "integration_endpoints"}


def _missing_fields(value: dict[str, Any], required: set[str]) -> list[str]:
    return sorted(required - set(value))


def validate_contract_bundle(spec: dict[str, Any], report: dict[str, Any]) -> dict[str, Any]:
    """Return a stable, machine-readable validation result for one bundle."""
    issues: list[str] = []

    missing_spec = _missing_fields(spec, SPEC_REQUIRED)
    if missing_spec:
        issues.append(f"SpecIR missing fields: {', '.join(missing_spec)}")
    missing_report = _missing_fields(report, REPORT_REQUIRED)
    if missing_report:
        issues.append(f"VerificationReport missing fields: {', '.join(missing_report)}")
    if issues:
        return {"ok": False, "verdict": report.get("verdict"), "issues": issues}

    if report["spec_ref"] != spec["spec_id"]:
        issues.append("VerificationReport spec_ref must match SpecIR spec_id")

    assumptions = spec["assumptions"]
    if not isinstance(assumptions, list):
        issues.append("SpecIR assumptions must be a list")
        assumptions = []
    unverified_assumptions = 0
    for index, assumption in enumerate(assumptions):
        if not isinstance(assumption, dict):
            issues.append(f"SpecIR assumption[{index}] must be an object")
            continue
        state = assumption.get("validation_state")
        if state not in VALID_ASSUMPTION_STATES:
            issues.append(f"SpecIR assumption[{index}] has invalid validation_state")
        elif state == "unverified":
            unverified_assumptions += 1
        elif state == "falsified":
            issues.append("falsified assumptions require infeasible or insufficient_evidence verdict")

    verdict = report["verdict"]
    if verdict not in VALID_VERDICTS:
        issues.append("VerificationReport verdict is invalid")

    checks = report["checks"]
    if not isinstance(checks, list) or not checks:
        issues.append("VerificationReport checks must be a non-empty list")
        checks = []
    failed_checks = 0
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            issues.append(f"VerificationReport check[{index}] must be an object")
            continue
        if check.get("result") not in VALID_CHECK_RESULTS:
            issues.append(f"VerificationReport check[{index}] has invalid result")
        elif check["result"] == "fail":
            failed_checks += 1

    if unverified_assumptions and verdict == "feasible":
        issues.append("unverified assumptions require conditionally_feasible or insufficient_evidence verdict")
    if failed_checks and verdict in {"feasible", "conditionally_feasible"}:
        issues.append("failed checks require infeasible or insufficient_evidence verdict")
    if failed_checks and not report["counterexamples"]:
        issues.append("failed checks require at least one counterexample")
    if unverified_assumptions and verdict == "conditionally_feasible" and not report["residual_risks"]:
        issues.append("conditionally_feasible verdict with unverified assumptions requires residual_risks")

    return {"ok": not issues, "verdict": verdict, "issues": issues}


def validate_full_contract_bundle(
    spec: dict[str, Any],
    target: dict[str, Any],
    platform_config: dict[str, Any],
    report: dict[str, Any],
) -> dict[str, Any]:
    """Validate a SpecIR/report bundle bound to observed target and platform state.

    This validates freshness/provenance *shape* and reference alignment; it does
    not independently establish that target facts are true.
    """
    result = validate_contract_bundle(spec, report)
    issues = list(result["issues"])

    missing_target = _missing_fields(target, TARGET_REQUIRED)
    if missing_target:
        issues.append(f"TargetDescription missing fields: {', '.join(missing_target)}")
    else:
        if not isinstance(target["observed_at"], str) or not target["observed_at"].strip():
            issues.append("TargetDescription observed_at is required")
        if not isinstance(target["provenance"], str) or not target["provenance"].strip():
            issues.append("TargetDescription provenance is required")
        if report.get("target_ref") != target.get("target_id"):
            issues.append("VerificationReport target_ref must match TargetDescription target_id")

    missing_config = _missing_fields(platform_config, PLATFORM_CONFIG_REQUIRED)
    if missing_config:
        issues.append(f"PlatformConfig missing fields: {', '.join(missing_config)}")
    else:
        if not isinstance(platform_config["permissions"], list) or not platform_config["permissions"]:
            issues.append("PlatformConfig permissions must be a non-empty list")
        if report.get("platform_config_ref") != platform_config.get("config_id"):
            issues.append("VerificationReport platform_config_ref must match PlatformConfig config_id")

    return {"ok": not issues, "verdict": report.get("verdict"), "issues": issues}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a minimal domain-compilation contract bundle.")
    parser.add_argument("spec", type=Path, help="path to SpecIR JSON")
    parser.add_argument("report", type=Path, help="path to VerificationReport JSON")
    parser.add_argument("--target", type=Path, help="optional path to TargetDescription JSON")
    parser.add_argument("--platform-config", type=Path, help="optional path to PlatformConfig JSON")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()

    if bool(args.target) != bool(args.platform_config):
        parser.error("--target and --platform-config must be supplied together")

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    report = json.loads(args.report.read_text(encoding="utf-8"))
    if args.target:
        target = json.loads(args.target.read_text(encoding="utf-8"))
        platform_config = json.loads(args.platform_config.read_text(encoding="utf-8"))
        result = validate_full_contract_bundle(spec, target, platform_config, report)
    else:
        result = validate_contract_bundle(spec, report)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"domain compilation contract ok={result['ok']} verdict={result['verdict']}")
        for issue in result["issues"]:
            print(f"- {issue}")
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
