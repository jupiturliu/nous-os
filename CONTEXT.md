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
- **Software Change** — a behavior-changing repository modification governed by one approved Spec and its Implementation Plan.
- **Spec** — a versioned YAML statement of Software Change intent, requirements, constraints, acceptance criteria, risks, and human authority.
- **Implementation Plan** — the approved YAML mapping from Spec requirements to affected repository paths and named safe checks.
- **Approval** — an explicit human decision recorded as JSON against immutable SHA-256 hashes of a Spec and Implementation Plan before implementation begins.
- **VerificationReport** — the final JSON result binding a committed Software Change to changed paths, named check outcomes, residual risks, and immutable input hashes.
- **Notification** — a privacy-allowlisted, best-effort signal that a workflow milestone occurred; notification failure never reverses a successfully completed workflow action.
- **Notification Adapter** — the configured delivery implementation for a Notification, initially an HTTPS webhook whose secret endpoint remains outside tracked source and evidence.
- **Gate** — a named, dependency-aware repository check with a stable passed, failed, or skipped outcome, executed locally and in CI through the same Harness verification Interface.
- **Scenario Replay** — a keyless execution that starts a real Profile through the shipping Harness entry path, substitutes only nondeterministic external Adapters, and verifies persisted world state.
- **Scenario Snapshot** — a reviewed, privacy-safe record of normalized CLI output, Evidence Event facts, Artifact metadata, Projections, and externally re-read scenario results.
