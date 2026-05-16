"""Deterministic CLS v2 calculator for NOUS OS runtime snapshots."""

from __future__ import annotations


WEIGHTS = {
    "outcome_quality_delta": 0.35,
    "correction_absorption": 0.20,
    "memory_reuse_precision": 0.15,
    "repeatability_gain": 0.15,
    "boundary_integrity": 0.10,
    "human_agency_preservation": 0.05,
}


def compute_cls_v2(components: dict[str, float]) -> float:
    """Compute weighted CLS v2 score from normalized component values."""
    missing = [key for key in WEIGHTS if key not in components]
    if missing:
        raise KeyError(f"Missing CLS v2 component: {missing[0]}")
    return round(sum(float(components[key]) * weight for key, weight in WEIGHTS.items()), 4)
