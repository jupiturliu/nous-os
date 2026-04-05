#!/usr/bin/env python3
"""NOUS OS demo wired to the real Aria/Synapse/TrustMem code in workspace."""

from __future__ import annotations

import importlib.util
import json
import sys
import threading
import time
from pathlib import Path
from queue import Queue, Empty
from typing import Dict, List


ROOT = Path(__file__).resolve().parent
NOUS_OS_ROOT = ROOT.parent
WORKSPACE = NOUS_OS_ROOT.parent
WORKSPACE_VENV_SITE = WORKSPACE / "venv" / "lib" / "python3.11" / "site-packages"
EXTRA_PYTHON_PATHS = [
    str(WORKSPACE_VENV_SITE),
    "/usr/lib/python3/dist-packages",
]
for extra_path in EXTRA_PYTHON_PATHS:
    if Path(extra_path).exists() and extra_path not in sys.path:
        sys.path.insert(0, extra_path)

ARIA_DIR = WORKSPACE / "aria"
SYNAPSE_DIR = WORKSPACE / "synapse"
SYNAPSE_CORE_DIR = SYNAPSE_DIR / "core"
SYNAPSE_ORCH_DIR = SYNAPSE_DIR / "orchestration"
TRUSTMEM_DIR = WORKSPACE / "trustmem"
TRUSTMEM_TOOLS_DIR = TRUSTMEM_DIR / "tools"
RUNTIME_DIR = ROOT / "runtime"
RUNTIME_DATA_DIR = RUNTIME_DIR / "data"
EPISODE_LOGGER_SCRIPT = RUNTIME_DIR / "episode_logger_local.py"
INSIGHTS_PATH = RUNTIME_DIR / "insights.json"
ALERTS_PATH = RUNTIME_DIR / "alerts.json"

for path in (str(SYNAPSE_DIR), str(SYNAPSE_CORE_DIR), str(SYNAPSE_ORCH_DIR), str(TRUSTMEM_TOOLS_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)

from singleton import reset_singletons
from worker import AgentWorker
import worker as synapse_worker_module
import aria_synapse_bridge as bridge_module
import human_override as override_module
from aria_synapse_bridge import AriaSynapseBridge
from human_override import HumanOverrideHandler


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


episode_logger = load_module("workspace_episode_logger", WORKSPACE / "tools" / "episode_logger.py")
episode_logger.EPISODES_DIR = RUNTIME_DATA_DIR / "episodes"
episode_logger.EPISODES_FILE = episode_logger.EPISODES_DIR / "episodes.jsonl"

trustmem_search = load_module("trustmem_knowledge_search", TRUSTMEM_TOOLS_DIR / "knowledge_search.py")

synapse_worker_module._EPISODE_LOGGER_PATH = EPISODE_LOGGER_SCRIPT
bridge_module._EPISODE_LOGGER_PATH = EPISODE_LOGGER_SCRIPT
override_module._INSIGHTS_PATH = INSIGHTS_PATH
override_module._ALERTS_PATH = ALERTS_PATH
override_module._EPISODE_LOGGER = EPISODE_LOGGER_SCRIPT


def ensure_runtime_state() -> None:
    (RUNTIME_DATA_DIR / "episodes").mkdir(parents=True, exist_ok=True)
    INSIGHTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if episode_logger.EPISODES_FILE.exists():
        episode_logger.EPISODES_FILE.unlink()
    INSIGHTS_PATH.write_text(json.dumps({"schema": {}, "insights": []}, ensure_ascii=False, indent=2))
    ALERTS_PATH.write_text(json.dumps({"items": []}, ensure_ascii=False, indent=2))


class DemoWorker(AgentWorker):
    def __init__(self, agent_id: str, topic: str, base_quality: float, summary: str):
        super().__init__(agent_id=agent_id, topics=[topic], backend="memory")
        self.base_quality = base_quality
        self.summary = summary

    def execute(self, context: Dict, payload: Dict, topic: str) -> Dict:
        memory_context = payload.get("memory_context") or []
        memory_boost = 0.16 if memory_context else 0.0
        knowledge_hits = payload.get("knowledge_hits") or []
        knowledge_bonus = 0.04 if knowledge_hits else 0.0
        # Give the batch enough time to fan out before any worker logs a new episode.
        time.sleep(0.15)
        quality = min(self.base_quality + memory_boost + knowledge_bonus, 0.95)
        result = {
            "agent": self.agent_id,
            "topic": topic,
            "summary": self.summary,
            "memory_hits": len(memory_context) if isinstance(memory_context, list) else 1,
            "knowledge_hits": len(knowledge_hits),
            "quality_score": round(quality, 2),
            "result": f"{self.agent_id} processed {payload.get('task', payload.get('intent', topic))}",
        }
        return {
            "output": result,
            "state_update": {
                "last_quality": result["quality_score"],
                "last_memory_hits": result["memory_hits"],
            },
        }


class AriaPlanner:
    def plan(self, goal: str, memory_hits: List, override_stats: Dict) -> List[Dict]:
        tasks = [
            {"id": "research-1", "type": "research", "task": f"Research the goal: {goal}"},
            {"id": "builder-1", "type": "builder", "task": f"Build an execution path for: {goal}"},
            {"id": "critic-1", "type": "critic", "task": f"Stress-test assumptions for: {goal}"},
        ]
        if memory_hits or override_stats.get("total", 0) > 0:
            tasks.append({"id": "risk-1", "type": "risk", "task": f"Apply override-derived risk checks to: {goal}"})
        return tasks


def start_workers() -> List[threading.Thread]:
    workers = [
        DemoWorker("research", "research", 0.67, "Mapped prior cases and missing evidence."),
        DemoWorker("builder", "builder", 0.65, "Proposed a short execution path."),
        DemoWorker("critic", "critic", 0.72, "Flagged weak assumptions and failure modes."),
        DemoWorker("risk", "risk", 0.78, "Applied remembered human override as a risk gate."),
    ]
    threads = []
    for worker in workers:
        thread = threading.Thread(target=worker.run, daemon=True)
        thread.start()
        threads.append(thread)
    time.sleep(0.3)
    return threads


def knowledge_lookup(goal: str) -> List[Dict]:
    try:
        return trustmem_search.search(goal, top_k=2, caller="nousos-demo")
    except Exception:
        return []


def wait_for_results(bridge: AriaSynapseBridge, expected: int) -> List[Dict]:
    queue: Queue = Queue()
    bridge.event_bus.subscribe_with_callback("task_completed", lambda event: queue.put(event))
    results = []
    deadline = time.time() + 10
    while len(results) < expected and time.time() < deadline:
        try:
            event = queue.get(timeout=0.5)
            payload = event.get("payload", {})
            if payload.get("output"):
                results.append(payload["output"])
        except Empty:
            continue
    return results


def dispatch_round(bridge: AriaSynapseBridge, planner: AriaPlanner, goal: str, label: str) -> List[Dict]:
    recall_hits = episode_logger.recall_similar(goal, top_k=3)
    override_stats = HumanOverrideHandler().get_override_stats()
    tasks = planner.plan(goal, recall_hits, override_stats)
    queue: Queue = Queue()
    bridge.event_bus.subscribe_with_callback("task_completed", lambda event: queue.put(event))

    knowledge_hits = knowledge_lookup(goal)
    for task in tasks:
        bridge.publish_with_memory({**task, "knowledge_hits": knowledge_hits, "intent": goal})

    results = []
    deadline = time.time() + 10
    while len(results) < len(tasks) and time.time() < deadline:
        try:
            event = queue.get(timeout=0.5)
        except Empty:
            continue
        payload = event.get("payload", {})
        output = payload.get("output")
        if output:
            results.append(output)

    print(f"\n=== {label} ===")
    print(f"Aria plan: {len(tasks)} tasks")
    print(f"TrustMem episode hits: {len(recall_hits)}")
    print(f"TrustMem knowledge hits: {len(knowledge_hits)}")
    for item in results:
        print(
            f"- {item['agent']}: quality={item['quality_score']:.2f} "
            f"memory={item['memory_hits']} knowledge={item['knowledge_hits']} | {item['summary']}"
        )
    return results


def avg_quality(results: List[Dict]) -> float:
    return round(sum(item["quality_score"] for item in results) / len(results), 2)


def print_runtime_files() -> None:
    print("\nRuntime state:")
    print(f"- episodes: {episode_logger.EPISODES_FILE}")
    print(f"- insights: {INSIGHTS_PATH}")
    print(f"- alerts: {ALERTS_PATH}")


def main() -> None:
    ensure_runtime_state()
    reset_singletons()
    start_workers()

    planner = AriaPlanner()
    bridge = AriaSynapseBridge(backend="memory")
    goal = "Evaluate whether to launch a multi-agent AI infra investment research sprint this week"

    round1 = dispatch_round(bridge, planner, goal, "Round 1: cold start")
    handler = HumanOverrideHandler()
    insight_id = handler.record_override(
        job_id="round-1-summary",
        original_decision={"action": "launch_sprint", "quality": avg_quality(round1)},
        override_reason="宏观风险没有被单独评估，先不要直接推进",
        domain="investment",
        context="需要把宏观 regime check 作为独立 gate",
    )
    print(f"\nHuman override recorded: {insight_id}")

    round2 = dispatch_round(bridge, planner, goal, "Round 2: memory + override")

    print("\n=== Delta ===")
    print(f"Round 1 avg quality: {avg_quality(round1):.2f}")
    print(f"Round 2 avg quality: {avg_quality(round2):.2f}")
    print(f"Quality delta: {avg_quality(round2) - avg_quality(round1):+.2f}")
    print_runtime_files()


if __name__ == "__main__":
    main()
