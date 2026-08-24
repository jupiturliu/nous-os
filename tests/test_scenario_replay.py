from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from nous_os.scenarios.replay import assert_snapshot_safe, replay_scenarios
from nous_os.scenarios.live import run_live_interfaces


ROOT = Path(__file__).resolve().parents[1]


class ScenarioReplayTests(unittest.TestCase):
    def test_real_profiles_match_reviewed_privacy_safe_snapshots(self):
        observed = replay_scenarios(ROOT)
        self.assertEqual(set(observed), {"student", "research", "trading-proof"})
        self.assertEqual(observed["student"]["world"]["saved_session"], "scenario-student-001")
        self.assertEqual(observed["research"]["world"]["notification_status"], "skipped")
        self.assertTrue(observed["trading-proof"]["world"]["all_components_zero"])

    def test_recording_is_explicit_and_round_trips_in_an_isolated_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshots = Path(directory)
            recorded = replay_scenarios(ROOT, snapshot_dir=snapshots, record=True)
            compared = replay_scenarios(ROOT, snapshot_dir=snapshots)
            self.assertEqual(recorded, compared)
            self.assertEqual(sorted(path.name for path in snapshots.iterdir()), [
                "research.json", "student.json", "trading-proof.json",
            ])

    def test_privacy_validator_rejects_content_secrets_endpoints_and_local_paths(self):
        unsafe_values = (
            {"markdown": "private research"},
            {"access_token": "fixture-secret"},
            {"safe": "https://example.invalid/hook"},
            {"safe": "/Users/example/private.txt"},
            {"safe": "learner@example.com"},
        )
        for value in unsafe_values:
            with self.assertRaises(ValueError):
                assert_snapshot_safe(value)

    def test_live_checks_mark_missing_credentials_skipped_without_returning_remote_content(self):
        report = run_live_interfaces(env={}, fetcher=lambda _: b"fixture")
        by_id = {check["id"]: check for check in report["checks"]}
        self.assertEqual(report["status"], "passed")
        self.assertEqual(by_id["notification-webhook"]["status"], "skipped")
        self.assertEqual(by_id["hermes-gateway"]["status"], "skipped")
        self.assertFalse(by_id["research-feed"]["remote_content_returned"])

    def test_live_checks_report_configured_interfaces_without_exposing_values(self):
        delivered = []

        class Adapter:
            def deliver(self, payload):
                delivered.append(payload)
                return 204

        report = run_live_interfaces(
            env={
                "NOUS_OS_RESEARCH_NOTIFICATION_WEBHOOK_URL": "https://secret.invalid/hook",
                "HERMES_API_SERVER_URL": "https://hermes.invalid/v1/chat/completions",
                "HERMES_API_SERVER_KEY": "fixture-secret",
            },
            fetcher=lambda _: b"fixture",
            webhook_factory=lambda _: Adapter(),
            hermes=lambda *_args, **_kwargs: {"route": "hermes-gateway", "reply": "private remote reply"},
        )
        serialized = str(report)
        self.assertEqual(report["status"], "passed")
        self.assertNotIn("fixture-secret", serialized)
        self.assertNotIn("private remote reply", serialized)
        self.assertEqual(set(delivered[0]), {"event_type", "capture_date", "status"})


if __name__ == "__main__":
    unittest.main()
