# NOUS OS Cloudflare Tunnel Runbook

This is the `trading-agent` style path for NOUS OS:

```text
Cloudflare frontend -> backend.nousos.ai tunnel -> 127.0.0.1:8787 -> local Hermes Gateway
```

## Local Services

Install or update the macOS services:

```bash
npm run deploy:macos
```

Verify:

```bash
launchctl list | grep com.nousos
curl http://127.0.0.1:8787/api/health
```

The installer writes:

```text
~/Library/LaunchAgents/com.nousos.webbackend.plist
~/Library/LaunchAgents/com.nousos.cloudflared.plist
~/.cloudflared/nous-os-backend.yml
```

## DNS Route

The tunnel has been created as `nous-os-backend`. The local credential file exists, but the current `cloudflared` login was originally set up for the trading zone. Log in with Cloudflare access to `nousos.ai` before routing DNS:

```bash
cloudflared tunnel login
cloudflared tunnel route dns --overwrite-dns nous-os-backend backend.nousos.ai
```

Expected route:

```text
backend.nousos.ai -> nous-os-backend tunnel -> http://127.0.0.1:8787
```

If the command creates a hostname under another zone, remove that DNS record in Cloudflare and retry after fixing zone access.

## Cloudflare Worker

The frontend Worker should use:

```text
NOUS_BACKEND_ORIGIN_URL=https://backend.nousos.ai
```

`wrangler.toml` routes the Worker to:

```text
nousos.ai/*
www.nousos.ai/*
```

For the route-based cutover, the existing Cloudflare DNS records must be Proxied:

```text
nousos.ai A records -> Proxied
www.nousos.ai CNAME -> Proxied
```

If they stay DNS-only, public traffic bypasses the Worker and continues to hit GitHub Pages.

The Worker never needs Hermes or model-provider keys. Hermes stays local behind the NOUS OS backend.
