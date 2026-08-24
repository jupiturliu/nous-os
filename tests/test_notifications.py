from __future__ import annotations

import json
import tempfile
import unittest
import urllib.error
from pathlib import Path

from nous_os.core import HarnessContext, RuntimePaths
from nous_os.notifications import NotificationCenter, WebhookNotificationAdapter
from nous_os.notifications.delivery import CredentialNotificationAdapter
from nous_os.plugins.research_line import ResearchLineRunner
from nous_os.security import CredentialRef, EnvironmentCredentialProvider


class _RecordingAdapter:
    def __init__(self, *, status_code=204, error=None, assertion=None):
        self.status_code = status_code
        self.error = error
        self.assertion = assertion
        self.payloads = []

    def deliver(self, payload):
        if self.assertion:
            self.assertion()
        self.payloads.append(payload)
        if self.error:
            raise self.error
        return self.status_code


class _Response:
    def __init__(self, status=204):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


class NotificationCenterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.paths = RuntimePaths.resolve(self.temp.name)
        self.context = HarnessContext(profile_name="research", paths=self.paths)

    def tearDown(self):
        self.temp.cleanup()

    def events(self):
        return list(self.context.events.events())

    def test_delivery_payload_is_an_exact_privacy_allowlist(self):
        adapter = _RecordingAdapter()
        result = NotificationCenter(self.context, adapter).research_line_completed("2026-08-23")
        self.assertEqual(result.status, "delivered")
        self.assertEqual(adapter.payloads, [{
            "event_type": "research-line.capture-completed",
            "capture_date": "2026-08-23",
            "status": "completed",
        }])
        event = self.events()[-1]
        self.assertEqual(event["event_type"], "notification.delivered")
        self.assertEqual(set(event["payload"]), {"notification_type", "capture_date", "delivery_status"})

    def test_timeout_transport_and_http_failure_are_redacted_and_non_throwing(self):
        cases = (
            (_RecordingAdapter(error=TimeoutError("secret timeout detail")), "timeout"),
            (_RecordingAdapter(error=urllib.error.URLError("secret transport detail")), "transport"),
            (_RecordingAdapter(status_code=503), "http_status"),
        )
        for adapter, expected_kind in cases:
            with self.subTest(expected_kind):
                result = NotificationCenter(self.context, adapter).research_line_completed("2026-08-23")
                self.assertEqual((result.status, result.failure_kind), ("failed", expected_kind))
                encoded = json.dumps(self.events()[-1], sort_keys=True)
                self.assertNotIn("secret", encoded)
                self.assertEqual(self.events()[-1]["payload"]["failure_kind"], expected_kind)

    def test_unconfigured_delivery_is_skipped_without_adapter(self):
        result = NotificationCenter(self.context, None).research_line_completed("2026-08-23")
        self.assertEqual((result.status, result.failure_kind), ("skipped", "not_configured"))
        self.assertEqual(self.events()[-1]["event_type"], "notification.skipped")

    def test_webhook_adapter_posts_sorted_json_without_disclosing_url_in_repr(self):
        calls = []

        def opener(request, *, timeout):
            calls.append((request, timeout))
            return _Response()

        secret_url = "https://notify.example/hooks/super-secret"
        adapter = WebhookNotificationAdapter(secret_url, timeout_seconds=2, opener=opener)
        status = adapter.deliver({
            "event_type": "research-line.capture-completed",
            "capture_date": "2026-08-23",
            "status": "completed",
        })
        self.assertEqual(status, 204)
        self.assertEqual(calls[0][1], 2)
        self.assertEqual(calls[0][0].method, "POST")
        self.assertEqual(json.loads(calls[0][0].data), {
            "event_type": "research-line.capture-completed",
            "capture_date": "2026-08-23",
            "status": "completed",
        })
        self.assertNotIn(secret_url, repr(adapter))

    def test_webhook_adapter_rejects_non_https_and_extra_payload_fields(self):
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            WebhookNotificationAdapter("http://notify.example/hook").deliver({
                "event_type": "research-line.capture-completed",
                "capture_date": "2026-08-23",
                "status": "completed",
            })
        with self.assertRaisesRegex(ValueError, "allowlist"):
            WebhookNotificationAdapter("https://notify.example/hook").deliver({
                "event_type": "research-line.capture-completed",
                "capture_date": "2026-08-23",
                "status": "completed",
                "markdown": "private",
            })

    def test_credential_adapter_observes_rotation_without_restart(self):
        environment = {"NOTIFY_URL": "https://notify.example/first"}
        endpoints = []

        class Adapter:
            def __init__(self, endpoint, *, timeout_seconds):
                endpoints.append((endpoint, timeout_seconds))

            def deliver(self, payload):
                return 204

        adapter = CredentialNotificationAdapter(
            EnvironmentCredentialProvider(environment),
            CredentialRef("NOTIFY_URL"),
            timeout_seconds=2,
            adapter_factory=Adapter,
        )
        adapter.deliver({
            "event_type": "research-line.capture-completed",
            "capture_date": "2026-08-23",
            "status": "completed",
        })
        environment["NOTIFY_URL"] = "https://notify.example/rotated"
        adapter.deliver({
            "event_type": "research-line.capture-completed",
            "capture_date": "2026-08-24",
            "status": "completed",
        })
        self.assertEqual([item[0] for item in endpoints], [
            "https://notify.example/first",
            "https://notify.example/rotated",
        ])
        self.assertNotIn("notify.example", repr(adapter))


class ResearchLineNotificationTests(unittest.TestCase):
    def test_capture_without_persistence_does_not_notify(self):
        with tempfile.TemporaryDirectory() as directory:
            adapter = _RecordingAdapter()
            context = HarnessContext(profile_name="research", paths=RuntimePaths.resolve(directory))
            context.register("notifications", NotificationCenter(context, adapter))
            capture_date, _ = ResearchLineRunner(context).capture(sources=[], capture_date="2026-08-23")
            self.assertEqual(capture_date, "2026-08-23")
            self.assertEqual(adapter.payloads, [])
            self.assertEqual(list(context.events.events()), [])

    def test_runner_notifies_once_only_after_inbox_file_exists(self):
        with tempfile.TemporaryDirectory() as directory:
            inbox = Path(directory) / "inbox"
            expected = inbox / "2026-08-23.md"
            adapter = _RecordingAdapter(assertion=lambda: self.assertTrue(expected.is_file()))
            context = HarnessContext(profile_name="research", paths=RuntimePaths.resolve(Path(directory) / "runtime"))
            context.register("notifications", NotificationCenter(context, adapter))
            runner = ResearchLineRunner(context)
            result = runner.write_inbox_file("2026-08-23", "# Safe content\n", inbox_dir=inbox)
            self.assertEqual(result, expected)
            self.assertEqual(len(adapter.payloads), 1)

    def test_delivery_failure_leaves_inbox_file_intact(self):
        with tempfile.TemporaryDirectory() as directory:
            inbox = Path(directory) / "inbox"
            adapter = _RecordingAdapter(error=TimeoutError("provider unavailable"))
            context = HarnessContext(profile_name="research", paths=RuntimePaths.resolve(Path(directory) / "runtime"))
            context.register("notifications", NotificationCenter(context, adapter))
            result = ResearchLineRunner(context).write_inbox_file(
                "2026-08-23", "# Capture remains durable\n", inbox_dir=inbox
            )
            self.assertEqual(result.read_text(), "# Capture remains durable\n")
            self.assertEqual(list(context.events.events())[-1]["event_type"], "notification.failed")


if __name__ == "__main__":
    unittest.main()
