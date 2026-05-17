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
        self.assertIn('NOUS_PUBLIC_ORIGIN = "https://nousos.ai"', wrangler)
        self.assertIn("workers_dev = true", wrangler)
        self.assertIn("preview_urls = false", wrangler)
        self.assertIn('pattern = "nousos.ai/*"', wrangler)
        self.assertIn('pattern = "www.nousos.ai/*"', wrangler)
        self.assertIn('zone_name = "nousos.ai"', wrangler)

    def test_worker_proxies_api_to_web_backend_not_hermes_gateway_or_provider(self) -> None:
        worker = (ROOT / "worker" / "index.mjs").read_text()

        self.assertIn("NOUS_BACKEND_ORIGIN_URL", worker)
        self.assertIn("NOUS_WEB_BACKEND_URL", worker)
        self.assertIn("url.pathname.startsWith('/api/')", worker)
        self.assertIn("proxyApiToBackend", worker)
        self.assertIn("env.ASSETS.fetch(request)", worker)
        self.assertNotIn("HERMES_GATEWAY_URL", worker)
        self.assertNotIn("HERMES_GATEWAY_API_KEY", worker)
        self.assertNotIn("/v1/chat/completions", worker)
        self.assertNotIn("OPENAI_API_KEY", worker)
        self.assertNotIn("api.openai.com", worker)

    def test_web_backend_uses_same_api_contract_and_gateway_boundary(self) -> None:
        server = (ROOT / "backend" / "server.cjs").read_text()

        self.assertIn("stage_static_site.sh", server)
        self.assertIn("/api/hermes-student-agent", server)
        self.assertIn("/api/student-sandbox-session", server)
        self.assertIn("/api/health", server)
        self.assertIn("HERMES_API_SERVER_URL", server)
        self.assertIn("API_SERVER_KEY", server)
        self.assertIn(".hermes", server)
        self.assertIn("HERMES_GATEWAY_URL", server)
        self.assertIn("http://127.0.0.1:8642", server)
        self.assertIn("/v1/chat/completions", server)
        self.assertIn("require('../api/hermes-student-agent')", server)
        self.assertIn("require('../api/student-sandbox-session')", server)

        wrapper = (ROOT / "scripts" / "serve_nous_site.cjs").read_text()
        self.assertIn("require('../backend/server.cjs').start()", wrapper)

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
        # NOUS_BACKEND_ORIGIN_URL moved from a Worker secret (set via the
        # workflow) to a Worker var in wrangler.toml. The hostname
        # backend.nousos.ai is public, not sensitive.
        wrangler_toml = (ROOT / "wrangler.toml").read_text()
        self.assertIn("NOUS_BACKEND_ORIGIN_URL", wrangler_toml)
        self.assertIn("https://backend.nousos.ai", wrangler_toml)

    def test_cloudflare_architecture_doc_explains_cutover_and_boundaries(self) -> None:
        doc = (ROOT / "docs" / "cloudflare-hermes-architecture.md").read_text()

        self.assertIn("Browser -> Cloudflare Worker Static Assets", doc)
        self.assertIn("NOUS OS web backend -> Hermes Gateway", doc)
        self.assertIn("Browser -> local NOUS OS webserver", doc)
        self.assertIn("Trading-Agent Precedent", doc)
        self.assertIn("/Users/liyao/nousos/trading-agent", doc)
        self.assertIn("docs/notes/deployment/DNS_SETUP_GUIDE.md", doc)
        self.assertIn("web/server.py", doc)
        self.assertIn("HERMES_API_SERVER_URL=http://127.0.0.1:8642/v1/chat/completions", doc)
        self.assertIn("ai.hermes.gateway", doc)
        self.assertIn("com.trading.cloudflared", doc)
        self.assertIn("com.nousos.webbackend", doc)
        self.assertIn("com.nousos.cloudflared", doc)
        self.assertIn("backend.nousos.ai", doc)
        self.assertIn("NOUS_BACKEND_ORIGIN_URL", doc)
        self.assertIn("Hermes Gateway", doc)
        self.assertIn("GitHub Pages-only limitation", doc)
        self.assertIn("nousos.ai/*", doc)
        self.assertIn("www.nousos.ai/*", doc)
        self.assertIn("DNS-only to Proxied", doc)
        self.assertIn("Disable the GitHub Pages workflow", doc)
        self.assertIn("website -> Cloudflare frontend -> NOUS OS web backend -> Hermes Gateway", doc)

    def test_macos_launchagents_follow_trading_agent_local_tunnel_pattern(self) -> None:
        package_json = (ROOT / "package.json").read_text()
        install = (ROOT / "deploy" / "macos" / "install.sh").read_text()
        backend_plist = (
            ROOT / "deploy" / "macos" / "launchagents" / "com.nousos.webbackend.plist"
        ).read_text()
        cloudflared_plist = (
            ROOT / "deploy" / "macos" / "launchagents" / "com.nousos.cloudflared.plist"
        ).read_text()
        tunnel_template = (
            ROOT / "deploy" / "cloudflare" / "nous-os-backend.yml.template"
        ).read_text()
        runbook = (ROOT / "docs" / "cloudflare-tunnel-runbook.md").read_text()

        self.assertIn('"deploy:macos": "bash deploy/macos/install.sh"', package_json)
        self.assertIn("DEFAULT_SERVICES=(webbackend cloudflared)", install)
        self.assertIn('full="com.nousos.$short"', install)
        self.assertIn('$HOME/.cloudflared/nous-os-backend.yml', install)
        self.assertIn("<string>com.nousos.webbackend</string>", backend_plist)
        self.assertIn("<string>/opt/homebrew/bin/node</string>", backend_plist)
        self.assertIn("<string>backend/server.cjs</string>", backend_plist)
        self.assertIn("<string>8787</string>", backend_plist)
        self.assertIn("<string>com.nousos.cloudflared</string>", cloudflared_plist)
        self.assertIn("<string>/opt/homebrew/bin/cloudflared</string>", cloudflared_plist)
        self.assertIn("<string>{{HOME}}/.cloudflared/nous-os-backend.yml</string>", cloudflared_plist)
        self.assertIn("tunnel: d149d690-3a16-40dc-8607-77a4cc00fe95", tunnel_template)
        self.assertIn("hostname: backend.nousos.ai", tunnel_template)
        self.assertIn("service: http://127.0.0.1:8787", tunnel_template)
        self.assertIn("cloudflared tunnel login", runbook)
        self.assertIn("NOUS_BACKEND_ORIGIN_URL=https://backend.nousos.ai", runbook)
        self.assertIn("nousos.ai/*", runbook)
        self.assertIn("www.nousos.ai/*", runbook)
        self.assertIn("DNS-only", runbook)
        self.assertIn("Proxied", runbook)

    def test_javascript_entrypoints_have_valid_syntax(self) -> None:
        for path in (
            ROOT / "worker" / "index.mjs",
            ROOT / "backend" / "server.cjs",
            ROOT / "scripts" / "serve_nous_site.cjs",
            ROOT / "api" / "hermes-student-agent.js",
            ROOT / "api" / "student-sandbox-session.js",
        ):
            result = subprocess.run(
                ["node", "--check", str(path)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, f"{path}: {result.stderr}")
