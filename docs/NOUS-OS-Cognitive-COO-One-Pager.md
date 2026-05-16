# NOUS OS Cognitive COO One-Pager

## 定位

NOUS OS 是面向 human-AI co-evolution 的 Cognitive COO Operating System。

它把人类意图、可信记忆、事件调度、领域运行时、结果反馈和人类权威连接成一个可验证、可复用、可自我改进的认知经营系统。

## 一句话

```text
NOUS OS = Obsidian knowledge sedimentation + verified memory + event mesh + domain runtime + outcome proof + human authority.
```

## 组件关系

```text
Human intent
  -> Hermes / Aria: COO control plane
  -> Obsidian: human-readable knowledge sedimentation
  -> TrustMem: trustworthy hippocampus
  -> Synapse: event-driven service mesh
  -> Domain runtime: first proof = Trading Brain / trading-agent
  -> Outcome proof: scorecards, reviews, learning updates
  -> Next cycle: better judgment with human authority preserved
```

## 关键产品边界

- TrustMem：agents' trustworthy hippocampus，负责记忆、信任、衰减、验证。
- Obsidian：human-readable knowledge sedimentation layer，负责 North Star、playbook、architecture map、handoff、review 和 durable judgment。
- Synapse：event-driven service mesh for agents，负责事件、DAG、worker、budget routing。
- Trading Brain：first vertical proof，基于 NOUS OS 的 Personal AI Trading COO。
- Dashboard / Obsidian / CLI：review surfaces，不是 live state source of truth。

## CLS v2

NOUS OS V2 使用 CLS v2 衡量闭环是否真的变好：

```text
CLS = 0.35 * outcome_quality_delta
    + 0.20 * correction_absorption
    + 0.15 * memory_reuse_precision
    + 0.15 * repeatability_gain
    + 0.10 * boundary_integrity
    + 0.05 * human_agency_preservation
```

解释：

- 不只看任务产出，而看结果是否变好。
- 不只记录 human correction，而看它是否改变下一轮行为。
- 不只召回记忆，而看记忆是否精准、有用。
- 不只自动化，而要保护人类最终权威。

## 当前状态

已完成：

- `nous-os` public/local demo
- heartbeat dashboard
- CLS v1/QCER benchmark frame
- CLS v2 calculator and snapshot fields
- domain evaluator interface
- cross-repo release gate
- Trading Brain proof-loop contracts

进行中：

- Trading Brain reviewed experiment -> learning update -> next-cycle policy input 闭环
- domain evaluator 替换 synthetic demo score
- release gate hardening

## 不做什么

NOUS OS 不是全自动交易系统，不替代人类判断，不绕过 broker/risk/reconciliation gate，不把 demo score 当 production evaluator，不声称当前已经是 multi-tenant SaaS。

## 参考

- [benchmark-spec.md](./benchmark-spec.md)
- [domain-evaluator-interface.md](./domain-evaluator-interface.md)
- [cross-repo-release-gate.md](./cross-repo-release-gate.md)
- [north-star-v2-roadmap.md](./north-star-v2-roadmap.md)
