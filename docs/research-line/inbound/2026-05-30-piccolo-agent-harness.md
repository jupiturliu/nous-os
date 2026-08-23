---
title: "How to Build Your Own Agent Harness"
authors: Mike Piccolo; signal surfaced by meng shao
year: 2026
venue: ii.dev / X article thread
kind: essay
status: note-written
captured: 2026-05-30
anchor_bucket: 6 · Individual essays & podcasts
source_url: https://x.com/shao__meng/status/2060539774134558969
article_url_observed: https://ii.dev/blog/how-to-build-your-own-agent-harness
access_state: partial-from-x-post-and-image; direct article fetch timed out 2026-05-30
---

# 2026-05-30 · Piccolo / meng shao — Agent Harness

## What it is

A practitioner seed on building a production-grade **Agent Harness**. The X post frames the problem as: production harnesses are not solved by simply picking LangChain / LangGraph / an SDK; a production harness must own a set of operational responsibilities and package each responsibility as installable, versioned, language-swappable workers. The visible image summarizes a 15-responsibility harness model, including turn execution, sandboxing, token accounting, approval policy, traces, session state, UI events, and Otel observability.

Source access note: the direct `ii.dev` article URL timed out from this environment, so this note is based on the public X post text and the attached image only. Treat as `scanned+note-written from partial source`, not a full article review.

## Why it matters for our line

This is directly relevant to NOUS OS because it describes the same missing middle layer we call **Harness Engineering**: not the model, not the app UI, but the boundary / worker / turn / policy / trace layer that makes an AI system safe enough to operate repeatedly. It gives an external vocabulary for why NOUS OS cannot be just prompts, a chatbot, or a framework wrapper.

## Where we share

- **Harness is a product surface, not a library choice.** The seed explicitly argues that production agent systems require responsibility decomposition beyond LangChain / LangGraph / SDK selection. This matches NOUS OS's `context index + boundary map + artifact contracts + evaluator specs + release gates + evidence write-back` framing.
- **Turn-level execution matters.** The image separates `turn-orchestrator`, `harness`, `approval-gate`, `provider`, and `llm-budget`, matching our view that the unit of safety is the turn/session loop, not a single model call.
- **Fail-closed / approval gate.** The pictured harness uses policy allow / deny / needs_approval and timeout-to-deny behavior. This is the same philosophy as NOUS OS's human-boundary and Trading Brain's no-live-promotion gate.
- **Observability is core.** Trace / logs / Otel are treated as first-class responsibilities, aligning with our release-gate and evidence-writeback stance.
- **Workers should be replaceable.** The post's installable/versioned/language-swappable worker idea maps well to NOUS OS lanes: source card extraction, evaluator contracts, boundary checks, reflection cards, release gates, etc.

## Where we differ / what we add

| External anchor | NOUS OS |
|---|---|
| Frames the harness mainly as production agent infrastructure. | Frames harness as human-AI co-evolution infrastructure: the harness must preserve and measure human capability, not merely complete tasks. |
| Emphasizes operational responsibilities such as FSM, stream, token, sandbox, trace. | Adds human-boundary integrity, source-check behavior, reflection evidence, and capability-without-AI delta. |
| Worker decomposition is primarily an engineering modularity concern. | Worker decomposition is also a research-method concern: each worker should leave inspectable evidence for later synthesis. |
| Success likely means reliable production execution. | Success means reliable execution **plus** measurable improvement in human judgment/capability and no boundary drift. |

The key delta: **Piccolo's harness makes agents production-safe; NOUS OS uses harness engineering to make human-AI loops evolution-safe.**

## What this changes in our practice

- Add this as an external harness benchmark in the NOUS OS Research Line atlas.
- Use the 15-responsibility list as a checklist against NOUS OS harness docs, especially around FSM, token accounting, sandboxing, session partitioning, and observability.
- Strengthen our vocabulary: "Harness 不做安替，而是系统必须为 Agent 完成的 Job 集合；每项 Job 都应该可插拔、可测试、可审计。"
- Do **not** copy the worker list blindly into NOUS OS. First map each responsibility to one of: already covered / missing deterministic workflow / missing evaluator / out of scope for student sandbox.
- Outcome: the useful responsibility vocabulary was absorbed into `docs/harness/README.md`; no separate benchmark map is maintained.

## Limitations of this work (from our perspective)

- Source is partial: article body was not fetched; this note relies on public X text and image.
- The visible material is an architecture checklist, not empirical evidence that a harness improves human capability.
- The framing appears agent-production oriented; it may not include educational / cognitive-growth metrics.
- The worker abstraction can create false comfort if it lacks outcome checks and human review evidence.
- No ticker / investment actionability; this is an architecture reference, not a capital signal.

## Open questions for follow-up

- What are the exact 15 responsibilities in the article body, and do they differ from the image summary?
- Which of the 15 are already covered by NOUS OS harness docs and which are missing?
- Should NOUS OS define a machine-readable `HarnessResponsibilityV1` contract for each lane?
- Can Trading Brain's self-improvement contracts be re-described as harness workers: proposal worker, shadow-apply worker, outcome-check worker?
- What is the minimal harness responsibility set for a student sandbox versus a trading COO proof loop?

## Citation

Piccolo, Mike. (2026). *How to Build Your Own Agent Harness*. ii.dev. Public signal surfaced by meng shao on X: https://x.com/shao__meng/status/2060539774134558969
