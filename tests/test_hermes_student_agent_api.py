from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class HermesStudentAgentApiTests(unittest.TestCase):
    def test_api_route_is_hermes_gateway_adapter_not_browser_llm_config(self) -> None:
        route_path = ROOT / "api" / "hermes-student-agent.js"
        self.assertTrue(route_path.exists(), "api/hermes-student-agent.js must exist")
        source = route_path.read_text()

        self.assertIn("HERMES_API_SERVER_URL", source)
        self.assertIn("HERMES_API_SERVER_KEY", source)
        self.assertIn("HERMES_GATEWAY_URL", source)
        self.assertIn("HERMES_GATEWAY_API_KEY", source)
        self.assertIn("HERMES_GATEWAY_MODEL", source)
        self.assertIn("/v1/chat/completions", source)
        self.assertIn("X-Hermes-Session-Key", source)
        self.assertIn("hermes-gateway", source)
        self.assertIn("hints, subquestions, source-check steps", source)
        self.assertIn("Do not write the final answer", source)
        self.assertIn("do_not_request_or_store_private_student_data", source)
        self.assertIn("module.exports._private", source)
        self.assertNotIn("OPENAI_API_KEY", source)
        self.assertNotIn("api.openai.com", source)
        self.assertIn("resolveHermesApiServerUrl", source)
        self.assertIn("resolveHermesApiServerKey", source)

    def test_api_route_has_valid_javascript_syntax(self) -> None:
        for route_path in (
            ROOT / "api" / "hermes-student-agent.js",
            ROOT / "api" / "student-sandbox-session.js",
        ):
            result = subprocess.run(
                ["node", "-c", str(route_path)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_student_sandbox_session_api_saves_local_redacted_records(self) -> None:
        route_path = ROOT / "api" / "student-sandbox-session.js"
        self.assertTrue(route_path.exists(), "api/student-sandbox-session.js must exist")
        source = route_path.read_text()

        self.assertIn("student-sandbox-sessions", source)
        self.assertIn("local-filesystem", source)
        self.assertIn("browser_storage: false", source)
        self.assertIn("redactPrivateText", source)
        self.assertIn("containsPrivatePattern", source)
        self.assertIn("module.exports._private", source)
        self.assertNotIn("OPENAI_API_KEY", source)
        self.assertNotIn("api.openai.com", source)

        script = """
          const route = require('./api/student-sandbox-session')._private;
          const record = route.buildRecord({
            session_id: 'student-test-session',
            worksheet: { question: 'Email me at student@example.com about batteries' },
            reflection: { reflect_help: 'Call 415-555-1212' },
            source_cards: [{ id: 'source-1', title: 'Study', author: 'NIH', date: '2025', evidence: 'Measured sleep', uncertainty: 'Small sample', decision: 'accepted' }],
            observer: { student_explained_question: 'yes', named_source_issue: 'yes', kept_human_responsibility: 'yes', used_ai_for_hints: 'yes' },
            chat_turns: [{ role: 'student', text: 'My SSN is 123-45-6789' }]
          });
          if (!record.privacy.private_pattern_detected) process.exit(2);
          const dump = JSON.stringify(record);
          if (dump.includes('student@example.com') || dump.includes('415-555-1212') || dump.includes('123-45-6789')) process.exit(3);
          if (record.storage.backend !== 'local-filesystem' || record.storage.browser_storage !== false) process.exit(4);
          if (record.source_cards.length !== 1 || record.source_cards[0].decision !== 'accepted') process.exit(5);
          if (record.research_signals.accepted_sources !== 1) process.exit(6);
          if (record.research_signals.observer_check_count !== 4) process.exit(7);
          if (record.readiness.ready_for_review !== false) process.exit(8);
          const packet = route.buildReviewPacket(record);
          if (!packet.includes('Student Sandbox v1 Trial Review')) process.exit(9);
          if (!packet.includes('Next-run Change')) process.exit(10);
          if (packet.includes('student@example.com') || packet.includes('415-555-1212') || packet.includes('123-45-6789')) process.exit(11);
        """
        result = subprocess.run(
            ["node", "-e", script],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
