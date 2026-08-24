"""Operational Telemetry capability Plugin."""

from __future__ import annotations

from typing import Any

from nous_os.core.context import HarnessContext
from nous_os.telemetry import DisabledTelemetrySink, JsonlTelemetrySink, OperationalTelemetry


class TelemetryPlugin:
    id = "telemetry"
    requires = ("permission-policy",)
    provides = ("telemetry",)
    effects = ("filesystem-write",)

    def start(self, context: HarnessContext, config: dict[str, Any]) -> None:
        allowed = {"mode"}
        unknown = set(config) - allowed
        if unknown:
            raise ValueError(f"unknown telemetry config fields: {', '.join(sorted(unknown))}")
        mode = config.get("mode", "disabled")
        if mode == "disabled":
            sink = DisabledTelemetrySink()
        elif mode == "jsonl":
            sink = JsonlTelemetrySink(context.paths)
        else:
            raise ValueError("telemetry mode must be disabled or jsonl")
        context.register("telemetry", OperationalTelemetry(context.profile_name, sink))

    def stop(self, context: HarnessContext) -> None:
        if context.has("telemetry"):
            context.resolve("telemetry").shutdown()
        context.unregister("telemetry")


plugin = TelemetryPlugin()
