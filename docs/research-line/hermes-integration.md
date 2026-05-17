# NOUS OS Research Line — Hermes Integration Spec (Wave 4)

This document specifies how Hermes runs the L2 (weekly triage) and L3 (quarterly synthesis) tiers of the Research Line external-input loop. It is the contract Codex implements on the Hermes side; it is the expectation the operator can hold Hermes to.

> **Status:** spec only. No Hermes-side code is written by this wave. Implementation is Wave 5, Codex-led.

## Why Hermes for L2/L3 (and explicitly not L1)

L1 capture is mechanical: fetch RSS, match keywords, write markdown. Reproducible, auditable, zero judgment. GitHub Actions + Python stdlib does this perfectly (see `cron-design.md`).

L2 and L3 are judgment work:

- L2: *"which 1–3 of this week's raw entries deserve a full 1-page note?"*
- L3: *"what did we read this quarter and what actually changed in our practice because of it?"*

Both require reading across many documents, both produce prose, both must leave a reviewable artifact (a PR) for the operator. This is exactly Hermes' job: cognitive control plane work where the answer is structured prose, not a key lookup.

The reverse — running L2/L3 in GitHub Actions with raw scripts — would require either calling out to an LLM from CI (introduces API-key complexity) or hand-writing scoring rules (defeats the whole point of judgment). The reverse — running L1 in Hermes — would introduce opaque LLM selection into a layer that must stay reproducible. Each tier sits where it sits because of what it is, not because of which tool is convenient.

## L2 · Weekly Triage

### Input

- All merged `docs/research-line/inbound/_inbox/YYYY-MM-DD.md` files from the past 7 days. ("Merged" = the L1 PR was reviewed and merged by the operator; closed PRs are NOT in scope.)
- Current state of `docs/research-line/anchor-atlas.md` (so Hermes knows which anchors are already `queued`, `scanned`, or `note-written`).
- The 3 seed inbound notes under `docs/research-line/inbound/2026-05-17-*.md` (as worked examples of the target voice and structure).
- `docs/research-line/inbound/_template.md` (the format every new note must follow).
- `docs/research-line/research-line.md` and `anchor-atlas.md` (so Hermes knows the line's positioning).

### What Hermes produces

A single PR per week, titled `L2 triage · week of YYYY-MM-DD`, containing:

1. **0 to 3 new inbound notes** under `docs/research-line/inbound/`, filenames `YYYY-MM-DD-<short-slug>.md`, each strictly following `_template.md` structure.
2. **Atlas updates** in *both* `docs/research-line/anchor-atlas.md` and `research-line-atlas.html`: flip the relevant anchor from `queued` / `scanned` to `note-written` and add the link to the inbound file.
3. **A one-paragraph "why these N" preface** in the PR description (NOT in any committed file), explaining the selection rationale against the rubric below.

If Hermes finds nothing worth promoting in a given week, the PR is still opened — empty of inbound changes — with a body explaining what was reviewed and why nothing rose to the bar. This is a first-class outcome, not a failure.

### Selection rubric (the L2 judgment Hermes applies)

For each candidate entry from the weekly inbox, score:

| Criterion | Question | Disqualifier |
|---|---|---|
| Distinctness | Does this add something not yet in our atlas (new anchor, new angle, fresh evidence)? | Substantially overlapping with an existing `note-written` anchor → demote. |
| Anchor specificity | Does it map cleanly to one of the 6 atlas buckets? | If it fits 3+ buckets equally well, it's too vague → demote. |
| Defensibility | Could a human write a credible "where we differ / what we add" line for this work? | If the differentiation would be hand-wavy, the work isn't ready to be `note-written` → leave as `scanned` in the atlas instead. |
| Freshness | Was the source published in the past 2 weeks? | Older items can still be promoted but only with explicit reasoning in the PR body. |
| Source diversity | Does promoting this entry duplicate the same source as last week's promotion? | If yes, prefer a different bucket this week. |

The cap is **3 per week**. If 5 entries score equally well, pick 3 and explain the choice in the PR body. If 0 entries pass, that is the right answer — do not lower the bar to hit a quota.

### Hermes boundaries (what it must NOT do)

- Never auto-merge the PR. The operator gates every promotion.
- Never edit existing inbound notes. New notes only.
- Never modify load-bearing structural sections of `research-line.md`, `anchor-atlas.md`, or `research-line-atlas.html` (north star, sub-lines, method commitments, bucket headings). Only append to bucket bodies and flip anchor status.
- Never refer to the operator, the operator's family, or any identifying detail in any draft note. If an inbox entry contained identifying detail that slipped past the L1 redaction, surface it in the PR body as a flag and exclude the entry.
- Never make HTTP requests to "verify" or "expand" an L1 entry. Work only from what L1 captured. (This preserves L1 as the canonical snapshot.)
- Never claim an anchor is "definitively positioned" — `note-written` means *we have written down our positioning*, not that the positioning is final.
- Never use the word "validated" / "confirmed" / "proven" about our own (a)/(b)/(c) instruments. Those words are reserved for outputs of session evidence, not Hermes prose.

### Cadence

Sundays, 12:00 UTC. After the week's final L1 capture has had time to be operator-reviewed.

If a Sunday's PR is missed (Hermes downtime, network), Hermes retries the next available 12-hour window. After 72 hours stale, the week is considered skipped and Hermes resumes next Sunday — do not back-fill.

### Operator's L2 cycle

- ~10 minutes per Sunday afternoon: read 1–3 draft notes, edit prose if needed, accept or reject.
- Reject = close PR. Acceptable failure mode; record reason in close comment so Hermes can learn (manually fed into the next prompt update).
- Merge → CI green → Cloudflare deploys → notes appear under `nousos.ai/docs/research-line/inbound/` and atlas status pills flip on `nousos.ai/research-line-atlas`.

## L3 · Quarterly Synthesis

### Input

- All inbound notes promoted during the quarter (top-level `docs/research-line/inbound/*.md`, excluding `_inbox/`).
- All session review packets in the quarter (Sandbox: `04 Reviews/Student Sandbox v1 Trial Review *.md`; trading-agent: outcome review packets, location TBD per Codex's evidence pipeline).
- The previous quarter's synthesis (`docs/research-line/synthesis/<prev>.md`), for continuity.
- `docs/research-line/research-line.md` § 2 (the two near-term instruments).
- `docs/research-line/synthesis/_template.md` (the format).

### What Hermes produces

A PR titled `L3 synthesis · YYYY-QN`, adding `docs/research-line/synthesis/YYYY-QN.md` (and only that file). Structure follows `_template.md`:

1. **Quarter at a glance** — N L1 days, N L2 promotions, N session reviews, N sub-line moves.
2. **3–5 most influential inbound notes** of the quarter, with one paragraph each on what they actually changed in our internal practice (specific doc / test / sub-line decision).
3. **Coverage observations** — new sources added or removed; keyword list adjustments; bucket health.
4. **Instrument signals** — did (a) capability-without-AI delta show any direction? did (b) calibrated trust show any direction? Be explicit at low N: "1 session, 1 direction, not validated".
5. **What we were wrong about** — predictions from prior quarters that didn't hold up. First-class negative results.
6. **Next quarter's planned shifts** — concrete (this list goes into the next pre-registration round).

### Hermes boundaries (L3-specific, in addition to L2's)

- Never make causal claims that exceed the evidence base. At N ≤ 5 sessions, the strongest allowable claim is "direction signal, not validation."
- Never extrapolate Sandbox findings to trading-agent or vice versa. They are different sub-lines with different unit definitions; cross-pollination requires explicit reasoning.
- Never recommend dropping a method commitment (pre-register, two raters, de-identified packets, negative results first-class, explicit N, no instrument inflation). Method commitments are durable.
- The synthesis is allowed to *propose* changes to the source list, keyword list, or atlas bucket structure; never *implement* those changes in the same PR. Structural changes are separate operator-reviewed PRs.

### Cadence

First Sunday of Jan / Apr / Jul / Oct, 12:00 UTC. First scheduled run: **2026-07-05** (start of Q3 2026), which gives roughly 7 weeks of L2 activity to synthesize from.

## Hermes skill structure

Two skills to be registered Hermes-side:

| Skill name | Trigger | Input contract | Output contract |
|---|---|---|---|
| `research-line-l2-triage` | weekly cron (Hermes-side) | inbox files of past 7 days + atlas + 3 seed notes | PR with 0–3 inbound notes + atlas updates |
| `research-line-l3-synthesis` | quarterly cron (Hermes-side) | inbound notes of quarter + session reviews + prior synthesis | PR with `synthesis/YYYY-QN.md` |

Skill prompt structure is Codex's call but should:
1. Embed `inbound/_template.md` (L2) and `synthesis/_template.md` (L3) verbatim in the system prompt.
2. Embed `_atlas-rubric` (the criterion table above for L2; the boundary list above for L3) verbatim.
3. Pull the input documents at runtime, not at prompt-bake time.
4. Output structured (JSON or PR-body markdown) for the GitHub PR creation step.

## Integration with existing infrastructure

### Trigger mechanism

Hermes-side scheduling — not GitHub Actions. Reasons:

- L2/L3 work belongs to Hermes operational responsibility (it is the cognitive job Hermes exists for); putting it in CI scatters concerns.
- Hermes can use its full skill / playbook / TrustMem context, which CI cannot.
- Operator already monitors Hermes; one fewer place to look.

Hermes uses whatever cron-equivalent it has internally. If Hermes lacks a scheduler, Codex adds one (it's a one-time platform addition).

### Repo write access

Hermes opens PRs against `jupiturliu/nous-os` using a **fine-grained personal access token**:

- Repository access: `jupiturliu/nous-os` only.
- Permissions: `Contents: Read and write`, `Pull requests: Read and write`. Nothing else.
- Expiration: 365 days. Re-issue annually; previous-quarter L3 must note the renewal date.
- Storage: Hermes' secret store (not GitHub Actions secrets, not in the repo, not in any docs).

This is a different token than the Cloudflare deploy chain uses. Two scopes, one purpose each.

### Branch / PR conventions

| Tier | Branch | PR title | PR label |
|---|---|---|---|
| L2 | `research-line/l2-triage-YYYY-MM-DD` | `L2 triage · week of YYYY-MM-DD` | `research-line:l2-triage` |
| L3 | `research-line/l3-synthesis-YYYY-QN` | `L3 synthesis · YYYY-QN` | `research-line:l3-synthesis` |

Labels need not exist before Hermes runs; if Hermes hits a missing-label error, it retries label creation then re-runs PR creation.

## Verification

### Per-PR contract test (downstream, after first PR lands)

When the first L2 PR opens, add a contract test to `tests/test_research_line_capture.py` (or a new sibling file) that asserts:

- L2 PR adds files only under `docs/research-line/inbound/` (no top-level changes outside this path + atlas updates).
- Each new inbound note matches the required sections from `_template.md` (the same assertions as `test_research_line_templates_exist_and_are_well_formed` but applied per-file).
- The atlas updates flip status pills for the same anchors that the new notes cover.

L3 contract test, when the first synthesis lands:

- File path is `docs/research-line/synthesis/YYYY-QN.md`.
- Has the 6 required sections from `synthesis/_template.md`.
- No claim contains the words "validated" / "confirmed" / "proven" applied to (a)/(b)/(c) instruments at N < 10 (the threshold is operator-tunable).

These tests do not exist yet; they are written reactively when the first Hermes PR lands.

### Operator monitoring

| Cadence | Check |
|---|---|
| Sunday 13:00 UTC | An `L2 triage · …` PR exists for the prior week. If missing, page Hermes operator. |
| Monthly | Count of merged L2 PRs ≥ 3 in the month. If 0, something is broken or the keyword list is too narrow. |
| Quarterly | An `L3 synthesis · YYYY-QN` PR exists in the first Sunday of the quarter. |
| Quarterly | Merge rate of Hermes-produced PRs ≥ 50% over the trailing quarter. Below 50% = prompt re-tuning needed; Hermes is misjudging the bar. |

## What this wave explicitly does NOT do

- **No Hermes-side code.** Skill implementation, prompt authoring, integration testing — all Wave 5 (Codex).
- **No changes to L1.** GitHub Actions cron stays as-is.
- **No new public HTML.** L2/L3 outputs already become public the moment they are merged (inbound/* and synthesis/* are shipped by `stage_static_site.sh`). A dedicated feed-style HTML page can come later when there is enough content to warrant a separate aggregator surface.
- **No retroactive triage.** The 3 seed inbound notes from 2026-05-17 stay as they are. Hermes does not re-judge or revise them.
- **No coupling to trading-agent's Hermes deployment.** Hermes' L2/L3 work and Hermes' trading-agent work share the same Hermes runtime but are separate skills with separate triggers and separate write-paths. They must not call each other.

## Open questions for Wave 5 (Codex)

1. Does Hermes already have a scheduler, or does Wave 5 need to add one?
2. Where in the Hermes skill registry do `research-line-l2-triage` and `research-line-l3-synthesis` belong (with student-agent-shaped skills? with a new "research-ops" cluster?).
3. Does Hermes have an existing pattern for reading from a local git checkout vs the GitHub API? Either works; pick once and document.
4. What is the Hermes-side telemetry for "skill ran, produced N tokens, exited with code"? L2/L3 monitoring needs this.
5. Should Hermes' L2 prompt embed the past 4 weeks of merged inbound notes as in-context examples, or only the 3 seeds? Token budget question.

## Related documents

- `docs/research-line/research-line.md` — the line's spec
- `docs/research-line/anchor-atlas.md` — what L2 is choosing against
- `docs/research-line/cron-design.md` — L1 architecture
- `docs/research-line/inbound/_template.md` — L2 output format
- `docs/research-line/preregistration/_template.md` — session-side counterpart
- `docs/research-line/synthesis/_template.md` — L3 output format (added in this wave)
- `docs/cloudflare-hermes-architecture.md` — Hermes' deployment context
