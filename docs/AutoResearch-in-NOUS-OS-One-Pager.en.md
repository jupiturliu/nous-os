# AutoResearch in NOUS OS — One Pager

## One-line definition

**AutoResearch is the research engine of NOUS OS.**

If:
- **TrustMem** is the memory layer
- **Synapse** is the coordination layer
- **Aria** is the consciousness and judgment layer

then:
- **AutoResearch** is the layer that helps the system discover problems, design experiments, call validators, compare results, and decide what to improve next.

It upgrades the system from “something that can answer” into “something that can continuously improve.”

---

## Why it matters

A real cognitive system cannot stop at:
- remembering
- understanding
- answering

It must also be able to:
- detect anomalies
- form hypotheses
- design experiments
- validate hypotheses
- derive conclusions
- drive the next iteration

That is the role of AutoResearch.

---

## Position inside NOUS OS

- **TrustMem** = memory layer (what to remember, what to trust)
- **Synapse** = neural layer (who executes, how coordination happens)
- **Aria** = consciousness layer (why, judgment, human alignment)
- **AutoResearch** = research layer (detect → experiment → validate → evolve)

---

## What it is not

A normal assistant / search / RAG system typically:
- answers the question you ask
- summarizes information
- gives a suggestion

AutoResearch works at a higher level.

It turns research itself into an executable loop:
1. generate testable hypotheses
2. design baseline + variants
3. call backtesting / replay / benchmarks
4. compare outcomes
5. recommend the next move

---

## What it already does in trading-agent

### DayTrading
AutoResearch helped us:
- realize that “no trades today” is not an answer but a research problem
- decompose the funnel into:
  - in-play filter
  - ORB
  - VWAP Bounce
  - Afternoon Breakout
  - scheduling layer
- identify the real bottlenecks:
  - insufficient scheduling
  - `catalyst_vol_mult`
  - `min_breakout_pct`
- build a production-aligned researcher
- recommend new paper-trading parameters:

```yaml
catalyst_vol_mult: 1.5
min_breakout_pct: 0.002
```

### Long-Term
AutoResearch helped us:
- show that “no new signals” is not because the thesis is absent
- decompose the funnel into:
  - portfolio construction / same-subsector exclusion
  - RS
  - momentum
  - technical confirmation
- falsify several candidate parameter directions:
  - loosening `min_rs`
  - loosening `min_momentum`
- conclude that the next real research direction is:
  - **same-subsector exclusion study**

---

## Relationship with Backtesting

### Backtesting answers:
> “How would this exact rule set have performed historically?”

### AutoResearch answers:
> “What is the next rule set worth testing, how should it be compared, and which direction is worth taking into paper trading?”

So the relationship is:

```text
AutoResearch designs the experiment
    ↓
Backtesting acts as the validator
    ↓
Aria performs attribution and decision support
    ↓
Move the best candidate into paper trading / production
```

---

## Why it is a core NOUS OS layer

Without AutoResearch, NOUS OS would still be:
- a system that remembers
- a system that coordinates
- a system that answers

With AutoResearch, it becomes:
- a system that detects its own problems
- designs experiments
- self-corrects
- evolves over time

In other words:

> **AutoResearch is what turns NOUS OS from an intelligent assistant into a true cognitive operating system.**

---

## Product significance

If we want to explain NOUS OS externally, this layer matters because it shifts the product from:
- **generation**

to:
- **compounding intelligence**

NOUS OS does not just answer well.
It gets better over time because it can research itself.

---

## Current experimental status (2026-04-06)

### Already concluded

#### DayTrading
Recommended next paper-trading parameters:
```yaml
catalyst_vol_mult: 1.5
min_breakout_pct: 0.002
```

#### Long-Term parameter layer
These directions underperformed baseline:
- `min_momentum = 0.015`
- `min_momentum = 0.010`
- `min_rs = 1.03`
- `min_rs = 1.00`
- `min_rs = 1.03 + min_momentum = 0.015`

Therefore:
> Do not continue prioritizing `min_rs` / `min_momentum` relaxation.

### Currently in progress
- production-aligned long-term structural researcher
- structural comparison across:
  - baseline
  - max 2 per subsector
  - leader + challenger
  - profit-gated second entry

---

## Final takeaway

> **AutoResearch does not simply automate thinking. It automates the transformation of judgment into a testable, comparable, evolvable research process.**
