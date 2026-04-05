#!/usr/bin/env python3
"""NOUS OS demo: Aria intent routing + Synapse task fan-out + TrustMem memory."""

from __future__ import annotations

import json
import random
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parent
MEMORY_PATH = ROOT / "demo_memory.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class MemoryItem:
    memory_type: str
    domain: str
    content: str
    trust: float
    tags: List[str]
    source_run: str
    created_at: str = field(default_factory=now_iso)


class TrustMemStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.data = self._load()

    def _load(self) -> Dict[str, List[dict]]:
        if not self.path.exists():
            return {"memories": []}
        return json.loads(self.path.read_text())

    def _save(self) -> None:
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=True))

    def search(self, domain: str, intent: str) -> List[dict]:
        hits = []
        query = set(intent.lower().split())
        for item in self.data["memories"]:
            if item["domain"] != domain:
                continue
            overlap = query.intersection({tag.lower() for tag in item["tags"]})
            score = item["trust"] + 0.1 * len(overlap)
            hits.append((score, item))
        hits.sort(key=lambda row: row[0], reverse=True)
        return [item for _, item in hits[:3]]

    def add_memory(self, memory: MemoryItem) -> None:
        self.data["memories"].append(memory.__dict__)
        self._save()

    def reset(self) -> None:
        self.data = {"memories": []}
        self._save()


class AriaAdapter:
    def plan(self, user_goal: str, memory_hits: List[dict]) -> List[dict]:
        caution = any("macro_risk" in item["tags"] for item in memory_hits)
        tasks = [
            {
                "agent": "research",
                "task": f"Map the opportunity and unknowns for: {user_goal}",
            },
            {
                "agent": "builder",
                "task": f"Draft an execution plan for: {user_goal}",
            },
            {
                "agent": "critic",
                "task": f"Stress-test assumptions for: {user_goal}",
            },
        ]
        if caution:
            tasks.append(
                {
                    "agent": "risk",
                    "task": f"Apply remembered macro-risk guardrails to: {user_goal}",
                }
            )
        return tasks

    def summarize(self, user_goal: str, results: List[dict], memory_hits: List[dict]) -> str:
        guidance = "with recalled memory" if memory_hits else "without prior memory"
        bullets = "\n".join(f"- {row['agent']}: {row['summary']}" for row in results)
        return f'Aria decision for "{user_goal}" {guidance}\n{bullets}'


class AgentWorker:
    def __init__(self, seed: int = 7) -> None:
        self.rng = random.Random(seed)

    def run(self, agent: str, task: str, memory_hits: List[dict]) -> dict:
        base_quality = {
            "research": 0.68,
            "builder": 0.65,
            "critic": 0.72,
            "risk": 0.76,
        }[agent]
        memory_boost = 0.14 if memory_hits else 0.0
        summary = {
            "research": "Found comparable cases and surfaced missing evidence.",
            "builder": "Produced a short execution path with milestones.",
            "critic": "Flagged confidence gaps and failure modes.",
            "risk": "Enforced the remembered macro filter before go-live.",
        }[agent]
        latency = round(self.rng.uniform(0.18, 0.42), 2)
        return {
            "agent": agent,
            "task": task,
            "summary": summary,
            "quality": round(min(base_quality + memory_boost, 0.96), 2),
            "latency": latency,
        }


class SynapseBus:
    def __init__(self, worker: AgentWorker) -> None:
        self.worker = worker

    def execute(self, tasks: List[dict], memory_hits: List[dict]) -> List[dict]:
        with ThreadPoolExecutor(max_workers=len(tasks)) as pool:
            futures = [
                pool.submit(self.worker.run, row["agent"], row["task"], memory_hits)
                for row in tasks
            ]
            return [future.result() for future in futures]


def average_quality(results: List[dict]) -> float:
    return round(sum(row["quality"] for row in results) / len(results), 2)


def total_latency(results: List[dict]) -> float:
    return round(max(row["latency"] for row in results), 2)


def print_run(title: str, summary: str, results: List[dict], memory_hits: List[dict]) -> None:
    print(f"\n=== {title} ===")
    print(summary)
    print(f"Memory hits: {len(memory_hits)}")
    for row in results:
        print(
            f"  [{row['agent']:<8}] q={row['quality']:.2f} "
            f"latency={row['latency']:.2f}s | {row['task']}"
        )
    print(
        f"Aggregate: quality={average_quality(results):.2f} "
        f"critical_path={total_latency(results):.2f}s"
    )


def main() -> None:
    store = TrustMemStore(MEMORY_PATH)
    store.reset()

    aria = AriaAdapter()
    synapse = SynapseBus(AgentWorker())

    goal = "Evaluate whether to launch a small AI infra trading research sprint this week"
    domain = "investment"

    first_hits = store.search(domain, goal)
    first_tasks = aria.plan(goal, first_hits)
    first_results = synapse.execute(first_tasks, first_hits)
    first_summary = aria.summarize(goal, first_results, first_hits)
    print_run("Run 1: cold start", first_summary, first_results, first_hits)

    store.add_memory(
        MemoryItem(
            memory_type="episode",
            domain=domain,
            content="Human override: do not approve AI infra trades without macro regime check.",
            trust=0.92,
            tags=["macro_risk", "investment", "override", "ai", "infra"],
            source_run="run-1",
        )
    )
    store.add_memory(
        MemoryItem(
            memory_type="pattern",
            domain=domain,
            content="Past good runs improved when critic findings were injected before execution.",
            trust=0.81,
            tags=["critic_first", "investment", "execution"],
            source_run="run-1",
        )
    )

    second_hits = store.search(domain, goal)
    second_tasks = aria.plan(goal, second_hits)
    second_results = synapse.execute(second_tasks, second_hits)
    second_summary = aria.summarize(goal, second_results, second_hits)
    print_run("Run 2: memory + human override", second_summary, second_results, second_hits)

    print("\n=== What changed ===")
    print(f"Quality delta: {average_quality(second_results) - average_quality(first_results):+.2f}")
    print(f"Speed delta: {total_latency(second_results) - total_latency(first_results):+.2f}s")
    print("Human feedback became reusable system memory, and Aria changed task routing on the next run.")


if __name__ == "__main__":
    main()
