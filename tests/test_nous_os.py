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
import student_sandbox_v0 as student_sandbox
import check_harness_inventory as harness_inventory


class BenchmarkTests(unittest.TestCase):
    def _sample_benchmark(self) -> dict:
        return heartbeat_demo.build_benchmark(
            round1={"metrics": {"avg_quality": 0.74, "tasks_dispatched": 2, "memory_hit_rate": 0.0}},
            round2={"metrics": {"avg_quality": 0.93, "tasks_dispatched": 3, "memory_hit_rate": 1.0}},
            alerts_count=2,
            episodes_logged=2,
            override={"kind": "risk", "reason": "Add a risk gate."},
        )

    def _write_trading_fixture(self, workspace: Path, username: str = "alice") -> None:
        user_root = workspace / "trading-agent" / "data" / "users" / username
        proof_dir = user_root / "promotion_reviews" / "proof_packs"
        market_dir = user_root / "market_proof"
        proof_dir.mkdir(parents=True)
        market_dir.mkdir(parents=True)
        boundary = {
            "broker_action_allowed": False,
            "creates_order_or_draft": False,
            "creates_promotion_or_approval": False,
            "mutates_runtime_live_state": False,
            "production_config_changed": False,
        }
        (proof_dir / "ec-0001.json").write_text(json.dumps({
            "candidate_id": "ec-0001",
            "capital_action_authorized": False,
            "execution_boundary": boundary,
        }))
        (market_dir / "baseline_comparisons.jsonl").write_text("\n".join([
            json.dumps({
                "outcome_label": "matured",
                "outperformed_benchmark": True,
                "execution_boundary": boundary,
            }),
            json.dumps({
                "outcome_label": "matured",
                "outperformed_benchmark": False,
                "execution_boundary": boundary,
            }),
        ]))
        (market_dir / "forecast_ledger_summary.json").write_text(json.dumps({
            "brier_improvement_over_baseline": 0.25,
            "execution_boundary": boundary,
        }))

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

    def test_trading_vertical_benchmark_uses_evidence_backed_evaluator_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            self._write_trading_fixture(workspace)
            benchmark = heartbeat_demo.maybe_apply_trading_evaluator(
                self._sample_benchmark(),
                "trading_vertical",
                workspace=workspace,
            )

        self.assertEqual(benchmark["evidence_source"], "trading_evaluator")
        self.assertEqual(benchmark["evaluator_user"], "alice")
        self.assertEqual(benchmark["cls_v2"]["components"]["outcome_quality_delta"], 0.5)
        self.assertEqual(benchmark["cls_v2"]["components"]["repeatability_gain"], 0.25)
        self.assertEqual(benchmark["cls_v2"]["components"]["boundary_integrity"], 1.0)

    def test_trading_vertical_benchmark_marks_synthetic_fallback_when_artifacts_absent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            benchmark = heartbeat_demo.maybe_apply_trading_evaluator(
                self._sample_benchmark(),
                "trading_vertical",
                workspace=Path(tmp),
            )

        self.assertEqual(benchmark["evidence_source"], "synthetic_demo_fallback")
        self.assertIn("no user has populated", benchmark["fallback_reason"])

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
        self.assertEqual(snapshot["demo_mode"], "student")
        self.assertEqual(snapshot["audience"], "high_school_student")
        self.assertEqual(snapshot["north_star"], "education/research-first human-AI co-evolution")
        self.assertTrue(snapshot["human_agency"]["human_keeps_final_responsibility"])
        self.assertIn("final responsibility", snapshot["human_agency"]["human_keeps"])
        self.assertIn("practice generation", snapshot["human_agency"]["ai_helps_with"])
        self.assertEqual(snapshot["reflection"]["prompt"], "What did the AI help with, and what remains my responsibility?")
        self.assertEqual(snapshot["first_vertical"]["name"], "trading-agent")
        self.assertEqual(snapshot["research_record"]["demo_mode"], "student")
        self.assertEqual(snapshot["research_record"]["human_boundary"]["kind"], "timing")
        self.assertTrue(snapshot["research_record"]["memory_update"]["stored"])
        self.assertFalse(snapshot["research_record"]["privacy"]["contains_private_student_data"])
        self.assertEqual(len(snapshot["safety_boundaries"]), 4)
        self.assertEqual(len(snapshot["timeline"]), 7)
        self.assertEqual(len(snapshot["topology"]["nodes"]), 9)
        self.assertIn("obsidian", {node["id"] for node in snapshot["topology"]["nodes"]})
        self.assertIn(("human", "obsidian"), {(edge["from"], edge["to"]) for edge in snapshot["topology"]["edges"]})
        self.assertIn(("obsidian", "trustmem"), {(edge["from"], edge["to"]) for edge in snapshot["topology"]["edges"]})
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

    def test_student_sandbox_emits_local_private_research_record(self) -> None:
        record = student_sandbox.build_sandbox_research_record(
            intent="My email is student@example.com and I need help planning a science project.",
            boundary_kind="learning",
        )

        self.assertEqual(record["demo_mode"], "student")
        self.assertEqual(record["human_boundary"]["kind"], "learning")
        self.assertIn("[redacted-email]", record["human_intent"])
        self.assertFalse(record["privacy"]["contains_private_student_data"])
        self.assertTrue(record["sandbox"]["local_only"])
        self.assertFalse(record["sandbox"]["external_model_calls"])
        self.assertTrue(record["sandbox"]["refuses_private_storage_without_anonymization"])
        self.assertTrue(record["sandbox"]["private_detail_detected"])
        self.assertGreaterEqual(len(record["sandbox"]["clarifying_questions"]), 3)
        self.assertGreaterEqual(len(record["sandbox"]["hints"]), 3)
        self.assertGreaterEqual(len(record["sandbox"]["practice"]), 1)
        self.assertGreaterEqual(len(record["sandbox"]["source_check"]), 2)
        self.assertIn("responsibility", record["reflection"]["prompt"])


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
        body = json.dumps({"goal": "Live goal", "override_kind": "cost", "demo_mode": "research_lab"}).encode("utf-8")
        handler = self._make_handler(
            "/api/run-heartbeat",
            body=body,
            headers={"Content-Length": str(len(body)), "Content-Type": "application/json"},
        )

        with mock.patch.object(dashboard_server, "run_heartbeat_flow", return_value=fake_snapshot) as mocked:
            handler.do_POST()
        payload = json.loads(handler.wfile.getvalue().decode("utf-8"))

        mocked.assert_called_once_with(goal="Live goal", override_kind="cost", demo_mode="research_lab")
        self.assertEqual(handler.status_code, 201)
        self.assertEqual(payload["override"]["kind"], "cost")


class SiteContractTests(unittest.TestCase):
    def test_harness_inventory_is_machine_readable_and_current(self) -> None:
        inventory_path = ROOT / "docs" / "harness" / "HARNESS_INVENTORY.json"
        inventory = json.loads(inventory_path.read_text())
        result = harness_inventory.validate_inventory(inventory_path)

        self.assertTrue(result["ok"], result["issues"])
        self.assertEqual(inventory["project"], "nous-os")
        surface_ids = {surface["id"] for surface in inventory["surfaces"]}
        self.assertIn("student_sandbox_v0", surface_ids)
        self.assertIn("trading_evaluator", surface_ids)
        self.assertIn("latest_research_record", surface_ids)
        self.assertIn("cross_repo_release_gate", surface_ids)
        self.assertIn("github_pages_workflow", surface_ids)
        self.assertIn("live trading state", inventory["default_boundary"])

    def test_v2_roadmap_and_evaluator_docs_are_linked(self) -> None:
        readme = (ROOT / "README.md").read_text()
        phase3 = (ROOT / "NOUS-OS-PHASE3.md").read_text()
        roadmap = ROOT / "docs" / "north-star-v2-roadmap.md"
        evaluator = ROOT / "docs" / "domain-evaluator-interface.md"
        release_gate = ROOT / "docs" / "cross-repo-release-gate.md"
        review_template = ROOT / "docs" / "review-template.md"
        demo_refresh_plan = ROOT / "docs" / "plans" / "2026-05-16-human-ai-coevolution-demo-refresh-plan.md"
        education_research = ROOT / "docs" / "education-research-narrative.md"
        harness_readme = ROOT / "docs" / "harness" / "README.md"
        harness_context = ROOT / "docs" / "harness" / "context-index.md"
        second_vertical = ROOT / "docs" / "second-vertical-entry-criteria.md"
        one_pager = ROOT / "docs" / "NOUS-OS-Cognitive-COO-One-Pager.md"
        one_pager_en = ROOT / "docs" / "NOUS-OS-Cognitive-COO-One-Pager.en.md"

        self.assertTrue(roadmap.exists())
        self.assertTrue(evaluator.exists())
        self.assertTrue(release_gate.exists())
        self.assertTrue(review_template.exists())
        self.assertTrue(demo_refresh_plan.exists())
        self.assertTrue(education_research.exists())
        self.assertTrue(harness_readme.exists())
        self.assertTrue(harness_context.exists())
        self.assertTrue(second_vertical.exists())
        self.assertTrue(one_pager.exists())
        self.assertTrue(one_pager_en.exists())
        self.assertIn("education and research project", readme)
        self.assertIn("docs/north-star-v2-roadmap.md", readme)
        self.assertIn("docs/education-research-narrative.md", readme)
        self.assertIn("docs/domain-evaluator-interface.md", readme)
        self.assertIn("docs/harness/README.md", readme)
        self.assertIn("docs/cross-repo-release-gate.md", readme)
        self.assertIn("docs/NOUS-OS-Cognitive-COO-One-Pager.md", readme)
        self.assertIn("docs/NOUS-OS-Cognitive-COO-One-Pager.en.md", readme)
        self.assertIn("docs/north-star-v2-roadmap.md", phase3)
        self.assertIn("second-vertical-entry-criteria.md", roadmap.read_text())
        self.assertIn("education and research project", roadmap.read_text())
        self.assertIn("first vertical application", roadmap.read_text())
        self.assertIn("education/research traction case", roadmap.read_text())
        self.assertIn("Humans and AI learn together — with boundaries", demo_refresh_plan.read_text())
        self.assertIn("Student Learning Companion", demo_refresh_plan.read_text())
        self.assertIn("Trading Agent Research Proof", demo_refresh_plan.read_text())
        self.assertIn("How should today's high-school students face AI", education_research.read_text())
        self.assertIn("Privacy boundary", education_research.read_text())
        self.assertIn("Trading Brain / `trading-agent` remains the first vertical application", education_research.read_text())
        self.assertIn("DomainEvaluator.evaluate(run_context, outcome_artifacts) -> CLSComponents", evaluator.read_text())
        self.assertIn("What confused the viewer?", review_template.read_text())
        self.assertIn("Boundary Clarity", review_template.read_text())
        self.assertIn("Next Run Change", review_template.read_text())
        self.assertIn("context index + boundary map + artifact contracts + evaluator specs + release gates + evidence write-back", harness_readme.read_text())
        self.assertIn("NOUS OS Harness Context Index", harness_context.read_text())
        self.assertIn("Second vertical work remains deferred", second_vertical.read_text())
        self.assertIn("Cognitive COO Operating System", one_pager_en.read_text())
        self.assertIn("TrustMem: agents' trustworthy hippocampus", one_pager_en.read_text())
        self.assertIn("Obsidian knowledge sedimentation", one_pager_en.read_text())

    def test_landing_page_uses_plain_human_ai_framing_without_overclaiming(self) -> None:
        html = (ROOT / "index.html").read_text()

        self.assertIn("Human-AI Learning System", html)
        self.assertIn("learning system", html)
        self.assertIn("learning notes", html)
        self.assertIn("demo/assets/architecture/nous-os-cognitive-coo-architecture-fireworks.png", html)
        self.assertIn("Trading Brain as the first vertical proof", html)
        self.assertIn("Production hardening is still in progress", html)
        self.assertNotIn("<em>Cognitive COO OS</em>", html)
        self.assertNotIn("COO Operating System", html)
        self.assertNotIn("fully autonomous trading system", html.lower())
        self.assertNotIn("production-ready multi-tenant saas", html.lower())

    def test_architecture_asset_exists_for_homepage(self) -> None:
        asset = ROOT / "demo" / "assets" / "architecture" / "nous-os-cognitive-coo-architecture-fireworks.png"

        self.assertTrue(asset.exists())

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

    def test_dashboard_snapshot_models_human_ai_coevolution(self) -> None:
        snapshot = json.loads((ROOT / "examples" / "runtime" / "dashboard-data.json").read_text())
        dashboard = (ROOT / "demo" / "heartbeat-dashboard.html").read_text()

        self.assertIn(snapshot["demo_mode"], {"student", "trading_vertical", "research_lab"})
        self.assertEqual(snapshot["north_star"], "education/research-first human-AI co-evolution")
        self.assertIn("human_sets_goal", snapshot["human_agency"])
        self.assertIn("safety_boundaries", snapshot)
        self.assertIn("reflection", snapshot)
        self.assertIn("research_record", snapshot)
        self.assertEqual(snapshot["first_vertical"]["name"], "trading-agent")
        self.assertIn("not to recommend trades", snapshot["goal"].lower() + snapshot["first_vertical"]["not_for"].lower())
        self.assertIn("Humans and AI learn together — with boundaries", dashboard)
        self.assertIn("Student Learning Companion", dashboard)
        self.assertIn("Trading Agent Research Proof", dashboard)
        self.assertIn("Research Lab / Teacher View", dashboard)
        self.assertIn("Human Agency", dashboard)
        self.assertIn("Safety Boundaries", dashboard)
        self.assertIn("Research Record", dashboard)
        self.assertIn("Evidence source", dashboard)
        self.assertIn("Synthetic demo benchmark", dashboard)
        self.assertIn("Evidence-backed evaluator", dashboard)
        self.assertIn("../examples/runtime/research-records/latest.json", dashboard)
        self.assertIn("node-obsidian", dashboard)
        self.assertIn("edge-obsidian-trustmem", dashboard)

    def test_latest_research_record_is_published_and_private_by_default(self) -> None:
        snapshot = json.loads((ROOT / "examples" / "runtime" / "dashboard-data.json").read_text())
        record_path = ROOT / "examples" / "runtime" / "research-records" / "latest.json"
        record = json.loads(record_path.read_text())

        self.assertTrue(record_path.exists())
        self.assertEqual(snapshot["research_record"]["run_id"], record["run_id"])
        self.assertEqual(record["demo_mode"], snapshot["demo_mode"])
        self.assertIn(record["audience"], {"student", "parent", "teacher", "researcher"})
        self.assertIn("human_intent", record)
        self.assertIn("ai_first_pass", record)
        self.assertIn("human_boundary", record)
        self.assertIn("memory_update", record)
        self.assertIn("ai_second_pass", record)
        self.assertIn("reflection", record)
        self.assertIn("metrics", record)
        self.assertFalse(record["privacy"]["contains_private_student_data"])
        self.assertTrue(record["memory_update"]["stored"])
        self.assertTrue(record["ai_second_pass"]["behavior_changed"])

    def test_pages_workflow_publishes_demo_and_favicon(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "pages.yml").read_text()

        self.assertIn("cp about.html _site/", workflow)
        self.assertIn("cp favicon.svg _site/", workflow)
        self.assertIn("cp docs/*.md _site/docs/", workflow)
        self.assertIn("cp -R docs/harness _site/docs/", workflow)
        self.assertIn("cp -R demo/assets _site/demo/", workflow)
        self.assertIn("cp demo/heartbeat-dashboard.html _site/demo/", workflow)
        self.assertIn("cp examples/runtime/dashboard-data.json _site/examples/runtime/", workflow)
        self.assertIn("cp examples/runtime/research-records/latest.json _site/examples/runtime/research-records/", workflow)

    def test_site_pages_reference_favicon(self) -> None:
        homepage = (ROOT / "index.html").read_text()
        demo_page = (ROOT / "demo" / "heartbeat-dashboard.html").read_text()
        about_page = (ROOT / "about.html").read_text()

        self.assertIn('<link rel="icon" href="favicon.svg" type="image/svg+xml">', homepage)
        self.assertIn('<link rel="icon" href="../favicon.svg" type="image/svg+xml">', demo_page)
        self.assertIn('<link rel="icon" href="favicon.svg" type="image/svg+xml">', about_page)

    def test_about_page_explains_nous_origin_and_human_ai_future(self) -> None:
        homepage = (ROOT / "index.html").read_text()
        about_page = (ROOT / "about.html").read_text()

        self.assertIn('href="/about.html"', homepage)
        self.assertIn("Why <em>NOUS</em>?", about_page)
        self.assertIn("Greek word for intellect", about_page)
        self.assertIn("exploring the future of AI and human beings together with my daughter", about_page)
        self.assertIn("Humans and AI can cooperate better", about_page)
        self.assertIn("Human-AI Learning System", about_page)
        self.assertIn("demo/assets/architecture/nous-os-cognitive-coo-architecture-fireworks.png", about_page)


if __name__ == "__main__":
    unittest.main()
