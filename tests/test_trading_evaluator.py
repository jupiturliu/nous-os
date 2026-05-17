"""Slice 1 contract tests for the read-only TradingEvaluator.

The evaluator maps existing trading-agent proof artifacts to CLS v2
components per docs/domain-evaluator-interface.md. These tests use
synthetic fixtures so they do not depend on the real trading-agent
workspace being populated.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "examples" / "runtime"
FIXTURES = ROOT / "tests" / "fixtures" / "trading_evaluator"

for path in (RUNTIME,):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from trading_evaluator import TradingEvaluator, CLS_V2_FIELDS


REQUIRED_SCHEMA = set(CLS_V2_FIELDS) | {"evidence_refs"}


def _make_workspace(tmp_path: Path, username: str, *, proof_packs: list[dict], market_proof: dict) -> Path:
    user_root = tmp_path / "trading-agent" / "data" / "users" / username
    (user_root / "market_proof").mkdir(parents=True, exist_ok=True)
    (user_root / "promotion_reviews" / "proof_packs").mkdir(parents=True, exist_ok=True)

    for pack in proof_packs:
        path = user_root / "promotion_reviews" / "proof_packs" / f"{pack['candidate_id']}.json"
        path.write_text(json.dumps(pack))

    for filename, payload in market_proof.items():
        path = user_root / "market_proof" / filename
        if filename.endswith(".jsonl"):
            path.write_text("\n".join(json.dumps(row) for row in payload))
        else:
            path.write_text(json.dumps(payload))

    return tmp_path


def _clean_boundary() -> dict:
    return {
        "broker_action_allowed": False,
        "creates_order_or_draft": False,
        "creates_promotion_or_approval": False,
        "mutates_runtime_live_state": False,
        "production_config_changed": False,
        "note": "synthetic fixture; no live effects",
    }


def _proof_pack(candidate_id: str, *, capital_authorized: bool = False, boundary_overrides: dict | None = None) -> dict:
    boundary = _clean_boundary()
    if boundary_overrides:
        boundary.update(boundary_overrides)
    return {
        "candidate_id": candidate_id,
        "capital_action_authorized": capital_authorized,
        "execution_boundary": boundary,
        "human_review_state": "pending",
    }


class TradingEvaluatorContractTests(unittest.TestCase):
    """Schema and contract guarantees the evaluator must satisfy."""

    def setUp(self) -> None:
        self._tmp = Path(__import__("tempfile").mkdtemp(prefix="trading_evaluator_test_"))
        self.addCleanup(self._cleanup)

    def _cleanup(self) -> None:
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)

    def test_evaluate_returns_full_cls_v2_schema(self) -> None:
        workspace = _make_workspace(
            self._tmp,
            "alice",
            proof_packs=[_proof_pack("ec-0001")],
            market_proof={},
        )
        evaluator = TradingEvaluator(workspace=workspace, username="alice")
        result = evaluator.evaluate(run_context={"run_id": "r1"}, outcome_artifacts=None)

        self.assertEqual(set(result), REQUIRED_SCHEMA)
        for field in CLS_V2_FIELDS:
            self.assertIsInstance(result[field], float, msg=f"{field} should be float")
            self.assertGreaterEqual(result[field], 0.0, msg=f"{field} below 0")
            self.assertLessEqual(result[field], 1.0, msg=f"{field} above 1")
        self.assertIsInstance(result["evidence_refs"], list)

    def test_boundary_integrity_drops_when_any_artifact_attests_live_effect(self) -> None:
        workspace = _make_workspace(
            self._tmp,
            "alice",
            proof_packs=[
                _proof_pack("ec-0001"),
                _proof_pack("ec-0002", boundary_overrides={"broker_action_allowed": True}),
            ],
            market_proof={},
        )
        evaluator = TradingEvaluator(workspace=workspace, username="alice")
        result = evaluator.evaluate(run_context={"run_id": "r1"})

        self.assertLess(result["boundary_integrity"], 1.0)
        self.assertGreater(result["boundary_integrity"], 0.0)

    def test_boundary_integrity_is_one_when_all_artifacts_are_clean(self) -> None:
        workspace = _make_workspace(
            self._tmp,
            "alice",
            proof_packs=[_proof_pack("ec-0001"), _proof_pack("ec-0002")],
            market_proof={},
        )
        evaluator = TradingEvaluator(workspace=workspace, username="alice")
        result = evaluator.evaluate(run_context={"run_id": "r1"})

        self.assertEqual(result["boundary_integrity"], 1.0)

    def test_human_agency_drops_when_capital_action_authorized(self) -> None:
        workspace = _make_workspace(
            self._tmp,
            "alice",
            proof_packs=[
                _proof_pack("ec-0001"),
                _proof_pack("ec-0002", capital_authorized=True),
            ],
            market_proof={},
        )
        evaluator = TradingEvaluator(workspace=workspace, username="alice")
        result = evaluator.evaluate(run_context={"run_id": "r1"})

        self.assertEqual(result["human_agency_preservation"], 0.5)

    def test_pending_components_return_zero_with_explicit_marker(self) -> None:
        workspace = _make_workspace(
            self._tmp,
            "alice",
            proof_packs=[_proof_pack("ec-0001")],
            market_proof={},
        )
        evaluator = TradingEvaluator(workspace=workspace, username="alice")
        result = evaluator.evaluate(run_context={"run_id": "r1"})

        self.assertEqual(result["correction_absorption"], 0.0)
        self.assertEqual(result["memory_reuse_precision"], 0.0)
        self.assertEqual(result["outcome_quality_delta"], 0.0)
        self.assertEqual(result["repeatability_gain"], 0.0)
        pending = [ref for ref in result["evidence_refs"] if ref.startswith("pending:")]
        self.assertTrue(pending, "Slice 1 must surface pending components, not paper them over")

    def test_evidence_refs_point_to_consumed_artifacts(self) -> None:
        workspace = _make_workspace(
            self._tmp,
            "alice",
            proof_packs=[_proof_pack("ec-0001"), _proof_pack("ec-0002")],
            market_proof={},
        )
        evaluator = TradingEvaluator(workspace=workspace, username="alice")
        result = evaluator.evaluate(run_context={"run_id": "r1"})

        consumed = [ref for ref in result["evidence_refs"] if "ec-0001" in ref or "ec-0002" in ref]
        self.assertEqual(len(consumed), 2)

    def test_missing_workspace_returns_zero_scores_with_explicit_reason(self) -> None:
        workspace = self._tmp / "nonexistent"
        evaluator = TradingEvaluator(workspace=workspace, username="alice")
        result = evaluator.evaluate(run_context={"run_id": "r1"})

        self.assertEqual(result["boundary_integrity"], 0.0)
        self.assertEqual(result["human_agency_preservation"], 0.0)
        self.assertIn("missing:trading_agent_workspace", " ".join(result["evidence_refs"]))


class TradingEvaluatorOutcomeSignalsTests(unittest.TestCase):
    """Slice 2: outcome_quality_delta + repeatability_gain mappings."""

    def setUp(self) -> None:
        self._tmp = Path(__import__("tempfile").mkdtemp(prefix="trading_evaluator_outcome_"))
        self.addCleanup(lambda: __import__("shutil").rmtree(self._tmp, ignore_errors=True))

    def test_outcome_quality_delta_is_outperform_rate_over_non_neutral_comparisons(self) -> None:
        comparisons = []
        for i in range(8):
            comparisons.append({
                "artifact_type": "market_proof_baseline_comparison",
                "outcome_label": "matured",
                "outperformed_benchmark": True,
                "decision_id": f"sd-good-{i}",
                "symbol": f"SYM{i}",
                "execution_boundary": _clean_boundary(),
            })
        for i in range(2):
            comparisons.append({
                "artifact_type": "market_proof_baseline_comparison",
                "outcome_label": "matured",
                "outperformed_benchmark": False,
                "decision_id": f"sd-bad-{i}",
                "symbol": f"SYM{i+10}",
                "execution_boundary": _clean_boundary(),
            })
        comparisons.append({
            "artifact_type": "market_proof_baseline_comparison",
            "outcome_label": "neutral_no_entry",
            "outperformed_benchmark": False,
            "decision_id": "sd-neutral-0",
            "symbol": "SKIP",
            "execution_boundary": _clean_boundary(),
        })

        workspace = _make_workspace(
            self._tmp,
            "alice",
            proof_packs=[_proof_pack("ec-0001")],
            market_proof={"baseline_comparisons.jsonl": comparisons},
        )
        evaluator = TradingEvaluator(workspace=workspace, username="alice")
        result = evaluator.evaluate(run_context={"run_id": "r1"})

        self.assertAlmostEqual(result["outcome_quality_delta"], 0.8, places=2)
        self.assertNotIn("pending:outcome_quality_delta", result["evidence_refs"])

    def test_outcome_quality_delta_stays_pending_when_no_resolved_comparisons(self) -> None:
        workspace = _make_workspace(
            self._tmp,
            "alice",
            proof_packs=[_proof_pack("ec-0001")],
            market_proof={"baseline_comparisons.jsonl": [
                {
                    "artifact_type": "market_proof_baseline_comparison",
                    "outcome_label": "neutral_no_entry",
                    "outperformed_benchmark": False,
                    "decision_id": "sd-neutral",
                    "symbol": "X",
                    "execution_boundary": _clean_boundary(),
                },
            ]},
        )
        evaluator = TradingEvaluator(workspace=workspace, username="alice")
        result = evaluator.evaluate(run_context={"run_id": "r1"})

        self.assertEqual(result["outcome_quality_delta"], 0.0)
        self.assertIn("pending:outcome_quality_delta", result["evidence_refs"])

    def test_repeatability_gain_uses_brier_improvement(self) -> None:
        workspace = _make_workspace(
            self._tmp,
            "alice",
            proof_packs=[_proof_pack("ec-0001")],
            market_proof={"forecast_ledger_summary.json": {
                "artifact_type": "forecast_ledger_summary",
                "brier_score": 0.20,
                "brier_improvement_over_baseline": 0.05,
                "execution_boundary": _clean_boundary(),
            }},
        )
        evaluator = TradingEvaluator(workspace=workspace, username="alice")
        result = evaluator.evaluate(run_context={"run_id": "r1"})

        self.assertAlmostEqual(result["repeatability_gain"], 0.05, places=4)
        self.assertNotIn("pending:repeatability_gain", result["evidence_refs"])

    def test_repeatability_gain_clamps_negative_improvement_to_zero(self) -> None:
        workspace = _make_workspace(
            self._tmp,
            "alice",
            proof_packs=[_proof_pack("ec-0001")],
            market_proof={"forecast_ledger_summary.json": {
                "artifact_type": "forecast_ledger_summary",
                "brier_improvement_over_baseline": -0.05,
                "execution_boundary": _clean_boundary(),
            }},
        )
        evaluator = TradingEvaluator(workspace=workspace, username="alice")
        result = evaluator.evaluate(run_context={"run_id": "r1"})

        self.assertEqual(result["repeatability_gain"], 0.0)
        self.assertNotIn("pending:repeatability_gain", result["evidence_refs"])

    def test_repeatability_gain_caps_at_one(self) -> None:
        workspace = _make_workspace(
            self._tmp,
            "alice",
            proof_packs=[_proof_pack("ec-0001")],
            market_proof={"forecast_ledger_summary.json": {
                "artifact_type": "forecast_ledger_summary",
                "brier_improvement_over_baseline": 2.5,
                "execution_boundary": _clean_boundary(),
            }},
        )
        evaluator = TradingEvaluator(workspace=workspace, username="alice")
        result = evaluator.evaluate(run_context={"run_id": "r1"})

        self.assertEqual(result["repeatability_gain"], 1.0)

    def test_repeatability_gain_stays_pending_when_summary_absent(self) -> None:
        workspace = _make_workspace(
            self._tmp,
            "alice",
            proof_packs=[_proof_pack("ec-0001")],
            market_proof={},
        )
        evaluator = TradingEvaluator(workspace=workspace, username="alice")
        result = evaluator.evaluate(run_context={"run_id": "r1"})

        self.assertEqual(result["repeatability_gain"], 0.0)
        self.assertIn("pending:repeatability_gain", result["evidence_refs"])


class TradingEvaluatorReadOnlyEnforcementTests(unittest.TestCase):
    """Hard boundary: evaluator must never write to disk."""

    def test_evaluate_never_opens_files_for_writing(self) -> None:
        import builtins
        tmp = Path(__import__("tempfile").mkdtemp(prefix="trading_evaluator_ro_"))
        self.addCleanup(lambda: __import__("shutil").rmtree(tmp, ignore_errors=True))
        workspace = _make_workspace(
            tmp,
            "alice",
            proof_packs=[_proof_pack("ec-0001")],
            market_proof={},
        )

        real_open = builtins.open
        opened_modes: list[str] = []

        def tracking_open(file, mode="r", *args, **kwargs):
            opened_modes.append(mode)
            return real_open(file, mode, *args, **kwargs)

        evaluator = TradingEvaluator(workspace=workspace, username="alice")
        with mock.patch("builtins.open", side_effect=tracking_open):
            evaluator.evaluate(run_context={"run_id": "r1"})

        write_modes = [m for m in opened_modes if any(flag in m for flag in ("w", "a", "x", "+"))]
        self.assertEqual(write_modes, [], f"Evaluator opened files for writing: {write_modes}")


if __name__ == "__main__":
    unittest.main()
