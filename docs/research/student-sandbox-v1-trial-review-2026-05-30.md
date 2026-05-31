# Student Sandbox v1 Trial Review — 2026-05-30

Process review of one **self-review (AI-conducted, operator-adjacent)** walkthrough of the
v1 20-minute loop. This is explicitly NOT a recruited-student session and NOT a student
evaluation/grade — it is a design-quality review of the loop, run by genuinely executing all
six phases (including a real two-source check) and recording where the scaffold helped vs.
created friction. Honesty label per ground-truth-first: no student was involved; observations
are about the v1 design, not about any person.

## Session metadata

- Date: 2026-05-30
- Observer role: self-review (AI-conducted, operator-adjacent dry trial)
- Topic area, not raw private prompt: "Do school smartphone bans improve student academic focus?" (high-school research-skills topic, source-rich, evidence-vs-opinion heavy)
- Student level: high_school (simulated intent)
- Artifact reviewed: `examples/runtime/research-records/student-sandbox-v1-latest.json` (built 2026-05-30T16:42)
- Consent / stop-anytime reminder given: n/a (no human subject)

## Privacy check

- Student name recorded? no
- School name recorded? no
- Email / account / family detail recorded? no
- Raw private prompt saved? no
- Redaction needed? no
- Redaction notes: artifact `privacy` block confirms `local_only: true`, `external_model_calls: false`, `contains_private_student_data: false`. The only external call in this trial was the observer's own source-check web search (research content, not student data) — consistent with the privacy policy.

## 20-minute loop completion

| Phase | Completed? | Evidence / note |
|---|---|---|
| Intent in student's words | yes | Wrote one-sentence question + prior belief ("bans probably help focus but the effect is likely overstated"). The "name what you already believe" step is the strongest part of phase 1 — it forces a falsifiable prior before any AI contact. |
| AI first pass as learning plan | yes / friction | Produced three subquestions (focus vs. grades vs. wellbeing; short- vs. long-term; who benefits most). The instruction "ask for a learning plan, not an answer paragraph" is correct in intent but assumes the student can resist the answer-dump habit; without a worked example of a "plan-not-answer" prompt, a ChatGPT-habituated student will likely still ask for the answer. |
| Human boundary selected | yes / unclear | Chose "facts" boundary. The five options (privacy / facts / learning / decision / values) are abstract for a high-schooler — "decision boundary" and "values boundary" are not self-explanatory and have no examples in the artifact. Real friction point. |
| Source check attempted | yes (strongest phase) | Checked two real sources: an advocacy org (smartphonefreechildhood.org) claiming "1–2 GCSE grades higher", and a peer-reviewed 2024 rapid review (Böttger & Zierer, *Education Sciences*) reporting a small but significant effect size (d=0.162). The checklist item "Evidence is separated from opinion" directly caught the advocacy framing vs. the modest peer-reviewed effect. This is the loop delivering exactly its intended discernment. |
| AI second pass changed behavior | yes | Revised plan downgraded the dramatic "1–2 grades" claim to "small positive effect, contested, larger for low-income students", explicitly carrying the source-quality note forward. Observable behavior change from first pass. |
| Reflection completed | yes | Answered the reflection card before any drafting. Sequencing (reflect-before-draft) preserves independence well. |

## Student understanding

- AI helped with: structuring subquestions, vocabulary (effect size, confounding), and naming common traps (advocacy framing, short-vs-long-term).
- Student verified: two sources for author/institution, date (both 2024), evidence type, and the gap between a dramatic advocacy claim and a modest peer-reviewed effect.
- Student boundary: "facts" — accuracy and source quality over persuasion.
- Student kept responsibility for: the final claim ("evidence leans positive but small and contested"), and judging whether two sources are enough (they are not — flagged as a next step).
- Student's next learning move: find one source that argues *against* bans to test the prior, not just confirm it.

## Theory track evidence

- Human capability delta: prior-belief step + source discernment produced a measurably more calibrated claim than the AI first pass alone.
- Source discernment: strong — advocacy-vs-peer-review distinction surfaced naturally from the checklist.
- Reflection quality: adequate; the four reflection prompts are answerable but generic.
- Trust calibration: improved — the student ended *less* certain than the AI's confident first pass, which is the correct direction.
- Independence preservation: preserved — reflect-before-draft and "human_keeps" fields at each phase kept judgment with the learner.
- What changed in the agent's second pass? It de-escalated an overstated claim and propagated the source-quality caveat — desired adaptation.
- What changed in the human-AI relationship? Moved from answer-provider to plan-critic; the human stayed the decider on sufficiency of evidence.
- What should be remembered / challenged / decayed / forgotten? Remember: the source-check checklist works. Challenge: whether 4 minutes is enough for a real two-source check. Decay: nothing yet. Forget: no raw content needs storing (privacy-clean).

## Confusion and friction

- Prompt wording: "ask for a learning plan, not an answer paragraph" needs one concrete example prompt.
- Source checklist: content is excellent; the friction is **time**, not wording — see timing below.
- Boundary choice: the five boundary types are abstract; need 1–2 concrete examples each.
- Reflection card: fine, slightly generic.
- Timing / cognitive load: **the main finding.** The six phases sum to exactly 20 minutes with zero buffer (3+4+3+4+3+3). `source_check` at 4 minutes is the bottleneck — genuinely evaluating two sources for author, date, evidence, and uncertainty took longer than 4 minutes even for an experienced reader. A real high-schooler will either rush the check (defeating the point) or overrun the loop.

## Parent / teacher / observer notes

- Was AI acting like a tutor instead of a ghostwriter? Yes — the "plan not answer" and "hints not answers" policy held; AI never wrote the claim.
- Could the student explain the question without AI? Yes — the intent phase forces this before AI contact.
- Did the student preserve their own judgment before drafting? Yes — reflect-before-draft enforced it.
- Was any safety/privacy instruction unclear? No — privacy block is explicit and local-only.

## Self-Evolution Metrics Snapshot

| Group | Strongest evidence | Weakest evidence | Next-run change |
|---|---|---|---|
| Human capability | prior-belief + source discernment calibrated the final claim | reflection prompts are generic | add a calibration prompt ("how did your confidence change?") |
| Agent adaptation | second pass de-escalated overstated claim | first pass still answer-shaped without an example | add a "plan-not-answer" example prompt |
| Relationship calibration | human stayed decider on evidence sufficiency | — | keep |
| Boundary integrity | privacy local-only held; human_keeps respected | boundary types abstract | add concrete examples per boundary |
| Outcome / transfer | student named a falsifying next step | only two sources (insufficient) in the time budget | rebalance time toward source_check |

Conclusion:

```text
Yes — the pair ended more reflective and better calibrated than the AI's confident first pass.
The decisive moment was the source check exposing an advocacy claim ("1-2 grades higher") against
a modest peer-reviewed effect (d=0.162). The loop's structure (prior belief -> AI plan -> human
boundary -> source check -> revised plan -> reflect-before-draft) did the work it was designed to
do. The limiting factor is time, not concept: source_check is the highest-value phase and the most
under-budgeted.
```

## Outcome classification

- **useful_but_confusing**

The loop works and the source-check is its standout strength; friction is concentrated in (a) tight source-check timing and (b) abstract boundary options.

## Next-run change

- Keep: the source-check checklist (esp. "evidence is separated from opinion"); the prior-belief step in phase 1; reflect-before-draft sequencing.
- Change: rebalance the 20-minute budget toward `source_check` — give it 5–6 min (e.g. trim `ai_second_pass` to 2 min, or extend the total loop to 22–24 min and label it "20-minute core + optional buffer"). Source-check is the cognitive bottleneck and the highest-value phase; under-budgeting it undermines the whole loop.
- Remove: nothing yet — do not cut scaffold before at least one recruited-student trial.
- Add: (1) one worked "plan-not-answer" example prompt in `ai_first_pass`; (2) 1–2 concrete examples for each of the five boundary types in `human_boundary`; (3) an explicit "two sources is a floor, not a finish" note so students don't treat the time box as sufficiency.

## Research note

> A single AI-conducted self-review walkthrough of the v1 20-minute loop (topic: school smartphone
> bans, a source-rich high-school research question) completed all six phases and confirmed the
> loop's core design works: the prior-belief step plus the source-quality checklist measurably
> de-escalated an overstated advocacy claim against a modest peer-reviewed effect, with judgment
> kept by the learner throughout. The dominant friction is timing — `source_check` (4 min) is the
> highest-value but most under-budgeted phase — followed by the abstractness of the five boundary
> options. Recommended v1 adjustment: rebalance time toward source-checking and add concrete
> examples for the boundary and "plan-not-answer" steps, before recruiting a real student trial.
> No private student data was involved; this was a design review, not a human-subject session.

## Linkage

- Plan: `docs/plans/2026-05-16-student-sandbox-research-study-v1-plan.md`
- Trial guide: `docs/student-sandbox-v1-trial-guide.md`
- Local scaffold: `examples/student_sandbox_v1.py`
- Artifact: `examples/runtime/research-records/student-sandbox-v1-latest.json`
- Sources checked in the trial:
  - [Smartphone Free Childhood — evidence page (advocacy org)](https://www.smartphonefreechildhood.org/resource/smartphone-free-schools-evidence)
  - [Böttger & Zierer 2024, "To Ban or Not to Ban", *Education Sciences* 14:906 (peer-reviewed rapid review, d=0.162)](https://www.mdpi.com/2227-7102/14/8/906)
  - [Campbell et al. 2024, "Evidence for and against banning mobile phones in schools: a scoping review", *SAGE*](https://journals.sagepub.com/doi/10.1177/20556365241270394)
