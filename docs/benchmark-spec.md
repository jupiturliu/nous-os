# NOUS OS Benchmark Spec

NOUS OS 不是单模型 benchmark，而是系统级 benchmark。核心问题不是“模型更聪明了吗”，而是：

1. 第二轮是否比第一轮更好
2. 人类纠正一次后，系统是否吸收了这条反馈
3. 记忆是否真的被复用
4. 这种提升是否可重复、可展示

## Evaluation Frame

使用 `baseline vs treatment`：

- `baseline`：第一轮冷启动，无历史记忆
- `treatment`：第二轮，带 memory recall + human override

## Public Metrics

### Q — Quality Improvement

定义：

```text
(quality_treatment - quality_baseline) / quality_baseline
```

含义：
- 第二轮结果是否显著优于第一轮

### C — Correction Absorption

定义：

```text
1.0 if a human correction is recorded and changes later behavior, else 0.0
```

含义：
- 人类纠正是否真的进入系统，而不是停留在日志里

### E — Memory Reuse

定义：

```text
second_run_tasks_with_memory / total_second_run_tasks
```

含义：
- 第二轮有多少任务真正复用了记忆

### R — Repeatability Gain

定义：

```text
(second_run_tasks - first_run_tasks) / first_run_tasks
```

含义：
- 系统是否根据第一轮和人类反馈，扩展或细化了第二轮计划

## CLS

定义一个简化版 `Cognitive Loop Score`：

```text
CLS = 0.4 * Q + 0.2 * C + 0.2 * E + 0.2 * R
```

说明：
- `Q` 权重最高，因为结果质量仍然是主目标
- `C`、`E`、`R` 分别衡量反馈吸收、记忆复用、跨轮改进

## Demo Mapping

在 `demo/heartbeat-dashboard.html` 里，这些指标应该都有明确映射：

- `Quality Lift` → Q
- `Human Policy` → C
- `Memory Loop / Memory Reuse` → E
- `Task Expansion` → R
- `CLS Score` → 汇总分

## What Counts As Publicly Convincing

如果一个 demo 同时满足下面几条，外部更容易承认它是“认知闭环”而不是普通 workflow：

- 第二轮质量稳定高于第一轮
- 人类 override 改变了第二轮任务结构
- 第二轮大部分任务命中了记忆
- 这种提升可以在不同 goal / override 类型下复现
