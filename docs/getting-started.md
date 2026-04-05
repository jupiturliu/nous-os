# Getting Started with NOUS OS

This guide shows the current TrustMem + Synapse integration path. References to `AriaSynapseBridge` describe the planned Phase 1 interface, not code shipped in this repository.

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

## Step 2 — Planned AriaSynapseBridge Integration

`AriaSynapseBridge` is the planned Phase 1 integration point. It is part of the target NOUS OS architecture, but Aria itself is not open-sourced in this repository yet.

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

After a few runs, check what the memory system has learned:

```bash
python3 synapse/reports/nous_os_roi.py
```

---

## Architecture Reference

See [ARCHITECTURE.md](../ARCHITECTURE.md) for the full three-layer design and integration details.

---

## How the Flywheel Self-Improves

| Run | Memory State | Quality | Time |
|-----|-------------|---------|------|
| 1st | Cold start (no memory) | ~0.65 | 2.3s |
| 2nd | Episode found + override context | ~0.87 | 1.1s |
| 3rd+ | Converged pattern, high confidence | ~0.92 | 0.8s |

Each override you record makes the next analysis more accurate — without changing any code.
