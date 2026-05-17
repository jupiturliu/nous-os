# Hermes Student Agent Gateway

NOUS OS Student Sandbox uses a browser chat surface backed by a server-side Hermes Gateway adapter.

The browser calls:

```text
POST /api/hermes-student-agent
```

That route calls Hermes Gateway through its OpenAI-compatible API:

```text
POST ${HERMES_API_SERVER_URL}
```

This keeps model selection, provider routing, tools, policy, and credentials behind Hermes Gateway instead of binding the website to a direct model vendor.

## Website Route

Deploy `api/hermes-student-agent.js` inside the NOUS OS web backend server. The Cloudflare Worker should proxy `/api/*` to that backend instead of calling Hermes Gateway directly.

For the full Cloudflare/local-webserver architecture, see [cloudflare-hermes-architecture.md](./cloudflare-hermes-architecture.md).

Required server environment:

```text
HERMES_API_SERVER_URL=http://127.0.0.1:8642/v1/chat/completions
```

Optional server environment:

```text
HERMES_API_SERVER_KEY=...
HERMES_API_SERVER_MODEL=hermes-agent
HERMES_ALLOWED_ORIGIN=https://nousos.ai
```

This mirrors `trading-agent`'s HTTP Gateway mode. Compatibility aliases are also supported: `HERMES_GATEWAY_URL` and `HERMES_GATEWAY_API_KEY`.

## Hermes Gateway

In the `hermes-agent` gateway runtime, enable the OpenAI-compatible API server:

```text
API_SERVER_ENABLED=true
API_SERVER_KEY=...
API_SERVER_MODEL_NAME=hermes-agent
API_SERVER_CORS_ORIGINS=https://nousos.ai
API_SERVER_HOST=127.0.0.1
API_SERVER_PORT=8642
```

Use `API_SERVER_HOST=0.0.0.0` only when the Gateway is intentionally exposed behind TLS, auth, and network controls.

## Security Boundary

The browser never receives Gateway keys. The web page sends a question and compact worksheet context only after the student clicks `Ask`.

GitHub Pages cannot execute `/api/hermes-student-agent.js` by itself. Production needs one of:

- Vercel, Netlify, Cloudflare Workers, or another serverless host for `/api/hermes-student-agent`
- a reverse proxy in front of `nousos.ai` that routes `/api/hermes-student-agent` to the Node handler
- a first-party backend that implements the same request contract and forwards to Hermes Gateway

## Student Agent Policy

The agent is optimized for the Student Sandbox:

- hints and subquestions, not final answers
- one boundary suggestion per turn
- one source-check or verification move per turn
- no requests for private student data
- human remains responsible for goals, values, verification, final claim, and final wording
