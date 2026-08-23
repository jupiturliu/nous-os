"""Capability registry and shared Harness context."""

from __future__ import annotations

from typing import Any

from .events import EventStore, EvidenceEvent
from .runtime import RuntimePaths


class HarnessContext:
    def __init__(self, *, profile_name: str, paths: RuntimePaths, events: EventStore | None = None):
        self.profile_name = profile_name
        self.paths = paths.ensure()
        self.events = events or EventStore(self.paths)
        self._capabilities: dict[str, Any] = {}

    def register(self, name: str, capability: Any) -> None:
        if name in self._capabilities:
            raise ValueError(f"capability already registered: {name}")
        self._capabilities[name] = capability

    def resolve(self, name: str) -> Any:
        try:
            return self._capabilities[name]
        except KeyError as error:
            raise KeyError(f"capability not available: {name}") from error

    def unregister(self, name: str) -> None:
        self._capabilities.pop(name, None)

    def has(self, name: str) -> bool:
        return name in self._capabilities

    def emit(self, event: EvidenceEvent) -> EvidenceEvent:
        if event.profile != self.profile_name:
            raise ValueError("event profile does not match Harness context")
        return self.events.append(event)
