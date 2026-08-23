from __future__ import annotations

import unittest

from nous_os.web.hermes import build_messages, resolve_url, system_prompt
from nous_os.workflows.student_sandbox import build_record


class HermesStudentAgentApiTests(unittest.TestCase):
    def test_hermes_adapter_preserves_gateway_and_learning_policy(self) -> None:
        env = {"HERMES_GATEWAY_URL": "http://127.0.0.1:8642/", "HERMES_GATEWAY_MODEL": "hermes-agent"}
        self.assertEqual(resolve_url(env), "http://127.0.0.1:8642/v1/chat/completions")
        prompt = system_prompt()
        self.assertIn("Do not write the final answer", prompt)
        self.assertIn("private student data", prompt)
        messages = build_messages("Help me research batteries", {
            "worksheet": {"question": "battery recycling", "boundary": "hints only"}
        })
        self.assertEqual([message["role"] for message in messages], ["system", "user"])
        self.assertIn("hints only", messages[1]["content"])

    def test_direct_api_server_url_takes_precedence(self) -> None:
        env = {
            "HERMES_API_SERVER_URL": "https://gateway.example/v1/chat/completions",
            "HERMES_GATEWAY_URL": "http://ignored.example",
        }
        self.assertEqual(resolve_url(env), env["HERMES_API_SERVER_URL"])

    def test_student_session_record_is_local_redacted_and_reviewable(self) -> None:
        record = build_record({
            "session_id": "student-test-session",
            "worksheet": {
                "question": "Email me at student@example.com about batteries",
                "boundary": "hints only",
            },
            "reflection": {"reflect_help": "Call 415-555-1212"},
            "source_cards": [{
                "id": "source-1", "title": "Study", "author": "NIH", "date": "2025",
                "evidence": "Measured sleep", "uncertainty": "Small sample", "decision": "accepted",
            }],
            "observer": {
                "student_explained_question": "yes", "named_source_issue": "yes",
                "kept_human_responsibility": "yes", "used_ai_for_hints": "yes",
            },
            "chat_turns": [{"role": "student", "text": "My SSN is 123-45-6789"}],
        })
        serialized = str(record)
        self.assertTrue(record["privacy"]["private_pattern_detected"])
        self.assertNotIn("student@example.com", serialized)
        self.assertNotIn("415-555-1212", serialized)
        self.assertNotIn("123-45-6789", serialized)
        self.assertEqual(record["storage"]["backend"], "nous-os-artifact-store")
        self.assertFalse(record["storage"]["browser_storage"])
        self.assertEqual(record["research_signals"]["accepted_sources"], 1)
        self.assertEqual(record["research_signals"]["observer_check_count"], 4)


if __name__ == "__main__":
    unittest.main()
