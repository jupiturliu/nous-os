# NOUS OS Domain Context

## Domain language

- **Harness** — the runtime that composes selected capabilities, workflows, paths, and evidence policy from a Profile.
- **Profile** — a versioned YAML composition describing which Plugins and workflows a Harness starts.
- **Plugin** — a lifecycle-managed provider of named capabilities to a Harness.
- **Capability** — a named behavior registered by a Plugin and resolved by workflows through the Harness context.
- **Evidence Event** — an immutable JSONL record describing an observed action, result, or decision and its artifact references.
- **Artifact** — content too large or sensitive for an Evidence Event, stored separately and addressed by identifier and SHA-256.
- **Projection** — a deterministic view derived from Evidence Events, such as dashboard data or the latest research record.
- **Public Snapshot** — a privacy-filtered Projection explicitly published into the static website source.
- **Runtime Home** — mutable local state rooted at `$NOUS_OS_HOME`, defaulting to `~/.nous-os`.
- **Student Sandbox** — a privacy-first learning workflow that preserves the student's authorship and human agency.
- **Research Line** — the research intake and synthesis workflow.
- **Heartbeat** — the orchestration workflow that evaluates a run, records evidence, and refreshes runtime projections.
- **Trading Proof** — the read-only vertical evaluator used to demonstrate evidence-backed domain evaluation.
