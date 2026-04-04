from __future__ import annotations

import json
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
SCRIPTS = ROOT / "scripts"

for path in (EXAMPLES, SCRIPTS):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

import nousos_heartbeat_demo as heartbeat_demo
import run_nous_dashboard as dashboard_server


class BenchmarkTests(unittest.TestCase):
    def test_build_benchmark_computes_expected_cls(self) -> None:
        round1 = {
            "metrics": {
                "avg_quality": 0.74,
                "tasks_dispatched": 2,
                "memory_hit_rate": 0.0,
            }
        }
        round2 = {
            "metrics": {
                "avg_quality": 0.93,
                "tasks_dispatched": 3,
                "memory_hit_rate": 1.0,
            }
        }
        override = {"kind": "risk", "reason": "Add a risk gate."}

        benchmark = heartbeat_demo.build_benchmark(
            round1=round1,
            round2=round2,
            alerts_count=2,
            episodes_logged=2,
            override=override,
        )

        self.assertEqual(benchmark["baseline"]["quality"], 0.74)
        self.assertEqual(benchmark["treatment"]["quality"], 0.93)
        self.assertEqual(benchmark["derived"]["episodes_logged"], 2)
        self.assertEqual(benchmark["derived"]["alerts_created"], 2)
        self.assertEqual(benchmark["public_standard"][0]["id"], "Q")
        self.assertEqual(benchmark["public_standard"][3]["id"], "R")

        q = round((0.93 - 0.74) / 0.74, 3)
        r = round((3 - 2) / 2, 3)
        expected_cls = round(0.4 * q + 0.2 * 1.0 + 0.2 * 1.0 + 0.2 * r, 3)
        self.assertEqual(benchmark["cls"]["score"], expected_cls)

    def test_build_dashboard_snapshot_contains_contract_fields(self) -> None:
        round1 = {
            "round": 1,
            "completed": [
                {"job_id": "impl-1", "topic": "implementation_queue", "output": {"quality_score": 0.72, "memory_hits": 0}}
            ],
            "metrics": {
                "tasks_dispatched": 2,
                "tasks_completed": 2,
                "avg_quality": 0.74,
                "memory_hit_rate": 0.0,
            },
        }
        round2 = {
            "round": 2,
            "completed": [
                {"job_id": "impl-2", "topic": "implementation_queue", "output": {"quality_score": 0.91, "memory_hits": 1}}
            ],
            "metrics": {
                "tasks_dispatched": 3,
                "tasks_completed": 3,
                "avg_quality": 0.93,
                "memory_hit_rate": 1.0,
            },
        }
        override = {"kind": "timing", "reason": "Add a sequencing checkpoint."}

        with tempfile.TemporaryDirectory() as tmp:
            runtime_root = Path(tmp)
            alerts_path = runtime_root / "agent-bus" / "alerts.json"
            episodes_path = runtime_root / "data" / "episodes" / "episodes.jsonl"
            dashboard_path = runtime_root / "dashboard-data.json"
            alerts_path.parent.mkdir(parents=True, exist_ok=True)
            episodes_path.parent.mkdir(parents=True, exist_ok=True)
            alerts_path.write_text(json.dumps({"items": [{"id": "a1"}, {"id": "a2"}]}))
            episodes_path.write_text('{"id":"e1"}\n{"id":"e2"}\n')

            with mock.patch.object(heartbeat_demo, "RUNTIME_AGENT_BUS", runtime_root / "agent-bus"), \
                 mock.patch.object(heartbeat_demo, "RUNTIME_EPISODES", episodes_path), \
                 mock.patch.object(heartbeat_demo, "RUNTIME_DASHBOARD", dashboard_path):
                snapshot = heartbeat_demo.build_dashboard_snapshot(
                    goal="Benchmark demo",
                    runs=[round1, round2],
                    override=override,
                )

        self.assertEqual(snapshot["current_round"], 2)
        self.assertEqual(snapshot["metrics"]["quality_delta"], 0.19)
        self.assertEqual(snapshot["metrics"]["episodes_logged"], 2)
        self.assertEqual(snapshot["metrics"]["alerts_created"], 2)
        self.assertEqual(snapshot["override"]["kind"], "timing")
        self.assertEqual(len(snapshot["timeline"]), 6)
        self.assertEqual(len(snapshot["topology"]["nodes"]), 8)
        self.assertIn("benchmark", snapshot)
        self.assertIn("cls_score", snapshot["metrics"])


class DashboardApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tempdir.name)
        self.dashboard_path = self.root / "dashboard-data.json"
        self.dashboard_path.write_text(json.dumps({"goal": "Saved snapshot", "metrics": {"avg_quality": 0.93}}))

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    def _make_handler(self, path: str, body: bytes = b"", headers: dict | None = None):
        handler = dashboard_server.DashboardHandler.__new__(dashboard_server.DashboardHandler)
        handler.path = path
        handler.headers = headers or {}
        handler.rfile = io.BytesIO(body)
        handler.wfile = io.BytesIO()
        handler.status_code = None
        handler.response_headers = {}
        handler.send_response = lambda status: setattr(handler, "status_code", status)
        handler.send_header = lambda key, value: handler.response_headers.__setitem__(key, value)
        handler.end_headers = lambda: None
        return handler

    def test_get_dashboard_data_returns_snapshot(self) -> None:
        handler = self._make_handler("/api/dashboard-data")
        with mock.patch.object(dashboard_server, "DASHBOARD_PATH", self.dashboard_path):
            handler.do_GET()
        payload = json.loads(handler.wfile.getvalue().decode("utf-8"))

        self.assertEqual(payload["goal"], "Saved snapshot")
        self.assertEqual(payload["metrics"]["avg_quality"], 0.93)
        self.assertEqual(handler.status_code, 200)

    def test_post_run_heartbeat_returns_created_snapshot(self) -> None:
        fake_snapshot = {
            "goal": "Live goal",
            "metrics": {"avg_quality": 0.9},
            "override": {"kind": "cost"},
        }
        body = json.dumps({"goal": "Live goal", "override_kind": "cost"}).encode("utf-8")
        handler = self._make_handler(
            "/api/run-heartbeat",
            body=body,
            headers={"Content-Length": str(len(body)), "Content-Type": "application/json"},
        )

        with mock.patch.object(dashboard_server, "run_heartbeat_flow", return_value=fake_snapshot) as mocked:
            handler.do_POST()
        payload = json.loads(handler.wfile.getvalue().decode("utf-8"))

        mocked.assert_called_once_with(goal="Live goal", override_kind="cost")
        self.assertEqual(handler.status_code, 201)
        self.assertEqual(payload["override"]["kind"], "cost")


class SiteContractTests(unittest.TestCase):
    def test_pages_workflow_publishes_demo_and_favicon(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "pages.yml").read_text()

        self.assertIn("cp favicon.svg _site/", workflow)
        self.assertIn("cp demo/heartbeat-dashboard.html _site/demo/", workflow)
        self.assertIn("cp examples/runtime/dashboard-data.json _site/examples/runtime/", workflow)

    def test_site_pages_reference_favicon(self) -> None:
        homepage = (ROOT / "index.html").read_text()
        demo_page = (ROOT / "demo" / "heartbeat-dashboard.html").read_text()

        self.assertIn('<link rel="icon" href="favicon.svg" type="image/svg+xml">', homepage)
        self.assertIn('<link rel="icon" href="../favicon.svg" type="image/svg+xml">', demo_page)


if __name__ == "__main__":
    unittest.main()
