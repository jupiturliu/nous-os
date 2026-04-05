# Heartbeat Demo

这个 demo 证明 Aria 现有 `heartbeat + agent-bus` 工作流可以平滑接到 NOUS OS：

1. Aria heartbeat 读取 `implementation_queue.json` / `learning_queue.json`
2. 用 `synapse/orchestration/aria_orchestrator.py` 的 `publish_from_agent_bus()` 发布到 Event Bus
3. `synapse` worker 基类自动做 TrustMem episode recall / log
4. 完成后回写 runtime queue 状态，并写入 `alerts.json`

## 运行

```bash
python3 examples/nousos_heartbeat_demo.py
```

正式入口：

```bash
python3 scripts/run_nous_heartbeat.py
```

它会同时生成前端可消费的数据文件：

```bash
examples/runtime/dashboard-data.json
```

## 可视化页面

```bash
python3 -m http.server
```

然后打开：

```text
http://localhost:8000/demo/heartbeat-dashboard.html
```

## 带按钮的本地控制台

```bash
python3 scripts/run_nous_dashboard.py
```

然后打开：

```text
http://127.0.0.1:8765/demo/heartbeat-dashboard.html
```

页面里的 `Run heartbeat` 按钮会直接调用本地 `POST /api/run-heartbeat`，重新生成 snapshot。

## Benchmark Mapping

这个 demo 现在不仅展示效果，也展示 benchmark：

- `Quality Lift` → Q: Quality Improvement
- `Human Policy` → C: Correction Absorption
- `TrustMem memory reuse` → E: Memory Reuse
- `Task Expansion` → R: Repeatability Gain
- `CLS Score` → 综合 `Cognitive Loop Score`

定义见 [benchmark-spec.md](./benchmark-spec.md)。

## 隔离运行态

为了不碰现有线上队列，demo 使用：

- `examples/runtime/agent-bus/implementation_queue.json`
- `examples/runtime/agent-bus/learning_queue.json`
- `examples/runtime/agent-bus/alerts.json`

## 价值

- 你能演示 Aria 仍然是唯一协调者
- 但底层派发从 JSON 轮询升级成 Synapse Event Bus
- TrustMem 记忆在派发前和执行后都参与闭环
