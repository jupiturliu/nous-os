# First Vertical Proof Bed Wiring Plan v0

> **Sprint name:** NOUS OS First Vertical Proof Bed Wiring v0
> **For Claude + Codex:** Build read-only TradingEvaluator that maps existing trading-agent proof artifacts to CLS v2 components, so `trading_vertical` demo mode is grounded in evidence rather than synthetic scores. Hermes is not an executor for this plan.

## Why this sprint

`docs/domain-evaluator-interface.md` defines `DomainEvaluator.evaluate(run_context, outcome_artifacts) -> CLSComponents` and explicitly says "Production domains must replace synthetic scores with domain evaluators tied to outcome artifacts." The `trading_vertical` demo mode advertises trading-agent as the first vertical research proof bed. But today:

- trading-agent has **zero references** to `DomainEvaluator` / `CLSComponents` / `cls_v2`
- `trading_vertical` demo mode emits the same synthetic `0.665` cls_v2 score as `student` mode — only labels differ
- trading-agent already produces rich proof artifacts (`promotion_reviews/proof_packs/*.json`, `market_proof/baseline_comparisons.jsonl`, `market_proof/forecast_resolutions.jsonl`, `market_proof/forecast_ledger_summary.json`) that map naturally to CLS v2 components

`docs/second-vertical-entry-criteria.md` lists 6 unlock conditions. This sprint directly advances:

- **#2** "At least three outcome artifacts flow into LearningUpdate examples or equivalent reviewed artifacts" — TradingEvaluator consumes the existing artifacts and emits stable evidence_refs
- **#3** "CLS v2 calculator and docs are stable" — first real domain implementation validates the contract

## Boundary (strict)

Per `docs/harness/README.md` and `docs/domain-evaluator-interface.md` "Authority Boundary" section:

- **Pure read.** No write handles anywhere in `trading-agent/`.
- **No mutation** of broker / order / fill / risk / live-queue / promotion / runtime state.
- **No imports** of trading-agent modules. Only filesystem access to data artifacts.
- **No secrets** in evidence_refs — paths and file basenames only.
- **No live trading authority claims.** Evaluator returns scores; it does not authorize anything.
- The evaluator stays in `nous-os`. **`trading-agent` is not modified** in this sprint.

## Architecture

```text
nous-os/examples/runtime/trading_evaluator.py    # sibling of cls_v2.py
  reads ->  <workspace>/trading-agent/data/users/<username>/market_proof/*.{json,jsonl}
            <workspace>/trading-agent/data/users/<username>/promotion_reviews/proof_packs/*.json
  emits ->  CLSComponents (per docs/domain-evaluator-interface.md schema)
```

Lives in `examples/runtime/` to match the existing pattern (`cls_v2.py`, `episode_logger_local.py`). Workspace root is configurable (default: walk up from nous-os to find a sibling `trading-agent/`, mirroring `scripts/check_cross_repo_release_gate.py --workspace` pattern).

## CLS v2 mapping

| Component | Real source | Implementation |
|---|---|---|
| `boundary_integrity` | every artifact's `execution_boundary` block | fraction of artifacts where `broker_action_allowed=false AND creates_order_or_draft=false AND creates_promotion_or_approval=false AND mutates_runtime_live_state=false AND production_config_changed=false`. 1.0 = all clean. |
| `human_agency_preservation` | `proof_packs[*].capital_action_authorized` | fraction equal to `false`. Anything authorizing capital action drops the score. |
| `outcome_quality_delta` | `baseline_comparisons.jsonl[*].outperformed_benchmark` | rate of `true` over resolved (non-`neutral_no_entry`) comparisons. |
| `repeatability_gain` | `forecast_ledger_summary.brier_improvement_over_baseline` | clamp to `[0, 1]` (negative → 0; cap at 1.0). |
| `correction_absorption` | proof_pack `human_review_state` distribution over time | deferred to a later slice — return `0.0` with `evidence_refs: ["pending:correction_absorption_design"]` |
| `memory_reuse_precision` | proof_pack `validated_claims` + `source_provenance` reuse rate | deferred — same pending marker |

The two `pending` markers are deliberate per `[[feedback_ground_truth_first_principle]]` — surface "not yet implemented" explicitly, do not paper over with 1.0 defaults.

## Slices

### Slice 1 — Skeleton + boundary signals (highest signal-to-noise first)

Files:
- `examples/runtime/trading_evaluator.py` (new — sibling of cls_v2.py)
- `tests/test_trading_evaluator.py` (new)
- `tests/fixtures/trading_evaluator/` (new — synthetic proof_packs + market_proof)

Implement:
- `TradingEvaluator(workspace, username)` class
- `.evaluate(run_context, outcome_artifacts=None) -> dict` returning all 6 CLS v2 fields + `evidence_refs`
- `boundary_integrity` and `human_agency_preservation` from real data shape
- 4 other components return `0.0` with explicit `evidence_refs` pending marker
- Synthetic fixture under `tests/fixtures/trading_evaluator/` so the test does NOT depend on real trading-agent state being populated

Acceptance:
- contract test green: schema matches `docs/domain-evaluator-interface.md` CLSComponents shape
- contract test green: when fixture contains one proof_pack with `capital_action_authorized=true`, `human_agency_preservation` drops below 1.0
- contract test green: when fixture contains one artifact with `broker_action_allowed=true`, `boundary_integrity` drops below 1.0
- contract test green: evaluator opens no write handles (use `unittest.mock` on `open` to assert mode is read-only)

### Slice 2 — Outcome + repeatability mappings

Files:
- `nous_os/evaluators/trading_evaluator.py` (extend)
- `tests/test_trading_evaluator.py` (extend)
- `tests/fixtures/trading_evaluator/` (extend)

Implement:
- `outcome_quality_delta` from `baseline_comparisons.jsonl`
- `repeatability_gain` from `forecast_ledger_summary.json`

Acceptance:
- contract test green: fixture with 8/10 `outperformed_benchmark=true` (excluding `neutral_no_entry`) gives `outcome_quality_delta ≈ 0.8`
- contract test green: `brier_improvement_over_baseline = 0.05` → `repeatability_gain = 0.05`; negative improvement → `0.0`; >1.0 capped to `1.0`

### Slice 3 — Wire into trading_vertical demo mode

Files:
- `examples/nousos_heartbeat_demo.py` (modify `build_benchmark()` path)
- `examples/runtime/dashboard-data.json` (regenerated)
- `tests/test_nous_os.py` (extend contract tests)

Implement:
- When `demo_mode=trading_vertical` AND the trading-agent workspace exists with at least one user directory containing real artifacts → benchmark CLS v2 routed through `TradingEvaluator`
- Otherwise fall back to synthetic, but emit `evidence_source: "synthetic_demo_fallback"` AND a visible reason (`"trading-agent workspace not found at <path>"` or `"no user directory has populated market_proof"`)
- Per `[[feedback_ground_truth_first_principle]]`: never silently substitute; the dashboard must show "synthetic" vs "evidence-backed" clearly

Acceptance:
- contract test green: with a fixture trading-agent workspace, `dashboard-data.json["benchmark"]["evidence_source"] == "trading_evaluator"` and `["benchmark"]["cls_v2"]["evidence_refs"]` contains stable file pointers
- contract test green: without trading-agent workspace, `evidence_source == "synthetic_demo_fallback"` and `fallback_reason` is non-empty
- contract test green: `student` and `research_lab` modes remain synthetic (the interface doc only commits trading-agent to a real evaluator)

## Verification

```bash
cd /Users/liyao/nousos/nous-os
python3 -m unittest discover -s tests -v
python3 scripts/run_nous_heartbeat.py  # spot-check default student mode
python3 -c "from examples.nousos_heartbeat_demo import run_heartbeat_flow; import json; print(json.dumps(run_heartbeat_flow(demo_mode='trading_vertical')['benchmark']['cls_v2'], indent=2))"
python3 scripts/check_cross_repo_release_gate.py --workspace /Users/liyao/nousos --json
```

## Out of scope (do not expand this sprint)

- Writing back into trading-agent
- Adding any UI on the trading-agent side
- Implementing `correction_absorption` or `memory_reuse_precision` (deferred with explicit pending markers)
- Release-gate allowlist (separate sprint — see "Open follow-on" below)
- README reproducibility smoke test (separate)
- Phase 4 student sandbox / Phase 5 review protocol (queued, separate)

## Open follow-on after this sprint

Two adjacent items that become more valuable once this sprint lands:

1. **Release gate allowlist** for `trustmem/knowledge/distilled/**` and trading-agent WIP, so `ok=true` is achievable and entry criterion #4 becomes meaningful.
2. **`correction_absorption` design** using proof_pack `human_review_state` time-series. Needs a separate small design doc before implementation.

## Definition of Done

- All three slices have green contract tests
- `trading_vertical` demo mode produces benchmark scores that change when real trading-agent artifacts change
- `evidence_refs` in the dashboard snapshot point to stable trading-agent artifact paths (no secrets, no live state)
- `docs/second-vertical-entry-criteria.md` is updated to mark #2 and #3 as advanced with citation to this evaluator
- A 4-line summary note added to Obsidian `02 Harness Engineering/` describing the new evaluator surface
