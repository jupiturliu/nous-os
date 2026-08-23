# Student Sandbox Deterministic Workflow

This document defines the product protocol behind Student Sandbox v1. It is the stable workflow that the web UI, backend, NOUS Guide, Claude handoffs, and future agent skills must follow.

The preference is **skill-first, harness-second**:

1. Capture exploratory agent judgment as skills while the co-evolution protocol is still being learned.
2. Observe which steps repeat across real sessions.
3. Promote stable, high-frequency, machine-checkable steps into deterministic software workflow, tests, and harness gates.
4. Keep agents operating inside the deterministic protocol once the protocol exists.

The reason is practical and philosophical: NOUS OS is still discovering what good human-AI co-evolution looks like, so early hard-coding can freeze the wrong behavior. But students, parents, and teachers still need a predictable session. Therefore skills preserve evolving judgment, while deterministic workflow preserves structure, privacy boundary, source check, evidence capture, and human responsibility.

A useful split:

- **Skill** answers: in this situation, what is a good judgment, challenge, coaching move, or exception handling path?
- **Deterministic workflow** answers: what must always be generated, checked, redacted, stored, and reviewed?
- **Harness/eval** answers: did the artifact meet the minimum contract, and can drift be detected?

## Workflow State Machine

| State | Required human action | AI may help with | Deterministic artifact |
|---|---|---|---|
| `intent` | Student writes the research question in their own words. | Clarify subquestions and vocabulary. | `worksheet.intent` |
| `ai_first_pass` | Student asks for a plan, not a final answer. | Produce a learning plan and source suggestions. | NOUS Guide first pass / prompt card |
| `human_boundary` | Student chooses what remains human controlled. | Restate the boundary and adapt the plan. | `worksheet.boundary` |
| `source_check` | Student inspects at least two sources. | Ask source-quality questions and surface uncertainty. | `source_cards[]` |
| `ai_second_pass` | Student revises the plan using evidence and boundary. | Critique gaps and propose next steps. | NOUS Guide second pass / prompt card |
| `reflection` | Student records what AI helped with, what was verified, and what remains their responsibility. | Compare first and second pass. | `reflection` |
| `review` | Parent/teacher/researcher reviews process evidence. | Summarize signals without private student data. | `research_signals`, `observer` |

The UI should not skip states automatically. The student decides when to run the AI helper and when to move to review.

## Product Contract

The Student Sandbox is a learning protocol, not a generic chatbot.

Required properties:

- no final-answer generation as the product promise;
- no account or login requirement for the demo;
- no raw private student identity in saved records;
- two structured source cards before review is considered complete;
- explicit human boundary before the second AI pass;
- review page for parent/teacher/research observation;
- local backend persistence for session records when the backend is available;
- deterministic `research_signals` derived from the session record.

The backend record should keep the contract machine-readable:

```json
{
  "session_id": "student-session-id",
  "worksheet": {},
  "source_cards": [],
  "reflection": {},
  "observer": {},
  "chat_turns": [],
  "research_signals": {}
}
```

`research_signals` must be derived from saved fields instead of being written by the model. This keeps analytics stable and reviewable.

## Agent Boundary

NOUS Guide, Claude, Codex, or any other agent can assist inside the protocol, but must not mutate the protocol itself during a student session.

Allowed agent behaviors:

- ask clarifying questions;
- propose source-check questions;
- point out missing evidence;
- suggest a revised plan after the human boundary is written;
- summarize process evidence for a reviewer;
- explain why a source may be weak or incomplete.

Disallowed agent behaviors:

- write the student's final assignment answer;
- infer or store private identity details;
- bypass the source-card step;
- mark a session complete without reflection;
- override the student's boundary;
- convert a demo session into a production student-data system.

## Skills Layer

Skills sit above this deterministic workflow. They are the first home for evolving agent judgment and the long-term home for exception handling, coaching style, challenge heuristics, and review interpretation.

Use skills before software when the workflow is still exploratory. Promote from skills into deterministic software only when the step is:

1. repeated across multiple real or dry-run sessions;
2. low-discretion enough to encode as a field, state, check, or script;
3. valuable to verify automatically;
4. safe to standardize without suppressing human agency.

Candidate skills:

| Skill | Purpose | Input | Output |
|---|---|---|---|
| `student-session-review` | Review one saved session for parent/teacher/research notes. | saved session record | review summary + next-run change |
| `source-quality-review` | Inspect source cards and ask better verification questions. | `source_cards[]` | source risk notes |
| `human-ai-boundary-coach` | Help a student express what remains human responsibility. | research topic + draft boundary | stronger boundary wording |
| `research-insight-summarizer` | Aggregate safe signals across sessions. | redacted session summaries | research observations |

These skills should read the deterministic artifacts rather than scraping page text. If a skill needs a new field, add the field to the software protocol and tests first.

## Current Implementation

Current web surfaces:

- `demo/student-sandbox-v1.html` - student workflow, source cards, observer notes, NOUS Guide, save flow.
- `demo/student-session-review.html` - latest or selected session review page.
- `demo/student-sandbox-v1-guide.html` - student/parent explanation page.

Current backend contract:

- `POST /api/student-sandbox-session` saves a redacted local session record.
- `GET /api/student-sandbox-session?session_id=<id>` returns one saved session.
- `GET /api/student-sandbox-session?list=1&limit=20` returns recent saved sessions.

Current research signal examples:

- `source_cards_total`
- `source_cards_complete`
- `accepted_sources`
- `reflection_fields_complete`
- `chat_turns_total`
- `has_human_boundary`
- `has_revised_plan`
- `observer_check_count`

## Next Hardening

High-value next steps:

1. Add a visible session list for parents/teachers so review does not require a copied session id.
2. Add deterministic completeness states in the UI: ready for first pass, ready for second pass, ready for review.
3. Add an exportable review packet that omits private fields by construction.
4. Promote stable agent review patterns into formal skills after several real sessions.
5. Keep the backend local-first; production deployment should use Redis or SQLite rather than memory-only state.
