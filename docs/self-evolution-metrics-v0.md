# Self-Evolution Metrics v0

NOUS OS should not only measure whether an AI agent produced a better answer. It should measure whether the human-agent loop is becoming wiser, more capable, more reflective, and more responsible over time.

This document defines initial metrics for human evolution, agent evolution, and relationship evolution.

## Status / How to use

Status: v0 metrics artifact for the Human-AI Co-Evolution Theory Track.

Use this document to design reviews, Student Sandbox trials, and trading-agent outcome reviews that measure the loop rather than only agent output. Pair it with:

- [Human-AI Symbiosis and Self-Evolution Theory](./human-ai-symbiosis-self-evolution.md)
- [Human-AI Co-Evolution Model v0](./human-ai-coevolution-model-v0.md)
- [Memory Philosophy v0](./memory-philosophy-v0.md)

Treat every metric as either a qualitative observation or a measurable proxy. Do not collapse the theory into a single score before repeated reviews justify it.

## Measurement principle

Avoid fake precision.

Some signals are quantitative. Many early signals are structured qualitative observations. That is acceptable if the observation protocol is explicit and repeatable.

The first goal is not a perfect score. The first goal is to prevent NOUS OS from optimizing only agent output while missing human capability and relationship quality.

## Metric groups

```text
Human capability
Agent adaptation
Relationship calibration
Boundary integrity
Outcome quality
```

## Human-side metrics

| Metric | Question | Observation method | Type |
|---|---|---|---|
| Human Intent Clarity | Did the human state what they are trying to understand, decide, create, or become? | compare initial prompt vs revised intent | qualitative / rubric |
| Source Discernment | Did the human check evidence instead of accepting AI output? | source checklist, citation review, contradiction notes | qualitative + count |
| Boundary Articulation | Did the human name privacy/fact/learning/decision/value/taste/responsibility boundaries? | boundary card or review note | qualitative |
| Human Capability Delta | Can the human explain or perform something better after the loop? | before/after explanation, transfer task | qualitative / rubric |
| Reflection Quality | Did the human explain what AI helped with, what they verified, and what remains their responsibility? | reflection card | qualitative |
| Transfer | Can the human apply the same learning pattern to a new domain? | follow-up task | qualitative |
| Responsibility Retention | Did the human retain final judgment and accountability? | review note, decision log | qualitative |

## Agent-side metrics

| Metric | Question | Observation method | Type |
|---|---|---|---|
| Boundary Integrity | Did the agent respect explicit and implicit boundaries? | boundary violations count + review | qualitative + count |
| Correction Absorption | Did the second pass change appropriately after human correction? | diff first vs second pass | qualitative / score |
| Memory Reuse Precision | Did memory help without stale or irrelevant baggage? | memory citation review | qualitative / score |
| Uncertainty Surfacing | Did the agent name uncertainty and unknowns? | uncertainty notes present | qualitative + count |
| Clarifying Question Quality | Did the agent ask useful questions before over-answering? | question rubric | qualitative |
| Challenge Quality | Did the agent challenge assumptions at the right moments? | observer review | qualitative |
| Learning Support | Did the agent help the human learn rather than only produce output? | hints/practice/explanation ratio | qualitative |

## Relationship metrics

| Metric | Question | Observation method | Type |
|---|---|---|---|
| Trust Calibration | Did confidence track evidence quality? | confidence vs evidence review | qualitative |
| Delegation Precision | Did the human delegate the right parts and retain the right parts? | task decomposition review | qualitative |
| Repeated Correction Reduction | Are the same corrections needed less often over time? | correction log trend | quantitative / trend |
| Mutual Adaptation | Did both human behavior and agent behavior change? | compare cycle notes | qualitative |
| Independence Preservation | Is the human stronger even without AI? | no-AI explanation or transfer prompt | qualitative |
| Relationship Explainability | Can the human explain how they collaborate with the agent? | interview prompt | qualitative |

## Extended CLS-style score concept

Existing CLS-style metrics focus on loop quality. For NOUS OS theory, extend the frame:

```text
Co-Evolution Score =
  Boundary Integrity
  + Correction Absorption
  + Memory Reuse Precision
  + Human Agency Preservation
  + Human Capability Delta
  + Reflection Quality
  + Trust Calibration
  + Outcome Quality Delta
```

Do not collapse this too early into one number. During v0, keep components visible.

## Student Sandbox measurement

A Student Sandbox trial can observe:

- Did the student write the question in their own words?
- Did the student select a boundary?
- Did the student check at least two source-quality properties?
- Did the AI provide hints rather than final answers?
- Did the student complete reflection?
- Could the student say what remains their responsibility?
- Could the student ask a better next question?

Possible rubric:

| Score | Meaning |
|---|---|
| 0 | absent |
| 1 | present only with heavy prompting |
| 2 | present with light prompting |
| 3 | student can explain independently |

## Trading-agent measurement

A trading-agent review can observe:

- Did agent research preserve capital authority boundaries?
- Did human approval remain explicit?
- Did reviewed outcomes feed future reasoning?
- Did memory cite evidence rather than vague lessons?
- Did the system avoid repeated post-fill/reconciliation mistakes?
- Did no-action decisions improve portfolio discipline?
- Did human judgment become clearer about risk, sizing, and uncertainty?

The trading proof bed adds stronger outcome feedback, but must not become the definition of NOUS OS.

## Measurement anti-patterns

Avoid:

- scoring only answer quality;
- rewarding output volume;
- treating confidence as correctness;
- treating memory hits as automatically good;
- measuring agent autonomy without measuring human agency;
- counting artifacts without checking whether they changed behavior;
- optimizing for user satisfaction when challenge was needed.

## Review questions

Every research review should ask:

1. What changed in the human?
2. What changed in the agent?
3. What changed in the relationship?
4. What boundary was preserved or violated?
5. What evidence supports the claimed improvement?
6. What should be remembered, challenged, decayed, or forgotten before the next cycle?

## Status

This is a v0 metrics frame. It should be refined after the first Student Sandbox trial and after more trading-agent reviewed outcome evidence.
