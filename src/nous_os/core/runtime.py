"""Runtime-home path policy."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuntimePaths:
    """All mutable paths owned by a Harness run."""

    home: Path

    @classmethod
    def resolve(cls, value: str | Path | None = None) -> "RuntimePaths":
        configured = value or os.environ.get("NOUS_OS_HOME")
        home = Path(configured).expanduser() if configured else Path.home() / ".nous-os"
        return cls(home.resolve())

    @property
    def event_log(self) -> Path:
        return self.home / "events" / "evidence.jsonl"

    @property
    def artifacts(self) -> Path:
        return self.home / "artifacts"

    @property
    def projections(self) -> Path:
        return self.home / "projections"

    @property
    def state(self) -> Path:
        return self.home / "state"

    @property
    def cache(self) -> Path:
        return self.home / "cache"

    def ensure(self) -> "RuntimePaths":
        for path in (self.event_log.parent, self.artifacts, self.projections, self.state, self.cache):
            path.mkdir(parents=True, exist_ok=True)
        return self
