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

Current as of 2026-08-23:

| Area | Status | Evidence |
|------|--------|----------|
| Core distribution | ✅ Python 3.11 package with one command Interface | `pyproject.toml`, `src/nous_os`, `tests` |
| External runtimes | ✅ Explicit Adapter seams; no sibling-path imports | `ARCHITECTURE.md`, `src/nous_os/workflows/heartbeat.py` |
| Harness kernel | ✅ Python Plugin lifecycle + YAML Profiles | `src/nous_os/core`, `config/profiles` |
| Heartbeat flywheel | ✅ Evidence-backed local workflow | `nous-os run heartbeat --profile research` |
| Dashboard | ✅ Python Web composition + Cloudflare edge Adapter | `nous-os serve web --profile student`, `apps/web` |
| Benchmark | ✅ Public Q/C/E/R + CLS projection | `docs/benchmark-spec.md`, `$NOUS_OS_HOME/projections/dashboard-data.json` |
| CI / deploy | ✅ Unit tests and Cloudflare Worker workflow | `.github/workflows/ci.yml`, `.github/workflows/cloudflare.yml` |

Remaining work is product hardening: wire production runtime Adapters, replace remaining demo-quality scoring with domain evaluators, and automate releases for upstream TrustMem/Synapse repos.

---

## Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) — Current Harness architecture and runtime composition
- [docs/architecture/repository-layout.md](./docs/architecture/repository-layout.md) — Canonical repository layout
- [CONTEXT.md](./CONTEXT.md) — Domain language used by code and documentation
- [docs/adr/](./docs/adr/) — Accepted architecture decisions
- [docs/north-star-v2-roadmap.md](./docs/north-star-v2-roadmap.md) — Human-AI learning roadmap and first-vertical proof scope
- [docs/education-research-narrative.md](./docs/education-research-narrative.md) — Education/research narrative for high-school students, human-AI co-evolution, and safety boundaries
- [docs/human-ai-symbiosis-self-evolution.md](./docs/human-ai-symbiosis-self-evolution.md) — Theory anchor for human-AI symbiosis and self-evolution
- [docs/human-ai-coevolution-model-v0.md](./docs/human-ai-coevolution-model-v0.md) — v0 model for the human-agent co-evolution loop
- [docs/self-evolution-metrics-v0.md](./docs/self-evolution-metrics-v0.md) — v0 metrics for human, agent, and relationship evolution
- [docs/memory-philosophy-v0.md](./docs/memory-philosophy-v0.md) — Memory rules for remember, challenge, decay, and forget
- [docs/cloudflare-hermes-architecture.md](./docs/cloudflare-hermes-architecture.md) — Cloudflare Worker, local webserver, and Hermes Gateway deployment architecture
- [docs/student-sandbox-deterministic-workflow.md](./docs/student-sandbox-deterministic-workflow.md) — Deterministic Student Sandbox workflow and skill/playbook boundary
- [docs/NOUS-OS-Cognitive-COO-One-Pager.md](./docs/NOUS-OS-Cognitive-COO-One-Pager.md) — Chinese one-page product narrative
- [docs/NOUS-OS-Cognitive-COO-One-Pager.en.md](./docs/NOUS-OS-Cognitive-COO-One-Pager.en.md) — English one-page product narrative
- [CO-EXIST-FLYWHEEL.md](./CO-EXIST-FLYWHEEL.md) — Flywheel design
- [docs/flywheel-architecture.md](./docs/flywheel-architecture.md) — Technical architecture
- [docs/getting-started.md](./docs/getting-started.md) — Getting started
- [docs/benchmark-spec.md](./docs/benchmark-spec.md) — How NOUS OS improvement is measured
- [docs/domain-evaluator-interface.md](./docs/domain-evaluator-interface.md) — Domain evaluator contract for CLS v2
- [docs/harness/README.md](./docs/harness/README.md) — Harness engineering context, boundaries, and verification commands
- [docs/cross-repo-release-gate.md](./docs/cross-repo-release-gate.md) — Read-only release readiness gate across NOUS OS repos

---

## Harness Quickstart

Create an environment and install the unified command Interface:

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
```

Validate the Harness composition and machine contracts:

```bash
.venv/bin/nous-os validate profile --profile student
.venv/bin/nous-os validate contracts
.venv/bin/nous-os validate harness
```

Run Heartbeat. Mutable state is written to `$NOUS_OS_HOME` (default `~/.nous-os`), not to the repository:

```bash
NOUS_OS_HOME=/tmp/nous-os-demo .venv/bin/nous-os run heartbeat --profile research
```

See [docs/heartbeat-demo.md](./docs/heartbeat-demo.md).

Start the local Web composition. It preserves `/api/health`, `/api/hermes-student-agent`, `/api/student-sandbox-session`, `/api/dashboard-data`, and `/api/run-heartbeat`:

```bash
.venv/bin/nous-os serve web --profile student
```

Then open `http://127.0.0.1:8787/demo/heartbeat-dashboard.html`.

Runtime projections become tracked website data only through explicit publication:

```bash
.venv/bin/nous-os publish-site-data --profile research
npm run site:stage
```

---

## Landing Page

**[nousos.ai](https://nousos.ai)**

---

## License

MIT © 2026 Liu Fei / jupiturliu
