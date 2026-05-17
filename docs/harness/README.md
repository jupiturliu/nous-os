# NOUS OS Harness Engineering

Harness Engineering is the NOUS OS control layer for making education/research-oriented agentic work reproducible, bounded, testable, and reviewable.

It combines:

```text
context index + boundary map + artifact contracts + evaluator specs + release gates + evidence write-back
```

## Scope

This harness covers the standalone `nous-os` repo and its cross-repo release surface across `trustmem`, `synapse`, `hermes-agent`, and `trading-agent`.

The first vertical proof bed remains Trading Brain / `trading-agent`; live trading state and capital authority remain outside NOUS OS harness authority.

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
| Context index | `docs/harness/context-index.md` | What agents should read before NOUS OS work |
| North Star roadmap | `docs/north-star-v2-roadmap.md` | Product direction and explicit deferrals |
| Domain evaluator interface | `docs/domain-evaluator-interface.md` | CLS v2 evaluator contract |
| Cross-repo release gate | `docs/cross-repo-release-gate.md` | Read-only readiness check across NOUS OS repos |
| Public release smoke docs | `docs/getting-started.md`, `docs/heartbeat-demo.md` | Demo/release verification path |
| Handoffs | `docs/harness/handoffs/` | Cross-agent pickup notes (Claude ↔ Codex) |

## Standard Verification

```bash
cd /Users/liyao/nousos/nous-os
python3 -m unittest discover -s tests -v
python3 scripts/check_cross_repo_release_gate.py --workspace /Users/liyao/nousos --json
```

Use `--run-tests` on the release gate only when the operator wants slower cross-repo validation.

## Obsidian Mirror

Human-readable coordination lives at:

```text
/Users/liyao/Documents/nousos/NousOS/02 Harness Engineering/NOUS OS Harness Engineering Playbook.md
```

Repo docs are source-of-truth for commands, contracts, and tests. Obsidian is the coordination and review surface.
