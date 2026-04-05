# Aria Heartbeat Integration

Aria 当前 heartbeat 是 prompt 驱动，不是单独 Python runner。最直接的接法是让 heartbeat 在发现 queue 里有 pending 项时，调用：

```bash
python3 /home/fei/.openclaw/workspace/nous-os/scripts/run_nous_heartbeat.py
```

## 推荐接法

在 Aria 的 heartbeat tool-call / exec 路径里加入：

```text
若 implementation_queue 或 learning_queue 有 pending 项，不要手工逐条 spawn。
优先执行：
python3 /home/fei/.openclaw/workspace/nous-os/scripts/run_nous_heartbeat.py

如果脚本返回 tasks_dispatched > 0：
- 说明任务已通过 Synapse Event Bus 派发
- 读取 examples/runtime/agent-bus/alerts.json 里的 summary
- 只向飞哥汇报关键完成项或异常
```

## 为什么这样接

- 保持 Aria 仍然是唯一协调者
- 但把底层执行从 JSON 轮询升级成 Synapse Event Bus
- TrustMem recall / episode logging 自动参与，不需要 Aria 额外手写逻辑
