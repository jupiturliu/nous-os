"""Plugin-owned checks over observable Harness facts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Optional


INVARIANT_PHASES = frozenset({"after-start", "workflow-complete", "before-stop"})
InvariantCheck = Callable[[], Optional[str]]


@dataclass(frozen=True)
class InvariantViolation(RuntimeError):
    owner: str
    invariant: str
    phase: str
    detail: str
    code: str = "INVARIANT"

    def __str__(self) -> str:
        return f"{self.code}: {self.owner}.{self.invariant} failed during {self.phase}: {self.detail}"


@dataclass(frozen=True)
class InvariantRegistration:
    owner: str
    name: str
    phases: tuple[str, ...]
    selected: bool

    def as_dict(self) -> dict:
        return {
            "owner": self.owner,
            "name": self.name,
            "phases": list(self.phases),
            "selected": self.selected,
        }


class InvariantRegistry:
    """Own selection, identity, attribution, and phase execution."""

    def __init__(
        self,
        *,
        enabled: bool = True,
        owner_allowlist: Iterable[str] = (),
        owner_blocklist: Iterable[str] = (),
    ):
        self.enabled = bool(enabled)
        self._allowlist = _names(owner_allowlist, "owner_allowlist")
        self._blocklist = _names(owner_blocklist, "owner_blocklist")
        self._checks: dict[tuple[str, str], tuple[tuple[str, ...], InvariantCheck]] = {}

    def register(self, owner: str, name: str, phases: Iterable[str], check: InvariantCheck) -> None:
        owner = _name(owner, "invariant owner")
        name = _name(name, "invariant name")
        phase_values = tuple(phases)
        if not phase_values or len(set(phase_values)) != len(phase_values) or set(phase_values) - INVARIANT_PHASES:
            raise ValueError("invariant phases must be unique members of the closed phase vocabulary")
        if not callable(check):
            raise ValueError("invariant check must be callable")
        key = (owner, name)
        if key in self._checks:
            raise ValueError(f"duplicate invariant registration: {owner}.{name}")
        self._checks[key] = (phase_values, check)

    def check(self, phase: str) -> tuple[str, ...]:
        if phase not in INVARIANT_PHASES:
            raise ValueError(f"unknown invariant phase: {phase}")
        executed = []
        for (owner, name), (phases, check) in self._checks.items():
            if phase not in phases or not self._selected(owner):
                continue
            executed.append(f"{owner}.{name}")
            try:
                detail = check()
            except InvariantViolation:
                raise
            except Exception as error:
                raise InvariantViolation(owner, name, phase, type(error).__name__) from error
            if detail:
                raise InvariantViolation(owner, name, phase, str(detail))
        return tuple(executed)

    def registrations(self) -> tuple[InvariantRegistration, ...]:
        return tuple(
            InvariantRegistration(owner, name, phases, self._selected(owner))
            for (owner, name), (phases, _) in self._checks.items()
        )

    def _selected(self, owner: str) -> bool:
        if not self.enabled or owner in self._blocklist:
            return False
        return not self._allowlist or owner in self._allowlist


def _names(values: Iterable[str], label: str) -> frozenset[str]:
    result = tuple(_name(value, label) for value in values)
    if len(set(result)) != len(result):
        raise ValueError(f"{label} must not contain duplicates")
    return frozenset(result)


def _name(value: str, label: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or any(character.isspace() for character in value):
        raise ValueError(f"{label} must be non-empty and contain no whitespace")
    return value
