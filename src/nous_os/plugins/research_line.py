"""Research Line capability Plugin."""

from __future__ import annotations

from typing import Any

from nous_os.core.context import HarnessContext
from nous_os.workflows import research_line


class ResearchLinePlugin:
    id = "research-line"
    requires = ("evidence-store",)
    provides = ("research-line",)

    def start(self, context: HarnessContext, config: dict[str, Any]) -> None:
        context.register("research-line", research_line)

    def stop(self, context: HarnessContext) -> None:
        context.unregister("research-line")


plugin = ResearchLinePlugin()
