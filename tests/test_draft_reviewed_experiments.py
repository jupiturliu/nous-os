"""Contract tests for draft_reviewed_experiments helper.

The helper reads existing trading-agent proof packs and produces draft
ReviewedExperiment payloads for human sign-off. Drafts must:

- ground hypothesis text in actual pack fields (no fabrication)
- redact capital-action verb tokens so the downstream writer accepts the text
- emit source_ref paths relative to the trading-agent repo root
- never reach the downstream writer until --apply is requested
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import draft_reviewed_experiments as helper


def _write_pack(packs_dir: Path, candidate_id: str, **overrides) -> Path:
    pack = {
        "candidate_id": candidate_id,
        "ticker": "hybrid_v2",
        "capital_action_authorized": False,
        "execution_boundary": {
            "broker_action_allowed": False,
            "creates_order_or_draft": False,
            "creates_promotion_or_approval": False,
            "mutates_runtime_live_state": False,
            "production_config_changed": False,
        },
        "blocking_states": ["human_review_required"],
        "required_human_decision": "recalibrate_or_defer: confidence bucket realized rate diverges from expected",
        "why_review_ready": "validated=40 matured=True",
        "validated_claims": [f"claim-{i}" for i in range(40)],
        "missing_evidence": [],
    }
    pack.update(overrides)
    path = packs_dir / f"{candidate_id}.json"
    path.write_text(json.dumps(pack))
    return path


def _make_workspace(tmp: Path, user: str = "alice") -> Path:
    packs_dir = (
        tmp / "trading-agent" / "data" / "users" / user
        / "promotion_reviews" / "proof_packs"
    )
    packs_dir.mkdir(parents=True)
    _write_pack(packs_dir, "ec-0001")
    _write_pack(packs_dir, "ec-0002", required_human_decision=None, why_review_ready=None)
    # index.json should be ignored, not turned into a draft.
    (packs_dir / "index.json").write_text(json.dumps({"schema_version": 1}))
    return tmp


class DraftBuildingTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = Path(tempfile.mkdtemp(prefix="draft_helper_test_"))
        self.addCleanup(lambda: shutil.rmtree(self._tmp, ignore_errors=True))
        self.workspace = _make_workspace(self._tmp)

    def _run(self, *extra: str) -> dict:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "draft_reviewed_experiments.py"),
             "--workspace", str(self.workspace),
             "--user", "alice",
             *extra],
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, msg=f"stderr={result.stderr}")
        return json.loads(result.stdout)

    def test_helper_skips_index_json_and_packs_without_candidate_id(self) -> None:
        out = self._run()
        candidate_ids = [d["candidate_id"] for d in out["drafts"]]
        self.assertEqual(candidate_ids, ["ec-0001", "ec-0002"])
        self.assertEqual(out["scanned"], 2)

    def test_draft_source_ref_is_relative_to_trading_agent_root(self) -> None:
        out = self._run()
        for draft in out["drafts"]:
            self.assertTrue(
                draft["source_ref"].startswith("data/users/alice/"),
                msg=f"unexpected source_ref: {draft['source_ref']}",
            )
            self.assertNotIn("trading-agent", draft["source_ref"])

    def test_hypothesis_uses_required_human_decision_when_available(self) -> None:
        out = self._run()
        ec1 = next(d for d in out["drafts"] if d["candidate_id"] == "ec-0001")
        self.assertIn("recalibrate_or_defer", ec1["hypothesis"])
        self.assertIn("ec-0001", ec1["hypothesis"])

    def test_hypothesis_falls_back_when_decision_field_missing(self) -> None:
        out = self._run()
        ec2 = next(d for d in out["drafts"] if d["candidate_id"] == "ec-0002")
        # Pack ec-0002 has no required_human_decision and no why_review_ready,
        # so the helper should fall back to the blocking_states phrasing.
        self.assertIn("blocking_states", ec2["hypothesis"])
        self.assertIn("ec-0002", ec2["hypothesis"])

    def test_capital_action_verbs_are_redacted(self) -> None:
        packs_dir = self.workspace / "trading-agent" / "data" / "users" / "alice" / "promotion_reviews" / "proof_packs"
        _write_pack(
            packs_dir, "ec-0099",
            required_human_decision="operator should approve the recalibration before next cycle",
        )
        out = self._run()
        bad = next(d for d in out["drafts"] if d["candidate_id"] == "ec-0099")
        haystack = " " + bad["hypothesis"].lower() + " "
        for token in (" approve ", " buy ", " sell ", " execute "):
            self.assertNotIn(token, haystack, msg=f"{token!r} leaked into hypothesis")
        self.assertIn("[approve_redacted]", bad["hypothesis"])

    def test_helper_does_not_apply_without_explicit_flag(self) -> None:
        out = self._run()
        self.assertEqual(out["applied"], [])
        for draft in out["drafts"]:
            self.assertFalse(draft["applied"])

    def test_apply_unknown_candidate_id_fails_loudly(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "draft_reviewed_experiments.py"),
             "--workspace", str(self.workspace),
             "--user", "alice",
             "--apply", "ec-9999",
             "--apply-dry-run"],
            capture_output=True, text=True, timeout=30,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ec-9999", result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
