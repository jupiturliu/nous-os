"""Student Sandbox capability Plugin."""

from __future__ import annotations

from typing import Any

from nous_os.core.context import HarnessContext
from nous_os.workflows.student_sandbox import StudentSandboxStore


class StudentSandboxPlugin:
    id = "student-sandbox"
    requires = ("evidence-store",)
    provides = ("student-sandbox",)
    effects = ("filesystem-read", "filesystem-write")

    def start(self, context: HarnessContext, config: dict[str, Any]) -> None:
        context.register("student-sandbox", StudentSandboxStore(context))

    def stop(self, context: HarnessContext) -> None:
        context.unregister("student-sandbox")


plugin = StudentSandboxPlugin()
