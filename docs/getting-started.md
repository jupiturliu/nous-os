# Getting Started with NOUS OS

This guide shows the current TrustMem + Synapse integration path. The `AriaSynapseBridge` and `AriaOrchestrator.publish_from_agent_bus()` implementations live in the sibling `synapse/` workspace repo; this repository keeps the NOUS OS narrative, demos, dashboard, and public benchmark surface.

This repository also includes a self-contained demo that preserves the NOUS OS layer boundaries without depending on the external component repos.

---

## Prerequisites

```bash
# Synapse
cd synapse && pip install -e .

# TrustMem (Node.js)
cd trustmem && npm install
```

---

## Step 1 — Run the Flywheel Demo

The fastest way to see the system in action (no real API needed):

```bash
python3 examples/nousos_demo.py
```

This shows the full loop:
1. Intent → TrustMem-style search
2. Synapse-style parallel execution
3. Episode log + quality evaluation
4. Promotion to shared memory
5. Human override recording
6. Second run with memory context

---

## Step 2 — AriaSynapseBridge Integration

`AriaSynapseBridge` is the Phase 1 integration point in the workspace Synapse repo. Aria itself is still treated as the private consciousness/alignment layer, while the bridge and heartbeat demo prove the public integration boundary.

```python
import sys
sys.path.insert(0, 'synapse')

from orchestration.aria_synapse_bridge import AriaSynapseBridge

bridge = AriaSynapseBridge()

# Dispatch a task — TrustMem context is auto-injected
job_id = bridge.publish_with_memory(
    task_type='investment_analysis',
    payload={
        'ticker': 'AAOI',
        'intent': '分析 AAOI 的投资机会',
    }
)

print(f"Dispatched: {job_id}")

# Check status
status = bridge.get_task_status(job_id)
print(f"Status: {status}")
```

---

## Step 3 — Record Human Overrides

When you correct an AI decision, record it so the next run benefits:

```python
from orchestration.human_override import HumanOverrideHandler

handler = HumanOverrideHandler()

insight_id = handler.record_override(
    job_id=job_id,
    original_decision={'action': 'buy AAOI', 'confidence': 0.72},
    override_reason='没考虑宏观风险，利率上行周期',
    domain='investment',
    context='Fed signaled 2 more rate hikes in 2026'
)

print(f"Override recorded: {insight_id}")
# → Written to knowledge/firsthand-insights/insights.json
# → Synapse episode marked had_correction=true
# → Aria alert queued for follow-up
```

---

## Step 4 — Check Memory ROI

For the current public demo, inspect the benchmark snapshot:

```bash
python3 scripts/run_nous_heartbeat.py
cat examples/runtime/dashboard-data.json
```

The snapshot maps directly to Q/C/E/R and CLS in [benchmark-spec.md](./benchmark-spec.md).

---

## Architecture Reference

See [ARCHITECTURE.md](../ARCHITECTURE.md) for the full three-layer design and integration details.

---

## Public Release Smoke

These commands require only this `nous-os` repository:

```bash
python3 examples/nousos_demo.py
python3 -m unittest discover -s tests -v
```

This command is self-contained. When sibling Synapse/Aria runtime modules are absent, it uses the local deterministic fallback harness:

```bash
python3 scripts/run_nous_heartbeat.py
```

This command requires the full `/Users/liyao/nousos` workspace with sibling repos:

```bash
python3 scripts/check_cross_repo_release_gate.py --workspace /Users/liyao/nousos --json
```

The cross-repo release gate is read-only. It reports repo existence, dirty state, and conservative doc scan findings; it does not mutate runtime state.

---

## How the Flywheel Self-Improves

| Run | Memory State | Quality | Time |
|-----|-------------|---------|------|
| 1st | Cold start (no memory) | ~0.65 | 2.3s |
| 2nd | Episode found + override context | ~0.87 | 1.1s |
| 3rd+ | Converged pattern, high confidence | ~0.92 | 0.8s |

Each override you record makes the next analysis more accurate — without changing any code.
