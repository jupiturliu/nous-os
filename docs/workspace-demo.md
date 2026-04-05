# Workspace Demo

这个入口直接复用 `workspace` 下三套代码，而不是只做本仓库内 mock：

- `aria`：沿用其架构角色，把 Aria 作为 planner / coordination layer 的接口边界
- `synapse`：直接 import `AgentWorker`、`AriaSynapseBridge`、`HumanOverrideHandler`
- `trustmem`：直接调用 `trustmem/tools/knowledge_search.py` 做知识检索

## 运行

```bash
python3 examples/nousos_workspace_demo.py
```

## 运行时数据

为了不污染现有工作区状态，demo 运行时数据写到：

- `examples/runtime/data/episodes/episodes.jsonl`
- `examples/runtime/insights.json`
- `examples/runtime/alerts.json`

## 证明点

- 多 worker 执行来自真实 `synapse` `AgentWorker` 基类
- task dispatch 经过真实 `AriaSynapseBridge`
- human override 经过真实 `HumanOverrideHandler`
- recall 走真实 episode logger 逻辑
- 长期知识补充来自真实 `trustmem` search 工具
