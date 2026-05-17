# Human-AI Co-Evolution Theory Track Development Plan

> Source plan: `docs/plans/2026-05-16-human-ai-coevolution-theory-track-plan.md`

## Goal

Turn the NOUS OS theory track into a disciplined research-development lane. The lane should produce theory artifacts, review protocols, and proof-bed mappings that explain what the infrastructure is for without expanding the product surface.

The core development question is:

```text
Does this make the human-agent pair wiser, more capable, more reflective, and more responsible over time?
```

If a task does not answer that question, it belongs outside this track.

## Operating Constraints

- Treat TrustMem, Synapse, Obsidian, Hermes, dashboards, Student Sandbox, and trading-agent as experimental apparatus.
- Do not add new agent runtimes, SaaS surfaces, login flows, autonomous execution, or product packaging.
- Keep repo docs as the source of truth for artifact contracts and verification.
- Keep Obsidian notes as the human-facing synthesis and discussion surface.
- Prefer small, reviewable Markdown/theory changes with explicit acceptance criteria.
- Any metric added must distinguish qualitative observation from measurable proxy; avoid fake precision.

## Phase 0 — Baseline Audit

**Objective:** Confirm what already exists before adding new theory work.

**Files to inspect:**

- `docs/human-ai-symbiosis-self-evolution.md`
- `docs/human-ai-coevolution-model-v0.md`
- `docs/self-evolution-metrics-v0.md`
- `docs/memory-philosophy-v0.md`
- `docs/education-research-narrative.md`
- `docs/student-sandbox-v1-trial-guide.md`
- `docs/student-sandbox-v1-review-template.md`
- `/Users/liyao/Documents/nousos/NousOS/00 North Star/NOUS OS Human-AI Symbiosis and Self-Evolution Thesis.md`

**Acceptance criteria:**

- Existing theory artifacts are listed as complete, partial, or missing.
- Gaps are mapped to the four deliverables in the source plan.
- No implementation task starts until the gap list is explicit.

## Phase 1 — Theory Artifact Freeze v0

**Objective:** Make the three core theory docs internally consistent and stable enough to reference from demos, reviews, and future plans.

**Tasks:**

1. Review `docs/human-ai-coevolution-model-v0.md` against the source plan.
2. Review `docs/self-evolution-metrics-v0.md` against the current CLS v2 / research-record fields.
3. Review `docs/memory-philosophy-v0.md` against TrustMem boundaries and Student Sandbox privacy constraints.
4. Add a short "Status / How to use this document" block to each theory doc if missing.
5. Cross-link the three theory docs and the original symbiosis thesis.

**Acceptance criteria:**

- The model doc defines the roles: human, agent, memory, evidence, boundary, review.
- The model doc defines the 7-stage minimum viable co-evolution loop.
- The model doc separates human evolution, agent evolution, and relationship evolution.
- The metrics doc separates human-side, agent-side, and relationship metrics.
- The metrics doc marks qualitative observations separately from measurable proxies.
- The memory doc defines remember, challenge, decay, and forget rules.
- The memory doc explicitly rejects stale personalization as the goal.

## Phase 2 — Proof-Bed Mapping

**Objective:** Tie theory claims to the two proof beds without making either proof bed the goal.

**Tasks:**

1. Add a "Theory mapping" section to `docs/student-sandbox-v1-trial-guide.md` or a linked appendix.
2. Add a "Theory mapping" section to the trading-agent / first-vertical docs:
   - `docs/second-vertical-entry-criteria.md`
   - `docs/domain-evaluator-interface.md`
   - or a small new bridge doc if existing docs would become noisy.
3. Map each proof bed to:
   - human evolution signals;
   - agent evolution signals;
   - relationship calibration signals;
   - failure modes being tested;
   - evidence artifacts that can support claims.

**Acceptance criteria:**

- Student Sandbox is described as a learning-boundary, fact-boundary, privacy-boundary, and reflection-quality proof bed.
- trading-agent is described as a decision-boundary, responsibility-boundary, outcome-review, and evidence-linked learning proof bed.
- No doc implies students should copy trading behavior or that trading-agent is NOUS OS's commercialization endpoint.

## Phase 3 — Review Protocol Upgrade

**Objective:** Make reviews collect theory evidence, not only UI or demo feedback.

**Tasks:**

1. Update `docs/review-template.md` with theory-track questions:
   - What changed in the human?
   - What changed in the agent?
   - What changed in the relationship?
   - What should be remembered, challenged, decayed, or forgotten?
2. Update `docs/student-sandbox-v1-review-template.md` to include:
   - human capability delta;
   - trust calibration;
   - reflection quality;
   - independence preservation;
   - source discernment.
3. Add a minimal example review note in Obsidian only after a real or simulated review is clearly labeled as such.

**Acceptance criteria:**

- Review templates can produce evidence for the theory docs.
- Review templates do not grade students.
- Review templates separate observation from interpretation.

## Phase 4 — Obsidian Synthesis

**Objective:** Keep the theory track visible in the human-facing NOUS OS workspace.

**Create/update:**

`/Users/liyao/Documents/nousos/NousOS/00 North Star/NOUS OS Human-AI Co-Evolution Theory Track.md`

**Required sections:**

- Theory track north star.
- Links to:
  - `NOUS OS Human-AI Symbiosis and Self-Evolution Thesis.md`;
  - `docs/human-ai-coevolution-model-v0.md`;
  - `docs/self-evolution-metrics-v0.md`;
  - `docs/memory-philosophy-v0.md`.
- Summary of the model, metrics, and memory philosophy.
- Current proof beds and what each tests.
- Open research questions for discussion.
- Reminder that infrastructure is experimental apparatus, not the goal.

**Acceptance criteria:**

- Obsidian note exists under `00 North Star`.
- It is a synthesis, not a duplicate of the repo docs.
- It clearly says repo docs are source of truth for contracts and verification.

## Phase 5 — Public Narrative Alignment

**Objective:** Make the public site and README reflect the theory track without overwhelming first-time visitors.

**Tasks:**

1. Add lightweight links from `README.md` to the theory docs after they are stable.
2. Consider adding one small "Theory track" link or sentence on `about.html`, not the homepage hero.
3. Keep homepage focused on the live demo and first-vertical proof; do not turn it into a theory paper.

**Acceptance criteria:**

- Public narrative says NOUS OS studies human-AI co-evolution, not just agent infrastructure.
- About page can explain why the theory matters.
- Homepage remains concise and demo-oriented.

## Verification

Run after repo changes:

```bash
cd /Users/liyao/nousos/nous-os
python3 -m unittest discover -s tests -v
python3 scripts/check_harness_inventory.py --json
git diff --check
```

If Obsidian notes are updated, verify paths stay inside:

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-/Users/liyao/Documents/nousos}"
realpath "$VAULT"
realpath "$VAULT/NousOS/00 North Star/NOUS OS Human-AI Co-Evolution Theory Track.md"
```

## Definition of Done

The theory track v0 is done when:

- the three core repo docs exist and cross-link each other;
- review templates capture human, agent, relationship, boundary, and memory evidence;
- Student Sandbox and trading-agent are mapped as proof beds;
- the Obsidian synthesis note exists and points humans to the right artifacts;
- public narrative links the theory without expanding the product surface;
- the standard NOUS OS test suite remains green.

## Immediate Next Sprint

1. Run Phase 0 baseline audit and write a short gap list.
2. Stabilize the three v0 theory docs with status blocks and cross-links.
3. Add theory-track questions to repo review templates.
4. Create the Obsidian synthesis note.
5. Run the standard verification commands and only then decide whether public README/About links are ready.
