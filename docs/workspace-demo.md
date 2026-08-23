# External Runtime Adapters

The former workspace-wired demo modified `sys.path` and coupled NOUS OS to a particular sibling-directory layout. It has been replaced by the Harness capability Interface.

## Heartbeat

Run the deterministic local Adapter:

```bash
NOUS_OS_HOME=/tmp/nous-os-demo nous-os run heartbeat --profile research
```

If Synapse is installed in the Python environment, Heartbeat may use its runtime Implementation. It no longer searches for or imports sibling repositories by filesystem position.

## Trading Proof

The read-only Trading evaluator accepts an explicit workspace through its constructor. For the Heartbeat demonstration, set:

```bash
NOUS_TRADING_WORKSPACE=/path/to/workspace nous-os run heartbeat --profile trading-proof --demo-mode trading_vertical
```

All mutable evidence, state and Projections remain under `$NOUS_OS_HOME`.
