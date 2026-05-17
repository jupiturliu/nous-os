# Domain Evaluator Interface

Domain evaluators convert domain-specific outcomes into NOUS OS CLS v2 components. They are scoring adapters, not authority adapters.

## Interface

```text
DomainEvaluator.evaluate(run_context, outcome_artifacts) -> CLSComponents
```

The runtime side lives in `examples/runtime/domain_evaluator.py`. New
domain evaluators should import `DomainEvaluator` (a runtime-checkable
`Protocol`) and `validate_cls_components()` from that module so contract
drift fails fast at the import and test boundary rather than at first
production use.

`run_context` should include the run id, domain, task type, memory inputs, human corrections, execution mode, and boundary policy.

`outcome_artifacts` should include immutable references to evidence: logs, review packets, result records, scorecards, replay outputs, or domain runtime ledgers.

## CLSComponents

```json
{
  "outcome_quality_delta": 0.0,
  "correction_absorption": 0.0,
  "memory_reuse_precision": 0.0,
  "repeatability_gain": 0.0,
  "boundary_integrity": 1.0,
  "human_agency_preservation": 1.0,
  "evidence_refs": []
}
```

All numeric fields are expected to be in `[0.0, 1.0]` for public reporting. A domain may keep richer raw metrics alongside the normalized values, but the normalized CLS v2 fields must remain comparable across domains.

## Component Semantics

| Component | Meaning |
|-----------|---------|
| `outcome_quality_delta` | Treatment run improved real outcome quality versus baseline, normalized for the domain |
| `correction_absorption` | Human correction changed later behavior, not just a log entry |
| `memory_reuse_precision` | Retrieved memory was relevant and useful, not merely present |
| `repeatability_gain` | Similar future work became more stable, faster, or lower-friction |
| `boundary_integrity` | Irreversible domain boundaries stayed intact |
| `human_agency_preservation` | The system strengthened human judgment instead of inducing blind automation |
| `evidence_refs` | Stable references proving the score, without embedding secrets or live state |

## Authority Boundary

A domain evaluator can score outcomes and cite evidence. It cannot authorize actions.

For Trading Brain, this means the evaluator must not buy, sell, execute, approve, place orders, cancel orders, change risk config, promote live, or mutate broker/runtime state. Those remain under the existing domain runtime and human approval boundaries.

## Demo vs Production

The NOUS OS heartbeat demo uses synthetic quality scores to make the loop visible. Production domains must replace those scores with domain evaluators tied to outcome artifacts.
