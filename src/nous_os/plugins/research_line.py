"""Research Line capability Plugin."""

from __future__ import annotations

from typing import Any

from nous_os.core.context import HarnessContext
from nous_os.workflows import research_line


class ResearchLineRunner:
    """Preserve the workflow Interface and notify only after durable output."""

    def __init__(self, context: HarnessContext):
        self._notifications = context.resolve("notifications")

    def capture(self, **arguments):
        return research_line.capture(**arguments)

    def write_inbox_file(self, capture_date: str, markdown: str, **arguments):
        path = research_line.write_inbox_file(capture_date, markdown, **arguments)
        self._notifications.research_line_completed(capture_date)
        return path


class ResearchLinePlugin:
    id = "research-line"
    requires = ("evidence-store", "notifications")
    provides = ("research-line",)
    effects = ("filesystem-write", "network-egress")

    def start(self, context: HarnessContext, config: dict[str, Any]) -> None:
        context.register("research-line", ResearchLineRunner(context))

    def stop(self, context: HarnessContext) -> None:
        context.unregister("research-line")


plugin = ResearchLinePlugin()
