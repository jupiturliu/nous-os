# Harness Verification Loop

The verification loop gives local development and CI one Interface for proving
that the assembled Harness works. Its Gate Module hides dependency validation,
bounded scheduling, subprocess isolation, diagnostics, and result ordering
behind `nous-os check`.

## Modes

| Mode | Intended use | Included checks |
|---|---|---|
| `quick` | Fast local feedback | Harness inventory, domain contracts, static site staging, all Profiles |
| `full` | Before an implementation commit | `quick`, assembled scenario replay, full unit suite |
| `ci` | Pull requests and pushes | `full`, then verify that tests changed no tracked source |
| `release` | Reproducible Python artifact verification | `ci`, then double build, archive/provenance inspection, and isolated installed-wheel smoke |

Run a mode in human-readable or machine-readable form:

```bash
nous-os check --mode quick
nous-os check --mode ci --json
```

Every Gate reports `passed`, `failed`, or `skipped`. A failed prerequisite skips
only its dependents; independent Gates continue. Exit code is non-zero whenever
the aggregate contains a failed or skipped Gate.

## Scenario replay

Student, Research, and Trading Proof scenarios load their real YAML Profiles,
start the shipping Plugins, exercise named Capabilities, read the resulting
world from the isolated Runtime Home, and stop the Harness. Network, time,
random identifiers, and temporary roots are the only replay substitutions.

Snapshots may contain normalized CLI output, allowlisted Evidence Event facts,
Artifact metadata, Projection paths, and re-read outcome facts. They must not
contain research markdown, remote replies, source titles or links, credentials,
webhook endpoints, absolute paths, or private-pattern text.

To intentionally update snapshots, record them locally and review every diff:

```bash
nous-os check --mode full --record-snapshots
git diff -- tests/snapshots
```

CI never records snapshots.

## Optional live verification

`.github/workflows/live-interface-smoke.yml` runs weekly and on demand with
synthetic non-private input. It checks an external research feed and exercises
the notification webhook or Hermes Gateway only when their deployment settings
exist. An absent credential produces a visible `skipped` result, not a false
pass. Reports include outcome classes only and never endpoint values, secrets,
or remote content.

This lane does not block ordinary pull requests. Offline replay remains the
required deterministic contract; live smoke detects provider integration drift.
