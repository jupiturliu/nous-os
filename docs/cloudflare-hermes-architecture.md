# Cloudflare + Hermes Gateway Architecture

NOUS OS should run as one product surface with two equivalent paths:

```text
Production:
Browser -> Cloudflare Worker Static Assets -> /api/hermes-student-agent -> Hermes Gateway

Local development:
Browser -> local NOUS OS webserver -> /api/hermes-student-agent -> local Hermes Gateway
```

This adapts the deployment pattern already proven in `trading-agent`:

- Cloudflare is the public edge.
- The app does not expose model-provider keys to the browser.
- The web surface calls a first-party API boundary.
- The API boundary calls Hermes Gateway through the OpenAI-compatible `/v1/chat/completions` endpoint.
- Local development keeps the same request shape against `127.0.0.1`.

`trading-agent` uses Cloudflare Tunnel into a local Python webserver because it owns private trading state, broker adapters, session files, and user ledgers. `nous-os` can use Cloudflare Worker Static Assets because the public site is static plus a narrow Hermes API route. The boundary is the same; the hosting substrate is lighter.

This replaces the GitHub Pages-only limitation. GitHub Pages can publish HTML, but it cannot execute `/api/*`. Cloudflare Worker Static Assets can serve the website and run the Hermes API boundary in the same deployment.

## Trading-Agent Precedent

The source pattern already exists in `/Users/liyao/nousos/trading-agent`:

| Concern | Trading-agent evidence | NOUS OS adaptation |
|---|---|---|
| Cloudflare public edge | `docs/notes/deployment/DNS_SETUP_GUIDE.md`, `docs/notes/product/release_runbook.md` | `wrangler.toml`, `.github/workflows/cloudflare.yml` |
| Local origin / dev server | `web/server.py` on `127.0.0.1:8766` | `scripts/serve_nous_site.cjs` on `127.0.0.1:8787` |
| Hermes Gateway endpoint | `HERMES_API_SERVER_URL=http://127.0.0.1:8642/v1/chat/completions` | `HERMES_GATEWAY_URL=http://127.0.0.1:8642` |
| Service health model | `ai.hermes.gateway`, `com.trading.webserver`, `com.trading.cloudflared` | CI-gated Worker deploy plus local smoke checks |
| Browser safety boundary | web calls first-party API routes, not model providers | browser calls `/api/hermes-student-agent` only |

The naming differs slightly because `trading-agent` stores the full chat completions URL in `HERMES_API_SERVER_URL`, while `nous-os` stores the Gateway root in `HERMES_GATEWAY_URL` and appends `/v1/chat/completions` in the adapter. That keeps the Worker and local webserver contract identical.

## Runtime Boundary

| Layer | Responsibility |
|---|---|
| Cloudflare Worker | static site, `/api/*` routing, CORS, Gateway credential boundary |
| Local webserver | same static site and API contract for development |
| Hermes Gateway | agent/model/provider/tool boundary |
| Browser | UI only; no Gateway keys and no direct model-provider calls |

The browser calls:

```text
POST /api/hermes-student-agent
```

The Worker or local webserver calls:

```text
POST ${HERMES_GATEWAY_URL}/v1/chat/completions
```

## Files

- `wrangler.toml` — Cloudflare Worker Static Assets config
- `worker/index.mjs` — production Worker API route
- `scripts/stage_static_site.sh` — deterministic `_site/` staging step
- `scripts/serve_nous_site.cjs` — local webserver with the same API route
- `api/hermes-student-agent.js` — Node/CommonJS local/serverless Hermes adapter
- `.github/workflows/cloudflare.yml` — CI-gated Cloudflare deploy workflow

## Production Deploy

Required GitHub secrets:

```text
CLOUDFLARE_ACCOUNT_ID
CLOUDFLARE_API_TOKEN
```

Required Cloudflare Worker secret:

```text
HERMES_GATEWAY_URL
```

Optional Cloudflare Worker secrets/vars:

```text
HERMES_GATEWAY_API_KEY
HERMES_GATEWAY_MODEL=hermes-agent
HERMES_ALLOWED_ORIGIN=https://nousos.ai
```

Deploy locally:

```bash
npm install
npm run site:stage
npx wrangler deploy
```

Run the Worker locally:

```bash
npm install
HERMES_GATEWAY_URL=http://127.0.0.1:8642 npm run worker:dev
```

## Local Webserver

Use this when developing without Cloudflare:

```bash
HERMES_GATEWAY_URL=http://127.0.0.1:8642 npm run site:dev
```

Open:

```text
http://127.0.0.1:8787/demo/student-sandbox-v1.html
```

The local server stages `_site/`, serves static assets, and handles:

```text
POST /api/hermes-student-agent
```

## Cutover

1. Keep GitHub Pages running until the Cloudflare Worker is verified.
2. Configure `nousos.ai` DNS to the Cloudflare Worker route.
3. Set `HERMES_GATEWAY_URL` and `HERMES_GATEWAY_API_KEY` in Cloudflare.
4. Smoke check the site HTML and `/api/hermes-student-agent`.
5. Disable the GitHub Pages workflow after Cloudflare is the production path.

## Safety

Do not put model provider keys in the browser. Do not call OpenAI, Anthropic, or any provider directly from the NOUS OS website. The stable contract is website -> NOUS OS API route -> Hermes Gateway.
