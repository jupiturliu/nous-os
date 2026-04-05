# NOUS OS

> **The Cognitive Operating System for Human-AI Co-evolution**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Website](https://img.shields.io/badge/website-nousos.ai-blue)](https://nousos.ai)

---

## What is NOUS OS

NOUS OS is not an app. It's **infrastructure** — a three-layer cognitive system that makes AI agents remember, coordinate, and evolve together with their human partners.

```
┌─────────────────────────────────────┐
│  Aria  —  Consciousness Layer       │  Human alignment, intent, judgment
│  (reference impl: github/aria)      │
├─────────────────────────────────────┤
│  Synapse  —  Signal Layer           │  Event Bus, DAG, Budget routing
│  (github/synapse)                   │
├─────────────────────────────────────┤
│  TrustMem  —  Memory Layer          │  Knowledge trust, decay, verification
│  (github/trustmem)                  │
└─────────────────────────────────────┘
```

---

## Components

| Layer | Repo | Role | Status |
|-------|------|------|--------|
| 🏛️ **Aria** | [jupiturliu/aria](https://github.com/jupiturliu/aria) *(private)* | Consciousness — intent, coordination, human alignment | Production |
| ⚡ **Synapse** | [jupiturliu/synapse](https://github.com/jupiturliu/synapse) | Signal — Event Bus, DAG executor, budget routing | Open Source |
| 🧠 **TrustMem** | [jupiturliu/trustmem](https://github.com/jupiturliu/trustmem) | Memory — trust scores, decay, verification | Open Source |

---

## Co-exist Flywheel

```
Human intent
    → Aria understands + TrustMem recalls relevant memory
    → Synapse routes tasks to workers (parallel, budget-aware)
    → Workers complete → TrustMem logs episode → promotes if quality ≥ 0.8
    → Human feedback/override → highest-weight insight → next run smarter
    ↑_______________________________________________________↑
                     compounds over time
```

---

## Integration Status

| Phase | Description | Tests |
|-------|-------------|-------|
| Phase 1 ✅ | Aria ↔ Synapse Bridge, Event Bus replaces JSON polling | 13/13 |
| Phase 2 ✅ | AgencyWorker TrustMem hooks, Human Override Flywheel, Quality scoring | 44/44 |
| Phase 3 ✅ | Demo script, ROI report, pre-publish checks | — |

---

## Documentation

- [NOUS-OS-SPEC.md](./NOUS-OS-SPEC.md) — Full system specification
- [CO-EXIST-FLYWHEEL.md](./CO-EXIST-FLYWHEEL.md) — Flywheel design
- [docs/flywheel-architecture.md](./docs/flywheel-architecture.md) — Technical architecture
- [docs/aria-integration.md](./docs/aria-integration.md) — Aria ↔ Synapse integration guide
- [docs/getting-started.md](./docs/getting-started.md) — Getting started
- [docs/demo-blueprint.md](./docs/demo-blueprint.md) — Runnable demo design
- [docs/benchmark-spec.md](./docs/benchmark-spec.md) — How NOUS OS improvement is measured

---

## Demo

Run the self-contained demo in this repo:

```bash
python3 examples/nousos_demo.py
```

It demonstrates:
- Aria-style intent routing
- Synapse-style multi-agent fan-out
- TrustMem-style memory recall and human override reuse

Run the workspace-wired demo when `aria/`, `synapse/`, and `trustmem/` exist under the shared workspace:

```bash
python3 examples/nousos_workspace_demo.py
```

See [docs/workspace-demo.md](./docs/workspace-demo.md) for details.

Run the heartbeat bridge demo to show how Aria's `agent-bus` flow upgrades into NOUS OS:

```bash
python3 examples/nousos_heartbeat_demo.py
```

See [docs/heartbeat-demo.md](./docs/heartbeat-demo.md).

Use the formal runner when you want a reusable heartbeat entry plus a dashboard snapshot:

```bash
python3 scripts/run_nous_heartbeat.py
python3 -m http.server
```

Then open `demo/heartbeat-dashboard.html`.

Or run the interactive local dashboard server:

```bash
python3 scripts/run_nous_dashboard.py
```

Then open `http://127.0.0.1:8765/demo/heartbeat-dashboard.html`.

---

## Landing Page

**[nousos.ai](https://nousos.ai)**

---

## License

MIT © 2026 Liu Fei / jupiturliu
