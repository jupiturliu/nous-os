# NOUS OS Student Sandbox + Research Study v1 Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Make the NOUS OS student-facing learning loop usable in a real 20-minute high-school research session, while producing privacy-first research observations for parent/teacher/research review.

**Architecture:** Build from the visible human-AI co-evolution loop backward: student intent -> AI first pass -> human boundary -> source/evidence check -> AI second pass -> reflection. Keep the implementation local-only and deterministic for v1 scaffold; no external model calls, no student identity collection, no SaaS/multi-user expansion.

**Tech Stack:** Python standard library, existing `examples/nousos_heartbeat_demo.py` research-record helpers, existing unittest suite, repo docs under `docs/`, NOUS OS Obsidian mirror under `/Users/liyao/Documents/nousos/NousOS/03 Development Plans/`.

---

## North Star

A high-school student should be able to complete one AI-assisted research learning loop in 20 minutes and clearly say:

1. what AI helped with;
2. what they verified;
3. what boundary they added;
4. what remains their responsibility;
5. what they will ask differently next time.

## Non-goals

- No login, multi-user SaaS, or classroom management layer.
- No external model calls in the local sandbox scaffold.
- No collection of names, school identifiers, emails, family details, account details, or raw private prompts.
- No second vertical beyond the existing trading-agent proof-bed framing.
- No trading/capital authority changes.

## Task 1: Add deterministic Student Sandbox v1 packet builder

**Objective:** Add a local-only v1 scaffold that returns a 20-minute learning loop, source checklist, reflection card, and research-study protocol.

**Files:**
- Create: `examples/student_sandbox_v1.py`
- Modify: `tests/test_nous_os.py`

**Step 1: Write failing tests**

Add tests for:

- `build_learning_loop_packet(...)` emits `version=student_sandbox_v1`.
- privacy is local-only, no external model calls, no private student data.
- redaction replaces emails with `[redacted-email]`.
- the loop totals 20 minutes and has phases: `intent`, `ai_first_pass`, `human_boundary`, `source_check`, `ai_second_pass`, `reflection`.
- AI policy is `hints_not_answers` and the packet contains no `final_answer` key/text.
- reflection prompts include: `What did AI help with?`, `What did I verify?`, `What remains my responsibility?`.
- `build_research_study_protocol()` is privacy-first and includes parent/teacher review plus success criteria.

**Step 2: Verify RED**

Run:

```bash
cd /Users/liyao/nousos/nous-os
python3 -m unittest tests.test_nous_os.BenchmarkTests.test_student_sandbox_v1_builds_20_minute_learning_loop_without_final_answer -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'student_sandbox_v1'`.

**Step 3: Implement minimal code**

Create `examples/student_sandbox_v1.py` with pure functions:

- `build_twenty_minute_loop()`
- `build_reflection_card()`
- `build_source_checklist()`
- `build_research_study_protocol()`
- `build_learning_loop_packet(research_question, student_level)`
- `run_student_sandbox_v1(...)`

Use existing `redact_demo_text`, `now_local`, and `write_json` helpers from `examples/nousos_heartbeat_demo.py`.

**Step 4: Verify GREEN**

Run the two focused v1 tests:

```bash
python3 -m unittest \
  tests.test_nous_os.BenchmarkTests.test_student_sandbox_v1_builds_20_minute_learning_loop_without_final_answer \
  tests.test_nous_os.BenchmarkTests.test_student_sandbox_v1_research_study_protocol_is_privacy_first \
  -v
```

Expected: PASS.

## Task 2: Wire v1 into harness inventory and docs

**Objective:** Make v1 discoverable as a harness surface, not just a loose example file.

**Files:**
- Modify: `docs/harness/HARNESS_INVENTORY.json`
- Modify: `docs/harness/README.md`
- Modify: `docs/harness/context-index.md`
- Modify: `tests/test_nous_os.py`

**Acceptance criteria:**

- Harness inventory includes a `student_sandbox_v1` surface pointing to `examples/student_sandbox_v1.py`.
- Harness README lists Student Sandbox v1 as the education/research learning-loop surface.
- Context index tells future agents to read the v1 plan and v1 sandbox before student-facing work.
- Tests assert `student_sandbox_v1` appears in the inventory.

## Task 3: Add a student/parent/teacher trial guide

**Objective:** Create a human-readable protocol for one 20-minute trial session.

**Files:**
- Create: `docs/student-sandbox-v1-trial-guide.md`
- Modify: `README.md` or `docs/education-research-narrative.md` if a lightweight public link is warranted.
- Test: `tests/test_nous_os.py`

**Acceptance criteria:**

The guide includes:

- before-session setup;
- student prompt script;
- allowed source checklist;
- privacy language;
- parent/teacher observation questions;
- after-session reflection;
- explicit statement that AI supplies hints, not final answers.

## Task 4: Emit a v1 research observation artifact

**Objective:** Make the v1 run command produce a structured observation artifact that is safe to review.

**Files:**
- Modify: `examples/student_sandbox_v1.py`
- Test: `tests/test_nous_os.py`

**Acceptance criteria:**

- CLI command writes `examples/runtime/research-records/student-sandbox-v1-latest.json`.
- Artifact includes version, generated_at, privacy block, loop phases, source checklist, reflection card, research_study protocol, and artifact_path.
- Artifact does not store raw private student data.

## Task 5: Obsidian mirror and review packet

**Objective:** Keep NOUS OS coordination visible in the user's Obsidian workspace.

**Files:**
- Create/Update: `/Users/liyao/Documents/nousos/NousOS/03 Development Plans/Student Sandbox + Research Study v1 Plan.md`
- Later create: `/Users/liyao/Documents/nousos/NousOS/04 Reviews/Student Sandbox v1 Trial Review - <date>.md`

**Acceptance criteria:**

- Mirror states repo plan is source of truth.
- Mirror includes North Star, non-goals, current scaffold status, and next tasks.
- Review packet template captures what the student understood, what confused them, what AI helped with, what was verified, and next-run change.

## Verification

Use standard NOUS OS verification:

```bash
cd /Users/liyao/nousos/nous-os
python3 -m unittest discover -s tests -v
python3 scripts/check_harness_inventory.py --json
```

If a command generates runtime JSON churn, either commit it intentionally as part of the artifact contract or restore it before finalizing.

## Current progress

Started 2026-05-16.

Completed initial scaffold:

- `examples/student_sandbox_v1.py`
- focused tests for 20-minute loop and privacy-first research protocol
- stable runtime artifact contract test for `student-sandbox-v1-latest.json`
- harness inventory/docs wiring for `student_sandbox_v1`
- `docs/student-sandbox-v1-trial-guide.md`
- `docs/student-sandbox-v1-review-template.md`

Remaining follow-up:

- Run the first real/student-adjacent 20-minute trial
- Fill a dated review packet from `docs/student-sandbox-v1-review-template.md` into Obsidian `04 Reviews/`
- Use the review to decide whether v1 needs prompt simplification, source-check simplification, or timing changes
