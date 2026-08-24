"""Notification capability Plugin."""

from __future__ import annotations

from typing import Any

from nous_os.core import HarnessContext
from nous_os.notifications import NotificationCenter
from nous_os.notifications.delivery import CredentialNotificationAdapter
from nous_os.security import CredentialRef


DEFAULT_WEBHOOK_REF = "NOUS_OS_RESEARCH_NOTIFICATION_WEBHOOK_URL"


class NotificationPlugin:
    id = "notifications"
    requires = ("evidence-store", "credential-provider")
    provides = ("notifications",)
    effects = ("network-egress",)

    def start(self, context: HarnessContext, config: dict[str, Any]) -> None:
        allowed = {"webhook_ref", "timeout_seconds"}
        unknown = set(config) - allowed
        if unknown:
            raise ValueError(f"unknown notification config fields: {', '.join(sorted(unknown))}")
        reference = CredentialRef(config.get("webhook_ref", DEFAULT_WEBHOOK_REF))
        timeout_seconds = config.get("timeout_seconds", 5)
        if not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0:
            raise ValueError("notification timeout_seconds must be positive")
        adapter = CredentialNotificationAdapter(
            context.resolve("credential-provider"),
            reference,
            timeout_seconds=timeout_seconds,
        )
        context.register("notifications", NotificationCenter(context, adapter))

    def stop(self, context: HarnessContext) -> None:
        context.unregister("notifications")


plugin = NotificationPlugin()
