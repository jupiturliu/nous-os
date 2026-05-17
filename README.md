# NOUS OS

> **Human-AI Learning System for Co-Evolution**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Website](https://img.shields.io/badge/website-nousos.ai-blue)](https://nousos.ai)

---

## What is NOUS OS

NOUS OS is not an app and not a commercialization-first product. It is an **education and research project** for studying how humans and AI can learn together: shared memory, event mesh, domain runtime, outcome proof, and human authority. The first vertical research proof is Trading Brain / `trading-agent`.

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

Current as of 2026-05-16:

| Area | Status | Evidence |
|------|--------|----------|
| Core repo | ✅ Standalone `nous-os` repo initialized | README, architecture docs, examples, tests |
| Aria ↔ Synapse | ✅ Bridge exists in workspace Synapse | `AriaSynapseBridge`, `AriaOrchestrator.publish_from_agent_bus()` |
| Heartbeat flywheel | ✅ Runnable local demo | `python3 scripts/run_nous_heartbeat.py` |
| Dashboard | ✅ Local interactive console + GitHub Pages artifact | `scripts/run_nous_dashboard.py`, `demo/heartbeat-dashboard.html` |
| Benchmark | ✅ Public Q/C/E/R + CLS snapshot | `docs/benchmark-spec.md`, `examples/runtime/dashboard-data.json` |
| CI / Pages | ✅ Unit tests and static deploy workflow | `.github/workflows/ci.yml`, `.github/workflows/pages.yml` |

Historical phase summary:

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1 | Aria ↔ Synapse Bridge, Event Bus replaces JSON polling | Complete |
| Phase 2 | Worker memory hooks, human override flywheel, quality scoring | Complete in demo/runtime path |
| Phase 3 | Standalone repo, heartbeat demo, dashboard, benchmark, publish path | Complete for local/public demo |

Remaining work is product hardening: wire a production Aria runtime, replace demo-quality scoring with domain evaluators, and add release automation for the upstream TrustMem/Synapse repos.

---

## Documentation

- [NOUS-OS-SPEC.md](./NOUS-OS-SPEC.md) — Full system specification
- [NOUS-OS-PHASE3.md](./NOUS-OS-PHASE3.md) — Current Phase 3 completion notes and next hardening work
- [docs/north-star-v2-roadmap.md](./docs/north-star-v2-roadmap.md) — Human-AI learning roadmap and first-vertical proof scope
- [docs/education-research-narrative.md](./docs/education-research-narrative.md) — Education/research narrative for high-school students, human-AI co-evolution, and safety boundaries
- [docs/NOUS-OS-Cognitive-COO-One-Pager.md](./docs/NOUS-OS-Cognitive-COO-One-Pager.md) — Chinese one-page product narrative
- [docs/NOUS-OS-Cognitive-COO-One-Pager.en.md](./docs/NOUS-OS-Cognitive-COO-One-Pager.en.md) — English one-page product narrative
- [CO-EXIST-FLYWHEEL.md](./CO-EXIST-FLYWHEEL.md) — Flywheel design
- [docs/flywheel-architecture.md](./docs/flywheel-architecture.md) — Technical architecture
- [docs/aria-integration.md](./docs/aria-integration.md) — Aria ↔ Synapse integration guide
- [docs/getting-started.md](./docs/getting-started.md) — Getting started
- [docs/demo-blueprint.md](./docs/demo-blueprint.md) — Runnable demo design
- [docs/benchmark-spec.md](./docs/benchmark-spec.md) — How NOUS OS improvement is measured
- [docs/domain-evaluator-interface.md](./docs/domain-evaluator-interface.md) — Domain evaluator contract for CLS v2
- [docs/harness/README.md](./docs/harness/README.md) — Harness engineering context, boundaries, and verification commands
- [docs/cross-repo-release-gate.md](./docs/cross-repo-release-gate.md) — Read-only release readiness gate across NOUS OS repos

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
