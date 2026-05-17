# Human-AI Co-Evolution Demo Refresh Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task. Preserve the education/research framing. Do not implement trading execution, broker authority, live risk mutation, or autonomous capital action.

**Goal:** Refresh the NOUS OS demo so a high-school student, parent, teacher, or researcher can clearly see how humans and AI co-evolve while human agency and safety boundaries stay explicit.

**Architecture:** Keep the existing two-run heartbeat architecture, but change the demo story from generic productivity improvement to a visibly educational human-AI co-evolution loop. The dashboard should show: human question -> AI first pass -> human boundary/feedback -> memory/proof update -> AI second pass -> student reflection. Trading-agent remains the first vertical application / research proof bed, but it is presented as a high-constraint safety case, not as an investing recommendation or commercialization endpoint.

**Tech Stack:** Python stdlib demo runtime, JSON dashboard snapshot, static HTML dashboard, unittest site contract tests, Obsidian narrative mirror.

---

## Design Review: Current Demo vs North Star

### What already works

- The demo already has a two-run loop:
  - Round 1 cold start.
  - Human override.
  - Round 2 with memory and improved routing.
- It already emits dashboard data under `examples/runtime/dashboard-data.json`.
- It already visualizes Aria, Synapse, TrustMem, alerts, timeline, metrics, and CLS / CLS v2.
- It already isolates runtime files under `examples/runtime/`, so it does not touch production queues.

### What does not yet fully meet the new design target

- The visible story is still mostly "product ask -> better agents" rather than "student question -> AI collaboration -> human boundary -> co-evolution".
- Safety boundaries are implied by override buttons, but not taught as a first-class concept.
- The human role is too narrow: one override. The demo should show human agency across intent, value, boundary, verification, reflection, and final responsibility.
- The first vertical trading-agent role is not clearly framed as education/research traction. Without explanation, viewers may mistake it for a trading product demo.
- The demo metrics show improvement, but they do not clearly connect improvement to a human learning loop.

## Target Demo Story

The demo should answer this question in one visible flow:

```text
How should a high-school student work with AI without handing over judgment, responsibility, privacy, or values?
```

The flow:

```text
1. Student asks a real question
2. AI proposes a first-pass plan
3. Human sets a boundary or correction
4. System records the correction as memory/evidence
5. AI changes the second-pass plan
6. Student reflects: what did I learn, what remains my responsibility?
7. Demo shows proof: memory reuse, correction absorption, boundary integrity, human agency preservation
```

## Proposed Dashboard Modes

### Mode 1 — Student Learning Companion

Default goal:

```text
I am a high-school student trying to understand how to use AI for a research project without losing my own thinking.
```

Override choices:

- `privacy`: Do not reveal private family/school/friend information.
- `facts`: Add source checks before accepting the answer.
- `learning`: Do not give final answers; guide me with hints and practice.
- `values`: Do not decide my goals for me.

Expected visible lesson:

```text
AI gets more useful after human feedback, but the human keeps goals, values, verification, and responsibility.
```

### Mode 2 — Trading Agent as First Vertical Research Proof

Default goal:

```text
Use trading-agent as a high-constraint research example to study AI boundaries, not to recommend trades.
```

Override choices:

- `capital_boundary`: No capital action without explicit human approval.
- `evidence`: Require provenance and measurable outcome before promotion.
- `reconciliation`: Block new action until prior state is reconciled.
- `no_action`: Preserve the right to decide that no action is the correct action.

Expected visible lesson:

```text
The first vertical shows why powerful agents need boundaries before autonomy.
```

### Mode 3 — Research Lab / Teacher View

Default goal:

```text
Run an education/research experiment showing whether human feedback changes the next AI cycle.
```

Override choices:

- `rubric`: Use a rubric before scoring quality.
- `reflection`: Add a student reflection checkpoint.
- `repeatability`: Require the same loop to be reproducible.
- `boundary`: Fail the run if human agency is not preserved.

Expected visible lesson:

```text
This is an experiment harness, not a product claim.
```

## Data Model Changes

Add these fields to the dashboard snapshot:

```json
{
  "demo_mode": "student|trading_vertical|research_lab",
  "audience": "high_school_student|parent|teacher|researcher",
  "north_star": "education/research-first human-AI co-evolution",
  "human_agency": {
    "human_sets_goal": true,
    "human_sets_boundary": true,
    "human_verifies": true,
    "human_keeps_final_responsibility": true
  },
  "safety_boundaries": [
    {"id": "privacy", "label": "Privacy Boundary", "status": "active", "evidence_ref": "runtime://human_override"},
    {"id": "facts", "label": "Fact Boundary", "status": "active", "evidence_ref": "runtime://round2"},
    {"id": "learning", "label": "Learning Boundary", "status": "active", "evidence_ref": "runtime://reflection"},
    {"id": "decision", "label": "Decision Boundary", "status": "active", "evidence_ref": "runtime://human_authority"},
    {"id": "values", "label": "Value Boundary", "status": "active", "evidence_ref": "runtime://student_reflection"}
  ],
  "reflection": {
    "prompt": "What did the AI help with, and what remains my responsibility?",
    "student_takeaway": "AI can assist my thinking, but it should not replace my judgment."
  },
  "first_vertical": {
    "name": "trading-agent",
    "role": "first vertical application / research proof bed",
    "not_for": "student investing advice or commercialization endpoint",
    "lesson": "High-stakes agents require approval gates, reconciliation, provenance, and review."
  }
}
```

## UI Changes

### Task 1: Reframe the hero copy

**Objective:** Make the first screen explain the education/research purpose.

**Files:**
- Modify: `demo/heartbeat-dashboard.html`

**Change:** Replace current hero line:

```text
Intent goes in. Better agents come back out.
```

with:

```text
Humans and AI learn together — with boundaries.
```

Replace lede with:

```text
Ask a question like a student, parent, teacher, or researcher. NOUS OS shows the loop: human goal, AI first pass, human boundary, memory update, second pass, and reflection. The point is not automation for its own sake; it is stronger human judgment with safer AI collaboration.
```

### Task 2: Add Demo Mode selector

**Objective:** Let the audience choose the narrative mode.

**Files:**
- Modify: `demo/heartbeat-dashboard.html`
- Modify: `examples/nousos_heartbeat_demo.py`
- Test: `tests/test_nous_os.py`

**Modes:**
- Student Learning Companion
- Trading Agent Research Proof
- Research Lab / Teacher View

**Acceptance:** Dashboard snapshot includes `demo_mode`; UI changes default goal and override labels based on mode.

### Task 3: Replace generic override choices with boundary choices

**Objective:** Teach safety boundaries directly.

**Files:**
- Modify: `examples/nousos_heartbeat_demo.py`
- Modify: `demo/heartbeat-dashboard.html`

**Student default override choices:**
- Privacy boundary
- Fact-check boundary
- Learning-not-answering boundary
- Value/goal boundary

**Trading vertical override choices:**
- Capital approval boundary
- Evidence/provenance boundary
- Reconciliation boundary
- No-action boundary

**Acceptance:** Override labels and reasons are displayed in plain language and logged in the snapshot.

### Task 4: Add a human-agency panel

**Objective:** Show what remains human-owned.

**Files:**
- Modify: `demo/heartbeat-dashboard.html`
- Modify: `examples/nousos_heartbeat_demo.py`

**Panel content:**

```text
Human keeps:
- goal
- values
- verification
- final responsibility

AI helps with:
- search
- decomposition
- simulation
- critique
- memory recall
- practice generation
```

**Acceptance:** A viewer can explain the human/AI boundary without reading repo docs.

### Task 5: Add student reflection as the final stage

**Objective:** Make co-evolution visible as human learning, not only model/task improvement.

**Files:**
- Modify: `examples/nousos_heartbeat_demo.py`
- Modify: `demo/heartbeat-dashboard.html`

**Add timeline stage:**

```text
Student Reflection: What did AI help with, what did I verify, and what remains my responsibility?
```

**Acceptance:** Timeline ends with reflection, not just quality improvement.

### Task 6: Reframe metrics around North Star

**Objective:** Make metrics map to human-AI co-evolution.

**Files:**
- Modify: `examples/nousos_heartbeat_demo.py`
- Modify: `demo/heartbeat-dashboard.html`
- Modify: `docs/benchmark-spec.md` if needed

**Metrics:**
- Correction Absorption
- Memory Reuse
- Boundary Integrity
- Human Agency Preservation
- Reflection Completeness
- Repeatability Gain

**Acceptance:** Dashboard says these are demo/harness metrics, not production proof.

### Task 7: Add first-vertical explainer card

**Objective:** Explain why trading-agent appears in an education/research project.

**Files:**
- Modify: `demo/heartbeat-dashboard.html`
- Modify: `examples/nousos_heartbeat_demo.py`

**Copy:**

```text
Trading-agent is the first vertical application because it is high-constraint and measurable. It is not shown as investing advice. It is a research proof bed for why powerful agents need human approval, evidence, reconciliation, no-action decisions, and post-outcome review.
```

**Acceptance:** The dashboard cannot be mistaken as encouraging students to trade.

### Task 8: Add static contract tests

**Objective:** Prevent drift from the North Star.

**Files:**
- Modify: `tests/test_nous_os.py`

**Assertions:**
- `demo/heartbeat-dashboard.html` contains `Humans and AI learn together — with boundaries`.
- `demo/heartbeat-dashboard.html` contains `not investing advice` or equivalent first-vertical boundary.
- `docs/education-research-narrative.md` contains `first vertical application`.
- Snapshot fixture contains `human_agency` and `safety_boundaries`.

### Task 9: Update docs and Obsidian mirror

**Objective:** Keep public docs and human-readable notes aligned.

**Files:**
- Modify: `docs/heartbeat-demo.md`
- Modify: `docs/demo-blueprint.md`
- Modify: `/Users/liyao/Documents/nousos/NousOS/03 Development Plans/NOUS OS Development Plans Index.md`
- Create/modify: `/Users/liyao/Documents/nousos/NousOS/03 Development Plans/Human-AI Co-Evolution Demo Refresh Plan.md`

**Acceptance:** A new contributor can understand the demo goal from docs without reading chat history.

## Suggested Implementation Order

1. Update Python snapshot schema first.
2. Update tests for expected schema and static copy.
3. Update HTML hero, mode selector, boundary panel, reflection stage, and first-vertical card.
4. Run `python3 scripts/run_nous_heartbeat.py` to regenerate `examples/runtime/dashboard-data.json`.
5. Run `python3 -m unittest discover -s tests -v`.
6. Run `python3 scripts/check_cross_repo_release_gate.py --workspace /Users/liyao/nousos --json` and record dirty-state interpretation.
7. Mirror final plan/status into Obsidian.

## Definition of Done

The demo satisfies the North Star when a viewer can answer these five questions after one run:

1. What did the human decide?
2. What did AI help with?
3. What boundary did the human add?
4. How did the system remember and change the next run?
5. What remains human responsibility?

If those five answers are visible, the demo demonstrates human-AI co-evolution rather than generic automation.
