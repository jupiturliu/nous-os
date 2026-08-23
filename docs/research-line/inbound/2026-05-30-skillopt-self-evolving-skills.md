---
title: "SkillOpt: Executive Strategy for Self-Evolving Agent Skills"
authors: Yifan Yang; Ziyang Gong; Weiquan Huang; Qihao Yang; Ziwei Zhou; Zisu Huang; Yan Li; Xuemei Gao; Qi Dai; Bei Liu; Kai Qiu; Yuqing Yang; Dongdong Chen; Xue Yang; Chong Luo
year: 2026
venue: arXiv / Microsoft project repo; surfaced by X
kind: preprint
status: note-written
captured: 2026-05-30
anchor_bucket: 4 · Industry research
source_url: https://x.com/thinkszyg/status/2060638656574972283
primary_url: https://arxiv.org/abs/2605.23904
repo_url: https://github.com/microsoft/SkillOpt
---

# 2026-05-30 · SkillOpt self-evolving skills

## What it is

SkillOpt is a 2026 preprint and Microsoft project repo that treats an agent `skill.md` as an external, trainable natural-language state. A target agent executes tasks with the current skill; rollouts are scored; a separate optimizer model proposes bounded add/delete/replace edits; and a held-out validation gate accepts only edits that strictly improve validation score. The accepted artifact is a compact skill document deployed with no extra inference-time model calls.

Source status: the X post was read; the arXiv abstract/HTML and GitHub README were checked. The method framing is directly supported by primary sources. Reported benchmark numbers should remain `pending reproduction` until the repo is run or third-party replications appear.

## Why it matters for our line

NOUS OS depends on reusable procedural memory that improves over repeated human-AI work without boundary drift. SkillOpt is a strong external anchor for the **skill as governed evolvable artifact** thesis: skill files should not be arbitrary prompts, but small, auditable, versioned policies updated through evidence and gates.

This directly supports the Harness Engineering lane:

```text
context index + boundary map + artifact contracts + evaluator specs + release gates + evidence write-back
```

SkillOpt adds a concrete loop for one evolvable resource type:

```text
skill rollout -> scored evidence -> bounded skill diff -> validation gate -> deploy/reject
```

## Where we share

- **Skills are first-class artifacts.** Skill documents are not disposable prompts; they are reusable procedural state.
- **Self-evolution needs gates.** The validation gate, rejected-edit buffer, and bounded textual learning rate align with NOUS OS release gates and Trading Brain’s human-gated promotion model.
- **Compactness matters.** Reported final skills are small enough to audit manually, which fits the NOUS OS principle that promoted agent behavior must remain reviewable.
- **Harness portability matters.** Reported transfer across Codex and Claude Code supports the idea that high-quality skills can outlive a single model shell.

## Where we differ / what we add

| External anchor | NOUS OS |
|---|---|
| Optimizes benchmark task success for agent skills. | Optimizes human-AI co-evolution: capability, responsibility, boundary integrity, and source discipline. |
| Uses held-out validation to accept skill edits. | Adds human review, privacy/capital/runtime boundaries, and reflection evidence before promotion. |
| Focuses on `skill.md` as the evolved artifact. | Treats skills as one resource among prompts, tools, memories, evaluator specs, notes, and review contracts. |
| Deployment means loading a better skill. | Deployment also requires proof that the human remains in authority and no live/capital surface is mutated without approval. |

The key delta: **SkillOpt shows how to train a skill; NOUS OS decides when a trained skill is safe to promote into a human-AI operating loop.**

## Reported results to track

- Six benchmarks, seven target models, three harnesses: direct chat, Codex, Claude Code.
- Best or tied on all 52 evaluated model/benchmark/harness cells.
- Reported GPT-5.5 gains over no skill: +23.5 direct chat, +24.8 Codex loop, +19.1 Claude Code.
- Reported Codex-trained SpreadsheetBench skill transfer to Claude Code: +59.7 points.
- Reported final skill size: 379–1,995 tokens, median roughly 920 tokens.

These are useful but not yet independently verified by us.

## What this changes in our practice

- Treat future skill changes as experimental diffs, not free-form rewrites.
- For low-risk NOUS OS / Trading Brain skills, consider a sandbox with train/validation/test cases and explicit rejection logs.
- Keep capital-adjacent and runtime-adjacent skills review-only until boundary/regression suites prove no forbidden behavior is introduced.
- Use repeated session failures as candidate training data, but never as automatic production mutation.

## Limitations of this work (from our perspective)

- Reported gains are author-reported preprint/project results until reproduced.
- Datasets are not included in the repo; reproduction requires task split preparation.
- Benchmark optimization can overfit if negative/boundary cases are weak.
- Agent task success does not by itself demonstrate safe human-AI co-evolution.
- Skill optimization for trading/research workflows must preserve source validation, action taxonomy, and human approval gates.

## Open questions for follow-up

- Can we run a small SkillOpt-like loop on a low-risk Trading Brain skill routing/eval suite?
- What is the minimum eval split needed to prevent skill-overfit and boundary regression?
- Should NOUS OS define a `SkillChangeProposalV1` artifact with before/after diff, evaluator results, rejected-edit trace, and human review state?
- Can compact learned skills improve source-validation quality without increasing hallucinated certainty?
- How should rejected edits be stored: as negative examples, TrustMem episodes, or repo-based eval cases?

## Citation

Yang, Y., Gong, Z., Huang, W., Yang, Q., Zhou, Z., Huang, Z., Li, Y., Gao, X., Dai, Q., Liu, B., Qiu, K., Yang, Y., Chen, D., Yang, X., & Luo, C. (2026). *SkillOpt: Executive Strategy for Self-Evolving Agent Skills*. arXiv:2605.23904. https://arxiv.org/abs/2605.23904
