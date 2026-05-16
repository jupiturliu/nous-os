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
RUNTIME = EXAMPLES / "runtime"

for path in (EXAMPLES, SCRIPTS, RUNTIME):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from cls_v2 import compute_cls_v2
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
        self.assertEqual(
            set(benchmark["cls_v2"]["components"]),
            {
                "outcome_quality_delta",
                "correction_absorption",
                "memory_reuse_precision",
                "repeatability_gain",
                "boundary_integrity",
                "human_agency_preservation",
            },
        )
        self.assertEqual(benchmark["cls_v2"]["score"], compute_cls_v2(benchmark["cls_v2"]["components"]))

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
        self.assertIn("cls_v2_score", snapshot["metrics"])
        self.assertIn("cls_v2", snapshot["benchmark"])

    def test_compute_cls_v2_weighted_sum(self) -> None:
        components = {
            "outcome_quality_delta": 0.5,
            "correction_absorption": 1.0,
            "memory_reuse_precision": 0.8,
            "repeatability_gain": 0.4,
            "boundary_integrity": 1.0,
            "human_agency_preservation": 1.0,
        }

        self.assertEqual(compute_cls_v2(components), 0.705)

    def test_compute_cls_v2_requires_all_components(self) -> None:
        with self.assertRaises(KeyError):
            compute_cls_v2({"outcome_quality_delta": 0.5})


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
    def test_v2_roadmap_and_evaluator_docs_are_linked(self) -> None:
        readme = (ROOT / "README.md").read_text()
        phase3 = (ROOT / "NOUS-OS-PHASE3.md").read_text()
        roadmap = ROOT / "docs" / "north-star-v2-roadmap.md"
        evaluator = ROOT / "docs" / "domain-evaluator-interface.md"
        release_gate = ROOT / "docs" / "cross-repo-release-gate.md"

        self.assertTrue(roadmap.exists())
        self.assertTrue(evaluator.exists())
        self.assertTrue(release_gate.exists())
        self.assertIn("docs/north-star-v2-roadmap.md", readme)
        self.assertIn("docs/domain-evaluator-interface.md", readme)
        self.assertIn("docs/cross-repo-release-gate.md", readme)
        self.assertIn("docs/north-star-v2-roadmap.md", phase3)
        self.assertIn("DomainEvaluator.evaluate(run_context, outcome_artifacts) -> CLSComponents", evaluator.read_text())

    def test_public_release_smoke_docs_reference_release_gate(self) -> None:
        getting_started = (ROOT / "docs" / "getting-started.md").read_text()
        heartbeat = (ROOT / "docs" / "heartbeat-demo.md").read_text()

        for text in (getting_started, heartbeat):
            self.assertIn("Public Release Smoke", text)
            self.assertIn("scripts/check_cross_repo_release_gate.py --workspace /Users/liyao/nousos --json", text)

    def test_dashboard_snapshot_contains_cls_v2_components(self) -> None:
        snapshot = json.loads((ROOT / "examples" / "runtime" / "dashboard-data.json").read_text())
        components = snapshot["benchmark"]["cls_v2"]["components"]

        self.assertEqual(
            set(components),
            {
                "outcome_quality_delta",
                "correction_absorption",
                "memory_reuse_precision",
                "repeatability_gain",
                "boundary_integrity",
                "human_agency_preservation",
            },
        )
        self.assertEqual(snapshot["metrics"]["cls_v2_score"], snapshot["benchmark"]["cls_v2"]["score"])

    def test_pages_workflow_publishes_demo_and_favicon(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "pages.yml").read_text()

        self.assertIn("cp favicon.svg _site/", workflow)
        self.assertIn("cp docs/*.md _site/docs/", workflow)
        self.assertIn("cp demo/heartbeat-dashboard.html _site/demo/", workflow)
        self.assertIn("cp examples/runtime/dashboard-data.json _site/examples/runtime/", workflow)

    def test_site_pages_reference_favicon(self) -> None:
        homepage = (ROOT / "index.html").read_text()
        demo_page = (ROOT / "demo" / "heartbeat-dashboard.html").read_text()

        self.assertIn('<link rel="icon" href="favicon.svg" type="image/svg+xml">', homepage)
        self.assertIn('<link rel="icon" href="../favicon.svg" type="image/svg+xml">', demo_page)


if __name__ == "__main__":
    unittest.main()
