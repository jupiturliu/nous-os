# Cloudflare + Hermes Gateway Architecture

NOUS OS should run as one product surface with two equivalent paths:

```text
Production:
Browser -> Cloudflare Worker Static Assets -> NOUS OS web backend -> Hermes Gateway

Local development:
Browser -> local NOUS OS webserver -> /api/hermes-student-agent -> local Hermes Gateway
```

This adapts the deployment pattern already proven in `trading-agent`:

- Cloudflare is the public edge.
- The app does not expose model-provider keys to the browser.
- The web surface calls a first-party API boundary.
- The Cloudflare frontend only talks to the NOUS OS web backend server.
- The web backend server calls Hermes Gateway through the OpenAI-compatible `/v1/chat/completions` endpoint.
- Local development keeps the same request shape against `127.0.0.1`.

`trading-agent` uses Cloudflare Tunnel into a local Python webserver because it owns private trading state, broker adapters, session files, and user ledgers. `nous-os` follows the same separation: Cloudflare owns frontend delivery, and a NOUS OS web backend server owns `/api/*` and Hermes Gateway access. The hosting substrate is lighter, but the boundary is the same.

This replaces the GitHub Pages-only limitation. GitHub Pages can publish HTML, but it cannot execute `/api/*` or proxy to a private backend. Cloudflare Worker Static Assets can serve the website and route `/api/*` to the NOUS OS backend.

## Trading-Agent Precedent

The source pattern already exists in `/Users/liyao/nousos/trading-agent`:

| Concern | Trading-agent evidence | NOUS OS adaptation |
|---|---|---|
| Cloudflare public edge | `docs/notes/deployment/DNS_SETUP_GUIDE.md`, `docs/notes/product/release_runbook.md` | `wrangler.toml`, `.github/workflows/cloudflare.yml` |
| Local origin / dev server | `web/server.py` on `127.0.0.1:8766` | `backend/server.cjs` on `127.0.0.1:8787` |
| Hermes Gateway endpoint | `HERMES_API_SERVER_URL=http://127.0.0.1:8642/v1/chat/completions` | backend uses `HERMES_API_SERVER_URL=http://127.0.0.1:8642/v1/chat/completions` |
| Service health model | `ai.hermes.gateway`, `com.trading.webserver`, `com.trading.cloudflared` | `com.nousos.webbackend`, `com.nousos.cloudflared`, CI-gated Worker deploy |
| Browser safety boundary | web calls first-party API routes, not model providers | browser calls `/api/hermes-student-agent` only |

The backend uses the same primary environment names as `trading-agent`: `HERMES_API_SERVER_URL` and `HERMES_API_SERVER_KEY`. `HERMES_GATEWAY_URL` and `HERMES_GATEWAY_API_KEY` remain supported as compatibility aliases.

## Runtime Boundary

| Layer | Responsibility |
|---|---|
| Cloudflare Worker | static site and `/api/*` proxy to the NOUS OS backend |
| NOUS OS web backend | API contract, CORS, Gateway credential boundary |
| Local webserver | same backend and API contract for development |
| Hermes Gateway | agent/model/provider/tool boundary |
| Browser | UI only; no Gateway keys and no direct model-provider calls |

The browser calls:

```text
POST /api/hermes-student-agent
```

The Cloudflare Worker calls:

```text
${NOUS_BACKEND_ORIGIN_URL}/api/hermes-student-agent
```

The NOUS OS web backend calls:

```text
POST ${HERMES_GATEWAY_URL}/v1/chat/completions
```

## Files

- `wrangler.toml` — Cloudflare Worker Static Assets config
- `worker/index.mjs` — production static frontend and `/api/*` backend proxy
- `scripts/stage_static_site.sh` — deterministic `_site/` staging step
- `backend/server.cjs` — NOUS OS web backend server
- `scripts/serve_nous_site.cjs` — compatibility wrapper for the backend server
- `api/hermes-student-agent.js` — Node/CommonJS Hermes Gateway adapter used by the backend
- `.github/workflows/cloudflare.yml` — CI-gated Cloudflare deploy workflow
- `deploy/macos/install.sh` — macOS LaunchAgent installer for the local backend and Cloudflare Tunnel
- `deploy/macos/launchagents/com.nousos.webbackend.plist` — keeps the NOUS OS backend running on `127.0.0.1:8787`
- `deploy/macos/launchagents/com.nousos.cloudflared.plist` — keeps the backend tunnel running
- `deploy/cloudflare/nous-os-backend.yml.template` — Cloudflare Tunnel ingress template for `backend.nousos.ai`

## Production Deploy

Required GitHub secrets:

```text
CLOUDFLARE_ACCOUNT_ID
CLOUDFLARE_API_TOKEN
NOUS_BACKEND_ORIGIN_URL
```

The deploy workflow writes `NOUS_BACKEND_ORIGIN_URL` into the Cloudflare Worker as a secret before `wrangler deploy`.

The Worker is routed to:

```text
nousos.ai/*
www.nousos.ai/*
```

These routes only receive traffic when the matching DNS records are proxied through Cloudflare. During cutover, keep the existing GitHub Pages A/CNAME records if needed, but switch them from DNS-only to Proxied so Cloudflare can run the Worker before any origin fallback.

Required Cloudflare Worker secret after deploy:

```text
NOUS_BACKEND_ORIGIN_URL=https://backend.nousos.ai
```

Required backend environment:

```text
HERMES_API_SERVER_URL=http://127.0.0.1:8642/v1/chat/completions
```

Optional backend environment:

```text
HERMES_API_SERVER_KEY
HERMES_API_SERVER_MODEL=hermes-agent
HERMES_ALLOWED_ORIGIN=https://nousos.ai
```

Deploy locally:

```bash
npm install
npm run site:stage
npx wrangler deploy
```

Run the local production backend and tunnel like `trading-agent`:

```bash
npm run deploy:macos
```

This installs:

```text
com.nousos.webbackend
com.nousos.cloudflared
```

The current tunnel template points `backend.nousos.ai` to:

```text
http://127.0.0.1:8787
```

The local `cloudflared` credential currently available on this machine is authenticated for the trading Cloudflare zone. Before the public DNS route can be completed, run `cloudflared tunnel login` with access to the `nousos.ai` zone, then route:

```bash
cloudflared tunnel route dns --overwrite-dns nous-os-backend backend.nousos.ai
```

If Cloudflare still appends another zone to the hostname, stop and fix the account or zone authorization in the Cloudflare dashboard before retrying.

Run the Worker locally:

```bash
npm install
NOUS_BACKEND_ORIGIN_URL=http://127.0.0.1:8787 npm run worker:dev
```

## Local Webserver

Use this when developing without Cloudflare:

```bash
HERMES_API_SERVER_URL=http://127.0.0.1:8642/v1/chat/completions npm run site:dev
```

Open:

```text
http://127.0.0.1:8787/demo/student-sandbox-v1.html
```

The local backend stages `_site/`, serves static assets for local convenience, and handles:

```text
POST /api/hermes-student-agent
GET /api/health
```

## Cutover

1. Keep GitHub Pages running until the Cloudflare Worker is verified.
2. Deploy the NOUS OS web backend server with `npm run deploy:macos`.
3. Expose `backend.nousos.ai` through Cloudflare Tunnel, using a `cloudflared` login that has access to the `nousos.ai` zone.
4. Configure `NOUS_BACKEND_ORIGIN_URL=https://backend.nousos.ai` on the Cloudflare Worker.
5. Set `HERMES_API_SERVER_URL` and, only if Hermes Gateway requires it, `HERMES_API_SERVER_KEY` on the backend server.
6. In Cloudflare DNS, switch the existing `nousos.ai` A records and `www.nousos.ai` CNAME from DNS-only to Proxied, or remove them and let Wrangler create Worker custom-domain records.
7. Smoke check the site HTML, `/api/health`, and `/api/hermes-student-agent`.
8. Disable the GitHub Pages workflow after Cloudflare is the production path.

## Safety

Do not put model provider keys in the browser or Cloudflare frontend layer. Do not call OpenAI, Anthropic, or any provider directly from the NOUS OS website. The stable contract is website -> Cloudflare frontend -> NOUS OS web backend -> Hermes Gateway.
