# Research-to-Product Gate

This gate prevents the Research Line from becoming inspirational writing with no product discipline, or from turning a single anecdote into overbuilt software.

Use this gate before changing Student Sandbox protocol, NOUS Guide behavior, review templates, metrics, memory rules, or public research claims based on research evidence.

## Required Fields

Every research-driven product change must name:

| Field | Requirement |
|---|---|
| Evidence | Link to a preregistration, review packet, session-review-index row, inbound note, or L3 synthesis. |
| Claim | One narrow claim the evidence supports. No broad causal claims at N <= 5. |
| Product implication | The exact protocol, UI, prompt, review, metric, or memory rule to change. |
| Human-agency risk | How the change could reduce student judgment, privacy, source verification, or responsibility. |
| Test / contract | The automated or manual check that prevents regression. |
| Scope limit | One focused change. No platform expansion bundled into the same change. |

## Gate Template

```markdown
## Research-to-product gate · <short title>

- Evidence:
- Claim:
- Product implication:
- Human-agency risk:
- Test / contract:
- Scope limit:
- Decision: accept / defer / reject
- Owner:
- Date:
```

## Acceptance Rules

- A failed or inconclusive prediction can still produce a product change, but the change must be framed as a response to failure, not as validation.
- Dry-runs may improve wording or usability, but cannot validate research claims.
- A single session can justify one focused next-run change, not a system rewrite.
- L1 inbound notes can inspire hypotheses, but cannot change product behavior without a gate.
- L2/L3 synthesis can propose changes, but each implementation still names the exact evidence and test.
- No gate may authorize production student data collection, grading, multi-user SaaS packaging, or final-answer generation.

## Current First Use

The first expected use is after Student Sandbox N=1:

```text
preregistration -> session review packet -> session-review-index row -> one next-run change -> product patch + test
```

Until that chain exists, Student Sandbox product changes should be limited to trial readiness and usability friction.
