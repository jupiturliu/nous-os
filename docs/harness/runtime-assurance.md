# Runtime Assurance and Safety

Runtime assurance makes the assembled Harness observable and fail closed without turning configuration approval into runtime authority. The central Interface is the Harness lifecycle; individual Plugins own their checks and Implementations.

## Profile v2 and Effects

Every Plugin declares zero or more Effects from this closed vocabulary:

- `filesystem-read`
- `filesystem-write`
- `network-egress`
- `network-listen`
- `public-publish`

Every Profile v2 explicitly lists `allowed_effects`. Before any Plugin starts, the Permission Policy validates all declarations and rejects unknown or unauthorized Effects. A Spec Approval authorizes a repository change; it never grants a runtime Effect.

Profile v1 migration is intentionally explicit: set `schema_version: 2` and add the minimum `allowed_effects` required by that Profile's Plugins.

## Invariant lifecycle

The Invariant Registry supports three phases:

| Phase | Meaning |
|---|---|
| `after-start` | Composition is complete and required runtime facts can be observed |
| `workflow-complete` | A workflow persisted its authoritative result |
| `before-stop` | Runtime relationships still hold before Capabilities are removed |

Each Invariant has an owner, stable name, phases, and check. Failures carry code `INVARIANT` plus owner, name, and phase. Selection uses exact owner allowlists and blocklists. Plugin shutdown runs in reverse order, continues after failures, removes all Capabilities, is idempotent, and aggregates attributable cleanup errors.

## Credential Provider

Profiles store only validated Credential References such as `NOUS_OS_RESEARCH_NOTIFICATION_WEBHOOK_URL`. The environment Adapter resolves the current value once for each operation, treats blank values as absent, and does not cache, so rotation is visible without restarting the Harness.

`describe()` returns only configured state, source, and writability. Values are forbidden from diagnostics, errors, Telemetry, Evidence Events, Artifacts, snapshots, and VerificationReports. Research Line notification delivery still validates HTTPS and remains best-effort.

## Readiness and diagnosis

Process liveness and Harness readiness are different Interfaces:

```text
GET /api/health  -> 200 while the Web process can answer
GET /api/ready   -> 200 only after startup and after-start Invariants pass
                 -> 503 with safe reasons otherwise
```

Inspect a composition without exposing credential values or machine paths:

```bash
nous-os diagnose --profile research
nous-os diagnose --profile research --json
```

The report includes Profile schema, Plugin order and Effects, Capabilities, selected Invariants, normalized Runtime Home readiness, credential configuration facts, Telemetry mode, and lifecycle readiness.

## Operational Telemetry

Operational Telemetry accepts only event kind, phase, outcome, duration, Profile name, Plugin id, and stable error class. Shipped Profiles use the disabled Adapter. An operator may select local JSONL mode in a deployment Profile:

```yaml
- id: telemetry
  module: nous_os.plugins.telemetry
  config:
    mode: jsonl
```

The local Adapter writes `$NOUS_OS_HOME/telemetry/operations.jsonl` with owner-only permissions. Sink emit and shutdown failures are contained and counted; they never alter workflow success or prevent teardown.

## Verification

```bash
python3 -m unittest tests.test_runtime_assurance -v
python3 -m unittest tests.test_notifications tests.test_harness_web -v
nous-os check --mode full
```
