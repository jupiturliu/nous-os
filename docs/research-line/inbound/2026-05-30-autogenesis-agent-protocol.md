---
title: "Autogenesis: A Self-Evolving Agent Protocol"
authors: Wentao Zhang; Zhe Zhao; Haibin Wen; Yingcheng Wu; Cankun Guo; Ming Yin; Bo An; Mengdi Wang
year: 2026
venue: arXiv / project repo; surfaced by 机器之心
kind: preprint
status: note-written
captured: 2026-05-30
anchor_bucket: 4 · Industry research
source_url: https://mp.weixin.qq.com/s/nQXjwCTJIuaQEi6EQpVNIg
primary_url: https://arxiv.org/abs/2604.15034
repo_url: https://github.com/DVampire/Autogenesis
---

# 2026-05-30 · Autogenesis agent protocol

## What it is

A 2026 preprint and project repo proposing **Autogenesis Protocol (AGP)**, a two-layer protocol for self-evolving LLM agent systems. AGP separates `what evolves` from `how evolution happens`: the **Resource Substrate Protocol Layer (RSPL)** registers prompts, agents, tools, environments, and memory as versioned resources; the **Self-Evolution Protocol Layer (SEPL)** defines a closed-loop interface for proposing, assessing, committing, auditing, and rolling back improvements. The associated **Autogenesis System (AGS)** is presented as a self-evolving multi-agent runtime.

Source status: the WeChat article was read; the arXiv abstract and GitHub README were checked. Core architecture framing is supported. Media benchmark claims should remain `pending validation` until full paper tables/scripts and independent reproduction are reviewed.

## Why it matters for our line

NOUS OS is explicitly trying to make human-AI loops stronger over time without boundary drift. Autogenesis is a close external anchor for the **agent-side self-evolution protocol** problem: once agents can modify prompts, tools, memory, environments, and internal agents, those changes need lifecycle governance. This maps directly to our Harness Engineering lane and Trading Brain's review-only self-improvement contracts.

## Where we share

- **Self-evolution must be governed.** Both AGP and NOUS OS reject the naive pattern of “reflect, rewrite prompt, hope it improved.”
- **Resources need lifecycle and versioning.** AGP's RSPL maps cleanly to our view that prompts, skills, tools, memories, evaluator specs, and contracts must be explicit artifacts.
- **Improvement should be closed-loop.** AGP's SEPL maps to our proof-loop spine: proposal → shadow/eval → review → commit/reject/rollback.
- **Traceability is non-negotiable.** AGP's auditable lineage/rollback matches NOUS OS release gates and Trading Brain's source-capture/claim/validation/result-proof artifacts.

## Where we differ / what we add

| External anchor | NOUS OS |
|---|---|
| Focuses on agent protocol and runtime self-evolution. | Focuses on human-AI co-evolution: the human's capability, responsibility, and boundary integrity are first-class. |
| Treats prompts/agents/tools/environments/memory as evolvable resources. | Adds human reflection evidence, source discipline, capability-without-AI delta, and review packets as evolvable/evaluable loop objects. |
| Benchmarks agent task success. | Requires evidence that the human-AI loop improves without over-delegation or boundary drift. |
| Commit/rollback is agent-system centered. | Commit/rollback is also human-governance centered; promotion into live/capital/runtime surfaces remains human-gated. |

The key delta: **Autogenesis governs how agents evolve themselves; NOUS OS governs how agent evolution affects human capability and responsibility.**

## What this changes in our practice

- Use AGP vocabulary as a benchmark for NOUS OS Harness Engineering: `resource substrate`, `self-evolution protocol`, `auditable lineage`, `rollback`.
- Compare AGP against Trading Brain's current `ImprovementProposalV1 -> ShadowApplyCandidateV1 -> NextCycleOutcomeCheckV1` chain.
- Treat benchmark claims as architecture motivation, not proof of safe self-evolution.
- Add a future map: `Autogenesis AGP vs NOUS OS / Trading Brain self-improvement contracts`.

## Limitations of this work (from our perspective)

- The GitHub README states the codebase is under active refactoring and only `examples/run_tool_calling_agent.py` is currently functional.
- Media-reported GAIA/HLE/LeetCode results require paper-body and reproduction validation.
- Task benchmark gains do not by themselves prove safe self-evolution under human/capital/privacy boundaries.
- Protocol generality may hide the hard parts: evaluator quality, permissioning, rollback correctness, and resource isolation.

## Open questions for follow-up

- Do AGP/AGS paper tables validate the WeChat benchmark numbers exactly?
- Does the GitHub repo contain executable reproduction scripts for GAIA/HLE/LeetCode?
- Can NOUS OS define a `ResourceSubstrateV1` schema for prompts/skills/tools/memory/evaluator contracts?
- Should Trading Brain's self-improvement checker add an explicit `resource_under_change` field modeled after RSPL?
- How should human reflection and capability-delta artifacts fit into AGP-style resource governance?

## Citation

Zhang, W., Zhao, Z., Wen, H., Wu, Y., Guo, C., Yin, M., An, B., & Wang, M. (2026). *Autogenesis: A Self-Evolving Agent Protocol*. arXiv:2604.15034. https://arxiv.org/abs/2604.15034
