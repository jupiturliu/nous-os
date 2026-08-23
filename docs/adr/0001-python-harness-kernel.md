# ADR 0001: Python single-distribution Harness kernel

## Status

Accepted

## Decision

NOUS OS ships as one Python 3.11 distribution named `nous-os`. The Harness kernel, capabilities, workflows, adapters, CLI, and local Web composition live under `src/nous_os`. YAML Profiles compose Plugins through a lifecycle-managed capability registry.

Node remains only for the Cloudflare/Wrangler toolchain. Hermes remains an external model/tool provider behind an Adapter.

## Consequences

Internal imports and script paths make a one-time breaking transition. Website URLs, HTTP routes, and primary Student Sandbox, Research Line, Heartbeat, and Trading Proof scenarios remain stable.
