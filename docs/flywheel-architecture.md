---
title: "Co-exist Flywheel: TrustMem + Synapse + Aria 三位一体集成架构"
author: aria
created: 2026-04-02
updated: 2026-04-02
confidence: 0.85
verified_by: []
verification_status: unverified
data_freshness: 2026-04-02
decay_class: slow
sources_count: 3
domain: ai-infra
---

# Co-exist Flywheel：TrustMem × Synapse × Aria 集成架构

> 目标：让 AI 和人类不只是协作，而是共同进化。每一次交互都让系统更聪明，每一次飞哥的判断都让 AI 更准确。

---

## 一、三者的本质定位

```
TrustMem  = 海马体（What to remember, what to trust）
             ↑ 负责：知识存储、置信度、衰减、跨 Agent 验证

Synapse   = 神经系统（How signals travel, who executes）
             ↑ 负责：Event Bus、DAG 并行调度、Budget 路由、故障隔离

Aria     = 前额叶皮质（Why, intent, judgment, human alignment）
             ↑ 负责：意图理解、人类对齐、飞哥↔系统接口、摩擦力
```

**现在的问题：** 三者都在跑，但互不感知。像有大脑、神经系统、记忆但三者没有连线。

---

## 二、集成后的 Flywheel 逻辑

```
飞哥发出一个意图（投资判断、技术问题、写作任务）
         │
         ▼
┌─────────────────────────────────┐
│         Aria（前额叶）          │
│  1. 理解意图，识别任务类型        │
│  2. TrustMem search → 有无相关记忆│  ← Step 1（已写入 SOUL.md）
│  3. 生成 DAG（任务分解）         │
│  4. 发布到 Synapse Event Bus     │  ← 新接入点
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│        Synapse（神经系统）        │
│  Event Bus → 路由到对应 Worker   │
│  Budget Scheduler 选最优模型     │
│  DAG Executor 并行执行子任务     │
│  Blackboard 汇聚中间状态         │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│       TrustMem（海马体）         │
│  每个 Worker 完成后 → log episode│  ← Step 2（已写入所有 SOUL.md）
│  quality ≥ 0.8 → promote        │  ← Step 3
│  知识衰减 → 自动刷新队列         │
│  飞哥 override → 写入 episodic   │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│      Aria 收到结果 + 记忆更新   │
│  向飞哥呈现（带置信度、来源）    │
│  飞哥反馈 → 写入 firsthand insight│
│  系统变得更懂飞哥                │
└─────────────────────────────────┘
         │
         └──────────────────────── 下次任务更快、更准 ↑
```

这就是 Flywheel：**每次交互都让系统更懂飞哥，每次飞哥的判断都让 AI 更准确。**

---

## 三、具体集成方案（三个阶段）

### Phase 1：最小可行集成（1-2周，改动最小）

**目标：** 让 Aria 的 agent-bus 走 Synapse Event Bus，替代文件轮询。

**当前问题：**
```
现在：Aria → 写 agent-bus/implementation_queue.json → VibeCoding polling 文件
问题：串行、polling 延迟、无优先级、无故障隔离
```

**Phase 1 方案：**
```python
# 在 Aria 的 HEARTBEAT 派发逻辑里，替换文件写入：

# 之前（文件轮询）：
with open('agent-bus/implementation_queue.json', 'w') as f:
    json.dump(queue, f)

# 之后（Synapse Event Bus）：
from synapse.event_bus import get_event_bus
bus = get_event_bus()
bus.publish('implementation_queue', {
    'task': task,
    'priority': 'high',
    'trustmem_context': trustmem_search_result,  # ← TrustMem 上下文随任务携带
    'timestamp': time.time()
})
```

**涉及的文件改动：**
- `~/.openclaw/workspace/synapse/orchestration/aria_orchestrator.py` — 已有框架，扩展即可
- `agent-bus/` 目录 — 逐步迁移到 Blackboard
- Heartbeat 派发逻辑 — 换成 bus.publish

**Phase 1 产出：**
- ✅ 零 polling 延迟（event-driven）
- ✅ Synapse Budget Scheduler 自动选模型（便宜任务用 MiniMax，重要任务用 Sonnet）
- ✅ TrustMem 上下文随任务传递（Worker 拿到任务时已有相关记忆）

---

### Phase 2：TrustMem 嵌入 Synapse Worker（2-4周）

**目标：** 每个 Worker 执行前自动 search，执行后自动 log。

```python
# 在 Synapse 的 AgentWorker 基类里加 TrustMem hooks：

class AgentWorker:
    def execute_task(self, task: Dict) -> Dict:
        # === TrustMem Hook: Before ===
        memory_context = trustmem_search(task['description'])
        task['memory_context'] = memory_context

        # 执行实际工作
        result = self._do_work(task)

        # === TrustMem Hook: After ===
        episode_logger.log(
            agent=self.agent_name,
            task=task['description'],
            outcome='success' if result['success'] else 'failure',
            quality=result.get('quality', 0.7),
            notes=result.get('summary', '')
        )

        if result.get('quality', 0) >= 0.8:
            trustmem_promote(result)

        return result
```

**Phase 2 产出：**
- ✅ 所有 Worker 自动享有 TrustMem 闭环（不需要每个 SOUL.md 手动提醒）
- ✅ 知识在 Synapse Worker 层面自动积累
- ✅ Agency agents 通过 agency_worker.py 自动继承（已有 agency_worker.py 文件）

---

### Phase 3：Flywheel 完全闭合（1-2个月）

**目标：** 飞哥的一手判断直接进入 Synapse 调度决策。

**核心机制：Human Override → System Learning**

```
飞哥否决一个 ARIA 推荐
    ↓
Aria 追问："否决原因？宏观变了 / 阈值太敏感 / 其他？"
    ↓
飞哥回答（30秒，一句话）
    ↓
写入 TrustMem firsthand-insights（confidence: 1.0，飞哥一手洞察最高权重）
    ↓
Synapse Budget Scheduler 读取 → 调整 task_routing 权重
    ↓
下次同类任务：Synapse 自动用更高权重执行飞哥偏好的判断路径
```

**同样的机制用于：**
- 飞哥说"这个研究结论有问题" → TrustMem disputed → Synapse 不再引用该知识
- 飞哥说"这个 Agent 太慢了" → episode quality 自动降权 → Synapse 减少调用
- 飞哥说"这个分析很准" → quality 升权 → Synapse 更多调用同类 Worker

---

## 四、Flywheel 的本质：双向学习

```
飞哥变得更厉害：
  系统在"成长区"深度辅助 → 飞哥习得判断力 → 移入"强认知区"
  → Aria 自动减少在该领域的介入（COGNITIVE-MAP.md 更新）

系统变得更聪明：
  飞哥的判断 → TrustMem firsthand insights → Synapse 调度优化
  → 下次类似任务：更快、更准、更便宜
  → 飞哥有更多时间做真正有价值的事

两者互相塑造 → Co-exist 不只是工具关系，是共同进化
```

---

## 五、立即可执行的 Phase 1 任务单

优先级排序：

| 优先级 | 任务 | 负责 | 预计时间 |
|--------|------|------|---------|
| P0 | aria_orchestrator.py 扩展：接收 Heartbeat 任务，发布到 Event Bus | VibeCoding | 2h |
| P0 | TrustMem search 结果注入 Event Bus payload | VibeCoding | 1h |
| P1 | AgentWorker 基类加 TrustMem before/after hooks | VibeCoding | 3h |
| P1 | agent-bus/implementation_queue.json → Blackboard 迁移 | VibeCoding | 2h |
| P2 | Budget Scheduler 读取 TrustMem firsthand insights 权重 | VibeCoding | 4h |
| P2 | Human Override → TrustMem → Synapse 反馈链路 | VibeCoding | 4h |

**总计 Phase 1 工程量：约 1-2 天 VibeCoding 时间。**

---

## 六、成功指标（3个月后验证）

| 指标 | 当前 | 目标 |
|------|------|------|
| 重复研究率 | 高（无记忆） | < 10%（TrustMem search first）|
| 任务并发度 | 1（串行） | 3-5（Synapse DAG 并行）|
| 模型成本/任务 | 全 Sonnet | 30-50% 降低（Budget Scheduler）|
| 飞哥否决后系统调整速度 | 从不调整 | 下次同类任务即生效 |
| COGNITIVE-MAP 更新频率 | 手动、偶尔 | 每月系统建议 |

---

*这是 Co-exist 的技术实现路径。三者集成后，系统不再是工具集合，而是一个有记忆、有神经、有意识的共生体。*
