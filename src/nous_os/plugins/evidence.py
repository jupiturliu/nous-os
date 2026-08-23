"""Evidence capability Plugin."""

from __future__ import annotations

from typing import Any

from nous_os.core.context import HarnessContext


class EvidencePlugin:
    id = "evidence"
    requires: tuple[str, ...] = ()
    provides = ("evidence-store",)

    def start(self, context: HarnessContext, config: dict[str, Any]) -> None:
        context.register("evidence-store", context.events)

    def stop(self, context: HarnessContext) -> None:
        context.unregister("evidence-store")


plugin = EvidencePlugin()
