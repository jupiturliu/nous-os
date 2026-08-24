"""Closed runtime effect vocabulary and fail-closed Profile policy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol, runtime_checkable


EFFECTS = frozenset({
    "filesystem-read",
    "filesystem-write",
    "network-egress",
    "network-listen",
    "public-publish",
})


@dataclass(frozen=True)
class PermissionDenied(RuntimeError):
    plugin_id: str
    denied_effects: tuple[str, ...]
    code: str = "PERMISSION_DENIED"

    def __str__(self) -> str:
        return f"{self.code}: Plugin {self.plugin_id!r} is not authorized for {', '.join(self.denied_effects)}"


@runtime_checkable
class PermissionPolicy(Protocol):
    allowed_effects: tuple[str, ...]

    def authorize(self, plugin_id: str, effects: Iterable[str]) -> None: ...


class ProfilePermissionPolicy:
    """Authorize Plugin effects against one immutable Profile allowlist."""

    def __init__(self, allowed_effects: Iterable[str]):
        values = tuple(allowed_effects)
        _validate_effects(values, "Profile allowed_effects")
        self.allowed_effects = tuple(sorted(values))
        self._allowed = frozenset(values)

    def authorize(self, plugin_id: str, effects: Iterable[str]) -> None:
        if not isinstance(plugin_id, str) or not plugin_id.strip() or plugin_id != plugin_id.strip():
            raise ValueError("Plugin id must be non-empty and whitespace-trimmed")
        declared = tuple(effects)
        _validate_effects(declared, f"Plugin {plugin_id!r} effects")
        denied = tuple(sorted(set(declared) - self._allowed))
        if denied:
            raise PermissionDenied(plugin_id, denied)


def _validate_effects(values: tuple[str, ...], label: str) -> None:
    if any(not isinstance(value, str) or value != value.strip() or not value for value in values):
        raise ValueError(f"{label} must contain non-empty trimmed strings")
    if len(set(values)) != len(values):
        raise ValueError(f"{label} must not contain duplicates")
    unknown = set(values) - EFFECTS
    if unknown:
        raise ValueError(f"{label} contains unknown effects: {', '.join(sorted(unknown))}")
