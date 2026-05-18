# Research Line Session Review Index

This index is the de-identified ledger of Student Sandbox and other NOUS OS research-line session reviews.

It is not the raw data store. Raw or human-readable review packets may live in Obsidian `NousOS/04 Reviews/`. This file tracks only the minimum public evidence pointers needed for the research line to count sessions, find the latest review, and decide the next product change.

## Counting Rules

- Count only sessions that have a pre-registration id and a de-identified review packet.
- Keep `N` explicit. Do not write "students tend to..." while `real_session_count <= 5`.
- Dry-runs and AI-simulated audits are useful, but they do not increment `real_session_count`.
- A review packet must not include student name, school, teacher name, email, phone, address, family details, or raw private prompt text.
- Every accepted product/protocol change must point to `next_run_change` from a review packet or to an L3 synthesis.

## Current Counts

| Metric | Count | Notes |
|---|---:|---|
| Real Student Sandbox sessions | 0 | No real/student-adjacent trial has been completed yet. |
| Student-adjacent sessions | 0 | Count here only when a real human participant completes the 20-minute loop. |
| AI-simulated dry-runs | 1 | Obsidian dry-run audit exists; it does not close Phase B. |
| Published de-identified review packets | 0 | First packet should be added after N=1. |
| Open next-run changes | 0 | Do not select one until the first real review packet exists. |

## Session Ledger

| Session id | Date | Type | Preregistration | Review packet | Prediction result | Next-run change | Public? |
|---|---|---|---|---|---|---|---|
| _pending-n1_ | TBD | real / student-adjacent | `docs/research-line/preregistration/<session-id>.md` | Obsidian `04 Reviews/<date> Student Sandbox v1 Trial Review.md` plus de-identified repo note when safe | TBD | TBD | no |

## Latest Review

- Latest real review: none yet.
- Latest dry-run: `2026-05-16 Student Sandbox v1 AI-Simulated Dry-Run Audit` in Obsidian.
- Next planned trial: first Student Sandbox v1 real or student-adjacent 20-minute session.
- Current open question: can the student explain what AI helped with, what they verified, and what remains human responsibility after the loop?

## Update Procedure

After a session:

1. Export the Markdown packet from `demo/student-session-review.html`.
2. Save the full de-identified packet in Obsidian `NousOS/04 Reviews/`.
3. Add or update one row in the ledger above.
4. Link the preregistration file and review packet.
5. Mark the prediction as `confirmed`, `partial`, `disconfirmed`, or `inconclusive`.
6. Add exactly one `next_run_change` only if the review evidence supports it.
7. If the product should change, open a separate change using `docs/research-line/research-to-product-gate.md`.

## Publication Rule

The website can display counts and latest-status summaries from this index. It should not expose raw student text. If a de-identified packet is safe to publish, add it as a reviewed research note and link it from the ledger.
