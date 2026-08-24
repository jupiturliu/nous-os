# NOUS OS Architecture

NOUS OS is an evidence-backed Harness for human-AI co-evolution workflows. It composes existing capabilities; Hermes remains the model/tool provider seam rather than being reimplemented here.

## Runtime composition

```text
YAML Profile v2 ── explicit Effect allowlist
    │
    ▼
Python Harness kernel ── authorizes Effects, loads Plugins in dependency order
    │
    ├── Permission Policy + Invariant Registry
    ├── Credential Provider + Telemetry Sink Adapters
    ├── Student Sandbox workflow ── Hermes Gateway Adapter
    ├── Research Line workflow
    ├── Heartbeat workflow ──────── installed Synapse or local Adapter
    └── Trading Proof evaluator ─── read-only filesystem Adapter
    │
    ▼
Evidence Event log + content-addressed Artifacts
    │
    ▼
Deterministic runtime Projections
    │ explicit publish only
    ▼
Public website snapshots
```

The kernel's small Interface owns Profile validation, Effect authorization, dependency ordering, Capability registration, phased Invariants, readiness, failure handling, and robust reverse teardown. This Depth provides Leverage to every workflow and keeps lifecycle knowledge local. Plugin start is fail closed: unauthorized Effects are rejected before any Plugin starts. Stop continues after individual failures, removes every provided Capability, and reports attributable aggregate errors.

Credential values stay outside tracked composition. Profiles contain only Credential References; the Credential Provider resolves the current value once per operation. Operational Telemetry uses a closed record vocabulary, is disabled by default, and contains Sink failure so diagnostic Implementation details cannot change workflow success.

## Source and artifact planes

| Plane | Location | Responsibility |
|---|---|---|
| Python source | `src/nous_os/` | Kernel, Plugins, workflows, evaluation and Web composition |
| Composition source | `config/profiles/` | Versioned YAML Profiles |
| Machine contracts | `contracts/` | Harness inventory and domain compilation bundles |
| Web source | `apps/web/` | Static source, staging manifest and Cloudflare Adapter |
| Runtime artifacts | `$NOUS_OS_HOME` | Events, Artifacts, Projections, state and cache |
| Staged deploy | `_site/` | Generated Cloudflare static asset tree |

Mutable runtime data never belongs in the source plane. `$NOUS_OS_HOME` defaults to `~/.nous-os`; tests always provide an isolated temporary directory.

## Evidence model

Every durable workflow result is represented by a versioned append-only Evidence Event. Large or private payloads are stored as immutable, SHA-256-addressed Artifacts and referenced from the event. Dashboard and research files are reconstructed from the event plus its verified Artifact.

`nous-os publish-site-data` is the only Interface that updates tracked Public Snapshots. It rejects private text patterns, secret-like fields and local filesystem paths.

## Web composition

The Python Web Module owns the stable local route Interface:

- `GET /api/health`
- `GET /api/ready`
- `POST /api/hermes-student-agent`
- `GET|POST /api/student-sandbox-session`
- `GET /api/dashboard-data`
- `POST /api/run-heartbeat`

Cloudflare Worker Static Assets serves the public website and forwards `/api/*` to the Python origin. Browser code never receives Hermes or model-provider credentials.

`/api/health` answers process liveness. `/api/ready` reports whether Harness startup and after-start Invariants succeeded, using only safe failure reasons.

## Human-AI flywheel

```text
Human intent
    → AI first pass
    → human correction or safety boundary
    → evidence and memory update
    → AI second pass
    → deterministic evaluation and reflection
    → human retains goals, values, verification and final responsibility
```

TrustMem, Synapse and Aria may supply external Implementations. The Harness depends only on named capabilities at explicit Seams, so the deterministic local Adapters remain runnable without sibling repositories.

See `docs/architecture/repository-layout.md` and `docs/adr/` for layout and decision records.
