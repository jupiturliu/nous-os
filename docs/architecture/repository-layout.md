# Repository layout

NOUS OS separates source, runtime artifacts, and deployable compositions:

- `src/nous_os/` contains the single Python distribution.
- `config/profiles/` contains versioned Harness compositions.
- `contracts/` contains machine-readable harness and domain contracts.
- `apps/web/` contains the static Web composition and Cloudflare Adapter.
- `examples/` contains runnable leaves, not reusable implementation.
- `tests/` exercises the same Interfaces used by callers.
- `$NOUS_OS_HOME` contains mutable Evidence Events, Artifacts, state, cache, and runtime Projections.

The Harness kernel is a deep Module: callers learn one lifecycle and capability Interface while configuration, ordering, validation, and teardown stay local. External systems sit at real Seams only when an in-memory or test Adapter also exists.
