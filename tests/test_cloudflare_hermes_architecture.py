from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CloudflareHermesArchitectureTests(unittest.TestCase):
    def test_cloudflare_worker_config_runs_api_before_static_assets(self) -> None:
        wrangler = (ROOT / "wrangler.toml").read_text()

        self.assertIn('main = "worker/index.mjs"', wrangler)
        self.assertIn('directory = "./_site"', wrangler)
        self.assertIn('binding = "ASSETS"', wrangler)
        self.assertIn('run_worker_first = ["/api/*"]', wrangler)
        self.assertIn('HERMES_GATEWAY_MODEL = "hermes-agent"', wrangler)
        self.assertIn('HERMES_ALLOWED_ORIGIN = "https://nousos.ai"', wrangler)

    def test_worker_proxies_student_agent_to_hermes_gateway_not_provider(self) -> None:
        worker = (ROOT / "worker" / "index.mjs").read_text()

        self.assertIn("/api/hermes-student-agent", worker)
        self.assertIn("HERMES_GATEWAY_URL", worker)
        self.assertIn("HERMES_GATEWAY_API_KEY", worker)
        self.assertIn("/v1/chat/completions", worker)
        self.assertIn("cloudflare-worker-to-hermes-gateway", worker)
        self.assertIn("env.ASSETS.fetch(request)", worker)
        self.assertNotIn("OPENAI_API_KEY", worker)
        self.assertNotIn("api.openai.com", worker)

    def test_local_webserver_uses_same_api_contract_and_gateway_boundary(self) -> None:
        server = (ROOT / "scripts" / "serve_nous_site.cjs").read_text()

        self.assertIn("stage_static_site.sh", server)
        self.assertIn("/api/hermes-student-agent", server)
        self.assertIn("HERMES_GATEWAY_URL", server)
        self.assertIn("http://127.0.0.1:8642", server)
        self.assertIn("require('../api/hermes-student-agent')", server)

    def test_cloudflare_deploy_workflow_is_ci_gated(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "cloudflare.yml").read_text()

        self.assertIn("workflow_run", workflow)
        self.assertIn("workflows:", workflow)
        self.assertIn("- CI", workflow)
        self.assertIn("npm run site:stage", workflow)
        self.assertIn("npx wrangler deploy", workflow)
        self.assertIn("CLOUDFLARE_ACCOUNT_ID", workflow)
        self.assertIn("CLOUDFLARE_API_TOKEN", workflow)
        self.assertIn("configured=false", workflow)
        self.assertIn("Cloudflare deployment skipped", workflow)

    def test_cloudflare_architecture_doc_explains_cutover_and_boundaries(self) -> None:
        doc = (ROOT / "docs" / "cloudflare-hermes-architecture.md").read_text()

        self.assertIn("Browser -> Cloudflare Worker Static Assets", doc)
        self.assertIn("Browser -> local NOUS OS webserver", doc)
        self.assertIn("Trading-Agent Precedent", doc)
        self.assertIn("/Users/liyao/nousos/trading-agent", doc)
        self.assertIn("docs/notes/deployment/DNS_SETUP_GUIDE.md", doc)
        self.assertIn("web/server.py", doc)
        self.assertIn("HERMES_API_SERVER_URL=http://127.0.0.1:8642/v1/chat/completions", doc)
        self.assertIn("ai.hermes.gateway", doc)
        self.assertIn("com.trading.cloudflared", doc)
        self.assertIn("Hermes Gateway", doc)
        self.assertIn("GitHub Pages-only limitation", doc)
        self.assertIn("Disable the GitHub Pages workflow", doc)
        self.assertIn("website -> NOUS OS API route -> Hermes Gateway", doc)

    def test_javascript_entrypoints_have_valid_syntax(self) -> None:
        for path in (
            ROOT / "worker" / "index.mjs",
            ROOT / "scripts" / "serve_nous_site.cjs",
            ROOT / "api" / "hermes-student-agent.js",
        ):
            result = subprocess.run(
                ["node", "--check", str(path)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, f"{path}: {result.stderr}")
