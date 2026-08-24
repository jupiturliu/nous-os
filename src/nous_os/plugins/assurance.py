"""Runtime Invariant Registry capability Plugin."""

from __future__ import annotations

from typing import Any

from nous_os.assurance import InvariantRegistry
from nous_os.core.context import HarnessContext


class AssurancePlugin:
    id = "assurance"
    requires = ("permission-policy",)
    provides = ("invariants",)
    effects: tuple[str, ...] = ()

    def start(self, context: HarnessContext, config: dict[str, Any]) -> None:
        allowed = {"enabled", "owner_allowlist", "owner_blocklist"}
        unknown = set(config) - allowed
        if unknown:
            raise ValueError(f"unknown assurance config fields: {', '.join(sorted(unknown))}")
        registry = InvariantRegistry(
            enabled=config.get("enabled", True),
            owner_allowlist=config.get("owner_allowlist", ()),
            owner_blocklist=config.get("owner_blocklist", ()),
        )
        context.register("invariants", registry)

    def stop(self, context: HarnessContext) -> None:
        context.unregister("invariants")


plugin = AssurancePlugin()
