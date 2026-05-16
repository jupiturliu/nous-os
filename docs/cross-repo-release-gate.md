# Cross-Repo Release Gate

NOUS OS V2 spans multiple repositories. The release gate is a read-only readiness snapshot for public/demo releases; it must not mutate runtime state, broker state, risk config, credentials, ledgers, or live queues.

## Repository Matrix

| Repo | Current command | Fallback command | Docs link | Secret/path scan | Status | Owner |
|------|-----------------|------------------|-----------|------------------|--------|-------|
| `nous-os` | `python3 -m unittest discover -s tests -v` | `python3 examples/nousos_demo.py` | `README.md`, `NOUS-OS-PHASE3.md` | required | unknown | Hermes |
| `trustmem` | project check script if available | `python3 tools/knowledge_search.py agent --top 1` | `README.md` | required | unknown | Hermes |
| `synapse` | `make test` | `python3 synapse.py test` | `README.md`, `ARCHITECTURE.md` | required | unknown | Hermes |
| `hermes-agent` | focused docs/tool tests | `python3 -m pytest tests -q` | `README.md`, docs | required | unknown | Hermes |
| `trading-agent` | `PYTHONPATH=. venv/bin/python3 -m pytest focused tests` | `PYTHONPATH=. venv/bin/python3 -m pytest tests/test_documentation_contract.py -q --tb=short` | `docs/harness` | required | unknown | Hermes |

## Read-Only Checks

The default release gate checks:

- repository exists
- git status is readable
- dirty/untracked state is reported
- public docs are scanned for obvious private absolute paths
- public docs are scanned for conservative secret-like tokens

Long tests are not run unless an operator explicitly passes `--run-tests`.

## Command

```bash
python3 scripts/check_cross_repo_release_gate.py --workspace /Users/liyao/nousos --json
```

Optional long validation:

```bash
python3 scripts/check_cross_repo_release_gate.py --workspace /Users/liyao/nousos --run-tests --json
```

## Boundary

This gate reports release readiness only. It does not authorize domain actions, broker actions, risk changes, live promotion, or runtime mutation.
