---
title: "AutoResearch in NOUS OS — One Pager"
author: aria
created: 2026-04-06
updated: 2026-04-06
confidence: 0.93
verified_by: []
verification_status: unverified
data_freshness: 2026-04-06
decay_class: slow
sources_count: 1
domain: ai-infra
---

# AutoResearch in NOUS OS — 一页纸说明

## 一句话定义

**AutoResearch 是 NOUS OS 的研究引擎。**

如果说：
- **TrustMem** 负责记忆
- **Synapse** 负责协调
- **Aria** 负责意识与判断

那么：
- **AutoResearch** 负责让系统自己发现问题、设计实验、调用验证器、比较结果，并推动下一轮改进。

它让系统从“会回答问题”升级成“会持续变强”。

---

## 为什么它重要

一个真正的认知系统，不能只做三件事：
- 记住
- 理解
- 回答

它还必须会：
- 发现异常
- 提出假设
- 设计实验
- 验证假设
- 形成结论
- 推进下一步

这就是 AutoResearch 的角色。

---

## 在 NOUS OS 里的位置

- **TrustMem** = 记忆层（记什么、信什么）
- **Synapse** = 神经层（谁来执行、如何协调）
- **Aria** = 意识层（为什么、判断、人类对齐）
- **AutoResearch** = 研究层（发现问题 → 设计实验 → 验证 → 进化）

---

## 它不是普通搜索

普通 assistant / search / RAG 通常做的是：
- 回答你问的问题
- 总结资料
- 给一个建议

AutoResearch 做的是更高一层：

把“研究本身”变成一个可执行流程。

它不会停在“也许可以这样”，而是会继续：
1. 形成可测试假设
2. 设计 baseline 与变体
3. 调用 backtesting / replay / benchmark
4. 比较结果
5. 给出下一步建议

---

## 在 trading-agent 里的具体作用

### DayTrading

它帮我们完成了：
- 发现“今天没信号”不是一个答案，而是一个问题
- 拆出：
  - in-play 层
  - ORB 层
  - VWAP Bounce 层
  - Afternoon Breakout 层
  - 调度层
- 找到真正的瓶颈：
  - 调度不足
  - `catalyst_vol_mult`
  - `min_breakout_pct`
- 用 production-aligned researcher 跑对比
- 给出推荐参数：
  - `catalyst_vol_mult = 1.5`
  - `min_breakout_pct = 0.002`

### Long-Term

它帮我们完成了：
- 发现“没信号”不是因为 thesis 不成立
- 逐层定位：
  - 组合规则层
  - RS 层
  - momentum 层
  - technical 层
- 用 alpha research 证伪了：
  - 放松 `min_rs`
  - 放松 `min_momentum`
- 把优化方向收束到：
  - `same-subsector exclusion study`

---

## AutoResearch 与 Backtesting 的关系

### Backtesting 回答：
> “这套规则历史上表现如何？”

### AutoResearch 回答：
> “接下来最该研究哪套规则，怎么比较，哪个方向值得进入 paper trading？”

所以：

```text
AutoResearch 设计实验
    ↓
Backtesting 负责验证
    ↓
Aria 负责归因和决策建议
    ↓
进入 paper trading / production
```

---

## 为什么它是 NOUS OS 的关键层

如果没有 AutoResearch，NOUS OS 只是：
- 一个会记忆的系统
- 一个会协调的系统
- 一个会回答的系统

有了 AutoResearch，它才变成：
- 一个会发现自己问题
- 会做实验
- 会修正
- 会持续演化的系统

也就是说：

> **AutoResearch 是 NOUS OS 从“智能助手”升级成“认知操作系统”的关键层。**

---

## 产品层面的意义

如果以后要讲 NOUS OS，这一层非常关键，因为它把系统能力从：
- **generation（生成）**

推进到：
- **compounding intelligence（复利式智能）**

它让 NOUS OS 不只是“答得好”，而是“随着时间变得更聪明”。

---

## 当前实验状态（2026-04-06）

### 已有结论

#### DayTrading
推荐进入新一轮 paper trading 的参数：
```yaml
catalyst_vol_mult: 1.5
min_breakout_pct: 0.002
```

#### Long-Term 参数层
以下方向都不如 baseline：
- `min_momentum = 0.015`
- `min_momentum = 0.010`
- `min_rs = 1.03`
- `min_rs = 1.00`
- `min_rs = 1.03 + min_momentum = 0.015`

因此：
> 不要继续优先调 `min_rs` / `min_momentum`

### 正在推进
- production-aligned long-term structural researcher
- 四组结构对比：
  - baseline
  - max 2
  - leader + challenger
  - profit-gated second entry

---

## 最后一句话

> **AutoResearch 不只是自动帮你想，而是自动把你的判断变成可验证、可比较、可推进的研究过程。**
