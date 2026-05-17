---
title: "L3 synthesis · YYYY-QN"
quarter: YYYY-QN
period_start: YYYY-MM-DD
period_end: YYYY-MM-DD
authored_by: Hermes (skill `research-line-l3-synthesis`)
status: draft  # set to `merged` only after operator review
---

# L3 synthesis · <YYYY-QN>

Quarterly synthesis of the NOUS OS Research Line. Produced by Hermes; reviewed, edited, and merged by the operator. Becomes part of the public research-line corpus on merge.

This document follows the contract in `docs/research-line/hermes-integration.md` § L3. The structural sections below are required; their order is required; the boundaries in the L3 boundary list of `hermes-integration.md` are required.

## 1 · Quarter at a glance

Numeric snapshot. Do not editorialize in this section — that is what sections 2–5 are for.

- **L1 capture days:** N (of expected M)
- **L2-promoted inbound notes:** N (of N candidate weeks)
- **Session reviews completed:** N total · Sandbox N · trading-agent N · personal-knowledge N
- **Sub-line movements this quarter:** list any sub-line that changed status (e.g., L3 sub-line went from "methodology not pinned" → "pilot started")
- **Atlas additions this quarter:** N new anchors added to atlas (across which buckets)

## 2 · Most influential inbound notes

3–5 notes from the quarter. For each:

### <inbound note title> — [link]

- **What we learned:** one or two sentences on the load-bearing insight.
- **What we changed because of it:** specific doc / test / sub-line decision. If nothing changed, say so and explain why we still kept the note.

(Repeat for each.)

## 3 · Coverage observations

What did our reading actually look like this quarter?

- **Bucket distribution of promoted notes:** how many fell in each of the 6 atlas buckets.
- **Sources to remove:** any source from `scripts/research_line_capture.py::SOURCES` that produced zero promotions this quarter. Explicitly name + reason.
- **Sources to add:** new candidate sources discovered during the quarter. Name + reason + first-pass keyword fit.
- **Keyword list adjustments:** any keyword that was load-bearing for ≥ 1 promotion this quarter, or any keyword that produced only firehose noise.
- **Languages:** were Chinese / non-English sources represented? Where did the manual inbound flow land?

## 4 · Instrument signals

The honest part. (a) and (b) are the near-term measurable instruments serving the (c) compounding-wisdom north star.

### (a) Capability-without-AI delta

- **Sessions contributing data:** N
- **Direction observed:** up / down / no signal / not enough data
- **Strongest example:** which session and what it showed
- **Anti-example, if any:** session where the direction reversed

At N < 5: state "direction signal, not validation" verbatim. Do not use "validated", "confirmed", or "proven".

### (b) Calibrated trust + responsibility retention

- **Cycles contributing data:** N (across Sandbox + trading-agent)
- **Direction observed:** up / down / no signal / not enough data
- **Strongest example:** which cycle and what it showed
- **Anti-example, if any:**

### (c) Compounding wisdom (north star)

This question is not testable at quarter granularity. The honest framing each quarter is one paragraph: *given the (a) and (b) directions this quarter, and given prior quarters, what is the multi-quarter trend on the north star — none yet, faint signal, clear signal?*

## 5 · What we were wrong about

First-class negative results. Predictions from prior quarters (in pre-registration files under `docs/research-line/preregistration/`) that did not hold up.

For each:

- **Prediction:** verbatim from the pre-registration.
- **Outcome:** what actually happened.
- **What it means for the model:** revised understanding.

If no negative results: that is itself worth flagging. It usually means we are not making bold-enough predictions, not that we are right about everything.

## 6 · Next quarter's planned shifts

Concrete. These feed the next round of pre-registrations.

- **Sources / keywords / atlas adjustments to ship:** (proposed only — actual changes ship as separate operator-reviewed PRs)
- **Sub-line decisions:** any move from one status to the next.
- **Method adjustments:** any of the 6 method commitments to refine (rare — they are durable by design).
- **Open questions to carry forward:** items that did not get answered this quarter.

---

## Reference

- Spec: `docs/research-line/hermes-integration.md` § L3
- Prior synthesis: `docs/research-line/synthesis/<previous>.md`
- Research-line spec: `docs/research-line/research-line.md`
- Anchor atlas: `docs/research-line/anchor-atlas.md`
