"""Best-effort notifications with an allowlisted payload and evidence write-back."""

from __future__ import annotations

import json
import socket
import urllib.error
import urllib.parse
import urllib.request
import uuid
from dataclasses import asdict, dataclass
from typing import Any, Callable, Protocol

from nous_os.core import EvidenceEvent, HarnessContext


RESEARCH_LINE_COMPLETED = "research-line.capture-completed"
ALLOWED_PAYLOAD_FIELDS = frozenset({"event_type", "capture_date", "status"})


class NotificationAdapter(Protocol):
    def deliver(self, payload: dict[str, str]) -> int: ...


@dataclass(frozen=True)
class DeliveryResult:
    status: str
    event_type: str
    capture_date: str
    failure_kind: str | None = None

    def as_dict(self) -> dict[str, str | None]:
        return asdict(self)


class WebhookNotificationAdapter:
    """POST the fixed notification payload to one operator-owned HTTPS webhook."""

    def __init__(
        self,
        webhook_url: str,
        *,
        timeout_seconds: float = 5.0,
        opener: Callable[..., Any] = urllib.request.urlopen,
    ):
        self._webhook_url = webhook_url
        self._timeout_seconds = timeout_seconds
        self._opener = opener

    def __repr__(self) -> str:
        return f"WebhookNotificationAdapter(webhook_url='[redacted]', timeout_seconds={self._timeout_seconds!r})"

    def deliver(self, payload: dict[str, str]) -> int:
        if set(payload) != ALLOWED_PAYLOAD_FIELDS:
            raise ValueError("notification payload does not match the privacy allowlist")
        parsed = urllib.parse.urlparse(self._webhook_url)
        if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
            raise ValueError("notification webhook must be an HTTPS URL without embedded credentials")
        if not isinstance(self._timeout_seconds, (int, float)) or self._timeout_seconds <= 0:
            raise ValueError("notification timeout must be positive")
        body = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        request = urllib.request.Request(
            self._webhook_url,
            data=body,
            headers={"Content-Type": "application/json", "User-Agent": "nous-os-notifications/1"},
            method="POST",
        )
        with self._opener(request, timeout=self._timeout_seconds) as response:
            return int(response.status)


class NotificationCenter:
    """Own delivery isolation, privacy invariants, outcomes, and Evidence Events."""

    def __init__(self, context: HarnessContext, adapter: NotificationAdapter | None):
        self._context = context
        self._adapter = adapter

    def research_line_completed(self, capture_date: str) -> DeliveryResult:
        payload = {
            "event_type": RESEARCH_LINE_COMPLETED,
            "capture_date": capture_date,
            "status": "completed",
        }
        if self._adapter is None:
            result = DeliveryResult("skipped", RESEARCH_LINE_COMPLETED, capture_date, "not_configured")
            self._record(result)
            return result
        try:
            status_code = self._adapter.deliver(payload)
            if not 200 <= status_code < 300:
                result = DeliveryResult("failed", RESEARCH_LINE_COMPLETED, capture_date, "http_status")
            else:
                result = DeliveryResult("delivered", RESEARCH_LINE_COMPLETED, capture_date)
        except Exception as error:  # Notification failures must never fail Research Line.
            result = DeliveryResult("failed", RESEARCH_LINE_COMPLETED, capture_date, _failure_kind(error))
        self._record(result)
        return result

    def _record(self, result: DeliveryResult) -> None:
        payload: dict[str, str] = {
            "notification_type": result.event_type,
            "capture_date": result.capture_date,
            "delivery_status": result.status,
        }
        if result.failure_kind:
            payload["failure_kind"] = result.failure_kind
        try:
            self._context.emit(EvidenceEvent(
                event_type=f"notification.{result.status}",
                run_id=f"notification-{uuid.uuid4().hex[:16]}",
                profile=self._context.profile_name,
                producer="notification-center",
                payload=payload,
                privacy="internal",
            ))
        except (OSError, ValueError):
            # Evidence storage is part of the best-effort notification subsystem.
            # A failure here must not invalidate a successfully persisted capture.
            return


def _failure_kind(error: Exception) -> str:
    if isinstance(error, (TimeoutError, socket.timeout)):
        return "timeout"
    if isinstance(error, urllib.error.HTTPError):
        return "http_status"
    if isinstance(error, urllib.error.URLError):
        return "transport"
    if isinstance(error, ValueError):
        return "invalid_configuration"
    return "adapter_error"
