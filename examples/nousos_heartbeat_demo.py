#!/usr/bin/env python3
"""Aria heartbeat demo wired to runtime agent-bus + Synapse + TrustMem."""

from __future__ import annotations

import json
import sys
import threading
import time
from pathlib import Path
from queue import Empty, Queue
from typing import Dict, List


ROOT = Path(__file__).resolve().parent
NOUS_OS_ROOT = ROOT.parent
WORKSPACE = NOUS_OS_ROOT.parent
EXTRA_PYTHON_PATHS = [
    str(WORKSPACE / "venv" / "lib" / "python3.11" / "site-packages"),
    "/usr/lib/python3/dist-packages",
    str(WORKSPACE / "synapse"),
    str(WORKSPACE / "synapse" / "core"),
    str(WORKSPACE / "synapse" / "orchestration"),
]
for extra_path in EXTRA_PYTHON_PATHS:
    if Path(extra_path).exists() and extra_path not in sys.path:
        sys.path.insert(0, extra_path)

try:
    from singleton import reset_singletons
    from worker import AgentWorker
    import worker as synapse_worker_module
    import aria_orchestrator as aria_orch_module
    from aria_orchestrator import AriaOrchestrator
    EXTERNAL_RUNTIME_AVAILABLE = True
except ModuleNotFoundError:
    reset_singletons = None
    AgentWorker = object
    synapse_worker_module = None
    aria_orch_module = None
    AriaOrchestrator = None
    EXTERNAL_RUNTIME_AVAILABLE = False


RUNTIME_DIR = ROOT / "runtime"
RUNTIME_AGENT_BUS = RUNTIME_DIR / "agent-bus"
RUNTIME_EPISODE_LOGGER = RUNTIME_DIR / "episode_logger_local.py"
RUNTIME_ALERTS = RUNTIME_DIR / "alerts.json"
RUNTIME_INSIGHTS = RUNTIME_DIR / "insights.json"
RUNTIME_EPISODES = RUNTIME_DIR / "data" / "episodes" / "episodes.jsonl"
RUNTIME_DASHBOARD = RUNTIME_DIR / "dashboard-data.json"

DEFAULT_GOAL = "Build a demo for multi-agent memory and human override evolution in NOUS OS"
DEFAULT_OVERRIDE_KIND = "risk"
OVERRIDE_PRESETS = {
    "risk": {
        "reason": "Human override: add an explicit risk gate before execution.",
        "implementation_suffix": "Apply risk guardrails before shipping",
        "quality_bonus": 0.04,
        "role": "risk_guard",
    },
    "cost": {
        "reason": "Human override: execution is too expensive, reduce scope and budget burn.",
        "implementation_suffix": "Trim cost and scope before shipping",
        "quality_bonus": 0.02,
        "role": "cost_guard",
    },
    "timing": {
        "reason": "Human override: timing is off, add a sequencing checkpoint before launch.",
        "implementation_suffix": "Re-sequence the launch plan before shipping",
        "quality_bonus": 0.03,
        "role": "timing_guard",
    },
}


def now_local() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def write_json(path: Path, payload: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))


def read_json(path: Path) -> Dict:
    if not path.exists():
        return {"items": []}
    return json.loads(path.read_text())


def count_episode_lines() -> int:
    if not RUNTIME_EPISODES.exists():
        return 0
    return sum(1 for line in RUNTIME_EPISODES.read_text().splitlines() if line.strip())


def reset_runtime_files() -> None:
    write_json(RUNTIME_AGENT_BUS / "implementation_queue.json", {"items": []})
    write_json(RUNTIME_AGENT_BUS / "learning_queue.json", {"items": []})
    write_json(RUNTIME_AGENT_BUS / "alerts.json", {"items": []})
    write_json(RUNTIME_ALERTS, {"items": []})
    write_json(RUNTIME_INSIGHTS, {"insights": []})
    RUNTIME_EPISODES.parent.mkdir(parents=True, exist_ok=True)
    if RUNTIME_EPISODES.exists():
        RUNTIME_EPISODES.unlink()


def seed_runtime_queues(goal: str, round_index: int, override_kind: str = DEFAULT_OVERRIDE_KIND) -> None:
    override_preset = OVERRIDE_PRESETS.get(override_kind, OVERRIDE_PRESETS[DEFAULT_OVERRIDE_KIND])
    impl_reason = (
        f"Aria wants a visible prototype for: {goal}"
        if round_index == 1
        else f"Aria wants a refined execution path with memory for: {goal}"
    )
    learning_reason = (
        f"Aria needs a research narrative for: {goal}"
        if round_index == 1
        else f"Aria wants the next run to reuse prior learning for: {goal}"
    )
    implementation_items = [
        {
            "id": f"impl-demo-{round_index:03d}",
            "task": f"Prototype the execution surface for: {goal}",
            "reason": impl_reason,
            "type": "implementation_queue",
            "priority": "high",
            "status": "pending",
            "created_at": now_local(),
            "round": round_index,
            "goal": goal,
        }
    ]
    learning_items = [
        {
            "id": f"learn-demo-{round_index:03d}",
            "topic": f"Research the flywheel story for: {goal}",
            "reason": learning_reason,
            "type": "learning_queue",
            "priority": "high",
            "status": "pending",
            "created_at": now_local(),
            "round": round_index,
            "goal": goal,
        }
    ]
    if round_index >= 2:
        implementation_items.append(
            {
                "id": f"risk-demo-{round_index:03d}",
                "task": f"{override_preset['implementation_suffix']}: {goal}",
                "reason": f"TrustMem already contains the previous round and a human correction about {override_kind}.",
                "type": "implementation_queue",
                "priority": "high",
                "status": "pending",
                "created_at": now_local(),
                "round": round_index,
                "goal": goal,
                "role": override_preset["role"],
                "override_kind": override_kind,
            }
        )

    write_json(RUNTIME_AGENT_BUS / "implementation_queue.json", {"items": implementation_items})
    write_json(RUNTIME_AGENT_BUS / "learning_queue.json", {"items": learning_items})


class QueueWorker(AgentWorker):
    def __init__(self, agent_id: str, topic: str, result_prefix: str, base_quality: float):
        super().__init__(agent_id=agent_id, topics=[topic], backend="memory")
        self.result_prefix = result_prefix
        self.base_quality = base_quality

    def execute(self, context: Dict, payload: Dict, topic: str) -> Dict:
        task_text = payload.get("task") or payload.get("topic") or topic
        memory_context = payload.get("memory_context") or []
        round_index = int(payload.get("round", 1))
        memory_hits = len(memory_context) if isinstance(memory_context, list) else int(bool(memory_context))
        quality_boost = 0.16 if memory_hits else 0.0
        round_boost = 0.02 if round_index >= 2 else 0.0
        role_boost = OVERRIDE_PRESETS.get(payload.get("override_kind"), {}).get("quality_bonus", 0.0)
        if payload.get("role") == "risk_guard" and role_boost == 0.0:
            role_boost = 0.04
        time.sleep(0.15)
        quality = min(self.base_quality + quality_boost + round_boost + role_boost, 0.95)
        return {
            "output": {
                "agent": self.agent_id,
                "topic": topic,
                "task": task_text,
                "quality_score": round(quality, 2),
                "summary": f"{self.result_prefix}: {task_text[:120]}",
                "memory_hits": memory_hits,
                "round": round_index,
                "goal": payload.get("goal"),
            },
            "state_update": {
                "last_task": task_text,
                "last_quality": round(quality, 2),
                "last_round": round_index,
            },
        }


def start_workers() -> None:
    ensure_runtime_available()
    workers = [
        QueueWorker("vibe-vpe", "implementation_queue", "Built implementation draft", 0.72),
        QueueWorker("research-cto", "learning_queue", "Produced research brief", 0.76),
    ]
    for worker in workers:
        thread = threading.Thread(target=worker.run, daemon=True)
        thread.start()
    time.sleep(0.25)


def update_queue_status(queue_name: str, item_id: str, output: Dict) -> None:
    queue_path = RUNTIME_AGENT_BUS / f"{queue_name}.json"
    data = read_json(queue_path)
    for item in data.get("items", []):
        if item.get("id") != item_id:
            continue
        item["status"] = "done"
        item["completed_at"] = now_local()
        item["result_path"] = f"runtime://{queue_name}/{item_id}"
        item["summary"] = output.get("summary")
        item["quality_score"] = output.get("quality_score")
        item["memory_hits"] = output.get("memory_hits", 0)
        break
    write_json(queue_path, data)


def append_alert(source: str, message: str, metadata: Dict) -> None:
    path = RUNTIME_AGENT_BUS / "alerts.json"
    alerts = read_json(path)
    alerts.setdefault("items", []).insert(
        0,
        {
            "id": f"{source}-{int(time.time() * 1000)}",
            "level": "medium",
            "type": "task_complete",
            "message": message,
            "source": source,
            "acknowledged": False,
            "action_required": False,
            "created_at": now_local(),
            "metadata": metadata,
        },
    )
    write_json(path, alerts)
    write_json(RUNTIME_ALERTS, alerts)


def record_override(goal: str, round1_avg_quality: float, override_kind: str = DEFAULT_OVERRIDE_KIND) -> Dict:
    override_preset = OVERRIDE_PRESETS.get(override_kind, OVERRIDE_PRESETS[DEFAULT_OVERRIDE_KIND])
    insights = read_json(RUNTIME_INSIGHTS)
    insight = {
        "id": f"override-{int(time.time() * 1000)}",
        "goal": goal,
        "reason": override_preset["reason"],
        "domain": "demo",
        "created_at": now_local(),
        "round_1_quality": round1_avg_quality,
        "kind": override_kind,
    }
    insights.setdefault("insights", []).append(insight)
    write_json(RUNTIME_INSIGHTS, insights)
    append_alert(
        "aria",
        f"Human override recorded for: {goal}",
        {"reason": insight["reason"], "round_1_quality": round1_avg_quality},
    )
    return insight


def handle_completion_events(orch: AriaOrchestrator, expected: int) -> List[Dict]:
    queue: Queue = Queue()
    orch.event_bus.subscribe_with_callback("task_completed", lambda event: queue.put(event))
    completed = []
    deadline = time.time() + 10
    while len(completed) < expected and time.time() < deadline:
        try:
            event = queue.get(timeout=0.5)
        except Empty:
            continue
        payload = event.get("payload", {})
        output = payload.get("output") or {}
        topic = payload.get("topic")
        job_id = payload.get("job_id")
        if not topic or not job_id:
            continue
        update_queue_status(topic, job_id, output)
        append_alert(
            output.get("agent", "worker"),
            f"{output.get('agent')} completed {topic}: {output.get('summary')}",
            {
                "job_id": job_id,
                "quality_score": output.get("quality_score"),
                "round": output.get("round"),
            },
        )
        completed.append({"job_id": job_id, "topic": topic, "output": output})
    return completed


def summarize_round(round_index: int, dispatch_results: Dict, completed: List[Dict]) -> Dict:
    avg_quality = 0.0
    if completed:
        avg_quality = round(
            sum(item["output"].get("quality_score", 0.0) for item in completed) / len(completed),
            2,
        )
    return {
        "round": round_index,
        "dispatch_results": dispatch_results,
        "completed": completed,
        "metrics": {
            "tasks_dispatched": sum(len(ids) for ids in dispatch_results.values()),
            "tasks_completed": len(completed),
            "avg_quality": avg_quality,
            "memory_hit_rate": round(
                sum(1 for item in completed if item["output"].get("memory_hits", 0) > 0) / len(completed),
                2,
            ) if completed else 0.0,
        },
        "queues": {
            "implementation_queue": read_json(RUNTIME_AGENT_BUS / "implementation_queue.json"),
            "learning_queue": read_json(RUNTIME_AGENT_BUS / "learning_queue.json"),
        },
    }


def build_benchmark(round1: Dict, round2: Dict, alerts_count: int, episodes_logged: int, override: Dict) -> Dict:
    q1 = round1["metrics"]["avg_quality"]
    q2 = round2["metrics"]["avg_quality"]
    quality_improvement = round((q2 - q1) / q1, 3) if q1 else 0.0

    t1 = round1["metrics"]["tasks_dispatched"]
    t2 = round2["metrics"]["tasks_dispatched"]
    task_expansion = round((t2 - t1) / t1, 3) if t1 else 0.0

    memory_reuse = round2["metrics"].get("memory_hit_rate", 0.0)
    correction_applied = 1.0 if override else 0.0

    q_component = max(0.0, quality_improvement)
    c_component = correction_applied
    e_component = max(0.0, memory_reuse)
    r_component = max(0.0, task_expansion)
    cls = round(0.4 * q_component + 0.2 * c_component + 0.2 * e_component + 0.2 * r_component, 3)

    return {
        "baseline": {
            "quality": q1,
            "tasks": t1,
            "memory_hit_rate": round1["metrics"].get("memory_hit_rate", 0.0),
        },
        "treatment": {
            "quality": q2,
            "tasks": t2,
            "memory_hit_rate": round2["metrics"].get("memory_hit_rate", 0.0),
        },
        "derived": {
            "quality_improvement_rate": quality_improvement,
            "task_expansion_rate": task_expansion,
            "memory_reuse_rate": memory_reuse,
            "correction_applied_rate": correction_applied,
            "episodes_logged": episodes_logged,
            "alerts_created": alerts_count,
        },
        "cls": {
            "score": cls,
            "components": {
                "q_quality_improvement": round(q_component, 3),
                "c_correction_absorption": round(c_component, 3),
                "e_memory_reuse": round(e_component, 3),
                "r_repeatability_gain": round(r_component, 3),
            },
        },
        "public_standard": [
            {
                "id": "Q",
                "label": "Quality Improvement",
                "detail": "Does the second run improve task quality against the baseline first run?",
                "value": round(quality_improvement, 3),
            },
            {
                "id": "C",
                "label": "Correction Absorption",
                "detail": "Does one human correction enter the system and alter later behavior?",
                "value": round(correction_applied, 3),
            },
            {
                "id": "E",
                "label": "Memory Reuse",
                "detail": "What fraction of second-run tasks actually reuse memory?",
                "value": round(memory_reuse, 3),
            },
            {
                "id": "R",
                "label": "Repeatability Gain",
                "detail": "Does the loop expand or refine the second-run plan in a measurable way?",
                "value": round(task_expansion, 3),
            },
        ],
    }


def build_timeline(goal: str, runs: List[Dict], override: Dict) -> List[Dict]:
    round1 = runs[0]
    round2 = runs[1]
    return [
        {
            "stage": "Human Intent",
            "title": "You set a goal",
            "detail": goal,
            "accent": "intent",
        },
        {
            "stage": "Aria Planning",
            "title": "Aria decomposes the work",
            "detail": f"Round 1 dispatched {round1['metrics']['tasks_dispatched']} tasks across implementation and research lanes.",
            "accent": "aria",
        },
        {
            "stage": "Synapse Execution",
            "title": "Workers complete the first pass",
            "detail": f"Cold-start quality landed at {round1['metrics']['avg_quality']:.2f}.",
            "accent": "synapse",
        },
        {
            "stage": "Human Override",
            "title": "The human tightens the policy",
            "detail": override["reason"],
            "accent": "override",
        },
        {
            "stage": "TrustMem Recall",
            "title": "Memory changes the second run",
            "detail": f"Round 2 recalled episode memory and expanded to {round2['metrics']['tasks_dispatched']} tasks.",
            "accent": "trustmem",
        },
        {
            "stage": "Compounding Loop",
            "title": "The system gets sharper",
            "detail": f"Average quality improved from {round1['metrics']['avg_quality']:.2f} to {round2['metrics']['avg_quality']:.2f}.",
            "accent": "compound",
        },
    ]


def build_topology(goal: str, runs: List[Dict], override: Dict) -> Dict:
    round1 = runs[0]
    round2 = runs[1]
    return {
        "nodes": [
            {"id": "human", "label": "Human", "kind": "human", "meta": goal},
            {"id": "aria", "label": "Aria", "kind": "aria", "meta": "intent router"},
            {"id": "synapse", "label": "Synapse", "kind": "synapse", "meta": f"{round2['metrics']['tasks_dispatched']} tasks"},
            {"id": "research", "label": "Research", "kind": "agent", "meta": "research lane"},
            {"id": "vibe", "label": "Vibe", "kind": "agent", "meta": "implementation lane"},
            {"id": "override", "label": "Override", "kind": "override", "meta": override["kind"]},
            {"id": "trustmem", "label": "TrustMem", "kind": "trustmem", "meta": f"{round2['metrics']['avg_quality']:.2f} round2"},
            {"id": "alerts", "label": "Alerts", "kind": "alerts", "meta": "return to Aria"},
        ],
        "edges": [
            {"from": "human", "to": "aria", "label": "goal"},
            {"from": "aria", "to": "synapse", "label": "plan"},
            {"from": "synapse", "to": "research", "label": f"r1 {round1['metrics']['tasks_dispatched']}"},
            {"from": "synapse", "to": "vibe", "label": f"r2 {round2['metrics']['tasks_dispatched']}"},
            {"from": "human", "to": "override", "label": "feedback"},
            {"from": "override", "to": "trustmem", "label": "policy"},
            {"from": "research", "to": "trustmem", "label": "episodes"},
            {"from": "vibe", "to": "trustmem", "label": "episodes"},
            {"from": "trustmem", "to": "synapse", "label": "recall"},
            {"from": "synapse", "to": "alerts", "label": "completion"},
            {"from": "alerts", "to": "aria", "label": "summary"},
        ],
    }


def build_dashboard_snapshot(goal: str, runs: List[Dict], override: Dict) -> Dict:
    round1 = runs[0]
    round2 = runs[1]
    alerts = read_json(RUNTIME_AGENT_BUS / "alerts.json")
    episodes_logged = count_episode_lines()
    alerts_count = len(alerts.get("items", []))
    quality_delta = round(round2["metrics"]["avg_quality"] - round1["metrics"]["avg_quality"], 2)
    benchmark = build_benchmark(round1, round2, alerts_count, episodes_logged, override)
    return {
        "generated_at": now_local(),
        "goal": goal,
        "current_round": 2,
        "runs": runs,
        "timeline": build_timeline(goal, runs, override),
        "topology": build_topology(goal, runs, override),
        "override": override,
        "benchmark": benchmark,
        "metrics": {
            "tasks_dispatched": round2["metrics"]["tasks_dispatched"],
            "tasks_completed": round2["metrics"]["tasks_completed"],
            "avg_quality": round2["metrics"]["avg_quality"],
            "episodes_logged": episodes_logged,
            "alerts_created": alerts_count,
            "quality_delta": quality_delta,
            "cls_score": benchmark["cls"]["score"],
        },
        "queues": {
            "implementation_queue": read_json(RUNTIME_AGENT_BUS / "implementation_queue.json"),
            "learning_queue": read_json(RUNTIME_AGENT_BUS / "learning_queue.json"),
            "alerts": alerts,
        },
        "completed": round2["completed"],
        "paths": {
            "implementation_queue": str(RUNTIME_AGENT_BUS / "implementation_queue.json"),
            "learning_queue": str(RUNTIME_AGENT_BUS / "learning_queue.json"),
            "alerts": str(RUNTIME_AGENT_BUS / "alerts.json"),
            "dashboard_data": str(RUNTIME_DASHBOARD),
        },
    }


def run_round(orch: AriaOrchestrator, goal: str, round_index: int, override_kind: str) -> Dict:
    seed_runtime_queues(goal, round_index, override_kind=override_kind)
    results = orch.publish_from_agent_bus()
    expected = sum(len(ids) for ids in results.values())
    completed = handle_completion_events(orch, expected)
    return summarize_round(round_index, results, completed)


def run_heartbeat_flow(goal: str = DEFAULT_GOAL, override_kind: str = DEFAULT_OVERRIDE_KIND) -> Dict:
    ensure_runtime_available()
    goal = (goal or DEFAULT_GOAL).strip() or DEFAULT_GOAL
    override_kind = override_kind if override_kind in OVERRIDE_PRESETS else DEFAULT_OVERRIDE_KIND
    reset_singletons()
    reset_runtime_files()

    synapse_worker_module._EPISODE_LOGGER_PATH = RUNTIME_EPISODE_LOGGER
    aria_orch_module._EPISODE_LOGGER_PATH = RUNTIME_EPISODE_LOGGER
    aria_orch_module._AGENT_BUS_DIR = RUNTIME_AGENT_BUS

    start_workers()
    orch = AriaOrchestrator()
    round1 = run_round(orch, goal, 1, override_kind)
    override = record_override(goal, round1["metrics"]["avg_quality"], override_kind=override_kind)
    round2 = run_round(orch, goal, 2, override_kind)
    snapshot = build_dashboard_snapshot(goal, [round1, round2], override)
    write_json(RUNTIME_DASHBOARD, snapshot)
    return snapshot


def ensure_runtime_available() -> None:
    if EXTERNAL_RUNTIME_AVAILABLE:
        return
    raise RuntimeError(
        "NOUS OS heartbeat runtime dependencies are unavailable. "
        "This demo requires the sibling workspace Synapse/Aria runtime."
    )


def main() -> None:
    snapshot = run_heartbeat_flow()
    print("=== Goal ===")
    print(snapshot["goal"])
    print("\n=== Timeline ===")
    for item in snapshot["timeline"]:
        print(f"- {item['stage']}: {item['detail']}")
    print("\n=== Round 2 Completed Tasks ===")
    for item in snapshot["completed"]:
        output = item["output"]
        print(
            f"- {item['topic']} / {item['job_id']}: "
            f"agent={output.get('agent')} quality={output.get('quality_score'):.2f} "
            f"memory={output.get('memory_hits')} | {output.get('summary')}"
        )
    print("\n=== Runtime Outputs ===")
    print(f"- dashboard_data: {RUNTIME_DASHBOARD}")


if __name__ == "__main__":
    main()
