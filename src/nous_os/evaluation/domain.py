"""Runtime-side DomainEvaluator Protocol.

The text contract lives at ``docs/domain-evaluator-interface.md``. This
module captures the runtime side so concrete evaluators (e.g.
``TradingEvaluator``) can be type-checked and contract-checked. It does
not authorize domain actions, run domain logic, or carry boundary
authority — it is a typing surface plus a single shape validator.

Future second-vertical evaluators should declare their conformance by
type-checking against ``DomainEvaluator`` and passing
``validate_cls_components()``. This avoids re-inventing the contract
(and silently drifting from it) for every domain.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


CLS_V2_COMPONENT_FIELDS: tuple[str, ...] = (
    "outcome_quality_delta",
    "correction_absorption",
    "memory_reuse_precision",
    "repeatability_gain",
    "boundary_integrity",
    "human_agency_preservation",
)
"""Canonical CLS v2 component field names per docs/domain-evaluator-interface.md."""


@runtime_checkable
class DomainEvaluator(Protocol):
    """The runtime shape every domain evaluator must satisfy.

    Per the text contract, an evaluator maps run context plus outcome
    artifacts to normalized CLS v2 components with stable evidence
    references. It must not authorize domain actions, mutate broker or
    risk config, or otherwise reach beyond its read-only scope.
    """

    def evaluate(self, run_context: dict, outcome_artifacts: dict | None = None) -> dict:
        ...


def validate_cls_components(result: dict) -> list[str]:
    """Return a list of contract violations; empty list means conformant.

    Checks the keys, value types, numeric range, and the presence of an
    ``evidence_refs`` list. Does not assess whether the values are
    *correct* — only that the shape matches the contract.
    """
    issues: list[str] = []

    if not isinstance(result, dict):
        return [f"result must be a dict, got {type(result).__name__}"]

    for field in CLS_V2_COMPONENT_FIELDS:
        if field not in result:
            issues.append(f"missing component: {field}")
            continue
        value = result[field]
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            issues.append(f"{field} must be numeric, got {type(value).__name__}")
            continue
        if value < 0.0 or value > 1.0:
            issues.append(f"{field} out of range [0,1]: {value}")

    refs = result.get("evidence_refs")
    if not isinstance(refs, list):
        issues.append(
            f"evidence_refs must be a list, got {type(refs).__name__ if refs is not None else 'missing'}"
        )
    elif not all(isinstance(item, str) for item in refs):
        issues.append("evidence_refs entries must all be strings")

    return issues
