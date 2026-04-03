# ARCHITECTURE.md — 五 Agent 协作架构
# Last Updated: 2026-03-22

Aria 是唯一协调者。所有 agent 间的调度统一由 Aria 管理。

---

## Agent 角色一览

| Agent | 名字 | 触发方式 | 核心职责 |
|-------|------|---------|---------|
| **main** | Aria | 飞哥直接对话 | 协调 + 长期记忆 + 主分析 |
| **briefing** | Briefing | Cron 7AM 自动 | 信息枢纽，写4个共享文件 |
| **trader** | Trader | Cron 9:30AM/4:30PM | 三位顾问市场分析 |
| **research** | Research | Aria spawn | 深度研究，可自 spawn |
| **vibe** | VibeCoding | Aria spawn / /vibe | 代码/工具/原型实现 |

---

## 依赖关系图

```
飞哥
  │
  ▼
Aria（唯一协调者）
  ├── Heartbeat 检查 agent-bus/ →
  │   ├── alerts.json           → 立刻通知飞哥
  │   ├── implementation_queue  → spawn VibeCoding
  │   └── learning_queue        → spawn Research
  │
  ├── /vibe <任务>              → spawn VibeCoding
  └── 分析请求                  → spawn Research

Briefing（7AM 自动，只写文件）
  ├── → Telegram 晨报
  ├── → agent-bus/daily_briefing.json  → Trader 读取
  ├── → agent-bus/learning_queue.json  → Aria heartbeat → Research
  └── → agent-bus/alerts.json          → Aria heartbeat → 通知飞哥

Trader（9:30AM / 4:30PM 自动）
  ├── 读 daily_briefing.json（来自 Briefing）
  ├── 读 Trading Agent 持仓状态
  └── → Telegram 日报

Research（被 Aria spawn）
  ├── 执行深度研究（可自 spawn 子 Research）
  └── → knowledge/ 知识库 + 可写 implementation_queue

VibeCoding（被 Aria spawn）
  ├── 执行代码/工具/原型实现
  └── → 结果文件 + Telegram 通知飞哥
```

---

## Agent Bus（共享通信文件）

路径：`~/.openclaw/workspace/agent-bus/`

| 文件 | 写入方 | 读取方 | 说明 |
|------|--------|--------|------|
| `daily_briefing.json` | Briefing | Trader | 每日各板块情绪信号 |
| `learning_queue.json` | Briefing / Research / Aria | Aria heartbeat → Research | 待深度研究的话题 |
| `implementation_queue.json` | Research / Aria | Aria heartbeat → VibeCoding | 待实现的代码/工具任务 |
| `alerts.json` | Briefing / Trader / Research | Aria heartbeat → 飞哥 | 重大事件 alert |

---

## Cron 时间轴（加州时间 PST）

```
07:00  🌅 Briefing 统一晨报
       → Telegram + daily_briefing.json + learning_queue + alerts

09:00  📝 Aria 内部积分卡晨问

09:30  📊 Trader 日报 + 个股监控（ALAB/TSLA/FCX/COPX）
       → 读 daily_briefing.json + 三位顾问分析 → Telegram

16:30  📊 Trader 收盘复盘 → Telegram

17:00  💰 财报速报 → Telegram

21:00  🌙 Aria 内部积分卡夜问

每周日 20:00  AI基础设施周报 → Telegram
每周日 18:00  财报周报（下周预览）→ Telegram
每周一 09:00  Aria 每周对齐 + Decision Log 回顾
```

---

## /vibe 命令路由

```
Telegram / WhatsApp：/vibe <任务描述>
  ↓
Aria 接收 → spawn VibeCoding
  ↓
VibeCoding 执行 → 结果写文件
  ↓
写入 alerts.json → Aria heartbeat → 转发 Telegram
```

示例：
- `/vibe 做一个股票收益曲线可视化页面`
- `/vibe 写一个 Python 脚本解析 daily_briefing.json`

---

## 关键设计原则

1. **Aria 是唯一入口** — 飞哥只和 Aria 说话，Aria 决定派给谁
2. **文件是消息总线** — agent 间通过 agent-bus/ 文件通信，不直接调用
3. **Briefing 只写文件** — Briefing 不协调，不决策，只生产数据
4. **Trader 和 Python Agent 分离** — Trader AI 是"大脑"，Python Trading Agent 是"手"
5. **Research/VibeCoding 完全被动** — 没有 heartbeat，等待 Aria 调度
