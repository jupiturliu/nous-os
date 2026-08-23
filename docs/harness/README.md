# NOUS OS Harness Engineering

Harness Engineering is the NOUS OS control layer for making education/research-oriented agentic work reproducible, bounded, testable, and reviewable.

It combines:

```text
context index + boundary map + artifact contracts + evaluator specs + release gates + evidence write-back
```

## Scope

This harness covers the standalone `nous-os` repo and its cross-repo release surface across `trustmem`, `synapse`, `hermes-agent`, and `trading-agent`.

The first vertical proof bed remains Trading Brain / `trading-agent`; live trading state and capital authority remain outside NOUS OS harness authority.

## Skill-first / Harness-second Operating Principle

NOUS OS should not turn every agent workflow into software immediately. The preferred maturation path is:

```text
exploratory agent work
  -> skill/playbook sedimentation
  -> repeated-session evidence
  -> deterministic artifact contract / script / test
  -> harness gate and Obsidian review packet
```

Use this split:

| Layer | Purpose | Good candidates |
|---|---|---|
| Skill | Preserve evolving judgment, coaching moves, exception handling, and anti-sycophancy heuristics | research synthesis, student facilitation, boundary coaching, memory review, post-session interpretation |
| Deterministic workflow | Standardize stable, repeated, machine-checkable scaffolding | folder creation, required note sections, source-card schema, redaction, completeness states, review packet generation |
| Harness/eval | Detect drift and enforce minimum contracts | no-final-answer invariant, privacy fields absent, source cards present, reflection complete, memory candidate provenance |

Rule of thumb: if the question is “what is good judgment in this context?”, keep it in a skill. If the question is “what must always be generated, checked, or stored?”, make it deterministic. If the question is “did this meet the minimum bar?”, make it a harness/eval.

## Boundary

NOUS OS harness checks are read-only unless a human explicitly asks for a scoped repo edit.

Forbidden by default:

- broker/order/fill mutation
- risk config mutation
- live queue mutation
- secrets disclosure or credential edits
- treating Obsidian notes as runtime truth
- treating synthetic demo scores as production evaluator truth

## Current Harness Surfaces

| Surface | Path | Purpose |
|---|---|---|
| Harness inventory | `docs/harness/HARNESS_INVENTORY.json` | Machine-readable list of harness surfaces, boundaries, artifacts, and verification commands |
| Context index | `docs/harness/context-index.md` | What agents should read before NOUS OS work |
| North Star roadmap | `docs/north-star-v2-roadmap.md` | Product direction and explicit deferrals |
| Domain evaluator interface | `docs/domain-evaluator-interface.md` | CLS v2 evaluator contract |
| Trading evaluator | `examples/runtime/trading_evaluator.py` | Read-only first vertical adapter from trading-agent proof artifacts to CLS v2 components |
| Cross-repo release gate | `docs/cross-repo-release-gate.md` | Read-only readiness check across NOUS OS repos |
| Public release smoke docs | `docs/getting-started.md`, `docs/heartbeat-demo.md` | Demo/release verification path |
| Student Sandbox v1 | `examples/student_sandbox_v1.py` | Local-only 20-minute high-school research learning loop + privacy-first study protocol |
| Handoffs | `docs/harness/handoffs/` | Cross-agent pickup notes (Claude ↔ Codex) |
| Agent Harness responsibility map | `docs/harness/agent-harness-responsibility-map.md` | External benchmark checklist mapping production Agent Harness responsibilities to NOUS OS harness surfaces |
| Domain compilation prototype | `docs/harness/domain-compilation-contract-map.md`, `scripts/check_domain_compilation_contract.py` | Narrow SpecIR/TargetDescription/PlatformConfig/VerificationReport contract and deterministic verifier |

## Standard Verification

```bash
cd /Users/liyao/nousos/nous-os
python3 -m unittest discover -s tests -v
python3 scripts/check_harness_inventory.py --json
python3 scripts/check_cross_repo_release_gate.py --workspace /Users/liyao/nousos --json
```

Use `--run-tests` on the release gate only when the operator wants slower cross-repo validation.

## Obsidian Mirror

Human-readable coordination lives at:

```text
/Users/liyao/Documents/nousos/NousOS/02 Harness Engineering/NOUS OS Harness Engineering Playbook.md
```

Repo docs are source-of-truth for commands, contracts, and tests. Obsidian is the coordination and review surface.
