---
title: "L3 synthesis · YYYY-MM-DD"
period_start: YYYY-MM-DD
period_end: YYYY-MM-DD
authored_by: Hermes (skill `research-line-l3-synthesis`)
status: draft  # set to `merged` only after operator review
---

# L3 synthesis · <YYYY-MM-DD>

Bi-weekly synthesis of the NOUS OS Research Line. Produced by Hermes; reviewed, edited, and merged by the operator. Becomes part of the public research-line corpus on merge.

The date in the filename and title is the Sunday on which the synthesis is produced; the period covered is the 14 days ending that Sunday.

This document follows the contract in `docs/research-line/hermes-integration.md` § L3. The structural sections below are required; their order is required; the boundaries in the L3 boundary list of `hermes-integration.md` are required.

## 1 · Period at a glance

Numeric snapshot of the last 14 days. Do not editorialize in this section — that is what sections 2–5 are for.

- **L1 capture days:** N (of expected ~14)
- **L2-promoted inbound notes:** N (over the 2 candidate weeks)
- **Session reviews completed:** N total · Sandbox N · trading-agent N · personal-knowledge N
- **Sub-line movements this period:** list any sub-line that changed status (e.g., L3 sub-line went from "methodology not pinned" → "pilot started")
- **Atlas additions this period:** N new anchors added to atlas (across which buckets)

## 2 · Most influential inbound notes

1–3 notes from the period. For each:

### <inbound note title> — [link]

- **What we learned:** one or two sentences on the load-bearing insight.
- **What we changed because of it:** specific doc / test / sub-line decision. If nothing changed, say so and explain why we still kept the note.

(Repeat for each.)

## 3 · Coverage observations

What did our reading actually look like this period?

- **Bucket distribution of promoted notes:** how many fell in each of the 6 atlas buckets.
- **Sources to remove:** any source from `nous_os.workflows.research_line::SOURCES` that produced zero promotions this period — but do not over-react to a single quiet bi-week; consider trend across recent periods.
- **Sources to add:** new candidate sources discovered during the period. Name + reason + first-pass keyword fit.
- **Keyword list adjustments:** any keyword that was load-bearing for ≥ 1 promotion this period, or any keyword that produced only firehose noise.
- **Languages:** were Chinese / non-English sources represented? Where did the manual inbound flow land?

## 4 · Instrument signals

The honest part. (a) and (b) are the near-term measurable instruments serving the (c) compounding-wisdom north star. At bi-weekly cadence, N is almost always tiny — be especially disciplined about not overclaiming.

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

This question is not testable at bi-week granularity. The honest framing each period is one short paragraph: *given the (a) and (b) directions in this 14-day window, and given prior periods, what is the multi-period trend on the north star — none yet, faint signal, clear signal?*

## 5 · What we were wrong about

First-class negative results. Predictions from prior periods (in pre-registration files under `docs/research-line/preregistration/` with `captured` date within this period's window) that did not hold up.

For each:

- **Prediction:** verbatim from the pre-registration.
- **Outcome:** what actually happened.
- **What it means for the model:** revised understanding.

If no completed pre-registrations in the period: say so. If completed but no negatives: that is itself worth flagging — it usually means we are not making bold-enough predictions, not that we are right about everything.

## 6 · Next period's planned shifts

Concrete. These feed the next 2 weeks' pre-registrations and L2 triage focus.

- **Sources / keywords / atlas adjustments to ship:** (proposed only — actual changes ship as separate operator-reviewed PRs)
- **Sub-line decisions:** any move from one status to the next.
- **Method adjustments:** any of the 6 method commitments to refine (rare — they are durable by design).
- **Open questions to carry forward:** items that did not get answered this period.

---

## Reference

- Spec: `docs/research-line/hermes-integration.md` § L3
- Prior synthesis: `docs/research-line/synthesis/<previous>.md`
- Research-line spec: `docs/research-line/research-line.md`
- Anchor atlas: `docs/research-line/anchor-atlas.md`
