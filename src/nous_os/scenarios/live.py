"""Optional live Interface smoke checks using synthetic non-private input."""

from __future__ import annotations

import argparse
import json
import os
from datetime import date
from typing import Any, Callable

from nous_os.notifications.delivery import RESEARCH_LINE_COMPLETED, WebhookNotificationAdapter
from nous_os.web.hermes import ask_hermes
from nous_os.workflows.research_line import SOURCES, _http_get


def run_live_interfaces(
    *,
    env: dict[str, str] | os._Environ[str] = os.environ,
    fetcher: Callable[[str], bytes] = _http_get,
    webhook_factory: Callable[[str], Any] = WebhookNotificationAdapter,
    hermes: Callable[..., dict[str, Any]] = ask_hermes,
) -> dict[str, Any]:
    """Exercise configured external Interfaces without returning remote content or secrets."""

    checks = [
        _feed_check(fetcher),
        _webhook_check(env, webhook_factory),
        _hermes_check(env, hermes),
    ]
    if any(check["status"] == "failed" for check in checks):
        status = "failed"
    elif all(check["status"] == "skipped" for check in checks):
        status = "skipped"
    else:
        status = "passed"
    return {"schema_version": 1, "status": status, "checks": checks}


def _feed_check(fetcher: Callable[[str], bytes]) -> dict[str, Any]:
    candidates = [source for source in SOURCES if source["url"].startswith("https://")]
    failures = 0
    for source in candidates:
        try:
            payload = fetcher(source["url"])
        except Exception:
            failures += 1
            continue
        if payload:
            return {
                "id": "research-feed",
                "status": "passed",
                "attempted": failures + 1,
                "remote_content_returned": False,
            }
        failures += 1
    return {
        "id": "research-feed",
        "status": "failed",
        "attempted": len(candidates),
        "failure_kind": "all_sources_unavailable",
        "remote_content_returned": False,
    }


def _webhook_check(env: dict[str, str] | os._Environ[str], factory: Callable[[str], Any]) -> dict[str, Any]:
    endpoint = env.get("NOUS_OS_RESEARCH_NOTIFICATION_WEBHOOK_URL", "").strip()
    if not endpoint:
        return {"id": "notification-webhook", "status": "skipped", "reason": "not_configured"}
    try:
        status_code = factory(endpoint).deliver({
            "event_type": RESEARCH_LINE_COMPLETED,
            "capture_date": f"synthetic-live-smoke-{date.today().isoformat()}",
            "status": "completed",
        })
    except Exception as error:
        return {
            "id": "notification-webhook",
            "status": "failed",
            "failure_kind": type(error).__name__,
        }
    return {
        "id": "notification-webhook",
        "status": "passed" if 200 <= status_code < 300 else "failed",
        "status_class": status_code // 100,
    }


def _hermes_check(env: dict[str, str] | os._Environ[str], hermes: Callable[..., dict[str, Any]]) -> dict[str, Any]:
    if not env.get("HERMES_API_SERVER_URL", "").strip():
        return {"id": "hermes-gateway", "status": "skipped", "reason": "not_configured"}
    try:
        result = hermes({
            "message": "Give one source-checking question for a synthetic classroom example.",
            "worksheet": {"boundary": "Hints only; no final answer and no private data."},
            "policy": {"synthetic": True, "private_data": False},
        }, env=env)
    except Exception as error:
        return {"id": "hermes-gateway", "status": "failed", "failure_kind": type(error).__name__}
    return {
        "id": "hermes-gateway",
        "status": "passed" if result.get("route") == "hermes-gateway" else "failed",
        "remote_content_returned": False,
    }


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description="Run optional NOUS OS live Interface smoke checks").parse_args(argv)
    report = run_live_interfaces()
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if report["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
