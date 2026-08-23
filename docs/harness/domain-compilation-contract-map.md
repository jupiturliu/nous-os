# Domain Compilation Contract Map — From AI Answers to Feasible Plans

Status: hypothesis / design reference  
Captured: 2026-07-12  
Scope: NOUS OS harness architecture; no runtime or capital action

## Core claim

Many domain workflows lack a **compilable work object**. They have natural-language requests, documents, spreadsheets, implicit expertise, and manual coordination, but no explicit representation of intent, implementation, target environment, or feasibility proof.

```text
natural-language intent
  -> candidate Spec IR
  -> candidate Impl IR
  + Target Description + Platform Config
  -> planner / compiler
  -> verifier suite
  -> feasible plan + evidence certificate + unresolved assumptions
```

A language model may generate useful candidates at every arrow. It must not be the final feasibility oracle. Feasibility is a property of a proposed implementation against a specified target, proven or falsified by appropriate verifiers.

## The five contract surfaces

| Surface | Question answered | Minimum contents | Failure if absent |
|---|---|---|---|
| `SpecIR` | What must be true for success? | goals, hard/soft constraints, acceptance tests, authority and risk boundaries, assumptions | AI optimizes style or an unstated proxy rather than the actual objective. |
| `ImplIR` | What will be built or done? | workflow/state machine, resources/BOM, parameters, dependencies, interfaces, rollback/fallback | Plan cannot be deployed, diffed, audited, or repeated. |
| `TargetDescription` | What is the real target world? | assets, topology, capacities, policies, physical/environmental/regulatory limits, current state, provenance/time | A logically good plan is applied to an imaginary environment. |
| `PlatformConfig` | Which platform/version/permissions are available? | software/hardware versions, feature flags, credentials/roles, tool limits, deployment window | A valid design fails at integration or authorization. |
| `VerificationReport` | What is proved, falsified, or unknown? | checks run, inputs/version hashes, pass/fail/inconclusive state, counterexamples, residual risk, human decision required | Output is asserted as feasible without evidence or accountability. |

`TargetDescription` is domain truth; `PlatformConfig` is deployable-environment truth. They should be separately versioned because a stable factory/site/business can run different software, permissions, or equipment configurations.

## Minimal schemas — design vocabulary, not frozen implementation

### SpecIR v0

```yaml
spec_id: string
intent: string
goals:
  - metric: string
    direction: maximize|minimize|satisfy
    threshold: number|string
hard_constraints:
  - id: string
    predicate: structured expression
    source: policy|law|physics|contract|human
soft_constraints:
  - id: string
    priority: integer
acceptance_tests:
  - id: string
    pass_condition: structured expression
authority:
  proposer: role
  verifier: role|system
  approver: role
assumptions:
  - statement: string
    validation_state: unverified|validated|falsified
```

### ImplIR v0

```yaml
impl_id: string
spec_ref: string
steps:
  - id: string
    action: typed verb
    inputs: [artifact_or_resource_ref]
    outputs: [artifact_or_state_ref]
    preconditions: [predicate]
    rollback: optional action
resources:
  - id: string
    quantity: number|string
interfaces:
  - producer: step_or_system
    consumer: step_or_system
    contract: schema_or_protocol_ref
```

### TargetDescription / PlatformConfig v0

```yaml
target_id: string
observed_at: ISO-8601
provenance: source_or_sensor_ref
assets: [typed asset]
capacities: [resource limit]
constraints: [physical|regulatory|contractual predicate]
current_state: [versioned fact]

platform_config:
  version: string
  permissions: [role/capability]
  enabled_features: [flag]
  integration_endpoints: [typed reference]
  maintenance_window: optional interval
```

### VerificationReport v0

```yaml
verification_id: string
spec_ref: string
impl_ref: string
target_ref: string
platform_config_ref: string
checks:
  - name: string
    class: lint|type|static|simulation|dynamic|audit
    result: pass|fail|inconclusive
    evidence_ref: artifact/hash/log
counterexamples: [minimal failing condition]
residual_risks: [unproved condition]
verdict: feasible|conditionally_feasible|infeasible|insufficient_evidence
human_decision_required: [explicit decision]
```

## Verifier ladder

| Layer | Detects | Does not prove |
|---|---|---|
| Lint/schema validation | missing fields, invalid references, basic policy omissions | real-world behavior |
| Type/static analysis | incompatible interfaces, impossible resource/permission combinations, policy violations | stochastic performance, hidden state |
| Planner/compiler | whether an implementation can be constructed from declared inputs | whether target facts are current/true |
| Simulation/digital twin | modeled capacity, cost, safety, schedule, reliability behavior | unmodeled reality or model error |
| Dynamic verification | actual observed execution behavior | generalization beyond observed operating conditions |
| Audit/provenance | evidence lineage, version alignment, approval boundaries | substantive correctness of false inputs |

A `pass` must always be read as: *passes these checks under these target/config versions*. It is never a timeless guarantee.

## Domain examples

| Domain | SpecIR | ImplIR | TD / Platform Config | Verifiers |
|---|---|---|---|---|
| Data center | MW, latency, PUE, availability, budget, safety | one-line topology, equipment list, cooling and deployment sequence | utility connection, transformer capacity, site water/cooling, installed equipment, firmware/permissions | electrical rules, load flow, thermal simulation, commissioning and telemetry |
| Manufacturing | yield, throughput, quality, safety, cost | routing, BOM, recipes, machine settings, scheduling | machine/tool state, material lots, operator certification, plant rules | process constraints, scheduling feasibility, digital twin, SPC and QA tests |
| Clinical workflow | patient outcome, exclusion criteria, safety, protocol compliance | protocol steps, drug/device/logistics, escalation | patient facts, available equipment, approved formulary, local policy | contraindication rules, protocol lint, trials/monitoring, clinician review |
| Financial research (review-only) | falsifiable thesis, risk limits, evidence quality | research plan, data transforms, scenario model, review stages | dataset version, market/session state, account permissions, policy boundaries | source checks, point-in-time tests, risk vetoes, shadow evaluation, human approval |

## NOUS OS mapping

| Domain-compilation surface | Existing NOUS OS surface | Gap to validate before implementation |
|---|---|---|
| SpecIR | task briefs, human-goal statements, boundary maps | machine-readable goal/acceptance/authority contract |
| ImplIR | skills, templates, deterministic workflows | typed, diffable implementation plan for repeated workflows |
| TargetDescription | context index, source cards, runtime/service truth in owning systems | versioned target facts and freshness/provenance rules |
| PlatformConfig | tool/runtime configuration, release gates | explicit capability/permission/config snapshots |
| VerificationReport | evaluator outputs, release-gate artifacts, evidence write-back | unified pass/fail/inconclusive result envelope and counterexample fields |

## Adoption rule: do not prematurely standardize

This is a vocabulary and responsibility map, **not** a mandate to create a universal DSL.

1. Capture three or more recurring failures where an AI proposal cannot be checked because a specific contract surface is missing.
2. Build the smallest structured artifact for that surface in one vertical.
3. Add a deterministic validator only when the same check repeats.
4. Record counterexamples and failed assumptions.
5. Promote a schema only after it improves verification or handoff quality across real cases.

Start with `VerificationReport v0` and a narrow `SpecIR v0` in one vertical; `ImplIR` and full TD should emerge from repeated operations, not from a top-down ontology exercise.

## Evaluation questions

- Did the structured Spec change the plan or merely reformat it?
- Can a verifier produce a concrete failing condition rather than a generic warning?
- Are target facts time-stamped, sourced, and owned?
- Does a human know which residual risk they—not the model—must accept?
- Does the next operator reproduce the decision without inheriting private context?
- Does the workflow improve outcome quality, not only formatting quality?

## First executable vertical: research-source intake

A deliberately narrow `SpecIR v0`, `TargetDescription v0`, `PlatformConfig v0`, and `VerificationReport v0` now exist for the recurring workflow `source capture -> evidence-labeled research note`:

- `examples/contracts/research-source-intake-spec-v0.json`
- `examples/contracts/research-source-intake-target-description-v0.json`
- `examples/contracts/research-source-intake-platform-config-v0.json`
- `examples/contracts/research-source-intake-verification-report-v0.json`
- `scripts/check_domain_compilation_contract.py`
- `tests/test_domain_compilation_contract.py`

Verification command:

```bash
python3 scripts/check_domain_compilation_contract.py \
  examples/contracts/research-source-intake-spec-v0.json \
  examples/contracts/research-source-intake-verification-report-v0.json \
  --target examples/contracts/research-source-intake-target-description-v0.json \
  --platform-config examples/contracts/research-source-intake-platform-config-v0.json --json
python3 -m unittest tests.test_domain_compilation_contract -v
```

The example intentionally yields `conditionally_feasible`, not `feasible`: the source is sufficiently structured for a limited conclusion, but its completeness remains unverified. The validator prevents an unverified assumption from being represented as an unqualified `feasible` verdict.

## Current decision

- Architecture status: research hypothesis plus one executable vertical prototype.
- Deterministic implementation: narrowly limited to contract-shape and verdict-qualification validation; it is not a semantic source-truth verifier.
- Human boundary: feasibility claims require named verifier evidence; approval remains human-owned where consequences require it.
