"""Declarative repository verification Interface."""

from .runner import CHECK_MODES, Gate, GateResult, CheckReport, ProcessOutcome, gates_for_mode, run_check, run_gates

__all__ = [
    "CheckReport",
    "CHECK_MODES",
    "Gate",
    "GateResult",
    "ProcessOutcome",
    "gates_for_mode",
    "run_check",
    "run_gates",
]
