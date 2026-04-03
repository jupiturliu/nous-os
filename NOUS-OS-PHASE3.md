# NOUS OS Phase 3 — Flywheel 验证 + 对外发布

**目标：** 让 Flywheel 完全可测量、可展示，并准备好 NOUS OS 作为独立项目对外发布。

---

## Phase 3 四个任务

### T1：Flywheel 端到端 Demo 脚本

`synapse/demo/nous_os_demo.py`

一个可运行的 demo，展示完整 Flywheel 循环：
1. 飞哥发出意图 → Aria 解析
2. TrustMem search（有无历史记忆）
3. Synapse DAG 并行执行
4. Worker 完成 → episode log → promote
5. 飞哥 override 一个决策 → HumanOverrideHandler
6. 下次同类任务 → Budget Scheduler 自动应用 firsthand insight boost
7. 打印 before/after 对比（有记忆 vs 无记忆，有 override vs 无 override）

### T2：NOUS OS Memory ROI 报告

`synapse/reports/nous_os_roi.py`

整合 TrustMem memory_roi.py + Synapse episode 统计，生成一份可读报告：
- 有记忆的任务 vs 无记忆的任务：成功率差异
- Human Override 频率 by domain
- Budget 节省（firsthand insight boost 触发次数 × 节省成本）
- Quality score 分布（Phase 1 前 vs Phase 2 后）

### T3：NOUS OS 独立 GitHub Repo 初始化

新建 `~/.openclaw/workspace/nous-os/`，包含：
- `README.md`（NOUS OS 整体介绍，三层架构，指向 TrustMem/Synapse）
- `ARCHITECTURE.md`（从 coexist-flywheel-architecture.md 提炼）
- `docs/getting-started.md`（如何把 TrustMem + Synapse 接起来）
- `examples/` （Phase 3 T1 的 demo 脚本）

### T4：发布 Checklist 自动化

`scripts/pre_publish_check.sh`

对 TrustMem 和 Synapse 执行发布前自动检查：
- [ ] 无 /home/fei/ 等个人路径
- [ ] 无 API keys / tokens
- [ ] README 包含 Quick Start
- [ ] README 包含 NOUS OS 章节
- [ ] 所有测试通过
- [ ] CHANGELOG 最新版本有记录

---

## 发布顺序（Phase 3 完成后）

```
Week 1: NOUS OS repo 上线 + TrustMem arXiv preprint
Week 2: Show HN: TrustMem
Week 3: Show HN: Synapse  
Week 4: 公众号：NOUS OS 完整叙事（面向飞哥读者）
```
