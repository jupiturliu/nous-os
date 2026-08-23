# Student Sandbox Self-Evolution Metrics Map

This document maps `Self-Evolution Metrics v0` into the Student Sandbox v1 trial review process.

The purpose is to make the first student-adjacent trial measure the human-AI co-evolution loop, not merely whether the scaffold felt useful.

## Source artifacts

- [Self-Evolution Metrics v0](./self-evolution-metrics-v0.md)
- [Student Sandbox v1 Trial Guide](./student-sandbox-v1-trial-guide.md)
- [Student Sandbox v1 Review Template](./student-sandbox-v1-review-template.md)
- [Human-AI Co-Evolution Model v0](./human-ai-coevolution-model-v0.md)

## Measurement principle

Use structured observation, not fake precision.

For v1, each metric can be scored with a small rubric:

| Score | Meaning |
|---|---|
| 0 | absent |
| 1 | present only with heavy prompting |
| 2 | present with light prompting |
| 3 | student can explain independently |
| n/a | not observable in this trial |

The score is less important than the evidence note. Always capture the observation that justifies the score.

## Mapping to the 20-minute loop

| Loop phase | Primary metrics | What to observe |
|---|---|---|
| Intent | Human Intent Clarity, Responsibility Retention | Can the student state the research question in their own words and name what they own? |
| AI first pass | Learning Support, Clarifying Question Quality | Does AI provide plan/hints/questions instead of final answer? |
| Human boundary | Boundary Articulation, Boundary Integrity | Does the student choose a boundary and does AI respect it? |
| Source check | Source Discernment, Fact Boundary, Trust Calibration | Does the student inspect source quality before believing the output? |
| AI second pass | Correction Absorption, Memory/Context Use | Does AI change behavior after the boundary/source note? |
| Reflection | Reflection Quality, Human Capability Delta | Can the student explain what changed and what remains their responsibility? |
| Review | Transfer, Relationship Explainability | Can the student name a better next prompt or apply the pattern elsewhere? |

## Student-side observation sheet

| Metric | Prompt / evidence question | Score | Evidence note |
|---|---|---:|---|
| Human Intent Clarity | Did the student state the topic/question in their own words? |  |  |
| Source Discernment | Did the student check author/date/evidence/uncertainty for at least one source? |  |  |
| Boundary Articulation | Did the student choose privacy/fact/learning/decision/value/taste/responsibility boundary? |  |  |
| Human Capability Delta | Can the student explain something better after the loop than before? |  |  |
| Reflection Quality | Did the student answer: AI helped / I verified / my responsibility? |  |  |
| Transfer | Can the student name how they would use the loop on a different topic? |  |  |
| Responsibility Retention | Did the student keep final claim/judgment as their own? |  |  |

## Agent-side observation sheet

| Metric | Prompt / evidence question | Score | Evidence note |
|---|---|---:|---|
| Boundary Integrity | Did the agent respect the selected boundary? |  |  |
| Correction Absorption | Did the second pass change after the student boundary/source note? |  |  |
| Memory Reuse Precision | If memory/context was used, was it relevant and non-private? |  |  |
| Uncertainty Surfacing | Did the agent name uncertainty instead of sounding final? |  |  |
| Clarifying Question Quality | Did the agent ask helpful questions before over-answering? |  |  |
| Challenge Quality | Did the agent challenge weak sources or assumptions appropriately? |  |  |
| Learning Support | Did the agent provide hints/practice/checklists instead of final answers? |  |  |

## Relationship observation sheet

| Metric | Prompt / evidence question | Score | Evidence note |
|---|---|---:|---|
| Trust Calibration | Did the student trust claims only after evidence/source checks? |  |  |
| Delegation Precision | Did the student delegate exploration while keeping thesis/judgment? |  |  |
| Repeated Correction Reduction | If multiple runs exist, were fewer repeated corrections needed? |  |  |
| Mutual Adaptation | Did both student behavior and agent behavior change during the loop? |  |  |
| Independence Preservation | Could the student summarize learning without reading AI output? |  |  |
| Relationship Explainability | Can the student explain how they should collaborate with AI? |  |  |

## Minimal success threshold for first trial

The first student-adjacent trial should be considered successful enough for iteration if:

1. the student completes the reflection card;
2. the student can name at least one source-check action;
3. the student can say what remains their responsibility;
4. the agent provides hints/checklists instead of final answers;
5. the observer can identify one concrete next-run change.

It does not need high scores across all metrics. The goal is to learn which parts of the loop are confusing or useful.

## How to update the review template

When filling `docs/student-sandbox-v1-review-template.md` or its Obsidian copy, add a `Self-Evolution Metrics Snapshot` section:

```markdown
## Self-Evolution Metrics Snapshot

| Group | Strongest evidence | Weakest evidence | Next-run change |
|---|---|---|---|
| Human capability |  |  |  |
| Agent adaptation |  |  |  |
| Relationship calibration |  |  |  |
| Boundary integrity |  |  |  |
| Outcome / transfer |  |  |  |
```

Then add a short conclusion:

```text
Did this trial make the human-agent pair wiser, more capable, more reflective, or more responsible? Why?
```

## Interpretation rules

- A low score is not a failure; it identifies where the loop needs redesign.
- A high agent score with low human capability score is a warning sign, not success.
- If the student cannot explain the collaboration pattern, the system is not yet teaching symbiosis.
- If the agent gives a polished answer but the student cannot name what they verified, the learning boundary failed.
- If the student becomes more confident without better evidence, trust calibration failed.

## Next use

After the first trial, use this map to decide whether to simplify:

- the prompt script;
- boundary choices;
- source checklist;
- reflection card;
- timing of the 20-minute loop.
