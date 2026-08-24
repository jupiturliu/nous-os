"""Capability registry and shared Harness context."""

from __future__ import annotations

from typing import Any

from nous_os.security import ProfilePermissionPolicy

from .events import EventStore, EvidenceEvent
from .runtime import RuntimePaths


class HarnessContext:
    def __init__(
        self,
        *,
        profile_name: str,
        paths: RuntimePaths,
        events: EventStore | None = None,
        permission_policy: ProfilePermissionPolicy | None = None,
    ):
        self.profile_name = profile_name
        self.paths = paths.ensure()
        self.events = events or EventStore(self.paths)
        self.permission_policy = permission_policy or ProfilePermissionPolicy(())
        self._capabilities: dict[str, Any] = {}
        self._lifecycle = "initialized"
        self._readiness_reasons: tuple[str, ...] = ("harness-not-started",)

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

    def capability_names(self) -> tuple[str, ...]:
        return tuple(sorted(self._capabilities))

    def clear_capabilities(self) -> None:
        self._capabilities.clear()

    def mark_starting(self) -> None:
        self._lifecycle = "starting"
        self._readiness_reasons = ("harness-starting",)

    def mark_ready(self) -> None:
        self._lifecycle = "ready"
        self._readiness_reasons = ()

    def mark_stopping(self) -> None:
        self._lifecycle = "stopping"
        self._readiness_reasons = ("harness-stopping",)

    def mark_stopped(self) -> None:
        self._lifecycle = "stopped"
        self._readiness_reasons = ("harness-stopped",)

    def mark_failed(self, reason: str) -> None:
        self._lifecycle = "failed"
        self._readiness_reasons = (_safe_reason(reason),)

    def mark_unready(self, reason: str) -> None:
        self._lifecycle = "unready"
        self._readiness_reasons = (_safe_reason(reason),)

    def readiness(self) -> dict[str, Any]:
        ready = self._lifecycle == "ready" and not self._readiness_reasons
        return {
            "ready": ready,
            "status": "ready" if ready else self._lifecycle,
            "reasons": list(self._readiness_reasons),
            "profile": self.profile_name,
        }

    def run_invariants(self, phase: str) -> tuple[str, ...]:
        if not self.has("invariants"):
            return ()
        return self.resolve("invariants").check(phase)

    def emit_telemetry(self, event: str, phase: str, outcome: str, **fields) -> bool:
        if not self.has("telemetry"):
            return False
        return bool(self.resolve("telemetry").emit(event, phase, outcome, **fields))


def _safe_reason(value: str) -> str:
    text = str(value)
    if not text or any(token in text.lower() for token in ("secret", "token", "password", "webhook", "http")):
        return "runtime-assurance-failure"
    if "/" in text or "\\" in text:
        return "runtime-assurance-failure"
    return text[:120]
