from __future__ import annotations

import json
import io
import os
import subprocess
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
import student_sandbox_v1
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

    def test_heartbeat_demo_import_does_not_emit_optional_redis_warning(self) -> None:
        result = subprocess.run(
            [sys.executable, "-c", "import sys; sys.path.insert(0, 'examples'); import nousos_heartbeat_demo"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertEqual(result.stdout, "")
        self.assertNotIn("Redis not available", result.stderr)
        self.assertNotIn("MemoryBackend only", result.stderr)

    def test_heartbeat_demo_run_does_not_emit_optional_redis_warning(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/run_nous_heartbeat.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        combined = result.stdout + result.stderr
        self.assertNotIn("Redis not available", combined)
        self.assertNotIn("MemoryBackend only", combined)

    def test_runtime_backend_policy_uses_redis_or_sqlite_in_production(self) -> None:
        with mock.patch.dict(os.environ, {"NOUS_OS_ENV": "production"}, clear=True):
            policy = heartbeat_demo.runtime_backend_policy()
            self.assertEqual(policy["requested_backend"], "sqlite")
            self.assertEqual(policy["episode_store"], "sqlite")
            self.assertFalse(policy["memory_fallback_allowed"])

        with mock.patch.dict(os.environ, {"NOUS_OS_ENV": "production", "REDIS_URL": "redis://localhost:6379"}, clear=True):
            policy = heartbeat_demo.runtime_backend_policy()
            self.assertEqual(policy["requested_backend"], "redis")
            self.assertEqual(policy["synapse_backend"], "redis")
            self.assertEqual(policy["episode_store"], "sqlite")

        with mock.patch.dict(
            os.environ,
            {"NOUS_OS_ENV": "production", "NOUS_OS_RUNTIME_BACKEND": "memory"},
            clear=True,
        ):
            self.assertEqual(heartbeat_demo.resolve_runtime_backend(), "sqlite")

    def test_student_sandbox_v1_builds_20_minute_learning_loop_without_final_answer(self) -> None:
        packet = student_sandbox_v1.build_learning_loop_packet(
            research_question="My email is student@example.com. How should I research CRISPR ethics for biology class?",
            student_level="high_school",
        )

        self.assertEqual(packet["version"], "student_sandbox_v1")
        self.assertEqual(packet["student_level"], "high_school")
        self.assertTrue(packet["privacy"]["local_only"])
        self.assertFalse(packet["privacy"]["external_model_calls"])
        self.assertFalse(packet["privacy"]["contains_private_student_data"])
        self.assertTrue(packet["privacy"]["private_detail_detected"])
        self.assertEqual(packet["student_intent"], "[redacted-by-policy]")
        self.assertNotIn("student@example.com", packet["student_intent"])
        self.assertEqual(packet["twenty_minute_loop"]["total_minutes"], 20)
        self.assertEqual(
            [phase["id"] for phase in packet["twenty_minute_loop"]["phases"]],
            ["intent", "ai_first_pass", "human_boundary", "source_check", "ai_second_pass", "reflection"],
        )
        self.assertEqual(packet["ai_support_policy"], "hints_not_answers")
        self.assertNotIn("final_answer", json.dumps(packet).lower())
        self.assertIn("What did AI help with?", packet["reflection_card"]["student_prompts"])
        self.assertIn("What did I verify?", packet["reflection_card"]["student_prompts"])
        self.assertIn("What remains my responsibility?", packet["reflection_card"]["student_prompts"])

    def test_student_sandbox_v1_replaces_intent_when_private_detail_detected(self) -> None:
        packet = student_sandbox_v1.build_learning_loop_packet(
            research_question="I am John Smith at Lincoln High and my email is jsmith@example.com, help me research X",
            student_level="high_school",
        )
        self.assertEqual(packet["student_intent"], "[redacted-by-policy]")
        self.assertTrue(packet["privacy"]["private_detail_detected"])
        self.assertFalse(packet["privacy"]["contains_private_student_data"])
        blob = json.dumps(packet)
        self.assertNotIn("John Smith", blob)
        self.assertNotIn("Lincoln High", blob)
        self.assertNotIn("jsmith@example.com", blob)

    def test_student_sandbox_v1_research_study_protocol_is_privacy_first(self) -> None:
        protocol = student_sandbox_v1.build_research_study_protocol()

        self.assertEqual(protocol["version"], "research_study_v0")
        self.assertEqual(protocol["session_length_minutes"], 20)
        self.assertFalse(protocol["collects_student_identity"])
        self.assertFalse(protocol["collects_school_name"])
        self.assertIn("parent_or_teacher_review", protocol)
        self.assertIn("student_can_explain_ai_help", protocol["success_criteria"])
        self.assertIn("student_can_name_human_responsibility", protocol["success_criteria"])
        self.assertIn("confusion_notes", protocol["observer_packet"])

    def test_student_sandbox_v1_run_writes_stable_private_artifact_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "research-records"
            packet = student_sandbox_v1.run_student_sandbox_v1(
                research_question="My email is student@example.com. How should I research climate adaptation?",
                output_dir=output_dir,
            )
            artifact = output_dir / "student-sandbox-v1-latest.json"
            saved = json.loads(artifact.read_text())

        self.assertEqual(packet["artifact_path"], str(artifact))
        self.assertEqual(saved["artifact_path"], str(artifact))
        self.assertEqual(saved["version"], "student_sandbox_v1")
        self.assertIn("generated_at", saved)
        self.assertEqual(saved["privacy"]["private_detail_detected"], True)
        self.assertFalse(saved["privacy"]["contains_private_student_data"])
        self.assertEqual(saved["twenty_minute_loop"]["total_minutes"], 20)
        self.assertIn("source_checklist", saved)
        self.assertIn("reflection_card", saved)
        self.assertIn("research_study", saved)
        self.assertNotIn("student@example.com", json.dumps(saved))

    def test_student_sandbox_v1_web_renders_phases_checklist_and_reflection(self) -> None:
        """The WYSIWYG page must mirror the deterministic builder's content."""

        web_path = ROOT / "demo" / "student-sandbox-v1.html"
        self.assertTrue(web_path.exists(), "demo/student-sandbox-v1.html must exist as the human-facing surface")
        html = web_path.read_text()

        builder_packet = student_sandbox_v1.build_learning_loop_packet(
            research_question="How should I research CRISPR ethics for biology class?",
        )
        phase_ids = [phase["id"] for phase in builder_packet["twenty_minute_loop"]["phases"]]
        for phase_id in phase_ids:
            self.assertIn(phase_id, html, f"phase id {phase_id!r} missing from web page")

        for checklist_item in builder_packet["source_checklist"]:
            self.assertIn(checklist_item, html, f"checklist item {checklist_item!r} missing from web page")

        for prompt in builder_packet["reflection_card"]["student_prompts"]:
            self.assertIn(prompt, html, f"reflection prompt {prompt!r} missing from web page")

        self.assertIn("local worksheet", html.lower(), "web page must surface local worksheet privacy framing")
        self.assertIn("hints_not_answers", html, "web page must surface AI support policy explicitly")
        self.assertIn("Guided worksheet", html)
        self.assertIn("no prompt engineering required", html)
        self.assertIn("Student session worksheet", html)
        self.assertIn("Structured source cards", html)
        self.assertIn("data-source-card=\"source-1\"", html)
        self.assertIn("data-source-card=\"source-2\"", html)
        self.assertIn("structuredSourceCards", html)
        self.assertIn("observerContext", html)
        self.assertIn("Copy prompt to AI", html)
        self.assertIn("Build local summary", html)
        self.assertIn("Open review", html)
        self.assertIn("Parent / teacher observation checklist", html)
        self.assertIn("NOUS Guide", html)
        self.assertIn("NOUS Guide student learning chat", html)
        self.assertIn("LLM agent", html)
        self.assertIn("secure NOUS backend route", html)
        self.assertIn("hermesEndpoint", html)
        self.assertIn("/api/hermes-student-agent", html)
        self.assertIn("sessionEndpoint", html)
        self.assertIn("/api/student-sandbox-session", html)
        self.assertIn("saveSession", html)
        self.assertIn("Local backend save", html)
        self.assertIn("local backend", html.lower())
        self.assertIn("fetch(hermesEndpoint", html)
        self.assertIn("fetch(sessionEndpoint", html)
        self.assertIn("source_cards", html)
        self.assertIn("observer", html)
        self.assertIn("HERMES_API_SERVER_URL", html)
        self.assertIn("HERMES_API_SERVER_KEY", html)
        self.assertIn("data-prompt-template=\"plan\"", html)
        self.assertIn("data-prompt-template=\"critique\"", html)
        self.assertIn("data-prompt-template=\"revise\"", html)
        self.assertIn("navigator.clipboard.writeText", html)
        self.assertNotIn("localStorage", html)
        self.assertNotIn("sessionStorage", html)
        self.assertNotIn("OPENAI_API_KEY", html)
        self.assertNotIn("final_answer", html.lower(), "web page must not promise or display a final answer")

    def test_student_session_review_page_reads_local_backend_record(self) -> None:
        review_path = ROOT / "demo" / "student-session-review.html"
        self.assertTrue(review_path.exists(), "demo/student-session-review.html must exist")
        html = review_path.read_text()

        self.assertIn("Student Session Review", html)
        self.assertIn("Session review for parents, teachers, and research notes", html)
        self.assertIn("/api/student-sandbox-session", html)
        self.assertIn("?list=1&limit=1", html)
        self.assertIn("source_cards", html)
        self.assertIn("research_signals", html)
        self.assertIn("NOUS Guide turns", html)
        self.assertNotIn("localStorage", html)
        self.assertNotIn("sessionStorage", html)

    def test_student_sandbox_v1_guide_explains_why_and_how(self) -> None:
        """The student/parent guide must keep its core invariants visible."""

        guide_path = ROOT / "demo" / "student-sandbox-v1-guide.html"
        self.assertTrue(guide_path.exists(), "demo/student-sandbox-v1-guide.html must exist as the why-and-how surface")
        html = guide_path.read_text()
        lower = html.lower()

        for must_contain in (
            "why we made this",
            "how to run a session",
            "hints, not answers",
            "no login",
            "20 minutes",
            "structured worksheet",
            "copy-to-ai prompt cards",
            "boundary",
            "reflection",
        ):
            self.assertIn(must_contain.lower(), lower, f"guide must contain {must_contain!r}")

        self.assertIn('href="student-sandbox-v1.html"', html, "guide must link back to the sandbox page")
        self.assertIn("redacted-by-policy", html, "guide must explain the privacy-redaction contract")
        self.assertNotIn("final answer is produced", html.lower())
        for forbidden in ("login required", "create account", "sign in", "upload your"):
            self.assertNotIn(forbidden, lower, f"guide must not promise {forbidden!r}")

    def test_student_sandbox_v1_recruitment_keeps_promises_honest(self) -> None:
        """Recruitment templates must not promise features the page does not deliver.

        The 'forbidden' scan is restricted to the blockquoted message bodies — the part
        operators actually copy and send — so the meta 'what not to promise' section
        can name red-flag phrases without tripping the test on itself.
        """

        recruitment_path = ROOT / "docs" / "student-sandbox-v1-recruitment.md"
        self.assertTrue(recruitment_path.exists(), "recruitment template must exist")
        body = recruitment_path.read_text()
        full_lower = body.lower()

        for must_contain in (
            "20 分钟",
            "20-minute",
            "for a parent",
            "for a teacher",
            "what not to promise",
            "<url>",
        ):
            self.assertIn(must_contain.lower(), full_lower, f"recruitment must contain {must_contain!r}")

        # Only the lines that operators actually paste are the contract surface.
        message_lines = [line[2:] for line in body.splitlines() if line.startswith("> ")]
        self.assertTrue(message_lines, "recruitment must include at least one blockquoted message body")
        message_text = "\n".join(message_lines).lower()

        for forbidden in (
            "personalized ai tutor",
            "ai writes",
            "saves your progress",
            "free trial",
            "sign up",
            "create an account",
            "we'll grade",
            "score your",
            "leaderboard",
        ):
            self.assertNotIn(forbidden, message_text, f"recruitment message must not promise {forbidden!r}")


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
        self.assertIn("student_sandbox_v1", surface_ids)
        self.assertIn("student_sandbox_v1_web", surface_ids)
        self.assertIn("trading_evaluator", surface_ids)
        self.assertIn("domain_evaluator_interface", surface_ids)
        self.assertIn("domain_evaluator_runtime", surface_ids)
        self.assertIn("first_vertical_wiring_plan", surface_ids)
        self.assertIn("harness_handoffs", surface_ids)
        self.assertIn("latest_research_record", surface_ids)
        self.assertIn("cross_repo_release_gate", surface_ids)
        self.assertIn("documentation_reproducibility_test", surface_ids)
        self.assertIn("github_pages_workflow", surface_ids)
        self.assertIn("live trading state", inventory["default_boundary"])

    def test_v2_roadmap_and_evaluator_docs_are_linked(self) -> None:
        readme = (ROOT / "README.md").read_text()
        phase3 = (ROOT / "NOUS-OS-PHASE3.md").read_text()
        roadmap = ROOT / "docs" / "north-star-v2-roadmap.md"
        evaluator = ROOT / "docs" / "domain-evaluator-interface.md"
        release_gate = ROOT / "docs" / "cross-repo-release-gate.md"
        review_template = ROOT / "docs" / "review-template.md"
        student_v1_review_template = ROOT / "docs" / "student-sandbox-v1-review-template.md"
        theory_track_plan = ROOT / "docs" / "plans" / "2026-05-16-human-ai-coevolution-theory-track-plan.md"
        theory_track_dev_plan = ROOT / "docs" / "plans" / "2026-05-16-human-ai-coevolution-theory-track-development-plan.md"
        symbiosis_theory = ROOT / "docs" / "human-ai-symbiosis-self-evolution.md"
        coevolution_model = ROOT / "docs" / "human-ai-coevolution-model-v0.md"
        self_evolution_metrics = ROOT / "docs" / "self-evolution-metrics-v0.md"
        memory_philosophy = ROOT / "docs" / "memory-philosophy-v0.md"
        demo_refresh_plan = ROOT / "docs" / "plans" / "2026-05-16-human-ai-coevolution-demo-refresh-plan.md"
        education_research = ROOT / "docs" / "education-research-narrative.md"
        harness_readme = ROOT / "docs" / "harness" / "README.md"
        harness_context = ROOT / "docs" / "harness" / "context-index.md"
        second_vertical = ROOT / "docs" / "second-vertical-entry-criteria.md"
        one_pager = ROOT / "docs" / "NOUS-OS-Cognitive-COO-One-Pager.md"
        one_pager_en = ROOT / "docs" / "NOUS-OS-Cognitive-COO-One-Pager.en.md"
        student_trial_guide = ROOT / "docs" / "student-sandbox-v1-trial-guide.md"
        student_workflow = ROOT / "docs" / "student-sandbox-deterministic-workflow.md"

        self.assertTrue(roadmap.exists())
        self.assertTrue(evaluator.exists())
        self.assertTrue(release_gate.exists())
        self.assertTrue(review_template.exists())
        self.assertTrue(student_v1_review_template.exists())
        self.assertTrue(theory_track_plan.exists())
        self.assertTrue(theory_track_dev_plan.exists())
        self.assertTrue(symbiosis_theory.exists())
        self.assertTrue(coevolution_model.exists())
        self.assertTrue(self_evolution_metrics.exists())
        self.assertTrue(memory_philosophy.exists())
        self.assertTrue(demo_refresh_plan.exists())
        self.assertTrue(education_research.exists())
        self.assertTrue(harness_readme.exists())
        self.assertTrue(harness_context.exists())
        self.assertTrue(second_vertical.exists())
        self.assertTrue(one_pager.exists())
        self.assertTrue(one_pager_en.exists())
        self.assertTrue(student_trial_guide.exists())
        self.assertTrue(student_workflow.exists())
        self.assertIn("education and research project", readme)
        self.assertIn("docs/north-star-v2-roadmap.md", readme)
        self.assertIn("docs/education-research-narrative.md", readme)
        self.assertIn("docs/human-ai-symbiosis-self-evolution.md", readme)
        self.assertIn("docs/human-ai-coevolution-model-v0.md", readme)
        self.assertIn("docs/self-evolution-metrics-v0.md", readme)
        self.assertIn("docs/memory-philosophy-v0.md", readme)
        self.assertIn("docs/domain-evaluator-interface.md", readme)
        self.assertIn("docs/harness/README.md", readme)
        self.assertIn("docs/cross-repo-release-gate.md", readme)
        self.assertIn("docs/student-sandbox-deterministic-workflow.md", readme)
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
        self.assertIn("Theory Track Evidence", review_template.read_text())
        self.assertIn("What changed in the human?", review_template.read_text())
        self.assertIn("What should be remembered before the next cycle?", review_template.read_text())
        self.assertIn("Next Run Change", review_template.read_text())
        self.assertIn("context index + boundary map + artifact contracts + evaluator specs + release gates + evidence write-back", harness_readme.read_text())
        self.assertIn("NOUS OS Harness Context Index", harness_context.read_text())
        self.assertIn("Second vertical work remains deferred", second_vertical.read_text())
        self.assertIn("Cognitive COO Operating System", one_pager_en.read_text())
        self.assertIn("TrustMem: agents' trustworthy hippocampus", one_pager_en.read_text())
        self.assertIn("Obsidian knowledge sedimentation", one_pager_en.read_text())
        student_trial_text = student_trial_guide.read_text()
        self.assertIn("20-minute", student_trial_text)
        self.assertIn("hints, not final answers", student_trial_text)
        self.assertIn("Privacy", student_trial_text)
        self.assertIn("What remains my responsibility?", student_trial_text)
        self.assertIn("/api/student-sandbox-session", student_trial_text)
        self.assertIn("student-session-review.html", student_trial_text)
        student_workflow_text = student_workflow.read_text()
        self.assertIn("deterministic software first", student_workflow_text)
        self.assertIn("Workflow State Machine", student_workflow_text)
        self.assertIn("Skills Layer", student_workflow_text)
        self.assertIn("NOUS Guide", student_workflow_text)
        self.assertIn("research_signals", student_workflow_text)
        self.assertIn("source_cards", student_workflow_text)
        self.assertIn("must not mutate the protocol itself", student_workflow_text)
        student_review_text = student_v1_review_template.read_text()
        self.assertIn("Student Sandbox v1 Trial Review", student_review_text)
        self.assertIn("What did the student understand?", student_review_text)
        self.assertIn("What confused the student?", student_review_text)
        self.assertIn("Theory track evidence", student_review_text)
        self.assertIn("Human capability delta", student_review_text)
        self.assertIn("Trust calibration", student_review_text)
        self.assertIn("What should be remembered, challenged, decayed, or forgotten?", student_review_text)
        self.assertIn("Next-run change", student_review_text)
        coevolution_model_text = coevolution_model.read_text()
        self.assertIn("Status / How to use", coevolution_model_text)
        self.assertIn("Human-AI Symbiosis and Self-Evolution Theory", coevolution_model_text)
        self.assertIn("Self-Evolution Metrics v0", coevolution_model_text)
        self.assertIn("Memory Philosophy v0", coevolution_model_text)
        self.assertIn("Student Sandbox and trading-agent are proof beds, not the goal", coevolution_model_text)
        metrics_text = self_evolution_metrics.read_text()
        self.assertIn("Status / How to use", metrics_text)
        self.assertIn("qualitative observation or a measurable proxy", metrics_text)
        self.assertIn("Human-AI Co-Evolution Model v0", metrics_text)
        memory_text = memory_philosophy.read_text()
        self.assertIn("Status / How to use", memory_text)
        self.assertIn("verified memory substrate, not a stale personalization engine", memory_text)
        self.assertIn("challenge, decay, and forgetting", memory_text)
        theory_plan_text = theory_track_dev_plan.read_text()
        self.assertIn("Phase 0", theory_plan_text)
        self.assertIn("Phase 5", theory_plan_text)
        self.assertIn("Definition of Done", theory_plan_text)

    def test_landing_page_uses_plain_human_ai_framing_without_overclaiming(self) -> None:
        html = (ROOT / "index.html").read_text()

        self.assertIn("Human-AI Learning System", html)
        self.assertIn("learning system", html)
        self.assertIn("learning notes", html)
        self.assertIn("demo/assets/architecture/nous-os-cognitive-coo-architecture-fireworks.png", html)
        self.assertIn("Trading Brain as the first vertical proof", html)
        self.assertIn("Production hardening is still in progress", html)
        self.assertEqual(html.count('href="/about.html"'), 1)
        self.assertNotIn('<li><a href="#demo">Demo</a></li>', html)
        self.assertIn('<li><a href="/about.html">About</a></li>', html)
        self.assertLess(
            html.index('<li><a href="https://github.com/jupiturliu/nous-os">GitHub</a></li>'),
            html.index('<li><a href="/about.html">About</a></li>'),
        )
        self.assertIn('class="btn-ghost btn-demo-nav">Demo</a>', html)
        self.assertIn("Follow the research build", html)
        self.assertIn("early reviewers", html)
        self.assertNotIn("<em>Cognitive COO OS</em>", html)
        self.assertNotIn("COO Operating System", html)
        self.assertNotIn("44/44 tests", html)
        self.assertNotIn("first 200 teams", html)
        self.assertNotIn("NOUS OS as a Service", html)
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
        self.assertIn("cp demo/student-sandbox-v1.html _site/demo/", workflow)
        self.assertIn("cp demo/student-sandbox-v1-guide.html _site/demo/", workflow)
        self.assertIn("cp demo/student-session-review.html _site/demo/", workflow)
        self.assertIn("cp examples/runtime/dashboard-data.json _site/examples/runtime/", workflow)
        self.assertIn("cp examples/runtime/research-records/latest.json _site/examples/runtime/research-records/", workflow)

    def test_site_pages_reference_favicon(self) -> None:
        homepage = (ROOT / "index.html").read_text()
        demo_page = (ROOT / "demo" / "heartbeat-dashboard.html").read_text()
        student_sandbox_page = (ROOT / "demo" / "student-sandbox-v1.html").read_text()
        about_page = (ROOT / "about.html").read_text()

        self.assertIn('<link rel="icon" href="favicon.svg" type="image/svg+xml">', homepage)
        self.assertIn('<link rel="icon" href="../favicon.svg" type="image/svg+xml">', demo_page)
        self.assertIn('<link rel="icon" href="../favicon.svg" type="image/svg+xml">', student_sandbox_page)
        self.assertIn('<link rel="icon" href="favicon.svg" type="image/svg+xml">', about_page)

    def test_homepage_publishes_research_track_links(self) -> None:
        homepage = (ROOT / "index.html").read_text()
        readme = (ROOT / "README.md").read_text()
        production_runtime = (ROOT / "docs" / "production-runtime.md").read_text()

        self.assertIn('id="research"', homepage)
        self.assertEqual(homepage.count('id="research"'), 1)
        self.assertIn('<a href="/research.html">Research</a>', homepage)
        self.assertIn('id="proof"', homepage)
        self.assertIn("Human-AI co-evolution", homepage)
        self.assertIn("/research.html#anchor", homepage)
        self.assertIn("/research.html#model", homepage)
        self.assertIn("/research.html#metrics", homepage)
        self.assertIn("/demo/student-sandbox-v1.html", homepage)
        self.assertIn("docs/production-runtime.md", readme)
        self.assertIn("NOUS_OS_RUNTIME_BACKEND=redis", production_runtime)
        self.assertIn("NOUS_OS_RUNTIME_BACKEND=sqlite", production_runtime)

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
