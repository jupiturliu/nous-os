# Agent Harness Responsibility Map — External Seed vs NOUS OS

Captured: 2026-05-30  
Source seed: Mike Piccolo / ii.dev, surfaced via meng shao X post  
Source URL: https://x.com/shao__meng/status/2060539774134558969  
Inbound note: `docs/research-line/inbound/2026-05-30-piccolo-agent-harness.md`

## Source-status caveat

The direct ii.dev article fetch timed out during capture. This map is therefore based on the visible X post text and attached image, not the full article body. Treat the external responsibility names as a first-pass checklist to refresh after full-source access.

## NOUS OS interpretation

Piccolo's visible thesis: production-grade Agent Harness is not a framework choice; it is a set of installable, versioned, language-swappable workers that own turn orchestration, policy, approval, budget, trace, sandbox, and session semantics.

NOUS OS extension:

```text
production-safe agent harness
  + human-boundary integrity
  + source/evidence discipline
  + reflection and learning evidence
  + capability-without-AI delta
  + result-proof loop
= evolution-safe human-AI harness
```

## Responsibility map

| External harness responsibility | NOUS OS equivalent surface | Current status | Evidence artifact | Verification / next check | Human-boundary relevance | Result-proof relevance |
|---|---|---|---|---|---|---|
| Worker packaging / versioning | Skill-first → deterministic workflow → harness gate maturation path | partial | `docs/harness/README.md`; Obsidian Harness Playbook | Add explicit worker lifecycle contract if repeated lanes emerge | medium | medium |
| Turn protocol | Student Sandbox 6-phase loop; trading proof loop turn/session artifacts | partial | `examples/student_sandbox_v1.py`; `docs/domain-evaluator-interface.md` | Define `TurnArtifactV1` only after repeated evidence | high | high |
| Turn FSM | Student Sandbox phase progression; Trading Brain proof-loop state | partial | `examples/student_sandbox_v1.py`; trading-agent proof artifacts | Consider deterministic FSM check for sandbox sessions | high | high |
| Provider abstraction | Out of scope for NOUS OS repo; owned by runtime clients such as Hermes / external AI tools | out-of-scope | `docs/harness/README.md` boundary | Keep provider details out unless needed for reproducible trial | low | low |
| Prompt / system prompt management | Skills, playbooks, templates, evaluator instructions | partial | Obsidian playbooks; docs templates | Keep judgment in skills, stable required sections in deterministic workflows | high | medium |
| Tool hooks | Hermes tools / external agent tools, but NOUS OS repo mainly documents boundaries | partial | `docs/harness/context-index.md` | Tool-use truth belongs in runtime harness docs, not research-line claims | high | medium |
| Approval gate | Human boundary phase; Trading Brain human approval before capital action | covered in principle | `docs/harness/README.md`; Trading Brain gates | Continue fail-closed default; no live mutation from NOUS OS harness | very high | high |
| Policy allow / deny / needs-approval | Boundary map and release gates | covered in principle | `docs/harness/README.md`; `docs/cross-repo-release-gate.md` | Add explicit policy vocabulary to future contracts if needed | very high | high |
| Timeout / fail-closed behavior | Human-boundary and capital/runtime mutation prohibition | partial | `docs/harness/README.md` | Make timeout-to-deny explicit for any future live workflow | very high | high |
| Token / budget accounting | Not yet central for Student Sandbox; relevant for production runtime | missing / deferred | none | Defer until cost/runtime is part of pilot | low-medium | low |
| Sandbox / environment isolation | Student Sandbox privacy-first local loop; live trading state outside authority | partial | `examples/student_sandbox_v1.py`; `docs/student-sandbox-v1-trial-guide.md` | Add explicit local-only and no-secret checks to gates if pilots expand | high | medium |
| Session partitioning | Session review / inbound capture / proof-loop artifact IDs | partial | research-line inbound notes; trading proof bundles | Define session IDs consistently across research-line and sandbox artifacts | medium | high |
| Trace / logs / observability | Release gates, evidence write-back, research-line capture | partial | `scripts/check_cross_repo_release_gate.py`; research-line artifacts | Add trace fields to future review packets only when useful | medium | high |
| UI events / stream | Student Sandbox web demo; static demos | partial / demo-only | `demo/student-sandbox-v1.html`; `demo/student-sandbox-v1-guide.html` | Not production requirement yet | medium | low |
| Otel / production telemetry | Not in NOUS OS research repo | out-of-scope / future | none | Revisit only for deployed runtime | low | medium |

## Gaps promoted from this seed

1. **Explicit responsibility vocabulary:** Current NOUS OS harness docs say `context index + boundary map + artifact contracts + evaluator specs + release gates + evidence write-back`; this map adds a more runtime-oriented checklist for future hardening.
2. **FSM clarity:** Student Sandbox has phases, but not yet a formal `TurnFSM` contract.
3. **Timeout/fail-closed language:** Boundary rules exist, but timeout-to-deny / missing-approval-to-deny should be explicit in any future live-ish workflow.
4. **Session partitioning:** Research-line notes, sandbox sessions, and trading proof loops use related but not unified session concepts.
5. **Budget/telemetry deferral:** Token/Otel style concerns are not needed for current research-line proof, but should be tracked as production-runtime gaps rather than ignored.

## Current action decision

- Architecture action: **keep as benchmark checklist**.
- Implementation action: **no immediate runtime change**.
- Research-line action: **captured as inbound note and atlas entry**.
- Trading action: **none**.
- Capital boundary: **no broker/order/risk/live-state mutation**.

## Future promotion gate

Only promote this from checklist to deterministic NOUS OS contract if at least one of the following becomes true:

1. Student Sandbox trials produce repeated session artifacts that need machine-checked FSM / turn IDs.
2. NOUS OS runtime moves from static/local demo into hosted multi-user workflow.
3. Trading Brain proof-loop contracts need a cross-domain harness vocabulary shared with NOUS OS.
4. A human operator asks for production-runtime hardening beyond research-line documentation.
