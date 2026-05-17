# Second Vertical Entry Criteria

NOUS OS V2 should not expand into Talent Brain, coding/research workspaces, or other verticals until the first vertical proof is repeatable.

## Not Now Rationale

Trading Brain is the first vertical proof because it has hard boundaries, high-stakes decisions, measurable outcomes, and a real human review loop. Expanding before that loop closes would create more surface area without proving the operating-system claim.

Second vertical work remains deferred until all criteria below are met.

## Entry Criteria

1. Trading Brain proof loop has a reviewed experiment ledger.
2. At least three outcome artifacts flow into `LearningUpdate` examples or equivalent reviewed artifacts.
3. CLS v2 calculator and docs are stable.
4. Cross-repo release gate passes in read-only mode or has only documented, accepted dirty-state exceptions.
5. Public demo can be reproduced from README / getting-started commands.
6. Human authority boundary is tested or documented for the first vertical.

## Current Progress

- `examples/runtime/trading_evaluator.py` is the first read-only adapter from trading-agent proof artifacts to CLS v2 components.
- Mapped signals (real evidence): `boundary_integrity`, `human_agency_preservation`, `outcome_quality_delta`, `repeatability_gain`.
- Deferred signals (explicit `pending:` markers, no synthetic defaults): `correction_absorption`, `memory_reuse_precision`.
- `examples/nousos_heartbeat_demo.py` routes `trading_vertical` demo mode through the evaluator when trading-agent artifacts exist, and falls back with `evidence_source: synthetic_demo_fallback` + an explicit `fallback_reason` otherwise. Other demo modes stay synthetic.
- This advances criteria 2 and 3. Criterion 6 progress is partial (the evaluator's read-only contract and boundary-integrity check are tested; broader boundary documentation for the first vertical remains owned by trading-agent).
- Criteria 1, 4, 5 are not yet closed by this evaluator alone.

## Allowed Before Entry

- Document second-vertical ideas as deferred candidates.
- Improve generic NOUS OS interfaces that Trading Brain already uses.
- Harden release gates, evaluators, memory safety, and dashboard snapshot reproducibility.

## Not Allowed Before Entry

- New broker integration.
- New trading strategy.
- New top-level dashboard surface for another vertical.
- Multi-tenant SaaS packaging.
- Any claim that NOUS OS is production-ready across domains.
