"""Credential references whose values stay outside tracked configuration."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Mapping, Protocol, runtime_checkable


REFERENCE_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True)
class CredentialRef:
    name: str

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not REFERENCE_PATTERN.fullmatch(self.name):
            raise ValueError("credential reference must be a POSIX environment name")

    def __repr__(self) -> str:
        return f"CredentialRef(name={self.name!r})"


@dataclass(frozen=True)
class ResolvedCredential:
    value: str
    source: str

    def __repr__(self) -> str:
        return f"ResolvedCredential(value='[redacted]', source={self.source!r})"


@dataclass(frozen=True)
class CredentialInfo:
    configured: bool
    source: str | None
    writable: bool


@runtime_checkable
class CredentialProvider(Protocol):
    mode: str

    def resolve(self, reference: CredentialRef) -> ResolvedCredential | None: ...

    def describe(self, reference: CredentialRef) -> CredentialInfo: ...


class EnvironmentCredentialProvider:
    """Resolve the live environment on every operation so rotation is immediate."""

    mode = "environment"

    def __init__(self, environment: Mapping[str, str] = os.environ):
        self._environment = environment

    def resolve(self, reference: CredentialRef) -> ResolvedCredential | None:
        value = self._environment.get(reference.name)
        if value is None or not str(value).strip():
            return None
        return ResolvedCredential(str(value), "environment")

    def describe(self, reference: CredentialRef) -> CredentialInfo:
        configured = self.resolve(reference) is not None
        return CredentialInfo(configured, "environment" if configured else None, False)
