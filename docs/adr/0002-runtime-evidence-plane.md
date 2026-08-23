# ADR 0002: Runtime and evidence plane

## Status

Accepted

## Decision

Mutable state lives below `$NOUS_OS_HOME`, defaulting to `~/.nous-os`. Workflows append versioned Evidence Events to `events/evidence.jsonl`; large or private payloads are stored as content-addressed Artifacts. Dashboard and research views are deterministic Projections.

Normal execution never updates tracked website data. `nous-os publish-site-data` is the only supported command that writes privacy-filtered Public Snapshots into the website source.
