# Hermes Student Agent Gateway

NOUS OS Student Sandbox uses a browser chat surface backed by a server-side Hermes Gateway adapter.

The browser calls:

```text
POST /api/hermes-student-agent
```

That route calls Hermes Gateway through its OpenAI-compatible API:

```text
POST ${HERMES_GATEWAY_URL}/v1/chat/completions
```

This keeps model selection, provider routing, tools, policy, and credentials behind Hermes Gateway instead of binding the website to a direct model vendor.

## Website Route

Deploy `api/hermes-student-agent.js` on a serverless or edge runtime that supports Node.js `fetch`.

Required server environment:

```text
HERMES_GATEWAY_URL=https://your-hermes-gateway.example.com
```

Optional server environment:

```text
HERMES_GATEWAY_API_KEY=...
HERMES_GATEWAY_MODEL=hermes-agent
HERMES_ALLOWED_ORIGIN=https://nousos.ai
```

`HERMES_GATEWAY_URL` should be the Gateway root URL. The adapter appends `/v1/chat/completions`.

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
