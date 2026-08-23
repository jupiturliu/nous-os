from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RepositoryArchitectureTests(unittest.TestCase):
    def test_product_source_has_no_path_injection_or_legacy_runtime_writes(self) -> None:
        violations = []
        for path in (ROOT / "src" / "nous_os").rglob("*.py"):
            source = path.read_text(encoding="utf-8")
            for forbidden in ("sys.path.insert", '"examples/runtime', "'examples/runtime"):
                if forbidden in source:
                    violations.append(f"{path.relative_to(ROOT)} contains {forbidden}")
        self.assertEqual(violations, [])

    def test_replaced_shallow_entrypoints_are_deleted(self) -> None:
        replaced = (
            "api/hermes-student-agent.js",
            "api/student-sandbox-session.js",
            "backend/server.cjs",
            "scripts/run_nous_dashboard.py",
            "scripts/run_nous_heartbeat.py",
            "scripts/serve_nous_site.cjs",
            "scripts/stage_static_site.sh",
            "examples/nous_os_demo.py",
            "examples/nousos_demo.py",
            "examples/nousos_workspace_demo.py",
            "examples/nousos_heartbeat_demo.py",
            "src/nous_os/workflows/student_sandbox_v0.py",
        )
        self.assertEqual([path for path in replaced if (ROOT / path).exists()], [])

    def test_superseded_documents_are_deleted(self) -> None:
        superseded = (
            ".codex",
            "ARIA-ARCHITECTURE.md",
            "CO-EXIST-FLYWHEEL.md",
            "NOUS-OS-PHASE3.md",
            "NOUS-OS-SPEC.md",
            "docs/aria-integration.md",
            "docs/aria-heartbeat-integration.md",
            "docs/demo-blueprint.md",
            "docs/hermes-student-agent-gateway.md",
            "docs/production-runtime.md",
            "docs/workspace-demo.md",
            "docs/plans",
            "docs/harness/handoffs",
        )
        self.assertEqual([path for path in superseded if (ROOT / path).exists()], [])

    def test_root_metadata_matches_public_claims(self) -> None:
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertTrue(license_text.startswith("MIT License\n"))
        self.assertIn("Copyright (c) 2026 Liu Fei / jupiturliu", license_text)
        self.assertIn("](LICENSE)", readme)

    def test_public_route_interface_remains_stable(self) -> None:
        source = (ROOT / "src" / "nous_os" / "web" / "server.py").read_text(encoding="utf-8")
        for route in (
            "/api/health",
            "/api/hermes-student-agent",
            "/api/student-sandbox-session",
            "/api/dashboard-data",
            "/api/run-heartbeat",
        ):
            self.assertIn(route, source)


if __name__ == "__main__":
    unittest.main()
