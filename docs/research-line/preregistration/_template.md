---
session_id: <SESSION_ID>
sub_line: L1 Student Sandbox | L2 trading-agent | L3 personal knowledge
captured: <YYYY-MM-DD>
operator: <name or initials>
observer: <name or initials, optional>
review_packet: <path after session; leave TBD before run>
review_index_row: docs/research-line/session-review-index.md#session-ledger
---

# Pre-registration · <SESSION_ID>

> Fill this **before** the session starts. 5 minutes max. Locks in expectations so that, after the fact, we can tell what we already knew vs what we learned.

## 1 · The single prediction

State one prediction the session will test. Specific, falsifiable, observable from the review packet alone.

> *(example)* The student will name at least 3 of the 4 reflection-card prompts in the post-session interview, and will identify at least one source they rejected during phase 4.

## 2 · What would make me revise my model

3 bullets. Concrete signals that, if observed, would change how we think about the loop — *not* just "the prediction was wrong."

- ...
- ...
- ...

## 3 · What I am NOT predicting

Name the things I deliberately have no opinion on, so that anything I notice in those areas counts as genuine discovery, not confirmation.

- ...

## 4 · Conditions

- Topic area (not raw private prompt): ...
- Session length: 20 minutes (Sandbox) | <other>
- Baseline condition? (no-AI / cold-chat-AI / none): ...
- Anything unusual about this session: ...

## 5 · Honest priors

What do I expect to happen, in plain language, in 1-2 sentences? Including the parts I would not stake on a prediction.

> ...

## 6 · Review packet link

Fill after the session:

- De-identified review packet:
- Session-review-index row updated: yes / no
- Research-to-product gate needed: yes / no

If the answer is `yes`, open a separate gate using `docs/research-line/research-to-product-gate.md`. Do not implement product changes inside the review packet.

---

**After the session:**

1. Save the review packet (Sandbox: export from `/demo/student-session-review.html` in the running Web composition; trading-agent: from `docs/review-template.md`).
2. In the review packet, link back to this preregistration file.
3. Update `docs/research-line/session-review-index.md`.
4. Mark the prediction in section 1 as **confirmed / partial / disconfirmed / inconclusive**.
5. Write 1 paragraph: what surprised me, what didn't, what changes about the loop design.
6. If changing product/protocol, fill the research-to-product gate first.

If `disconfirmed` and we still claim the loop "worked," we have drifted. That's the first-class negative result our method commitments require us to publish.
