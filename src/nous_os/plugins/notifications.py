"""Notification capability Plugin."""

from __future__ import annotations

import os
from typing import Any

from nous_os.core import HarnessContext
from nous_os.notifications import NotificationCenter, WebhookNotificationAdapter


DEFAULT_WEBHOOK_ENV = "NOUS_OS_RESEARCH_NOTIFICATION_WEBHOOK_URL"


class NotificationPlugin:
    id = "notifications"
    requires = ("evidence-store",)
    provides = ("notifications",)

    def start(self, context: HarnessContext, config: dict[str, Any]) -> None:
        allowed = {"webhook_env", "timeout_seconds"}
        unknown = set(config) - allowed
        if unknown:
            raise ValueError(f"unknown notification config fields: {', '.join(sorted(unknown))}")
        environment_name = config.get("webhook_env", DEFAULT_WEBHOOK_ENV)
        timeout_seconds = config.get("timeout_seconds", 5)
        if not isinstance(environment_name, str) or not environment_name:
            raise ValueError("notification webhook_env must be a non-empty string")
        if not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0:
            raise ValueError("notification timeout_seconds must be positive")
        endpoint = os.environ.get(environment_name)
        adapter = WebhookNotificationAdapter(endpoint, timeout_seconds=timeout_seconds) if endpoint else None
        context.register("notifications", NotificationCenter(context, adapter))

    def stop(self, context: HarnessContext) -> None:
        context.unregister("notifications")


plugin = NotificationPlugin()
