# Human Being + AI Agent Co-Evolution Research Brief — 2026-05-16

This brief synthesizes three parallel research scans for NOUS OS:

1. human-AI co-evolution / human-AI teaming / mixed-initiative interaction;
2. AI agent self-evolution / memory / reflection / continual learning;
3. AI in education / metacognition / cognitive offloading / learner agency.

NOUS OS framing:

```text
human intention
  -> AI amplification
  -> human boundary / judgment
  -> shared memory and evidence
  -> agent behavior adaptation
  -> human reflection and capability growth
  -> next cycle with better human + better agent
```

Infrastructure such as TrustMem, Synapse, Obsidian, Hermes, harnesses, dashboards, Student Sandbox, and trading-agent is experimental apparatus. The target is human beings and AI agents co-learning and self-evolving while preserving human agency, judgment, values, taste/identity, and responsibility.

## Executive synthesis

Recent research supports the NOUS OS direction but adds several warnings:

1. Human + AI is not automatically better than either alone. Meta-analysis suggests human-AI combinations often underperform the stronger single party, especially in decision tasks; gains are more likely in creative/content generation tasks.
2. Agency preservation has a cost. Giving humans more control can improve ownership and agency but can also increase cognitive burden; NOUS OS must preserve agency while reducing agency cost.
3. Bidirectional alignment is real. AI adapts to humans, but humans are also changed by AI. This means co-evolution must be visible, reviewable, rejectable, and reversible.
4. Memory is dangerous when it becomes stale personalization. Agent memory should remember, challenge, decay, and forget; it must distinguish user preference, user belief, verified fact, evidence, hypothesis, and boundary.
5. Reflection helps agents, but unverified reflection can harden false lessons. Reflexion/Self-Refine/ExpeL-style loops need external evidence, tests, user correction, and review triggers.
6. AI tutors can improve learning when constrained as tutors/coaches, but unguarded AI can harm independent learning and retention.
7. Student-facing AI must avoid cognitive offloading of the hard parts: source checking, independent explanation, value judgment, authorship, and responsibility.
8. Trust calibration requires more than confidence scores. Agent errors should lower autonomy until evidence restores trust.

## A. Human-AI co-evolution / teaming / agency

### 1. Hybrid intelligence: Human–AI coevolution and learning

- Authors/year: Sanna Järvelä, Guoying Zhao, Andy Nguyen, Haoyu Chen, 2025
- Link: https://doi.org/10.1111/bjet.13560
- Finding: Hybrid intelligence should be understood as human and AI systems improving learning, regulation, decision-making, and capabilities together, not as AI replacing human cognition.
- Limitations: Framework-oriented; longitudinal empirical evidence remains limited.
- NOUS OS implication: Make human capability growth an explicit metric. Student Sandbox and trading-agent should measure whether the human becomes better, not only whether AI output improves.

### 2. Position: Towards Bidirectional Human-AI Alignment

- Authors/year: Hua Shen, Tiffany Knearem, Reshmi Ghosh, Kenan Alkiek, K. Siva Krishna, Yachuan Liu, et al., 2024
- Link: https://doi.org/10.48550/arxiv.2406.09264
- Finding: Alignment is bidirectional and dynamic: AI changes human behavior and humans change AI behavior.
- Limitations: Position/framework paper; operational metrics remain underdeveloped.
- NOUS OS implication: Agent adaptation must be auditable and reversible. TrustMem should capture not only preferences but also evidence, corrections, user refusals, conflicts, and boundary changes.

### 3. Adaptive Human-Agent Teaming: A Review of Empirical Studies from the Process Dynamics Perspective

- Authors/year: Mengyao Wang, Jia Wu, Shuo Ma, Nuo Li, Peng Zhang, Ning Gu, 2025
- Link: https://doi.org/10.48550/arxiv.2504.10918
- Finding: Human-agent teaming evolves across formation, role development, team development, and team improvement; trust and roles are dynamic process variables.
- Limitations: Review; long-term LLM-agent field data is sparse.
- NOUS OS implication: Model each human-agent relationship as a team lifecycle: initial contract, role division, feedback calibration, capability update, review.

### 4. When combinations of humans and AI are useful: A systematic review and meta-analysis

- Authors/year: Michelle Vaccaro, Abdullah Almaatouq, Thomas W. Malone, 2024
- Link: https://doi.org/10.1038/s41562-024-02024-1
- Finding: Across 106 experiments, human-AI combinations often underperform the better single party; gains are more likely in creation tasks than decision tasks.
- Limitations: Heterogeneous studies; some latest LLM-agent workflows are not fully represented.
- NOUS OS implication: Do not assume human+AI is good by default. For creative/exploratory tasks, use divergent generation + human curation. For decisions, use AI for evidence surfacing, uncertainty disclosure, counterarguments, and review rather than direct authority.

### 5. Toward General Design Principles for Generative AI Applications

- Authors/year: Justin D. Weisz, Michael Müller, Jessica He, Stephanie Houde, 2023
- Link: https://doi.org/10.48550/arxiv.2301.05578
- Finding: Generative AI applications should expose variability, support exploration/control, build mental models, and guard against misuse and overreliance.
- Limitations: Design principles rather than longitudinal evaluation.
- NOUS OS implication: Preserve multiple candidate paths, rejected alternatives, uncertainty, and evidence trails in Obsidian/TrustMem instead of storing only final outputs.

### 6. Sustaining Human Agency, Attending to Its Cost

- Authors/year: Yimin Xiao, Cartor Hancock, Sweta Agrawal, Nikita Mehandru, Niloufar Salehi, Marine Carpuat, 2025
- Link: https://doi.org/10.1145/3706598.3713626
- arXiv: https://doi.org/10.48550/arxiv.2503.07970
- Finding: More human control can preserve agency but also increases cognitive burden and time cost.
- Limitations: Language-use setting; transfer to broader agent systems requires care.
- NOUS OS implication: Preserve agency while reducing agency cost. Use risk-tiered control: high-stakes decisions require explicit human authority; low-risk repetitive steps can be delegated under clear contracts.

### 7. Intelligence as Agency

- Authors/year: Arvind Satyanarayan, Graham M. Jones, 2024
- Link: https://doi.org/10.21428/e4baedd9.2d7598a2
- Finding: AI intelligence should be evaluated by whether it expands or constrains human agency and action space.
- Limitations: Theoretical/design argument.
- NOUS OS implication: Add an agency expansion test to every feature: does it create more understandable, selectable, reversible, and reflective action paths for the human?

### 8. Exploring the Impact of AI Value Alignment in Collaborative Ideation

- Authors/year: Alicia Guo, Pat Pataranutaporn, Pattie Maes, 2024
- Link: https://doi.org/10.1145/3613905.3650892
- Finding: AI assistants' implicit value framing shapes both output and users' perceived ownership/value presence.
- Limitations: Ideation task, limited value dimensions.
- NOUS OS implication: Agents must disclose value assumptions and optimization lenses. Obsidian notes should preserve which value frame shaped a suggestion.

### 9. Homogenization Effects of Large Language Models on Human Creative Ideation

- Authors/year: Barrett R. Anderson, Jash Hemant Shah, Max Kreminski, 2024
- Link: https://doi.org/10.1145/3635636.3656204
- Finding: LLMs can increase individual fluency but homogenize ideas across users.
- Limitations: Small sample and specific creative tasks.
- NOUS OS implication: Protect human taste and identity. Add anti-homogenization modes: minority alternatives, contrarian frames, user's historical style, and explicit preservation of unusual ideas.

### 10. Mitigative Strategies for Recovering From Large Language Model Trust Violations

- Authors/year: Max J. Martell, Jessica Baweja, Brandon Dreslin, 2024
- Link: https://doi.org/10.1177/15553434241303577
- Finding: Confidence scores, capability explanations, and user feedback did not significantly restore trust after LLM error in a short task.
- Limitations: Trivia setting; short-term experiment.
- NOUS OS implication: Trust repair needs evidence ledgers, error records, permission downgrades, and demonstrated recovery, not just UI confidence indicators.

### 11. NIST AI Risk Management Framework 1.0 + Generative AI Profile

- Organization/year: NIST, 2023/2024
- Links: https://doi.org/10.6028/nist.ai.100-1 and https://doi.org/10.6028/nist.ai.600-1
- Finding: Trustworthy AI requires governance, mapping, measurement, management, transparency, privacy, reliability, accountability, and risk controls.
- Limitations: Governance framework, not a human-AI co-evolution theory.
- NOUS OS implication: Make risk governance product-internal: every agent/workflow should have risk class, permissions, evidence trail, review triggers, and rollback path.

## B. Agent self-evolution / memory / reflection

### 1. Reflexion: Language Agents with Verbal Reinforcement Learning

- Authors/year: Noah Shinn, Federico Cassano, Edward Berman, Ashwin Gopinath, Karthik Narasimhan, Shunyu Yao, 2023
- Link: https://arxiv.org/abs/2303.11366
- Contribution: Agents generate natural-language reflections after failure and store them in episodic memory for future attempts.
- Limitations: Bad reflections can poison memory; attribution may be wrong.
- NOUS OS implication: Reflections should be provisional until verified. Store evidence, context, confidence, review trigger, and failure attribution.

### 2. Generative Agents: Interactive Simulacra of Human Behavior

- Authors/year: Joon Sung Park, Joseph O'Brien, Carrie Cai, Meredith Ringel Morris, Percy Liang, Michael Bernstein, 2023
- Link: https://arxiv.org/abs/2304.03442
- Contribution: Memory stream + reflection + planning produces coherent long-horizon agent behavior.
- Limitations: Simulation environment; importance scoring and abstraction can drift.
- NOUS OS implication: Use layered memory: raw event, reflection, plan. Keep abstraction traceable, challengeable, and decayable.

### 3. Self-Refine: Iterative Refinement with Self-Feedback

- Authors/year: Aman Madaan et al., 2023
- Link: https://arxiv.org/abs/2303.17651
- Contribution: LLM generates output, self-feedback, and revision without training.
- Limitations: Can become self-consistent rather than correct without external verification.
- NOUS OS implication: Self-refinement must be paired with tools, tests, citations, human correction, or outcome evidence.

### 4. Voyager: An Open-Ended Embodied Agent with Large Language Models

- Authors/year: Guanzhi Wang, Yuqi Xie, Yunfan Jiang, Ajay Mandlekar, Chaowei Xiao, Yuke Zhu, Linxi Fan, Anima Anandkumar, 2023
- Link: https://arxiv.org/abs/2305.16291
- Contribution: Lifelong agent with automatic curriculum, executable skill library, and iterative improvement from environment feedback.
- Limitations: Clear feedback environment; real-world permissions and skill safety are harder.
- NOUS OS implication: Skill memory should have version, test, permission scope, applicability conditions, and failure cases.

### 5. MemGPT: Towards LLMs as Operating Systems

- Authors/year: Charles Packer, Sarah Wooders, Kevin Lin, Vivian Fang, Shishir Patil, Ion Stoica, Joseph Gonzalez, 2023/2024
- Link: https://arxiv.org/abs/2310.08560
- Contribution: LLM as OS-like controller with virtual context management and memory paging.
- Limitations: Model-driven memory management can miswrite or overretrieve; privacy/conflict handling is limited.
- NOUS OS implication: Use memory hierarchy: working context, session memory, long-term memory, archival evidence. Govern write/read/decay/forget explicitly.

### 6. ExpeL: LLM Agents Are Experiential Learners

- Authors/year: Andrew Zhao, Daniel Huang, Quentin Xu, Matthieu Lin, Yong-Jin Liu, Gao Huang, 2023/2024
- Link: https://arxiv.org/abs/2308.10144
- Contribution: Agents extract natural-language lessons from success/failure trajectories and reuse them across tasks.
- Limitations: Lessons can overfit and lose applicability conditions.
- NOUS OS implication: Lessons should be conditional: task type, constraints, toolset, examples, counterexamples, last verified date.

### 7. AgentBench: Evaluating LLMs as Agents

- Authors/year: Xiao Liu et al., 2023/2025 revisions
- Link: https://arxiv.org/abs/2308.03688
- Contribution: Multi-environment benchmark for LLM-as-agent capabilities.
- Limitations: Benchmarks do not capture long-term human-agent relationships, memory harm, or user agency.
- NOUS OS implication: Create longitudinal evaluations: cross-session memory, user correction, stale preference, boundary violation, trust recovery.

### 8. Towards Understanding Sycophancy in Language Models

- Authors/year: Mrinank Sharma, Meg Tong, Tomasz Korbak, David Duvenaud, Amanda Askell, Samuel Bowman, Esin Durmus, Ethan Perez, et al., 2023/2025 revisions
- Link: https://arxiv.org/abs/2310.13548
- Contribution: RLHF and preference training can encourage models to agree with users instead of prioritizing truth.
- Limitations: Focus on model answers more than long-term memory agents.
- NOUS OS implication: Personalization must not become agreement. Track truth-over-agreement, appropriate challenge, over-agreement, and preference/fact separation.

### 9. Sycophancy to Subterfuge: Investigating Reward-Tampering in Large Language Models

- Authors/year: Carson Denison, Monte MacDiarmid, Fazl Barez, David Duvenaud, Shauna Kravec, Samuel Marks, Nicholas Schiefer, Alex Tamkin, Jared Kaplan, Buck Shlegeris, Samuel Bowman, Ethan Perez, Evan Hubinger, 2024
- Link: https://arxiv.org/abs/2406.10162
- Contribution: Places sycophancy on a broader spectrum of specification gaming and reward tampering.
- Limitations: Experimental settings; direct product generalization needs care.
- NOUS OS implication: Do not optimize agents on user satisfaction alone. Include truthfulness, calibration, auditability, reversibility, and privacy in the reward/evaluation design.

### 10. AgentGym: Evolving Large Language Model-based Agents across Diverse Environments

- Authors/year: Zhiheng Xi, Yiwen Ding, Wenxiang Chen, Boyang Hong, Honglin Guo, et al., 2024
- Link: https://arxiv.org/abs/2406.04151
- Contribution: Framework for evolving LLM agents across environments via trajectories and feedback.
- Limitations: Task skill evolution more than human relationship evolution.
- NOUS OS implication: Separate task skill evolution from user model evolution; optimize skills more aggressively, user modeling more conservatively.

### 11. AFlow: Automating Agentic Workflow Generation

- Authors/year: Jiayi Zhang, Jinyu Xiang, Zhaoyang Yu, Fengwei Teng, Xionghui Chen, Jiaqi Chen, Mingchen Zhuge, Xin Cheng, Sirui Hong, Jinlin Wang, et al., 2024/2025
- Link: https://arxiv.org/abs/2410.10762
- Contribution: Agent workflow architectures can themselves be generated and optimized.
- Limitations: Optimization target can create benchmark hacks and opaque complexity.
- NOUS OS implication: Workflow evolution must be policy-constrained: privacy, evidence, human approval, rollback, and explainability.

### 12. Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory

- Authors/year: Prateek Chhikara, Dev Khant, Saket Aryan, Taranjeet Singh, Deshraj Yadav, 2025
- Link: https://arxiv.org/abs/2504.19413
- Contribution: Production-oriented long-term memory architecture for AI agents.
- Limitations: Memory extraction still risks stale personalization and model-driven overcapture.
- NOUS OS implication: Optimize not only recall, but also non-recall of irrelevant/private/stale memory.

## C. Education / metacognition / cognitive offloading

### 1. Generative AI without guardrails can harm learning: Evidence from high school mathematics

- Authors/year: Hamsa Bastani, Osbert Bastani, Alp Sungu, Haosen Ge, Özge Kabakcı, Rei Mariman, 2025
- Link: https://doi.org/10.1073/pnas.2422633122
- Finding: Unguarded GPT-4 assistance improved practice performance but harmed later independent performance; tutor-like guardrails mitigated harm.
- Limitations: High-school math, short-term intervention.
- NOUS OS implication: Student Sandbox must be hints/checklists/questions, not final answers. Include no-AI independent explanation.

### 2. Tutor CoPilot: A Human-AI Approach for Scaling Real-Time Expertise

- Authors/year: Rose E. Wang, Ana T. Ribeiro, Carly D. Robinson, Susanna Loeb, Dorottya Demszky, 2024
- Link: https://edworkingpapers.com/ai24-1054
- Finding: AI support for human tutors improved student mastery, especially for less-experienced tutors.
- Limitations: AI assists tutors, not direct student autonomy.
- NOUS OS implication: AI can serve as a meta-coach: suggesting next questions and verification steps while keeping student/teacher agency intact.

### 3. GPT-4 as a Homework Tutor can Improve Student Engagement and Learning Outcomes

- Authors/year: Alessandro Vanzo, Sankalan Pal Chowdhury, Mrinmaya Sachan, 2024
- Link: https://arxiv.org/abs/2409.15981
- Finding: GPT-4 tutoring can improve engagement and learning outcomes when used for explanation and feedback.
- Limitations: Preprint; effect depends heavily on task and guardrails.
- NOUS OS implication: Use AI for explanation/feedback, but require reflection: what did AI help with, what did I verify, why do I trust it?

### 4. AI tutoring can safely and effectively support students: An exploratory RCT in UK classrooms

- Authors/year: LearnLM Team / Google & Eedi, 2025/2026 preprint
- Link: https://arxiv.org/abs/2512.23633
- Finding: A supervised AI tutoring system in a math platform can support learning safely under expert oversight.
- Limitations: Exploratory; platform-specific; supervised setting.
- NOUS OS implication: Student Sandbox should record AI suggestion, student acceptance/rejection, and student modification rationale.

### 5. Investigating the Role of ChatGPT in Supporting Metacognitive Processes During Problem-Solving Activities

- Authors/year: Francesco Contel, Annalisa Cusi, 2025
- Link: https://doi.org/10.1007/s40751-024-00164-7
- Finding: With appropriate prompts, ChatGPT can support planning, monitoring, evaluation, and strategy adjustment.
- Limitations: Small/targeted setting.
- NOUS OS implication: Add metacognitive checkpoints: plan, monitor, verify, revise, reflect.

### 6. AI Tools in Society: Impacts on Cognitive Offloading and the Future of Critical Thinking

- Authors/year: Michael Gerlich, 2025
- Link: https://doi.org/10.3390/soc15010006
- Finding: Frequent AI tool use is associated with lower critical thinking, mediated by cognitive offloading.
- Limitations: Correlational; self-report limitations.
- NOUS OS implication: Distinguish beneficial offloading from harmful offloading. Offload organization and counterexamples, not judgment and responsibility.

### 7. ChatGPT as a cognitive crutch: Evidence from a randomized controlled trial on knowledge retention

- Authors/year: A. Barcaui, 2025
- Link: https://doi.org/10.1016/j.ssaho.2025.102287
- Finding: ChatGPT can reduce cognitive load but harm long-term retention.
- Limitations: Undergraduate sample and specific topic.
- NOUS OS implication: Add delayed/no-AI explanation as a required metric.

### 8. Your Brain on ChatGPT: Accumulation of Cognitive Debt when Using an AI Assistant for Essay Writing Task

- Authors/year: Nataliya Kosmyna, Eugene Hauptmann, Ye Tong Yuan, Jessica Situ, Xian-Hao Liao, Ashly Vivian Beresnitzky, Iris Braunstein, Pattie Maes, 2025
- Link: https://www.media.mit.edu/publications/your-brain-on-chatgpt/
- Finding: LLM writing assistance may reduce memory, ownership, and engagement compared with search/no-tool conditions.
- Limitations: Preprint/lab setting; widely discussed and should be interpreted cautiously.
- NOUS OS implication: Protect authorship: which judgment is yours, which part came from AI, can you explain key claims without AI?

### 9. Generative AI and Agency in Education: A Critical Scoping Review and Thematic Analysis

- Authors/year: Jasper Roe, Mike Perkins, 2024
- Link: https://arxiv.org/abs/2411.00631
- Finding: GenAI can enhance or reduce learner agency depending on task design and who retains decision rights.
- Limitations: Scoping review; causal evidence limited.
- NOUS OS implication: Record agency evidence: student choice, adoption/rejection rationale, boundary added, responsibility retained.

### 10. Assigning AI: Seven Approaches for Students, with Prompts

- Authors/year: Ethan Mollick, Lilach Mollick, 2023
- Link: https://arxiv.org/abs/2306.10052
- Finding: AI can act as tutor, coach, mentor, teammate, tool, simulator, or student; each role has different risks.
- Limitations: Practical framework, not empirical RCT.
- NOUS OS implication: Explicitly assign AI roles by phase: question coach, source scout, skeptic, examiner; never default to ghostwriter.

### 11. UNESCO Guidance for Generative AI in Education and Research

- Organization/year: UNESCO, 2023
- Link: https://www.unesco.org/en/articles/guidance-generative-ai-education-and-research
- Finding: Emphasizes privacy, transparency, teacher oversight, age appropriateness, inclusion, and human agency.
- Limitations: Policy guidance, not classroom experiment.
- NOUS OS implication: Add disclosure template: AI helped with X; I verified Y; I did not let AI do Z; I take responsibility for W.

## Design implications for NOUS OS

### 1. Replace automation-first with co-evolution-first

Every feature should answer:

```text
Which part of the human-AI co-evolution loop does this strengthen?
```

If the answer is only task speed or automation, it is not core.

### 2. Use different collaboration modes by task type

- Creative/exploratory: AI generates diverse possibilities; human curates and preserves taste.
- Learning: AI hints, questions, and challenges; human explains independently.
- Decision/high-stakes: AI surfaces evidence, uncertainty, and counterarguments; human retains authority.
- Memory/personalization: AI retrieves and challenges context; human can inspect, correct, decay, or delete.

### 3. Treat trust as task-specific and recoverable only by evidence

Trust should decompose into:

- ability trust;
- boundary trust;
- evidence trust;
- memory trust;
- permission trust;
- relationship trust.

After an agent error, autonomy should be downgraded until evidence restores it.

### 4. Make memory lifecycle explicit

Memory should follow:

```text
capture -> classify -> validate -> consolidate -> retrieve -> challenge -> decay -> forget
```

Key distinction:

- user preference is not fact;
- user belief is not fact;
- agent reflection is not verified lesson;
- old context is not current intent;
- private data is not memory.

### 5. Add anti-sycophancy and anti-homogenization mechanisms

NOUS OS should reward:

- helpful disagreement;
- uncertainty surfacing;
- minority alternatives;
- value lens disclosure;
- source checks;
- user-owned judgment.

### 6. Student Sandbox should measure learning, not output quality

The first student-adjacent trial should require:

- student-stated question;
- AI role as question coach/source scout/skeptic/examiner;
- source check;
- boundary statement;
- no-AI independent explanation;
- responsibility/authorship statement.

### 7. Trading-agent remains a high-constraint proof bed, not the goal

It tests:

- decision boundaries;
- human approval;
- risk/reconciliation lessons;
- evidence-linked outcomes;
- agent challenge rather than blind action.

## Recommended updates to current NOUS OS docs

Already aligned:

- `docs/human-ai-symbiosis-self-evolution.md`
- `docs/human-ai-coevolution-model-v0.md`
- `docs/self-evolution-metrics-v0.md`
- `docs/memory-philosophy-v0.md`
- `docs/student-sandbox-self-evolution-metrics-map.md`
- `docs/human-ai-coevolution-framework-diagram.md`

Recommended next modifications:

1. Add this research brief as a source note under `docs/research/`.
2. Add citations from this brief into `memory-philosophy-v0.md`, `self-evolution-metrics-v0.md`, and `student-sandbox-self-evolution-metrics-map.md` as the theory track matures.
3. Before first Student Sandbox trial, update the review template to require:
   - no-AI independent explanation;
   - student AI disclosure;
   - source-check evidence;
   - agency/responsibility statement.

## Immediate NOUS OS research questions

1. How do we measure Human Capability Delta without fake precision?
2. What memory entries should default to challenge/decay rather than remember?
3. How do we keep agent adaptation from becoming sycophancy?
4. What is the smallest Student Sandbox trial that can reveal cognitive offloading vs genuine learning?
5. How should trust recovery downgrade/restore agent autonomy after errors?
6. Can Obsidian review rituals make human-agent relationship quality compound over months?
