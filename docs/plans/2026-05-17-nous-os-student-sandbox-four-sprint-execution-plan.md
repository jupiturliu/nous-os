# NOUS OS Student Sandbox Four-Sprint Execution Plan

> Date: 2026-05-17
> Status: implementation track

## Scope

Focus NOUS OS development on the education/research proof bed. Do not expand into a generic platform, multi-user SaaS, second vertical, broker integration, or production student data collection.

The work advances four sprints:

1. Trial readiness.
2. First real or student-adjacent trial.
3. Evidence-based improvement.
4. Research track productization.

## Sprint 1: Trial Readiness

Goal: make the Student Sandbox usable for a parent, teacher, or researcher before the first real session.

Deliverables:

- visible session list on the review page;
- deterministic readiness states on the sandbox page;
- de-identified Markdown review packet export;
- backend session records include review readiness signals.

Acceptance:

- no browser storage;
- no raw private student identity in the export packet;
- student must click to ask NOUS Guide;
- review does not require copying a session id.

## Sprint 2: First Trial Preparation

Goal: make the system ready for one real or student-adjacent 20-minute learning loop.

Deliverables:

- public research page explains the trial status honestly;
- review packet makes the Obsidian handoff explicit;
- current status is labeled `N = 0 real student sessions` until a human trial is complete.

Acceptance:

- the product can generate the review artifact needed for `/Users/liyao/Documents/nousos/NousOS/04 Reviews/`;
- the website does not claim a completed real trial before it happens.

## Sprint 3: Evidence-Based Improvement

Goal: ensure the next product change is selected from review evidence, not speculation.

Process:

1. Run a session.
2. Export the review packet.
3. Fill the dated Obsidian review.
4. Select exactly one next-run change.
5. Implement that change with tests.

Allowed improvement classes:

- simplify prompt cards;
- simplify source cards;
- improve the review page;
- tighten NOUS Guide system prompt;
- add guided step buttons.

## Sprint 4: Research Track Productization

Goal: make research readable on the website instead of forcing reviewers through raw Markdown.

Deliverables:

- `research.html` publishes the Student Sandbox evidence loop;
- source Markdown remains available as reviewer source material;
- the site separates theory, model, metrics, trial status, and memory philosophy.

Acceptance:

- a parent, teacher, or researcher can understand the current research state from the website;
- raw Markdown is a source link, not the primary reading path;
- claims stay bounded by the actual evidence count.

## Current Non-Goals

- production student accounts;
- multi-tenant data collection;
- grading students;
- final-answer generation;
- autonomous agent marketplace;
- trading-agent feature work;
- broker, strategy, risk, or capital authority changes.
