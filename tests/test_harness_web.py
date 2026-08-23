from __future__ import annotations

import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path

from nous_os.artifacts import publish_site_data, stage_site
from nous_os.core import HarnessContext, RuntimePaths
from nous_os.web import create_server
from nous_os.workflows.student_sandbox import StudentSandboxStore


class HarnessWebTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.paths = RuntimePaths.resolve(self.temp.name)
        self.static = Path(self.temp.name) / "static"
        self.static.mkdir()
        (self.static / "index.html").write_text("<h1>NOUS OS</h1>")
        self.context = HarnessContext(profile_name="student", paths=self.paths)
        self.context.register("student-sandbox", StudentSandboxStore(self.context))
        self.server = create_server(self.context, static_root=self.static, port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temp.cleanup()

    def request(self, method, path, payload=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        body = json.dumps(payload).encode() if payload is not None else None
        headers = {"Content-Type": "application/json"} if body else {}
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        data = response.read()
        connection.close()
        return response.status, response.getheader("Content-Type"), data

    def test_health_static_and_dashboard_routes(self):
        status, _, body = self.request("GET", "/api/health")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["profile"], "student")
        status, _, body = self.request("GET", "/")
        self.assertEqual((status, body), (200, b"<h1>NOUS OS</h1>"))
        status, _, _ = self.request("GET", "/api/dashboard-data")
        self.assertEqual(status, 404)

    def test_student_session_route_is_event_backed(self):
        status, _, body = self.request("POST", "/api/student-sandbox-session", {
            "session_id": "student-session-web",
            "worksheet": {"question": "Call 415-555-1212", "boundary": "student decides"},
        })
        self.assertEqual(status, 200)
        self.assertTrue(json.loads(body)["private_pattern_detected"])
        status, _, body = self.request("GET", "/api/student-sandbox-session?session_id=student-session-web")
        self.assertEqual(status, 200)
        self.assertIn("[redacted-phone]", json.loads(body)["worksheet"]["question"])
        status, content_type, body = self.request(
            "GET", "/api/student-sandbox-session?session_id=student-session-web&format=markdown"
        )
        self.assertEqual(status, 200)
        self.assertIn("text/markdown", content_type)
        self.assertIn(b"Trial Review", body)


class SiteArtifactTests(unittest.TestCase):
    def test_manifest_stages_stable_public_paths(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=root) as directory:
            target = Path(directory) / "_site"
            stage_site(root, target)
            self.assertTrue((target / "index.html").exists())
            self.assertTrue((target / "demo" / "student-sandbox-v1.html").exists())
            self.assertTrue((target / "examples" / "runtime" / "dashboard-data.json").exists())
            self.assertTrue((target / "docs" / "harness" / "README.md").exists())
            self.assertTrue((target / "LICENSE").exists())

    def test_publication_is_explicit_and_rejects_private_data(self):
        with tempfile.TemporaryDirectory() as runtime, tempfile.TemporaryDirectory() as public:
            paths = RuntimePaths.resolve(runtime).ensure()
            research = paths.projections / "research-records"
            research.mkdir(parents=True)
            (paths.projections / "dashboard-data.json").write_text(json.dumps({"privacy": "public"}))
            (research / "latest.json").write_text(json.dumps({"privacy": "public"}))
            dashboard, latest = publish_site_data(paths, public)
            self.assertTrue(dashboard.exists())
            self.assertTrue(latest.exists())
            (paths.projections / "dashboard-data.json").write_text(json.dumps({"email": "learner@example.com"}))
            with self.assertRaisesRegex(ValueError, "private text"):
                publish_site_data(paths, public)


if __name__ == "__main__":
    unittest.main()
