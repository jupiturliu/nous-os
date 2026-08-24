# Notifications

The Notification Module provides privacy-allowlisted, best-effort milestone delivery. Research Line uses it only after an inbox file has been persisted successfully.

## Privacy contract

The outbound Research Line completion payload contains exactly:

```json
{
  "capture_date": "2026-08-23",
  "event_type": "research-line.capture-completed",
  "status": "completed"
}
```

Captured markdown, source metadata, titles, links, summaries, local paths, credentials, and endpoint identifiers never cross the Notification Adapter seam. Evidence Events store only the notification type, capture date, delivery status, and a bounded failure category.

## Configuration

Set the webhook URL in runtime secret configuration, never in tracked YAML:

```bash
export NOUS_OS_RESEARCH_NOTIFICATION_WEBHOOK_URL="https://operator-owned.example/hooks/..."
nous-os run research-line --profile research
```

The URL must use HTTPS and must not contain embedded username/password credentials. The repository's scheduled capture workflow reads the same name from a GitHub Actions secret.

When the variable is absent, the Notification Module records `notification.skipped` without opening a network connection. Successful delivery records `notification.delivered`. Timeout, non-2xx response, invalid configuration, or transport failure records `notification.failed`; none of these outcomes changes a successful Research Line exit into a failure.

Dry-run capture prints markdown but does not persist an inbox file and therefore does not notify.
