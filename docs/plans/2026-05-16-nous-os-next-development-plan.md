# NOUS OS Next Development Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task. Preserve the education/research-first framing. Do not implement trading execution, broker authority, live risk mutation, autonomous capital action, multi-tenant SaaS, or student data collection beyond local/demo artifacts.

**Goal:** Move NOUS OS from foundation-setting into a real education/research development phase centered on a clear human-AI co-evolution demo, a repeatable research harness, and trading-agent as the first high-constraint vertical proof bed.

**Architecture:** Build from the demo backward. The next development wave should first make the human-AI co-evolution loop visible and runnable, then turn every run into a structured research record, then use trading-agent as the advanced first vertical boundary case. Avoid platform expansion until the demo can clearly show human intent, AI first pass, human boundary, memory/evidence update, AI second pass, student reflection, and preserved human responsibility.

**Tech Stack:** Python stdlib demo runtime, JSON snapshot artifacts, static HTML dashboard, unittest contract tests, Obsidian mirror notes, existing Synapse/TrustMem/trading-agent references as read-only proof/context.

---

## Strategic Thesis

NOUS OS should not become “another agent framework.” Its differentiator is the human cognitive development loop:

```text
Human/student intent
  -> AI first pass
  -> human boundary / correction
  -> memory + evidence update
  -> AI second pass changes behavior
  -> reflection
  -> human keeps goal, values, verification, and responsibility
```

The next development phase should prove this loop visibly and repeatedly.

The core product/research question is:

```text
How should high-school students and the next generation work with AI without handing over judgment, responsibility, privacy, or values?
```

## What NOT To Build Yet

Do not prioritize:

- multi-user login
- SaaS onboarding
- agent marketplace
- a generic platform dashboard
- a second vertical
- moving trading-agent UI into NOUS OS
- collecting real student private data
- live trading / broker integration
- autonomous execution

These are premature until the core human-AI co-evolution loop is obvious and repeatable.

## Phase 1 — Narrative Demo: Human-AI Co-Evolution Demo v0

**Goal:** Make the demo understandable to a high-school student, parent, teacher, or researcher within 60 seconds.

**Primary source plan:** `docs/plans/2026-05-16-human-ai-coevolution-demo-refresh-plan.md`

### Required demo flow

```text
1. Human/student asks a question
2. AI proposes a first-pass plan
3. Human sets a boundary or correction
4. System records the correction as memory/evidence
5. AI changes the second-pass plan
6. Student reflects: what did I learn, what remains my responsibility?
7. Demo shows proof: memory reuse, correction absorption, boundary integrity, human agency preservation
```

### Required visible panels

- Scenario selector:
  - Student Learning Companion
  - Trading Agent Research Proof
  - Research Lab / Teacher View
- Safety Boundaries panel:
  - privacy
  - facts
  - learning
  - decision
  - values
- Human Agency panel:
  - human keeps goal, values, verification, final responsibility
  - AI helps search, decomposition, simulation, critique, memory recall, practice generation
- Reflection panel:
  - what did AI help with?
  - what did I verify?
  - what remains my responsibility?
- First Vertical explainer:
  - trading-agent is the first vertical application / high-constraint research proof bed
  - not investing advice
  - not a commercialization endpoint

### Acceptance criteria

A viewer can answer:

1. What did the human decide?
2. What did AI help with?
3. What boundary did the human add?
4. How did memory/evidence change the next run?
5. What remains human responsibility?

## Phase 2 — Research Harness: Structured Experiment Records

**Goal:** Turn each demo run into a reusable education/research artifact, not just a visual performance.

**Status:** Implemented in the repo runtime. `examples/nousos_heartbeat_demo.py` now writes a structured record for each heartbeat run under `examples/runtime/research-records/`, and `latest.json` is published with the static demo for review.

### Required artifact

Create a local structured artifact per run:

```json
{
  "run_id": "string",
  "demo_mode": "student|trading_vertical|research_lab",
  "audience": "student|parent|teacher|researcher",
  "human_intent": "string",
  "ai_first_pass": {"summary": "string", "risks": []},
  "human_boundary": {"kind": "privacy|facts|learning|decision|values|capital|evidence|reconciliation|no_action", "reason": "string"},
  "memory_update": {"stored": true, "evidence_refs": []},
  "ai_second_pass": {"summary": "string", "behavior_changed": true},
  "reflection": {"prompt": "string", "student_takeaway": "string"},
  "metrics": {
    "correction_absorption": 0.0,
    "memory_reuse": 0.0,
    "boundary_integrity": 0.0,
    "human_agency_preservation": 0.0,
    "reflection_completeness": 0.0,
    "repeatability_gain": 0.0
  }
}
```

### Implementation target

- Create: `examples/runtime/research-records/`
- Modify: `examples/nousos_heartbeat_demo.py`
- Modify: `examples/runtime/dashboard-data.json`
- Modify: `tests/test_nous_os.py`

### Acceptance criteria

- Every demo run emits a research record.
- The record does not contain private student data by default.
- The record links to dashboard snapshot evidence.
- Tests verify required fields exist.

### Implemented artifact paths

```text
examples/runtime/research-records/<run_id>.json
examples/runtime/research-records/latest.json
```

## Phase 3 — First Vertical Proof: Trading-Agent Boundary Case

**Goal:** Use trading-agent as the first vertical education/research traction case for high-constraint human-AI boundaries.

### Framing

Trading-agent should not be presented as investing advice or as NOUS OS commercialization. It should be presented as an advanced research case:

```text
The stronger the agent and the higher the stakes, the more explicit the human boundary must be.
```

### Required boundary lessons

- No capital action without explicit human approval.
- Evidence/provenance is required before promotion.
- Reconciliation must happen before follow-on action.
- No-action is a valid, often wise, decision.
- Post-outcome review feeds the next learning loop.

### Implementation target

- Modify: `docs/education-research-narrative.md`
- Modify: `docs/north-star-v2-roadmap.md`
- Modify: `demo/heartbeat-dashboard.html`
- Modify: `examples/nousos_heartbeat_demo.py`

### Acceptance criteria

- Dashboard has a Trading Agent Research Proof mode.
- The mode explicitly says “not investing advice.”
- The mode demonstrates approval/evidence/reconciliation/no-action/review as safety boundaries.

## Phase 4 — Student Agent Sandbox v0

**Goal:** Create a safe, local-only student-facing sandbox for AI-assisted learning and reflection.

### Scope

This is not a general agent platform. It is a local education/research sandbox with constrained behaviors.

### Initial scenario

```text
A high-school student wants help planning a research project without losing their own thinking.
```

### Required behavior

- AI asks clarifying questions before answering.
- AI offers hints and practice instead of final answers when learning boundary is active.
- AI asks for source checks when fact boundary is active.
- AI refuses to store private details unless explicitly anonymized.
- AI ends with a reflection prompt.

### Acceptance criteria

- Can run locally without external student data collection.
- Produces a research record.
- Shows what the student retained responsibility for.

## Phase 5 — Review and Iteration Protocol

**Goal:** Make development itself follow the NOUS OS learning loop.

After every demo/user test, create a review entry with:

- audience type
- what confused the viewer
- which boundary was unclear
- whether the viewer could explain human vs AI roles
- what should change in the next run

Store human-readable reviews under:

```text
/Users/liyao/Documents/nousos/NousOS/04 Reviews/
```

Store machine-readable local artifacts under:

```text
/Users/liyao/nousos/nous-os/examples/runtime/research-records/
```

## Immediate Next Sprint

### Sprint name

```text
NOUS OS Human-AI Co-Evolution Demo v0
```

### Sprint objective

Make the demo visibly show that AI helps, but humans keep goals, values, verification, boundaries, reflection, and responsibility.

### Sprint tasks

1. Implement demo mode schema in `examples/nousos_heartbeat_demo.py`.
2. Add `human_agency`, `safety_boundaries`, `reflection`, and `first_vertical` fields to the snapshot.
3. Update `demo/heartbeat-dashboard.html` hero and copy.
4. Add Scenario Selector UI.
5. Add Boundary Panel UI.
6. Add Human Agency Panel UI.
7. Add Student Reflection stage to the timeline.
8. Add Trading Agent Research Proof explainer.
9. Generate `examples/runtime/dashboard-data.json` from the updated flow.
10. Add/expand contract tests in `tests/test_nous_os.py`.
11. Update `docs/heartbeat-demo.md` and `docs/demo-blueprint.md`.
12. Mirror completion status into Obsidian.

### Verification commands

```bash
cd /Users/liyao/nousos/nous-os
python3 scripts/run_nous_heartbeat.py
python3 -m unittest discover -s tests -v
python3 scripts/check_cross_repo_release_gate.py --workspace /Users/liyao/nousos --json
```

Interpret release-gate `ok=false` carefully: dirty/untracked files are readiness findings, not necessarily functional failures.

## Definition of Done for the Next Development Phase

NOUS OS is ready for the next phase when:

- A high-school student can understand the demo without engineering explanation.
- A parent/teacher can identify the safety boundaries.
- A researcher can inspect the structured run artifact.
- A technical viewer can see how Aria/Synapse/TrustMem/trading-agent relate without confusing the demo for trading advice.
- The dashboard visibly proves that human feedback changes the next AI cycle.
- The final step is reflection, not automation.

## North Star Reminder

NOUS OS exists to study and teach human-AI co-evolution. AI is not the endpoint. Automation is not the endpoint. Human cognitive growth — memory, attention, judgment, reflection, meaning, and responsibility — is the endpoint.
