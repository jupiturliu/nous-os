"""Heartbeat workflow capability Plugin."""

from __future__ import annotations

from typing import Any

from nous_os.core.context import HarnessContext
from nous_os.workflows.heartbeat import run_heartbeat_flow


class HeartbeatRunner:
    def __init__(self, context: HarnessContext):
        self.context = context

    def run(self, *, goal=None, override_kind=None, demo_mode=None):
        return run_heartbeat_flow(
            goal=goal,
            override_kind=override_kind,
            demo_mode=demo_mode,
            runtime_home=self.context.paths.home,
            profile=self.context.profile_name,
        )


class HeartbeatPlugin:
    id = "heartbeat"
    requires = ("evidence-store",)
    provides = ("heartbeat",)
    effects = ("filesystem-read", "filesystem-write")

    def start(self, context: HarnessContext, config: dict[str, Any]) -> None:
        context.register("heartbeat", HeartbeatRunner(context))

    def stop(self, context: HarnessContext) -> None:
        context.unregister("heartbeat")


plugin = HeartbeatPlugin()
