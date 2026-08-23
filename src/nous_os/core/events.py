"""Append-only evidence and content-addressed artifact storage."""

from __future__ import annotations

import hashlib
import json
import os
import threading
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import fcntl

from .runtime import RuntimePaths


@dataclass(frozen=True)
class ArtifactRef:
    artifact_id: str
    kind: str
    path: str
    sha256: str


@dataclass(frozen=True)
class EvidenceEvent:
    event_type: str
    run_id: str
    profile: str
    producer: str
    payload: dict[str, Any] = field(default_factory=dict)
    evidence_refs: tuple[ArtifactRef, ...] = ()
    privacy: str = "internal"
    schema_version: int = 1
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )

    def as_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["evidence_refs"] = [asdict(ref) for ref in self.evidence_refs]
        return result


class EventStore:
    """Own append, artifact, and replay behavior behind one Interface."""

    _lock = threading.Lock()

    def __init__(self, paths: RuntimePaths):
        self.paths = paths.ensure()

    def append(self, event: EvidenceEvent) -> EvidenceEvent:
        line = json.dumps(event.as_dict(), ensure_ascii=False, sort_keys=True) + "\n"
        with self._lock:
            fd = os.open(self.paths.event_log, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX)
                remaining = memoryview(line.encode("utf-8"))
                while remaining:
                    remaining = remaining[os.write(fd, remaining):]
                os.fsync(fd)
            finally:
                fcntl.flock(fd, fcntl.LOCK_UN)
                os.close(fd)
        return event

    def events(self) -> Iterable[dict[str, Any]]:
        if not self.paths.event_log.exists():
            return ()
        records: list[dict[str, Any]] = []
        for line_number, line in enumerate(self.paths.event_log.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(f"invalid evidence JSONL at line {line_number}: {error}") from error
        return tuple(records)

    def write_artifact(self, kind: str, payload: Any, artifact_id: str | None = None) -> ArtifactRef:
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8") + b"\n"
        digest = hashlib.sha256(encoded).hexdigest()
        safe_kind = _safe_segment(kind)
        safe_id = _safe_segment(artifact_id or digest[:20])
        directory = self.paths.artifacts / safe_kind
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{safe_id}.json"
        temporary = path.with_suffix(".json.tmp")
        temporary.write_bytes(encoded)
        os.chmod(temporary, 0o600)
        temporary.replace(path)
        return ArtifactRef(
            artifact_id=safe_id,
            kind=safe_kind,
            path=path.relative_to(self.paths.home).as_posix(),
            sha256=digest,
        )


def _safe_segment(value: str) -> str:
    if not value or any(character not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for character in value):
        raise ValueError(f"unsafe artifact path segment: {value!r}")
    return value
