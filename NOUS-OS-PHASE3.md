# NOUS OS Phase 3 — Flywheel 验证 + 对外发布

**状态更新时间：** 2026-05-16

**目标：** 让 Flywheel 完全可测量、可展示，并准备好 NOUS OS 作为独立项目对外发布。

**当前结论：** Phase 3 的本地/公开 demo 形态已经完成。NOUS OS repo 已独立存在，heartbeat bridge、dashboard、benchmark snapshot、CI 和 GitHub Pages 发布路径都已落地。剩余工作不再是“能否演示”，而是生产化接线和发布自动化。

---

## Phase 3 四个任务状态

### T1：Flywheel 端到端 Demo 脚本 ✅

已落地为：

- `examples/nousos_demo.py` — 仓库内自包含 demo
- `examples/nousos_workspace_demo.py` — 复用 workspace 下真实 Synapse / TrustMem 边界
- `examples/nousos_heartbeat_demo.py` — Aria heartbeat + agent-bus 风格的闭环 demo
- `scripts/run_nous_heartbeat.py` — 正式 heartbeat runner

覆盖完整 Flywheel 循环：
1. 飞哥发出意图 → Aria 解析
2. TrustMem search（有无历史记忆）
3. Synapse DAG 并行执行
4. Worker 完成 → episode log → promote
5. 飞哥 override 一个决策 → HumanOverrideHandler
6. 下次同类任务 → Budget Scheduler 自动应用 firsthand insight boost
7. 打印 before/after 对比（有记忆 vs 无记忆，有 override vs 无 override）

### T2：NOUS OS Memory ROI / Benchmark 报告 ✅

已落地为可公开解释的 benchmark frame：

- `docs/benchmark-spec.md`
- `examples/runtime/dashboard-data.json`
- `demo/heartbeat-dashboard.html`

当前指标：

- Q：第二轮质量提升
- C：Human correction 是否进入下一轮行为
- E：第二轮 memory reuse rate
- R：第二轮任务结构是否扩展/细化
- CLS：Cognitive Loop Score 汇总分

### T3：NOUS OS 独立 GitHub Repo 初始化 ✅

当前 repo 已包含：

- `README.md`
- `ARCHITECTURE.md`
- `NOUS-OS-SPEC.md`
- `CO-EXIST-FLYWHEEL.md`
- `docs/getting-started.md`
- `docs/heartbeat-demo.md`
- `docs/benchmark-spec.md`
- `examples/`
- `scripts/`
- `tests/`
- `.github/workflows/ci.yml`
- `.github/workflows/pages.yml`

### T4：发布 Checklist 自动化 🟡

已完成：

- Unit test CI：`python -m unittest discover -s tests -v`
- GitHub Pages staging：homepage、favicon、dashboard、dashboard snapshot
- Static site deployment after CI success

仍需补齐：

- TrustMem / Synapse release checklist script
- secret/path scan
- upstream README / CHANGELOG consistency check
- cross-repo test gate

---

## 当前运行入口

```bash
python3 examples/nousos_demo.py
python3 examples/nousos_workspace_demo.py
python3 scripts/run_nous_heartbeat.py
python3 scripts/run_nous_dashboard.py
```

Dashboard:

```text
http://127.0.0.1:8765/demo/heartbeat-dashboard.html
```

## 下一阶段：Production Hardening

1. 生产 Aria runtime 接线：把 demo heartbeat 的 runtime agent-bus 替换为真实 Aria queue / policy source。
2. 领域评分器：把 demo 的 synthetic quality score 替换为投资、研究、代码等领域 evaluator。
3. Cross-repo release gate：对 `trustmem`、`synapse`、`nous-os` 做统一测试、路径扫描、密钥扫描和 changelog 检查。
4. Dashboard 数据持久化：保留多次 run 的历史曲线，而不是只发布一个 snapshot。
5. Public release package：固定 README、one-pager、demo script、benchmark report 的对外叙事。

## 发布顺序建议

```
Week 1: NOUS OS repo + dashboard demo public
Week 2: TrustMem arXiv / technical post
Week 3: Show HN: TrustMem
Week 4: Show HN: Synapse
Week 5: 公众号：NOUS OS 完整叙事（面向飞哥读者）
```
