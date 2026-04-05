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

- 多 agent 可以在共享记忆之上执行，而不是每轮冷启动。
- 人类 override 不只是日志，而是下一轮调度策略的输入。
- Aria 可以先作为一个 adapter interface 存在，后面再替换成私有生产实现。

## 下一步替换成真实组件

- 把 `AriaAdapter.plan()` 替换为真实 Aria 的 intent router / policy layer。
- 把 `SynapseBus.execute()` 替换为 `synapse` 的 event bus + DAG executor。
- 把 `TrustMemStore` 替换为 `trustmem` 的检索、trust score、decay、promotion 逻辑。
