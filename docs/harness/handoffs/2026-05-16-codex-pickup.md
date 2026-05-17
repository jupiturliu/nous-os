# Codex Handoff — 2026-05-16

**From:** Claude (harness inventory pass)
**To:** Codex (implementation continuation)
**Branch state:** clean. Latest commit `7b12ff5 Emit structured research records`.
**Plan source:** `docs/plans/2026-05-16-nous-os-next-development-plan.md`

## TL;DR

Phase 1 sprint v0 (12 tasks, lines 253-266 of the plan) is **functionally complete and committed**. All 16 contract tests pass. End-to-end runs verified for `student` / `trading_vertical` / `research_lab` demo modes. Next real work is Phase 3-5 plus a visibility audit.

## What is already done (do not redo)

| Sprint task | Evidence |
|---|---|
| 1. Demo mode schema in `nousos_heartbeat_demo.py` | `DEMO_MODES` with student / trading_vertical / research_lab, `normalize_demo_mode()` |
| 2. `human_agency` / `safety_boundaries` / `reflection` / `first_vertical` fields | Present in `examples/runtime/dashboard-data.json` and `build_dashboard_snapshot()` |
| 3. Dashboard hero + copy refresh | `demo/heartbeat-dashboard.html` rewritten in commit `2f2fb72` |
| 4. Scenario selector UI | `.mode-chip` buttons + `setMode()` POST `demo_mode` to `/run` |
| 5. Boundary panel UI | `#boundaryList` renders `snapshot.safety_boundaries` |
| 6. Human agency panel UI | renders `snapshot.human_agency` (keeps/helps_with) |
| 7. Reflection step in timeline | "Step 6 Student reflection" emitted in `build_timeline()` |
| 8. Trading Agent Research Proof explainer | `first_vertical` block + dedicated mode chip |
| 9. dashboard-data.json regenerated | up to date with full schema |
| 10. Contract tests in `tests/test_nous_os.py` | 16 tests green incl. `test_dashboard_snapshot_models_human_ai_coevolution`, `test_latest_research_record_is_published_and_private_by_default` |
| 11. `docs/heartbeat-demo.md` + `docs/demo-blueprint.md` | both updated in `2f2fb72` / `7b12ff5` |
| 12. Obsidian mirror | `02 Harness Engineering/NOUS OS Harness Engineering Playbook.md` and `03 Development Plans/NOUS OS Next Development Plan.md` present |

Mode → boundary catalog mapping confirmed by runtime probe:
- `student` → privacy / facts / learning / values
- `trading_vertical` → capital_boundary / evidence / reconciliation / no_action
- `research_lab` → rubric / reflection / repeatability / boundary

## What to pick up next

### 1. Phase 3 visibility audit (closed)

**Decided by human 2026-05-16:** the panel-level `first_vertical.not_for` line is sufficient — no headline-level disclaimer required.

Verified 2026-05-16 with Playwright against local static serving: after clicking the **Trading Agent Research Proof** chip, the active mode updates and the `first_vertical` panel renders the existing "not to recommend trades, not student investing advice, and not a commercialization endpoint" line. Phase 3 is closed.

### 2. Phase 4 Student Agent Sandbox v0 (closed)

**Decided by human 2026-05-16:** first scenario = the plan's default ("a high-school student wants help planning a research project without losing their own thinking").

Implemented as `examples/student_sandbox_v0.py`, with contract coverage in `tests/test_nous_os.py` and a machine-readable surface entry in `docs/harness/HARNESS_INVENTORY.json`. It remains local-only, does not call external models, redacts private details before record emission, and writes the compatible research record shape.

Closed constraints:
- local-only, no external student data collection;
- AI asks clarifying questions before answering;
- AI gives hints + practice instead of final answers when learning boundary is active;
- AI asks for source checks when fact boundary is active;
- AI refuses to store private details unless anonymized;
- AI ends every session with a reflection prompt;
- produces a research record (reuse `build_research_record()` plumbing — do not invent a parallel schema).

No network endpoint was added.

### 3. Phase 5 review protocol scaffolding (scaffold closed; external review remains)

**Decided by human 2026-05-16:** review entries go directly under `/Users/liyao/Documents/nousos/NousOS/04 Reviews/` — no per-audience subfolders.

Plan section "Phase 5" (lines 217-239). Completed pieces:
- repo: `docs/review-template.md` captures audience type, viewer confusion, boundary clarity, and next-run change;
- Obsidian: `/Users/liyao/Documents/nousos/NousOS/04 Reviews/NOUS OS Review Log.md` contains the internal Claude/Codex pickup review plus the 2026-05-16 Playwright visibility audit evidence.

Research records under `examples/runtime/research-records/` already exist — Phase 5 is the human-readable side, not a duplicate of the machine artifact.

Remaining Phase 5 work: run the demo with an actual student, parent, teacher, or researcher and record what they cannot explain without coaching.

## Hard boundaries (do not violate)

Per `docs/harness/README.md`:
- no broker / order / fill / risk / live-queue mutation
- no secrets or credential edits
- do not treat Obsidian notes as runtime truth
- do not treat synthetic demo scores as production evaluator truth
- trading-agent live state and capital authority are **outside** NOUS OS harness authority
- no multi-user login, SaaS onboarding, agent marketplace, second vertical, autonomous execution (Plan section "What NOT To Build Yet")

## Verification commands

```bash
cd /Users/liyao/nousos/nous-os
python3 -m unittest discover -s tests -v
python3 scripts/run_nous_heartbeat.py
python3 scripts/check_cross_repo_release_gate.py --workspace /Users/liyao/nousos --json
```

Release-gate `ok=false` on dirty/untracked is a readiness finding, not a functional failure.

## Role split reminder

- **Claude + Codex** = development executors.
- **Hermes** = architecture-design only. Do not delegate sprint tasks to Hermes despite the plan doc's "For Hermes" framing on line 3 — that framing is legacy.

## Human decisions (2026-05-16)

All three pickup-blocking questions answered — Codex can start without waiting:

1. **Phase 3 disclaimer:** panel-level line is enough. No headline-level disclaimer.
2. **Phase 4 sandbox scenario:** use the plan's default — research project planning.
3. **Phase 5 review folder:** `04 Reviews/` flat, no per-audience subfolders.
