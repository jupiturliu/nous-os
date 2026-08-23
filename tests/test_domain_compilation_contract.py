"""Contract tests for the minimal Domain Compilation v0 verifier."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

from nous_os.contracts.domain_compilation import validate_contract_bundle, validate_full_contract_bundle


class DomainCompilationContractTests(unittest.TestCase):
    def _spec(self, assumption_state: str = "validated") -> dict:
        return {
            "spec_id": "research-intake-v0",
            "intent": "Publish a source-grounded research note.",
            "goals": [{"metric": "source_provenance", "direction": "satisfy", "threshold": "primary_or_labeled_secondary"}],
            "hard_constraints": [{"id": "no-unsupported-claim", "predicate": "all material claims have evidence or are labeled", "source": "human"}],
            "acceptance_tests": [{"id": "evidence-present", "pass_condition": "every material claim has provenance"}],
            "authority": {"proposer": "agent", "verifier": "deterministic_validator", "approver": "human"},
            "assumptions": [{"statement": "The source is complete enough for the stated conclusion.", "validation_state": assumption_state}],
        }

    def _report(self, verdict: str = "feasible", residual_risks: list[str] | None = None) -> dict:
        return {
            "verification_id": "verify-research-intake-v0",
            "spec_ref": "research-intake-v0",
            "impl_ref": "research-source-intake-v0",
            "target_ref": "public-source-snapshot-v0",
            "platform_config_ref": "logged-out-public-web-recovery-v0",
            "checks": [{"name": "schema", "class": "lint", "result": "pass", "evidence_ref": "capture.json"}],
            "counterexamples": [],
            "residual_risks": residual_risks or [],
            "verdict": verdict,
            "human_decision_required": [],
        }

    def test_validated_spec_can_be_feasible(self) -> None:
        result = validate_contract_bundle(self._spec(), self._report())
        self.assertTrue(result["ok"])
        self.assertEqual(result["verdict"], "feasible")
        self.assertEqual(result["issues"], [])

    def test_unverified_assumption_blocks_unqualified_feasible_verdict(self) -> None:
        result = validate_contract_bundle(self._spec("unverified"), self._report("feasible"))
        self.assertFalse(result["ok"])
        self.assertIn("unverified assumptions require conditionally_feasible or insufficient_evidence verdict", result["issues"])

    def test_unverified_assumption_allows_conditionally_feasible_with_residual_risk(self) -> None:
        result = validate_contract_bundle(
            self._spec("unverified"),
            self._report("conditionally_feasible", ["The source may omit material context."]),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["verdict"], "conditionally_feasible")

    def _target(self) -> dict:
        return {
            "target_id": "public-source-snapshot-v0",
            "observed_at": "2026-07-12T16:22:45Z",
            "provenance": "public syndication payload",
            "assets": ["X status metadata", "linked-article preview"],
            "capacities": ["logged-out access only"],
            "constraints": ["full X Article body requires login"],
            "current_state": ["partial source recovery"],
        }

    def _platform_config(self) -> dict:
        return {
            "config_id": "logged-out-public-web-recovery-v0",
            "version": "v0",
            "permissions": ["public web only"],
            "enabled_features": ["syndication endpoint"],
            "integration_endpoints": ["cdn.syndication.twimg.com"],
        }

    def test_full_bundle_accepts_target_with_timestamp_provenance_and_matching_refs(self) -> None:
        result = validate_full_contract_bundle(
            self._spec("unverified"),
            self._target(),
            self._platform_config(),
            self._report("conditionally_feasible", ["The source may omit material context."]),
        )
        self.assertTrue(result["ok"])

    def test_full_bundle_rejects_report_bound_to_different_target(self) -> None:
        report = self._report("conditionally_feasible", ["The source may omit material context."])
        report["target_ref"] = "other-target"
        result = validate_full_contract_bundle(self._spec("unverified"), self._target(), self._platform_config(), report)
        self.assertFalse(result["ok"])
        self.assertIn("VerificationReport target_ref must match TargetDescription target_id", result["issues"])

    def test_full_bundle_rejects_target_without_provenance(self) -> None:
        target = self._target()
        target["provenance"] = ""
        result = validate_full_contract_bundle(
            self._spec("unverified"),
            target,
            self._platform_config(),
            self._report("conditionally_feasible", ["The source may omit material context."]),
        )
        self.assertFalse(result["ok"])
        self.assertIn("TargetDescription provenance is required", result["issues"])

    def test_cli_validates_full_bundle_when_target_and_config_are_supplied(self) -> None:
        report = self._report("conditionally_feasible", ["The source may omit material context."])
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            paths = {
                "spec": temp / "spec.json",
                "target": temp / "target.json",
                "config": temp / "config.json",
                "report": temp / "report.json",
            }
            for key, value in {
                "spec": self._spec("unverified"),
                "target": self._target(),
                "config": self._platform_config(),
                "report": report,
            }.items():
                paths[key].write_text(json.dumps(value), encoding="utf-8")
            run = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "nous_os",
                    "contract",
                    "validate",
                    str(paths["spec"]),
                    str(paths["report"]),
                    "--target",
                    str(paths["target"]),
                    "--platform-config",
                    str(paths["config"]),
                ],
                cwd=ROOT,
                env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertTrue(json.loads(run.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
