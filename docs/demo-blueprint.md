# NOUS OS Demo Blueprint

这个 demo 不是在仓库里直接复刻真实 `Aria` / `Synapse` / `TrustMem` 实现，而是保留三层职责边界，先证明 `nousos` 想讲的闭环可以跑通：

1. `AriaAdapter`
负责意图理解、任务编排、是否把人类历史反馈纳入当前决策。

2. `SynapseBus`
负责把任务并发扇出给多个 agent，模拟 event bus / DAG executor 的角色。

3. `TrustMemStore`
负责持久化 episode、override、pattern，并在下一轮命中时给 Aria 注入上下文。

## 运行

```bash
python3 examples/nousos_demo.py
```

## 这个 demo 证明什么

当前 demo 证明了基础闭环：

- 多 agent 可以在共享记忆之上执行，而不是每轮冷启动。
- 人类 override 不只是日志，而是下一轮调度策略的输入。
- Aria 可以先作为一个 adapter interface 存在，后面再替换成私有生产实现。

## Current Demo North Star

根据 NOUS OS 的 education/research-first 定位，当前 demo 不只展示“agent 变强”，而要展示“人与 AI 如何共同演进”：

```text
student/human intent
  -> AI first pass
  -> human boundary / correction
  -> memory + evidence update
  -> AI second pass changes behavior
  -> student reflection
  -> human keeps goal, values, verification, and final responsibility
```

具体实现计划见：

```text
docs/plans/2026-05-16-human-ai-coevolution-demo-refresh-plan.md
```

核心展示目标：

1. 观众能看到人决定了什么。
2. 观众能看到 AI 帮助了什么。
3. 观众能看到人设置了什么边界。
4. 观众能看到系统如何记住并改变下一轮。
5. 观众能看到什么仍然必须由人负责。

Dashboard 现在提供三个 narrative mode：

1. Student Learning Companion
2. Trading Agent Research Proof
3. Research Lab / Teacher View

每个 mode 都有对应 human boundary choices，并写入 `examples/runtime/dashboard-data.json`。Trading-agent 仍然是第一个垂直类应用 / research proof bed，但被明确解释为高约束边界研究案例，不是投资建议或商业化终点。

## Research Harness Artifact

当前 heartbeat demo 每次运行都会生成一个 structured research record：

```text
examples/runtime/research-records/<run_id>.json
examples/runtime/research-records/latest.json
```

这个 record 让 demo 从“看起来有动效的页面”变成可复盘的 education/research harness。它记录：

- human intent
- AI first pass
- selected human boundary
- memory/evidence update
- AI second pass behavior change
- reflection prompt / student takeaway
- correction absorption, memory reuse, boundary integrity, human agency preservation, reflection completeness, repeatability gain

`latest.json` 会随 GitHub Pages 发布，历史 run files 只作为本地研究记录保留。

## 下一步替换成真实组件

- 把 `AriaAdapter.plan()` 替换为真实 Aria 的 intent router / policy layer。
- 把 `SynapseBus.execute()` 替换为 `synapse` 的 event bus + DAG executor。
- 把 `TrustMemStore` 替换为 `trustmem` 的检索、trust score、decay、promotion 逻辑。
