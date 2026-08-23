# Heartbeat Demo

这个 demo 证明 Aria 现有 `heartbeat + agent-bus` 工作流可以平滑接到 NOUS OS：

1. Aria heartbeat 读取 `implementation_queue.json` / `learning_queue.json`
2. 用 `synapse/orchestration/aria_orchestrator.py` 的 `publish_from_agent_bus()` 发布到 Event Bus
3. `synapse` worker 基类自动做 TrustMem episode recall / log
4. 完成后回写 runtime queue 状态，并写入 `alerts.json`

## 运行

```bash
NOUS_OS_HOME=/tmp/nous-os-demo nous-os run heartbeat --profile research
```

它会同时生成前端可消费的数据文件：

```bash
$NOUS_OS_HOME/projections/dashboard-data.json
$NOUS_OS_HOME/projections/research-records/latest.json
```

## 可视化页面

```bash
nous-os serve web --profile student
```

然后打开：

```text
http://127.0.0.1:8787/demo/heartbeat-dashboard.html
```

页面里的 `Run heartbeat` 按钮会直接调用本地 `POST /api/run-heartbeat`，重新生成 snapshot。

## Human-AI Co-Evolution Demo

当前 heartbeat demo 展示两轮闭环，并把可视化目标从“agent 变强”升级为“人与 AI 共同演进，同时保留人类边界”：

```text
student/human intent
  -> AI first pass
  -> human boundary / correction
  -> TrustMem memory + evidence update
  -> AI second pass changes behavior
  -> student reflection
  -> human keeps goal, values, verification, and final responsibility
```

Demonstrated surfaces:

- Demo Mode selector: Student Learning Companion / Trading Agent Research Proof / Research Lab.
- Safety Boundaries panel: privacy, facts, learning, decision, values.
- Human Agency panel: human keeps goal, values, verification, final responsibility.
- Student Reflection final timeline stage.
- First Vertical Explainer: trading-agent is a high-constraint education/research proof bed, not investing advice.

The generated snapshot includes:

```json
{
  "demo_mode": "student|trading_vertical|research_lab",
  "north_star": "education/research-first human-AI co-evolution",
  "human_agency": "...",
  "safety_boundaries": "...",
  "reflection": "...",
  "first_vertical": "trading-agent research proof bed"
}
```

Every run also emits a structured education/research record:

```text
$NOUS_OS_HOME/projections/research-records/<run_id>.json
$NOUS_OS_HOME/projections/research-records/latest.json
```

The per-run files are local research projections and are ignored by git. Reviewers update the tracked Public Snapshot only with `nous-os publish-site-data --profile research`.

## Student Sandbox v0

Phase 4 starts with a local-only sandbox:

```bash
nous-os serve web --profile student
```

It asks clarifying questions, returns hints and practice instead of a final answer, requires source checks, redacts private details before record emission, and ends with a reflection prompt. It writes:

```text
$NOUS_OS_HOME/projections/research-records/student-sandbox-latest.json
```

## Benchmark Mapping

这个 demo 现在不仅展示效果，也展示 benchmark：

- `Quality Lift` → Q: Quality Improvement
- `Human Policy` → C: Correction Absorption
- `TrustMem memory reuse` → E: Memory Reuse
- `Task Expansion` → R: Repeatability Gain
- `CLS Score` → 综合 `Cognitive Loop Score`

定义见 [benchmark-spec.md](./benchmark-spec.md)。

## Public Release Smoke

This command set checks the public demo path and the read-only cross-repo release gate:

```bash
NOUS_OS_HOME=/tmp/nous-os-smoke nous-os run heartbeat --profile research
nous-os validate harness
nous-os validate contracts
python3 scripts/check_cross_repo_release_gate.py --workspace /Users/liyao/nousos --json
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Heartbeat and the unit tests run inside this repository. When installed Synapse/Aria runtime modules are unavailable, Heartbeat uses the local deterministic Adapter. `check_cross_repo_release_gate.py` expects the full workspace with sibling `synapse`, `trustmem`, `hermes-agent`, and `trading-agent` repos.

## 隔离运行态

为了不碰现有线上队列，demo 使用：

- `$NOUS_OS_HOME/state/heartbeat/agent-bus/implementation_queue.json`
- `$NOUS_OS_HOME/state/heartbeat/agent-bus/learning_queue.json`
- `$NOUS_OS_HOME/state/heartbeat/agent-bus/alerts.json`

## 价值

- 你能演示 Aria 仍然是唯一协调者
- 但底层派发从 JSON 轮询升级成 Synapse Event Bus
- TrustMem 记忆在派发前和执行后都参与闭环
