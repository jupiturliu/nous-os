"""Best-effort operational records with a deliberately closed vocabulary."""

from __future__ import annotations

import json
import os
import threading
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable

from nous_os.core.runtime import RuntimePaths


TELEMETRY_EVENTS = frozenset({"plugin-start", "plugin-stop", "workflow", "invariant", "shutdown"})
TELEMETRY_PHASES = frozenset({"start", "after-start", "run", "before-stop", "stop"})
TELEMETRY_OUTCOMES = frozenset({"passed", "failed", "skipped"})


@dataclass(frozen=True)
class TelemetryRecord:
    event: str
    phase: str
    outcome: str
    profile: str
    plugin_id: str | None = None
    duration_ms: int | None = None
    error_class: str | None = None

    def __post_init__(self) -> None:
        if self.event not in TELEMETRY_EVENTS:
            raise ValueError(f"unknown telemetry event: {self.event}")
        if self.phase not in TELEMETRY_PHASES:
            raise ValueError(f"unknown telemetry phase: {self.phase}")
        if self.outcome not in TELEMETRY_OUTCOMES:
            raise ValueError(f"unknown telemetry outcome: {self.outcome}")
        if self.duration_ms is not None and self.duration_ms < 0:
            raise ValueError("telemetry duration_ms must not be negative")
        for label, value in (("profile", self.profile), ("plugin_id", self.plugin_id), ("error_class", self.error_class)):
            if value is not None and (not isinstance(value, str) or not value or _looks_sensitive(value)):
                raise ValueError(f"unsafe telemetry {label}")

    def as_dict(self) -> dict:
        return {key: value for key, value in asdict(self).items() if value is not None}


@runtime_checkable
class TelemetrySink(Protocol):
    mode: str

    def emit(self, record: TelemetryRecord) -> None: ...

    def shutdown(self) -> None: ...


class DisabledTelemetrySink:
    mode = "disabled"

    def emit(self, record: TelemetryRecord) -> None:
        return

    def shutdown(self) -> None:
        return


class JsonlTelemetrySink:
    mode = "jsonl"
    _lock = threading.Lock()

    def __init__(self, paths: RuntimePaths):
        self.path = paths.home / "telemetry" / "operations.jsonl"

    def emit(self, record: TelemetryRecord) -> None:
        line = json.dumps(record.as_dict(), ensure_ascii=False, sort_keys=True) + "\n"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            fd = os.open(self.path, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
            try:
                remaining = memoryview(line.encode("utf-8"))
                while remaining:
                    remaining = remaining[os.write(fd, remaining):]
            finally:
                os.close(fd)

    def shutdown(self) -> None:
        return


class OperationalTelemetry:
    """Contain Adapter failures and expose safe configuration facts."""

    def __init__(self, profile: str, sink: TelemetrySink):
        self.profile = profile
        self.sink = sink
        self.failures = 0

    @property
    def mode(self) -> str:
        return self.sink.mode

    def emit(self, event: str, phase: str, outcome: str, **fields) -> bool:
        try:
            self.sink.emit(TelemetryRecord(event, phase, outcome, self.profile, **fields))
        except Exception:
            self.failures += 1
            return False
        return True

    def shutdown(self) -> bool:
        try:
            self.sink.shutdown()
        except Exception:
            self.failures += 1
            return False
        return True

    def describe(self) -> dict:
        return {"mode": self.mode, "delivery": "best-effort", "failures": self.failures}


def _looks_sensitive(value: str) -> bool:
    lowered = value.lower()
    return (
        any(token in lowered for token in ("password", "secret", "token", "webhook", "http://", "https://"))
        or value.startswith(("/Users/", "/home/", "/private/", "/tmp/"))
        or bool(Path(value).drive)
    )
