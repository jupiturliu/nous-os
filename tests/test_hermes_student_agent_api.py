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
        route_path = ROOT / "api" / "hermes-student-agent.js"
        result = subprocess.run(
            ["node", "-c", str(route_path)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
