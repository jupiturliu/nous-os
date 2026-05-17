# NOUS OS Production Runtime

NOUS OS keeps the public demo deterministic, but production deployment should not rely on an in-memory-only runtime.

## Backend Policy

Use `NOUS_OS_ENV=production` to activate production backend resolution.

| Setting | Behavior |
|---------|----------|
| `NOUS_OS_RUNTIME_BACKEND=redis` | Use Redis for Synapse EventBus/Blackboard and SQLite for local episode artifacts. |
| `NOUS_OS_RUNTIME_BACKEND=sqlite` | Use SQLite for durable NOUS episode artifacts; Synapse worker fanout remains local-memory because upstream Synapse supports `memory` and `redis`. |
| unset + `REDIS_URL` present | Resolve to Redis. |
| unset + no `REDIS_URL` | Resolve to SQLite instead of pretending MemoryBackend is production durable state. |
| `NOUS_OS_RUNTIME_BACKEND=memory` in production | Resolved to SQLite unless `NOUS_OS_ALLOW_MEMORY_IN_PRODUCTION=1` is explicitly set for a temporary diagnostic run. |

Local development and CI continue to default to memory for fast deterministic tests.

## Recommended Production Environment

```bash
export NOUS_OS_ENV=production
export NOUS_OS_RUNTIME_BACKEND=redis
export REDIS_URL=redis://localhost:6379
```

For a single-node deployment without Redis:

```bash
export NOUS_OS_ENV=production
export NOUS_OS_RUNTIME_BACKEND=sqlite
```

The local episode logger writes SQLite-compatible artifacts at:

```text
examples/runtime/data/episodes/episodes.sqlite
```

## Runtime Contract

`examples/nousos_heartbeat_demo.py` exposes `runtime_backend_policy()` in the dashboard snapshot under `runtime_backend`. This makes the chosen production behavior visible and testable.
