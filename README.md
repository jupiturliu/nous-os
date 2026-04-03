# NOUS OS

> **The Cognitive Operating System for Human-AI Co-evolution**

NOUS OS is a three-layer architecture that makes every human-AI interaction a learning step — not just a transaction. Each decision sharpens memory. Each override corrects the model. Each run is faster and more accurate than the last.

Aria is part of the architecture, but its implementation is not open-sourced in this repository yet.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    NOUS OS — Three Layers                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Aria  (Prefrontal Cortex)                           │  │
│  │  Intent · Judgment · Human Alignment · Override      │  │
│  └──────────────────────────────┬───────────────────────┘  │
│                                 │                           │
│  ┌──────────────────────────────▼───────────────────────┐  │
│  │  Synapse  (Nervous System)                           │  │
│  │  Event Bus · DAG Executor · Budget Scheduler         │  │
│  │  Worker Pool · Blackboard · Fault Isolation          │  │
│  └──────────────────────────────┬───────────────────────┘  │
│                                 │                           │
│  ┌──────────────────────────────▼───────────────────────┐  │
│  │  TrustMem  (Hippocampus)                             │  │
│  │  Episode Store · Confidence · Decay · Promotion      │  │
│  │  Firsthand Insight · Cross-Agent Verification        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Co-exist Flywheel

The Flywheel is the core loop that makes the system self-improving:

```
Intent  →  TrustMem Search  →  Synapse DAG  →  Workers
   ↑                                                  │
   │         Episode Log + Quality Eval               │
   │                    │                             ▼
   └── Human Override ←─┘←─── promote (quality≥0.8) ─┘
           (recorded as firsthand insight)
```

Each cycle:
- **Without memory**: cold start, baseline quality
- **With memory**: context-aware, higher quality, faster
- **After override**: the correction is stored and applied next run

---

## Quick Links

| Component | Description |
|-----------|-------------|
| [TrustMem](../trustmem/) | Episodic memory, confidence scoring, decay |
| [Synapse](../synapse/) | Event bus, DAG executor, budget scheduler |
| [Demo](../synapse/demo/nous_os_demo.py) | End-to-end Flywheel demo |
| [Architecture](ARCHITECTURE.md) | Deep architecture doc |
| [Getting Started](docs/getting-started.md) | Connect TrustMem + Synapse |

---

## Getting Started

**3 steps to run NOUS OS:**

```bash
# 1. Run the Flywheel demo (no real API needed)
python3 synapse/demo/nous_os_demo.py

# 2. Check Memory ROI
python3 synapse/reports/nous_os_roi.py

# 3. Pre-publish check before releasing components
bash scripts/pre_publish_check.sh
```

---

## License

MIT © 2026 Liu Fei / jupiturliu
