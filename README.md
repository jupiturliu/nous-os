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

---

## Landing Page

**[nousos.ai](https://nousos.ai)**

---

## License

MIT © 2026 Liu Fei / jupiturliu
