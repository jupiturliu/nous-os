# NOUS OS Architecture

> Distilled from `knowledge/ai-infra/coexist-flywheel-architecture.md`

---

## Core Principle

NOUS OS maps AI cognition to neuroscience:

| Layer | Neuroscience Analogy | Responsibility |
|-------|---------------------|----------------|
| **TrustMem** | Hippocampus | What to remember, what to trust |
| **Synapse** | Nervous System | How signals travel, who executes |
| **Aria** | Prefrontal Cortex | Why, intent, judgment, human alignment |

The problem NOUS OS solves: these three were running independently. Like having a brain, nervous system, and memory but with no wiring between them.

Note: in this repository, Aria is documented as the planned judgment/alignment layer. The open-source code here focuses on TrustMem, Synapse, and their integration points.

---

## Flywheel Loop

```
Human Intent (Liu Fei)
        │
        ▼
┌───────────────────────┐
│  Aria (Prefrontal)    │
│  1. Parse intent      │
│  2. TrustMem search   │ ← Was this done before? What was learned?
│  3. Build DAG         │
│  4. Publish to Bus    │
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│  Synapse (Nervous)    │
│  Event Bus routing    │
│  Budget Scheduler     │ ← Best model for cost/quality tradeoff
│  DAG parallel exec    │
│  Blackboard state     │
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│  TrustMem (Memory)    │
│  Episode log          │ ← Every task completion is recorded
│  quality ≥ 0.8 →      │
│    promote to shared  │
│  Human override →     │ ← Corrections become firsthand insights
│    write episodic     │
└───────────────────────┘
           │
           └── Next run: faster + more accurate ↑
```

---

## Three Integration Phases

### Phase 1 — Event-Driven Dispatch (Minimal Change)

Replace file polling with Synapse Event Bus:

```python
# Before (file polling)
with open('agent-bus/implementation_queue.json', 'w') as f:
    json.dump(queue, f)

# After (event-driven via the planned AriaSynapseBridge)
from synapse.orchestration.aria_synapse_bridge import AriaSynapseBridge
bridge = AriaSynapseBridge()
job_id = bridge.publish_with_memory(task_type='analysis', payload=task)
```

**Result:** Zero polling latency, Budget Scheduler auto-selects model, TrustMem context travels with the task.

This bridge is part of the target architecture and may live outside this repository until Aria is publicly released.

### Phase 2 — TrustMem Embedded in Workers

Every Worker automatically searches before execution and logs after:

```python
class AgentWorker:
    def execute_task(self, task):
        memory_context = trustmem_search(task['description'])
        task['memory_context'] = memory_context
        result = self._run(task)
        episode_logger.log(task, result)
        return result
```

### Phase 3 — Human Override Closed Loop

When Liu Fei overrides an AI decision:

```python
handler = HumanOverrideHandler()
handler.record_override(
    job_id=job_id,
    original_decision=ai_result,
    override_reason="didn't account for macro risk",
    domain="investment"
)
# → writes to insights.json (weight=1.0)
# → marks episode had_correction=true
# → fires Aria follow-up alert
```

---

## Quality & Promotion

```
Task Complete
    │
    ▼
Episode logged (always)
    │
quality ≥ 0.8?
    ├── YES → promote to shared semantic memory
    └── NO  → stays in episodic only (still searchable)
```

Human overrides always land in `firsthand-insights/insights.json` with `weight=1.0`, bypassing the quality gate.

---

## Budget Scheduler

In the target architecture, Aria sets policy in `budget_policy.yaml`. Scheduler enforces in real-time:

- **Cheap tasks** → MiniMax / Haiku
- **Important tasks** → Claude Sonnet / Opus
- **Over budget** → auto-downgrade to fallback model
- **Firsthand insight** → boost priority (ignore budget cap)

---

## Key Files

```
synapse/
├── core/
│   ├── budget_scheduler.py     # Model selection + cost tracking
│   ├── dag_executor.py         # Parallel task execution
│   └── event_bus.py            # Pub/sub backbone
├── orchestration/
│   ├── aria_synapse_bridge.py  # Planned Aria ↔ Synapse interface (Phase 1)
│   ├── human_override.py       # Override closed-loop handler
│   └── orchestrator.py         # Main orchestration logic
└── demo/
    └── nous_os_demo.py         # End-to-end Flywheel demo
```
