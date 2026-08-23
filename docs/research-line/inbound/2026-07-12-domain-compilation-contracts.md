---
title: "Domain Compilation Contracts: SpecIR, ImplIR, TD, Platform Config and Verifier"
kind: internal-architecture-hypothesis
status: note-written
captured: 2026-07-12
source: user-authored synthesis in Hermes session
---

# 2026-07-12 · Domain Compilation Contracts

## What it is

An internal NOUS OS architecture hypothesis: a broad class of AI failures occurs because a domain has no compilable representation of intent, implementation, target environment, platform configuration, and feasibility proof.

## Why it matters

It reframes the product problem from “make the model answer better” to “create a checked translation from human intent to a target-specific, evidence-backed plan.” It also gives a sharper language for why many document/chat workflows remain non-deployable: their real Spec, Impl, target state, and verification logic remain distributed across people, PDF, Excel, institutional memory, and informal review.

## What NOUS OS shares

- Context, boundary, artifact, evaluator, release-gate, and evidence-writeback layers already approximate parts of the compilation chain.
- Human authority remains necessary when constraints reflect values, responsibility, or irreversible consequence.
- A verifier must return inspectable evidence and counterexamples, rather than a model-confidence statement.

## What changes in practice

Before adding an agent feature or workflow, classify its dominant failure:

- missing or ambiguous `SpecIR`;
- unstructured / non-deployable `ImplIR`;
- stale, missing, or unsourced `Target Description`;
- unavailable or incompatible `Platform Config`;
- no verifier or only a cosmetic checker.

The next artifact should fix the narrowest missing surface—not add more prompts.

## Guardrail

Do not create a universal industry DSL in advance. Promote a structured contract only after recurrent failures in a named vertical demonstrate that it improves verification, handoff, or outcome quality.

## Related artifact

- `docs/harness/domain-compilation-contract-map.md`
- Obsidian: `NousOS/02 Harness Engineering/2026-07-12 Domain Compilation Contracts - SpecIR ImplIR TD Verifier.md`
