# Memory Philosophy v0

Memory is one of the most dangerous and most powerful parts of NOUS OS.

A human-AI co-evolution system should not remember everything. It should remember what helps the human-agent pair become wiser, more capable, more reflective, and more responsible over time.

TrustMem is therefore not a personalization database. It is a verified memory substrate for learning, challenge, decay, and evidence-linked adaptation.

## Status / How to use

Status: v0 memory artifact for the Human-AI Co-Evolution Theory Track.

Use this document before adding durable memory, personalization, student-facing records, or trading-agent learning updates. Pair it with:

- [Human-AI Symbiosis and Self-Evolution Theory](./human-ai-symbiosis-self-evolution.md)
- [Human-AI Co-Evolution Model v0](./human-ai-coevolution-model-v0.md)
- [Self-Evolution Metrics v0](./self-evolution-metrics-v0.md)

TrustMem should be treated as a verified memory substrate, not a stale personalization engine. Memory must support challenge, decay, and forgetting.

## Core thesis

Good memory does not merely make the agent more familiar.

Good memory helps the pair:

- preserve important context;
- avoid repeated mistakes;
- challenge stale assumptions;
- strengthen human judgment;
- adapt agent behavior with evidence;
- forget or decay what would otherwise become harmful overfitting.

## Memory classes

| Class | Description | Default handling |
|---|---|---|
| Facts | Stable factual context, paths, project boundaries, durable constraints | remember if verified |
| Preferences | Human-stated preferences and communication style | remember, but allow override |
| Lessons | Repeatedly validated workflow or judgment lessons | promote after evidence |
| Boundaries | Privacy, fact, learning, decision, value, taste, responsibility lines | remember strongly |
| Values | What the human says matters and why | remember carefully; do not overinfer |
| Hypotheses | Tentative beliefs or theories | store as tentative, require review |
| Mistakes | Errors, failure modes, repeated corrections | remember as caution, not identity |
| Unresolved questions | Known unknowns and open research threads | keep visible until resolved/decayed |
| Artifacts | Links to plans, reviews, proof packs, trial notes | cite, do not duplicate raw data |
| Private data | Identity details, secrets, credentials, sensitive third-party data | do not store |

## Four memory actions

NOUS OS memory should support four actions:

```text
remember
challenge
decay
forget
```

### Remember

Remember when the information is:

- stable;
- human-confirmed;
- useful across future sessions;
- evidence-backed;
- likely to prevent repeated mistakes;
- aligned with human agency and safety boundaries.

Examples:

- project paths;
- durable North Star;
- recurring user preferences;
- verified workflow lessons;
- explicit boundaries.

### Challenge

Challenge when memory might be true historically but harmful if blindly reused.

Examples:

- old assumptions about a market regime;
- stale personal preferences;
- prior strategy lessons that may not apply;
- the human's repeated blind spot;
- an agent habit that made previous output smoother but less honest.

Challenge means the agent says, in effect:

```text
I remember this, but should we still trust it here?
```

### Decay

Decay when memory becomes less reliable over time.

Examples:

- current facts;
- project status;
- plans and phase completion;
- model/provider/tool behavior;
- tactical beliefs;
- emotional states;
- unverified hypotheses.

Decay prevents memory from becoming fossilized context.

### Forget

Forget or refuse to store when information is:

- private or unsafe;
- no longer useful;
- contradicted by later evidence;
- identity-fossilizing;
- a one-off task outcome;
- stale project progress;
- likely to bias future judgment.

Forgetting is not failure. It is part of healthy cognition.

## Human judgment preservation

Memory should strengthen human judgment, not replace it.

A memory is good if it helps the human ask:

- What did I believe before?
- Why did I believe it?
- What changed?
- What evidence supports this?
- What would make me update?
- Am I solving the real problem, or just repeating a familiar pattern?

A memory is harmful if it causes the agent to skip these questions.

## Agent adaptation rule

Before adapting to a memory, the agent should ask:

1. Is this memory relevant to the current intent?
2. Is it still true enough?
3. Is it evidence-backed or merely repeated?
4. Does it preserve human agency?
5. Could it reinforce a stale identity, preference, or mistake?
6. Should I use it, challenge it, decay it, or ignore it?

## Memory and boundaries

Some boundaries should be remembered strongly:

- do not expose private data;
- do not treat AI output as truth;
- do not replace learning with ghostwriting;
- do not authorize high-stakes action without human approval;
- do not decide human values;
- do not overwrite human taste/identity;
- do not shift responsibility to the agent.

These boundaries define the safe shape of human-AI symbiosis.

## Failure modes

| Failure mode | Description | Mitigation |
|---|---|---|
| Over-personalization | Agent becomes too tailored to old preferences | add decay and current-intent check |
| Confirmation loop | Memory reinforces prior beliefs | require contradiction search and evidence review |
| Sycophantic memory | Agent remembers what pleases the human | store corrections and challenge triggers |
| Privacy leakage | Sensitive details become durable context | refuse storage and redact artifacts |
| Fossilized identity | Human's past self becomes a constraint on future growth | mark identity claims as revisable |
| Stale operational state | Old project status is treated as current truth | keep progress out of durable memory |
| Memory theater | Agent cites memory without changing behavior | require second-pass behavior diff |
| Context clutter | Too much memory lowers reasoning quality | summarize, consolidate, decay, delete |

## Memory in Student Sandbox

For students, memory should avoid identity capture.

Remember:

- learning strategies that worked;
- source-check habits;
- boundaries the student chose;
- reflection patterns;
- unresolved questions.

Do not remember:

- raw prompts with private details;
- school identity;
- family details;
- grades or labels as identity;
- embarrassing mistakes as durable traits.

The memory should help the student grow, not trap them in a profile.

## Memory in trading-agent

For trading-agent, memory should be evidence-linked and outcome-tested.

Remember:

- repeated risk-control lessons;
- reconciliation failures;
- reviewed outcomes;
- evidence-backed thesis updates;
- boundary rules.

Challenge or decay:

- stale market regime assumptions;
- old ticker narratives;
- unproven strategy beliefs;
- temporary portfolio state;
- one-off emotional reactions.

## Operational memory protocol

Before any durable memory is written or reused, classify it with this protocol.

### Step 1: Classify

Ask which class the candidate belongs to:

```text
fact / preference / lesson / boundary / value / hypothesis / mistake / unresolved_question / artifact / private_data
```

If it is private data, stop: redact or refuse storage.

### Step 2: Assign confidence

Use simple confidence labels instead of false precision:

| Confidence | Meaning | Default action |
|---|---|---|
| verified | human-confirmed and evidence-backed | remember or promote |
| observed | seen in one or more interactions but not fully verified | remember lightly or keep as hypothesis |
| tentative | plausible but unproven | store only as hypothesis or question |
| stale | may have been true but time/context changed | challenge or decay |
| contradicted | later evidence disputes it | forget, replace, or preserve only as cautionary history |

### Step 3: Choose action

Pick one:

```text
remember / challenge / decay / forget
```

The action must be justified in one sentence:

```text
This should be remembered/challenged/decayed/forgotten because ______.
```

### Step 4: Attach evidence

A durable memory should point to at least one of:

- human statement;
- review note;
- artifact path;
- test result;
- outcome ledger;
- repeated correction;
- source document.

If there is no evidence, keep it as a hypothesis or unresolved question.

### Step 5: Define review trigger

Every non-boundary memory should have a review trigger:

- time-based: review after N weeks/months;
- evidence-based: review when contradicted by outcome;
- context-based: review when entering a new domain;
- human-based: review when the human corrects it.

Boundaries can persist strongly, but even boundary wording can be refined after review.

## Memory lifecycle table

| Memory type | Remember | Challenge | Decay | Forget |
|---|---|---|---|---|
| Stable path / repo convention | yes | when repo moves | rarely | if obsolete |
| User preference | yes | when current request differs | if unused or contradicted | if user revokes |
| Workflow lesson | after repeated evidence | when context changes | if not used | if harmful/stale |
| Student learning pattern | as strategy, not identity | when it narrows growth | after trial window | if private/labeling |
| Trading lesson | only evidence-linked | when market regime changes | as outcome evidence ages | if disproven |
| Emotional state | generally no | n/a | quickly | usually |
| Hypothesis | as tentative | always | if unreviewed | if contradicted |
| Boundary | strongly | only to clarify wording | rarely | only if human revises |

## Memory review ritual

A monthly or phase-end memory review should ask:

1. Which memories improved judgment this cycle?
2. Which memories caused stale assumptions or over-personalization?
3. Which repeated corrections should become durable lessons?
4. Which stored lessons need evidence links?
5. Which hypotheses should graduate, remain tentative, or be forgotten?
6. Which private or identity-capturing details should be removed?
7. Which memories helped the human become more capable without AI?

This ritual turns memory from passive storage into co-evolution governance.

## Student Sandbox memory packet

A safe Student Sandbox memory packet should store process, not identity:

```yaml
learning_strategy_used: "source checklist before drafting"
boundary_selected: "facts"
student_reflection_summary: "AI helped decompose; student verified author/date; responsibility remains with student"
next_learning_move: "ask for counterarguments before thesis"
private_data_stored: false
review_trigger: "after next student-adjacent trial"
```

It should not store:

```yaml
student_name: ...
school_name: ...
raw_prompt: ...
family_context: ...
identity_label: "bad at research"
```

## Trading-agent memory packet

A safe trading memory packet should be evidence-linked and risk-aware:

```yaml
lesson: "Target-reached exit signals require mandatory trim/trailing-stop review before same-symbol add signals."
evidence: "reviewed outcome / reconciliation artifact path"
boundary: "no natural-language capital authorization"
review_trigger: "when same-symbol buy/add appears after target-reached exit"
action: "remember strongly; challenge any conflicting buy signal"
```

It should not store temporary state as durable memory:

```yaml
current_position_size: ...
today_signal_status: ...
short_lived_alert: ...
```

## Design rule

The memory question is not:

```text
Can the agent remember this?
```

The question is:

```text
Will remembering this make the human-agent pair wiser, more capable, more reflective, and more responsible over time?
```

If not, challenge, decay, or forget.
