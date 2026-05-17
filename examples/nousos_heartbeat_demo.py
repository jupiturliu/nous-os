#!/usr/bin/env python3
"""Aria heartbeat demo wired to runtime agent-bus + Synapse + TrustMem."""

from __future__ import annotations

import json
import re
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
    import core.worker as synapse_core_worker_module
    import aria_orchestrator as aria_orch_module
    from aria_orchestrator import AriaOrchestrator
    EXTERNAL_RUNTIME_AVAILABLE = True
except ModuleNotFoundError:
    reset_singletons = None
    AgentWorker = object
    synapse_worker_module = None
    synapse_core_worker_module = None
    aria_orch_module = None
    AriaOrchestrator = None
    EXTERNAL_RUNTIME_AVAILABLE = False


RUNTIME_DIR = ROOT / "runtime"
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

from cls_v2 import compute_cls_v2
from trading_evaluator import TradingEvaluator, CLS_V2_FIELDS as TRADING_CLS_FIELDS

RUNTIME_AGENT_BUS = RUNTIME_DIR / "agent-bus"
RUNTIME_EPISODE_LOGGER = RUNTIME_DIR / "episode_logger_local.py"
RUNTIME_ALERTS = RUNTIME_DIR / "alerts.json"
RUNTIME_INSIGHTS = RUNTIME_DIR / "insights.json"
RUNTIME_EPISODES = RUNTIME_DIR / "data" / "episodes" / "episodes.jsonl"
RUNTIME_EPISODES_SQLITE = RUNTIME_DIR / "data" / "episodes" / "episodes.sqlite"
RUNTIME_DASHBOARD = RUNTIME_DIR / "dashboard-data.json"
RUNTIME_RESEARCH_RECORDS = RUNTIME_DIR / "research-records"

DEFAULT_DEMO_MODE = "student"
DEFAULT_GOAL = "I am a high-school student trying to understand how to use AI for a research project without losing my own thinking."
DEFAULT_OVERRIDE_KIND = "privacy"
HUMAN_AGENCY = {
    "human_sets_goal": True,
    "human_sets_boundary": True,
    "human_verifies": True,
    "human_keeps_final_responsibility": True,
    "human_keeps": ["goal", "values", "verification", "final responsibility"],
    "ai_helps_with": ["search", "decomposition", "simulation", "critique", "memory recall", "practice generation"],
}
FIRST_VERTICAL = {
    "name": "trading-agent",
    "role": "first vertical application / research proof bed",
    "not_for": "not to recommend trades, not student investing advice, and not a commercialization endpoint",
    "lesson": "High-stakes agents require approval gates, reconciliation, provenance, and review.",
}
DEMO_MODES = {
    "student": {
        "label": "Student Learning Companion",
        "audience": "high_school_student",
        "goal": DEFAULT_GOAL,
        "lesson": "AI gets more useful after human feedback, but the human keeps goals, values, verification, and responsibility.",
        "reflection": {
            "prompt": "What did the AI help with, and what remains my responsibility?",
            "student_takeaway": "AI can assist my thinking, but it should not replace my judgment.",
        },
        "boundaries": ["privacy", "facts", "learning", "values"],
    },
    "trading_vertical": {
        "label": "Trading Agent Research Proof",
        "audience": "researcher",
        "goal": "Use trading-agent as a high-constraint research example to study AI boundaries, not to recommend trades.",
        "lesson": "The first vertical shows why powerful agents need boundaries before autonomy.",
        "reflection": {
            "prompt": "Which approvals, evidence, and reconciliation steps must stay human-owned?",
            "student_takeaway": "A high-stakes agent should prove boundary integrity before it earns more autonomy.",
        },
        "boundaries": ["capital_boundary", "evidence", "reconciliation", "no_action"],
    },
    "research_lab": {
        "label": "Research Lab / Teacher View",
        "audience": "teacher",
        "goal": "Run an education/research experiment showing whether human feedback changes the next AI cycle.",
        "lesson": "This is an experiment harness, not a product claim.",
        "reflection": {
            "prompt": "What changed after feedback, and can another observer reproduce the loop?",
            "student_takeaway": "Human feedback should leave measurable evidence, not just a better-looking answer.",
        },
        "boundaries": ["rubric", "reflection", "repeatability", "boundary"],
    },
}
OVERRIDE_PRESETS = {
    "privacy": {
        "label": "Privacy boundary",
        "reason": "Human boundary: do not reveal private family, school, or friend information.",
        "implementation_suffix": "Protect privacy while guiding the research project",
        "quality_bonus": 0.04,
        "role": "privacy_guard",
    },
    "facts": {
        "label": "Fact-check boundary",
        "reason": "Human boundary: add source checks before accepting the answer.",
        "implementation_suffix": "Add source checks and evidence prompts before final claims",
        "quality_bonus": 0.03,
        "role": "fact_guard",
    },
    "learning": {
        "label": "Learning-not-answering boundary",
        "reason": "Human boundary: do not give final answers; guide with hints and practice.",
        "implementation_suffix": "Convert final answers into hints, practice, and reflection",
        "quality_bonus": 0.04,
        "role": "learning_guard",
    },
    "values": {
        "label": "Value/goal boundary",
        "reason": "Human boundary: do not decide the student's goals or values for them.",
        "implementation_suffix": "Keep goals and values with the human while AI supports options",
        "quality_bonus": 0.03,
        "role": "values_guard",
    },
    "capital_boundary": {
        "label": "Capital approval boundary",
        "reason": "Human boundary: no capital action without explicit human approval.",
        "implementation_suffix": "Add explicit human approval before any capital action",
        "quality_bonus": 0.04,
        "role": "capital_guard",
    },
    "evidence": {
        "label": "Evidence/provenance boundary",
        "reason": "Human boundary: require provenance and measurable outcome before promotion.",
        "implementation_suffix": "Attach provenance and outcome evidence before promotion",
        "quality_bonus": 0.03,
        "role": "evidence_guard",
    },
    "reconciliation": {
        "label": "Reconciliation boundary",
        "reason": "Human boundary: block new action until prior state is reconciled.",
        "implementation_suffix": "Reconcile prior state before creating any new action",
        "quality_bonus": 0.03,
        "role": "reconciliation_guard",
    },
    "no_action": {
        "label": "No-action boundary",
        "reason": "Human boundary: preserve the right to decide that no action is the correct action.",
        "implementation_suffix": "Keep no-action as an explicit valid decision",
        "quality_bonus": 0.03,
        "role": "no_action_guard",
    },
    "rubric": {
        "label": "Rubric boundary",
        "reason": "Human boundary: use a rubric before scoring quality.",
        "implementation_suffix": "Score the run against an explicit rubric",
        "quality_bonus": 0.03,
        "role": "rubric_guard",
    },
    "reflection": {
        "label": "Reflection checkpoint",
        "reason": "Human boundary: add a student reflection checkpoint before closing the loop.",
        "implementation_suffix": "Add a reflection checkpoint before finalizing the run",
        "quality_bonus": 0.04,
        "role": "reflection_guard",
    },
    "repeatability": {
        "label": "Repeatability requirement",
        "reason": "Human boundary: require the same loop to be reproducible.",
        "implementation_suffix": "Make the loop reproducible for another observer",
        "quality_bonus": 0.03,
        "role": "repeatability_guard",
    },
    "boundary": {
        "label": "Human agency boundary",
        "reason": "Human boundary: fail the run if human agency is not preserved.",
        "implementation_suffix": "Check human agency preservation before treating the run as valid",
        "quality_bonus": 0.04,
        "role": "agency_guard",
    },
    "risk": {
        "label": "Risk boundary",
        "reason": "Human boundary: add an explicit risk gate before execution.",
        "implementation_suffix": "Apply risk guardrails before shipping",
        "quality_bonus": 0.04,
        "role": "risk_guard",
    },
    "cost": {
        "label": "Cost boundary",
        "reason": "Human boundary: execution is too expensive, reduce scope and budget burn.",
        "implementation_suffix": "Trim cost and scope before shipping",
        "quality_bonus": 0.02,
        "role": "cost_guard",
    },
    "timing": {
        "label": "Timing boundary",
        "reason": "Human boundary: timing is off, add a sequencing checkpoint before launch.",
        "implementation_suffix": "Re-sequence the launch plan before shipping",
        "quality_bonus": 0.03,
        "role": "timing_guard",
    },
}


def now_local() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def now_run_id() -> str:
    return time.strftime("%Y%m%dT%H%M%S")


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


def redact_demo_text(text: str | None) -> str:
    if not text:
        return ""
    redacted = re.sub(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", "[redacted-email]", text)
    redacted = re.sub(r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b", "[redacted-phone]", redacted)
    redacted = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[redacted-id]", redacted)
    return redacted


def normalize_demo_mode(demo_mode: str | None) -> str:
    return demo_mode if demo_mode in DEMO_MODES else DEFAULT_DEMO_MODE


def default_override_for_mode(demo_mode: str) -> str:
    return DEMO_MODES[normalize_demo_mode(demo_mode)]["boundaries"][0]


def normalize_override_kind(override_kind: str | None, demo_mode: str) -> str:
    mode = normalize_demo_mode(demo_mode)
    if override_kind in DEMO_MODES[mode]["boundaries"]:
        return override_kind
    if override_kind in OVERRIDE_PRESETS:
        return override_kind
    return default_override_for_mode(mode)


def boundary_catalog(demo_mode: str, selected_kind: str) -> List[Dict]:
    mode = normalize_demo_mode(demo_mode)
    boundaries = []
    for kind in DEMO_MODES[mode]["boundaries"]:
        preset = OVERRIDE_PRESETS[kind]
        boundaries.append(
            {
                "id": kind,
                "label": preset["label"],
                "status": "active" if kind == selected_kind else "available",
                "reason": preset["reason"],
                "evidence_ref": "runtime://human_override" if kind == selected_kind else "runtime://boundary_catalog",
            }
        )
    return boundaries


def reset_runtime_files() -> None:
    write_json(RUNTIME_AGENT_BUS / "implementation_queue.json", {"items": []})
    write_json(RUNTIME_AGENT_BUS / "learning_queue.json", {"items": []})
    write_json(RUNTIME_AGENT_BUS / "alerts.json", {"items": []})
    write_json(RUNTIME_ALERTS, {"items": []})
    write_json(RUNTIME_INSIGHTS, {"insights": []})
    RUNTIME_EPISODES.parent.mkdir(parents=True, exist_ok=True)
    if RUNTIME_EPISODES.exists():
        RUNTIME_EPISODES.unlink()
    if RUNTIME_EPISODES_SQLITE.exists():
        RUNTIME_EPISODES_SQLITE.unlink()


def seed_runtime_queues(goal: str, round_index: int, override_kind: str = DEFAULT_OVERRIDE_KIND, demo_mode: str = DEFAULT_DEMO_MODE) -> None:
    override_preset = OVERRIDE_PRESETS.get(override_kind, OVERRIDE_PRESETS[DEFAULT_OVERRIDE_KIND])
    mode = DEMO_MODES[normalize_demo_mode(demo_mode)]
    impl_reason = (
        f"Aria wants a visible {mode['label']} first pass for: {goal}"
        if round_index == 1
        else f"Aria wants a refined second pass that applies the human boundary for: {goal}"
    )
    learning_reason = (
        f"Aria needs an education/research narrative for: {goal}"
        if round_index == 1
        else f"Aria wants the next run to reuse prior learning and preserve human agency for: {goal}"
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
            "demo_mode": normalize_demo_mode(demo_mode),
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
            "demo_mode": normalize_demo_mode(demo_mode),
        }
    ]
    if round_index >= 2:
        implementation_items.append(
            {
                "id": f"boundary-demo-{round_index:03d}",
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
                "boundary_label": override_preset["label"],
                "demo_mode": normalize_demo_mode(demo_mode),
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


def record_override(goal: str, round1_avg_quality: float, override_kind: str = DEFAULT_OVERRIDE_KIND, demo_mode: str = DEFAULT_DEMO_MODE) -> Dict:
    override_preset = OVERRIDE_PRESETS.get(override_kind, OVERRIDE_PRESETS[DEFAULT_OVERRIDE_KIND])
    insights = read_json(RUNTIME_INSIGHTS)
    insight = {
        "id": f"override-{int(time.time() * 1000)}",
        "goal": goal,
        "label": override_preset["label"],
        "reason": override_preset["reason"],
        "domain": "demo",
        "created_at": now_local(),
        "round_1_quality": round1_avg_quality,
        "kind": override_kind,
        "demo_mode": normalize_demo_mode(demo_mode),
        "evidence_ref": "runtime://human_override",
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
    cls_v2_components = {
        "outcome_quality_delta": round(min(1.0, q_component), 3),
        "correction_absorption": round(c_component, 3),
        "memory_reuse_precision": round(min(1.0, e_component), 3),
        "repeatability_gain": round(min(1.0, r_component), 3),
        "boundary_integrity": 1.0,
        "human_agency_preservation": 1.0 if override else 0.0,
    }

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
        "cls_v2": {
            "score": compute_cls_v2(cls_v2_components),
            "components": cls_v2_components,
            "evidence_refs": [
                "runtime://round1",
                "runtime://round2",
                "runtime://human_override" if override else "runtime://no_override",
            ],
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


TRADING_EVALUATOR_MODE = "trading_vertical"


def _trading_workspace_root() -> Path:
    return WORKSPACE


def _first_populated_trading_user(workspace: Path) -> str | None:
    users_dir = workspace / "trading-agent" / "data" / "users"
    if not users_dir.exists():
        return None
    for path in sorted(users_dir.iterdir()):
        if not path.is_dir():
            continue
        packs_dir = path / "promotion_reviews" / "proof_packs"
        market_dir = path / "market_proof"
        if not packs_dir.exists() or not market_dir.exists():
            continue
        for pack in packs_dir.glob("*.json"):
            if pack.name != "index.json":
                return path.name
    return None


def maybe_apply_trading_evaluator(
    benchmark: Dict,
    demo_mode: str,
    workspace: Path | None = None,
) -> Dict:
    """Route trading_vertical CLS v2 through the real domain evaluator.

    Other demo modes are unchanged. When trading-agent artifacts are not
    available the benchmark is left synthetic but flagged with an explicit
    fallback reason — never silently substituted.
    """
    if normalize_demo_mode(demo_mode) != TRADING_EVALUATOR_MODE:
        benchmark["evidence_source"] = "synthetic_demo"
        benchmark["cls_v2"]["evidence_source"] = "synthetic_demo"
        return benchmark

    workspace = workspace or _trading_workspace_root()
    username = _first_populated_trading_user(workspace)
    if username is None:
        benchmark["evidence_source"] = "synthetic_demo_fallback"
        benchmark["fallback_reason"] = (
            f"trading-agent workspace not found or no user has populated "
            f"market_proof plus promotion_reviews/proof_packs at {workspace}/trading-agent"
        )
        benchmark["cls_v2"]["evidence_source"] = "synthetic_demo_fallback"
        benchmark["cls_v2"]["fallback_reason"] = (
            f"trading-agent workspace not found or no user has populated "
            f"market_proof plus promotion_reviews/proof_packs at {workspace}/trading-agent"
        )
        return benchmark

    evaluator = TradingEvaluator(workspace=workspace, username=username)
    real = evaluator.evaluate(run_context={"demo_mode": TRADING_EVALUATOR_MODE, "username": username})
    pending = [ref for ref in real["evidence_refs"] if ref.startswith("pending:")]
    missing = [ref for ref in real["evidence_refs"] if ref.startswith("missing:")]
    if missing:
        benchmark["evidence_source"] = "synthetic_demo_fallback"
        benchmark["fallback_reason"] = ", ".join(missing)
        benchmark["cls_v2"]["evidence_source"] = "synthetic_demo_fallback"
        benchmark["cls_v2"]["fallback_reason"] = ", ".join(missing)
        return benchmark

    components = {field: real[field] for field in TRADING_CLS_FIELDS}
    benchmark["evidence_source"] = "trading_evaluator"
    benchmark["evaluator_user"] = username
    benchmark["cls_v2"] = {
        "score": compute_cls_v2(components),
        "components": components,
        "evidence_refs": real["evidence_refs"],
        "evidence_source": "trading_evaluator",
        "trading_username": username,
        "pending_components": [marker.split(":", 1)[1] for marker in pending],
    }
    return benchmark


def build_timeline(goal: str, runs: List[Dict], override: Dict, demo_mode: str = DEFAULT_DEMO_MODE) -> List[Dict]:
    round1 = runs[0]
    round2 = runs[1]
    mode = DEMO_MODES[normalize_demo_mode(demo_mode)]
    return [
        {
            "stage": "Step 1",
            "title": "Student / human sets intent",
            "detail": goal,
            "accent": "intent",
        },
        {
            "stage": "Step 2",
            "title": "AI first pass",
            "detail": f"Aria and Synapse produce a first pass with {round1['metrics']['tasks_dispatched']} tasks and {round1['metrics']['avg_quality']:.2f} baseline quality.",
            "accent": "aria",
        },
        {
            "stage": "Step 3",
            "title": "Human boundary / correction",
            "detail": override["reason"],
            "accent": "override",
        },
        {
            "stage": "Step 4",
            "title": "Memory and evidence update",
            "detail": f"Round 2 recalled episode memory and expanded to {round2['metrics']['tasks_dispatched']} tasks.",
            "accent": "trustmem",
        },
        {
            "stage": "Step 5",
            "title": "AI second pass changes behavior",
            "detail": f"Average quality improved from {round1['metrics']['avg_quality']:.2f} to {round2['metrics']['avg_quality']:.2f}.",
            "accent": "compound",
        },
        {
            "stage": "Step 6",
            "title": "Student reflection",
            "detail": mode["reflection"]["student_takeaway"],
            "accent": "reflection",
        },
        {
            "stage": "Step 7",
            "title": "What remains human-owned",
            "detail": "Human keeps goal, values, verification, and final responsibility.",
            "accent": "human",
        },
    ]


def build_topology(goal: str, runs: List[Dict], override: Dict) -> Dict:
    round1 = runs[0]
    round2 = runs[1]
    return {
        "nodes": [
            {"id": "human", "label": "Human", "kind": "human", "meta": goal},
            {"id": "obsidian", "label": "Obsidian", "kind": "knowledge", "meta": "readable notes"},
            {"id": "aria", "label": "Aria", "kind": "aria", "meta": "intent router"},
            {"id": "synapse", "label": "Synapse", "kind": "synapse", "meta": f"{round2['metrics']['tasks_dispatched']} tasks"},
            {"id": "research", "label": "Research", "kind": "agent", "meta": "research lane"},
            {"id": "vibe", "label": "Vibe", "kind": "agent", "meta": "implementation lane"},
            {"id": "override", "label": "Override", "kind": "override", "meta": override["kind"]},
            {"id": "trustmem", "label": "TrustMem", "kind": "trustmem", "meta": f"{round2['metrics']['avg_quality']:.2f} round2"},
            {"id": "alerts", "label": "Alerts", "kind": "alerts", "meta": "return to Aria"},
        ],
        "edges": [
            {"from": "human", "to": "obsidian", "label": "notes"},
            {"from": "obsidian", "to": "aria", "label": "context"},
            {"from": "aria", "to": "synapse", "label": "plan"},
            {"from": "synapse", "to": "research", "label": f"r1 {round1['metrics']['tasks_dispatched']}"},
            {"from": "synapse", "to": "vibe", "label": f"r2 {round2['metrics']['tasks_dispatched']}"},
            {"from": "human", "to": "override", "label": "feedback"},
            {"from": "override", "to": "trustmem", "label": "policy"},
            {"from": "obsidian", "to": "trustmem", "label": "sediment"},
            {"from": "research", "to": "trustmem", "label": "episodes"},
            {"from": "vibe", "to": "trustmem", "label": "episodes"},
            {"from": "trustmem", "to": "synapse", "label": "recall"},
            {"from": "synapse", "to": "alerts", "label": "completion"},
            {"from": "alerts", "to": "aria", "label": "summary"},
        ],
    }


def summarize_completed(completed: List[Dict]) -> str:
    if not completed:
        return "No completed agent outputs were recorded."
    summaries = []
    for item in completed[:3]:
        output = item.get("output", {})
        agent = output.get("agent") or item.get("topic") or "agent"
        summary = redact_demo_text(output.get("summary") or output.get("task") or "")
        quality = output.get("quality_score")
        quality_text = f" q={quality}" if quality is not None else ""
        summaries.append(f"{agent}{quality_text}: {summary}")
    return " | ".join(summaries)


def build_research_record(goal: str, runs: List[Dict], override: Dict, benchmark: Dict, demo_mode: str) -> Dict:
    demo_mode = normalize_demo_mode(demo_mode)
    mode = DEMO_MODES[demo_mode]
    round1 = runs[0]
    round2 = runs[1]
    components = benchmark["cls_v2"]["components"]
    run_id = f"{now_run_id()}-{demo_mode}-{override.get('kind', 'boundary')}"
    return {
        "run_id": run_id,
        "generated_at": now_local(),
        "demo_mode": demo_mode,
        "audience": "student" if mode["audience"] == "high_school_student" else mode["audience"],
        "human_intent": redact_demo_text(goal),
        "ai_first_pass": {
            "summary": summarize_completed(round1.get("completed", [])),
            "risks": [
                "first pass may be fluent without enough evidence",
                "student/private context must stay minimized",
            ],
        },
        "human_boundary": {
            "kind": override.get("kind"),
            "label": override.get("label") or OVERRIDE_PRESETS.get(override.get("kind"), {}).get("label", "Human boundary"),
            "reason": redact_demo_text(override.get("reason")),
        },
        "memory_update": {
            "stored": True,
            "evidence_refs": [
                "runtime://human_override",
                "runtime://round1",
                "runtime://round2",
                "examples/runtime/dashboard-data.json",
            ],
        },
        "ai_second_pass": {
            "summary": summarize_completed(round2.get("completed", [])),
            "behavior_changed": True,
            "evidence_refs": benchmark["cls_v2"]["evidence_refs"],
        },
        "reflection": mode["reflection"],
        "metrics": {
            "correction_absorption": components["correction_absorption"],
            "memory_reuse": components["memory_reuse_precision"],
            "boundary_integrity": components["boundary_integrity"],
            "human_agency_preservation": components["human_agency_preservation"],
            "reflection_completeness": 1.0 if mode.get("reflection") else 0.0,
            "repeatability_gain": components["repeatability_gain"],
        },
        "privacy": {
            "contains_private_student_data": False,
            "redaction_applied": True,
            "policy": "local/demo artifact only; do not collect real student private data",
        },
        "snapshot_ref": "examples/runtime/dashboard-data.json",
    }


def write_research_record(snapshot: Dict) -> Path:
    record = snapshot["research_record"]
    record_path = RUNTIME_RESEARCH_RECORDS / f"{record['run_id']}.json"
    latest_path = RUNTIME_RESEARCH_RECORDS / "latest.json"
    record["artifact_path"] = str(record_path)
    record["latest_path"] = str(latest_path)
    write_json(record_path, record)
    write_json(latest_path, record)
    snapshot.setdefault("paths", {})["research_record"] = str(record_path)
    snapshot["paths"]["latest_research_record"] = str(latest_path)
    return record_path


def build_dashboard_snapshot(goal: str, runs: List[Dict], override: Dict, demo_mode: str = DEFAULT_DEMO_MODE) -> Dict:
    demo_mode = normalize_demo_mode(demo_mode)
    mode = DEMO_MODES[demo_mode]
    round1 = runs[0]
    round2 = runs[1]
    alerts = read_json(RUNTIME_AGENT_BUS / "alerts.json")
    episodes_logged = count_episode_lines()
    alerts_count = len(alerts.get("items", []))
    quality_delta = round(round2["metrics"]["avg_quality"] - round1["metrics"]["avg_quality"], 2)
    benchmark = build_benchmark(round1, round2, alerts_count, episodes_logged, override)
    benchmark = maybe_apply_trading_evaluator(benchmark, demo_mode)
    return {
        "generated_at": now_local(),
        "demo_mode": demo_mode,
        "demo_mode_label": mode["label"],
        "audience": mode["audience"],
        "north_star": "education/research-first human-AI co-evolution",
        "mode_lesson": mode["lesson"],
        "goal": goal,
        "human_agency": HUMAN_AGENCY,
        "safety_boundaries": boundary_catalog(demo_mode, override.get("kind", default_override_for_mode(demo_mode))),
        "reflection": mode["reflection"],
        "first_vertical": FIRST_VERTICAL,
        "research_record": build_research_record(goal, runs, override, benchmark, demo_mode),
        "current_round": 2,
        "runs": runs,
        "timeline": build_timeline(goal, runs, override, demo_mode=demo_mode),
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
            "cls_v2_score": benchmark["cls_v2"]["score"],
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


def run_round(orch: AriaOrchestrator, goal: str, round_index: int, override_kind: str, demo_mode: str) -> Dict:
    if not EXTERNAL_RUNTIME_AVAILABLE:
        return run_local_round(goal, round_index, override_kind, demo_mode)
    seed_runtime_queues(goal, round_index, override_kind=override_kind, demo_mode=demo_mode)
    results = orch.publish_from_agent_bus()
    expected = sum(len(ids) for ids in results.values())
    completed = handle_completion_events(orch, expected)
    return summarize_round(round_index, results, completed)


def run_local_round(goal: str, round_index: int, override_kind: str, demo_mode: str) -> Dict:
    seed_runtime_queues(goal, round_index, override_kind=override_kind, demo_mode=demo_mode)
    dispatch_results: Dict[str, List[str]] = {}
    completed: List[Dict] = []
    queue_specs = [
        ("implementation_queue", "vibe-vpe", "Built implementation draft", 0.72, "task"),
        ("learning_queue", "research-cto", "Produced research brief", 0.76, "topic"),
    ]
    for queue_name, agent, result_prefix, base_quality, text_key in queue_specs:
        queue_data = read_json(RUNTIME_AGENT_BUS / f"{queue_name}.json")
        dispatch_results[queue_name] = []
        for item in queue_data.get("items", []):
            job_id = item["id"]
            dispatch_results[queue_name].append(job_id)
            memory_hits = 1 if round_index >= 2 else 0
            quality_boost = 0.16 if memory_hits else 0.0
            round_boost = 0.02 if round_index >= 2 else 0.0
            role_boost = OVERRIDE_PRESETS.get(item.get("override_kind"), {}).get("quality_bonus", 0.0)
            quality = min(base_quality + quality_boost + round_boost + role_boost, 0.95)
            task_text = item.get(text_key) or item.get("task") or item.get("topic") or queue_name
            output = {
                "agent": agent,
                "topic": queue_name,
                "task": task_text,
                "quality_score": round(quality, 2),
                "summary": f"{result_prefix}: {task_text[:120]}",
                "memory_hits": memory_hits,
                "round": round_index,
                "goal": goal,
            }
            update_queue_status(queue_name, job_id, output)
            append_alert(
                agent,
                f"{agent} completed {queue_name}: {output['summary']}",
                {
                    "job_id": job_id,
                    "quality_score": output["quality_score"],
                    "round": round_index,
                },
            )
            append_local_episode(queue_name, job_id, output)
            completed.append({"job_id": job_id, "topic": queue_name, "output": output})
    return summarize_round(round_index, dispatch_results, completed)


def append_local_episode(queue_name: str, job_id: str, output: Dict) -> None:
    RUNTIME_EPISODES.parent.mkdir(parents=True, exist_ok=True)
    with open(RUNTIME_EPISODES, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "job_id": job_id,
            "topic": queue_name,
            "agent": output.get("agent"),
            "quality_score": output.get("quality_score"),
            "memory_hits": output.get("memory_hits", 0),
            "round": output.get("round"),
            "created_at": now_local(),
        }, ensure_ascii=False) + "\n")


def run_heartbeat_flow(goal: str = DEFAULT_GOAL, override_kind: str = DEFAULT_OVERRIDE_KIND, demo_mode: str = DEFAULT_DEMO_MODE) -> Dict:
    demo_mode = normalize_demo_mode(demo_mode)
    goal = (goal or DEMO_MODES[demo_mode]["goal"]).strip() or DEMO_MODES[demo_mode]["goal"]
    override_kind = normalize_override_kind(override_kind, demo_mode)
    if EXTERNAL_RUNTIME_AVAILABLE:
        reset_singletons()
    reset_runtime_files()

    if EXTERNAL_RUNTIME_AVAILABLE:
        synapse_worker_module._EPISODE_LOGGER_PATH = RUNTIME_EPISODE_LOGGER
        synapse_core_worker_module._EPISODE_LOGGER_PATH = RUNTIME_EPISODE_LOGGER
        aria_orch_module._EPISODE_LOGGER_PATH = RUNTIME_EPISODE_LOGGER
        aria_orch_module._AGENT_BUS_DIR = RUNTIME_AGENT_BUS

    orch = None
    if EXTERNAL_RUNTIME_AVAILABLE:
        start_workers()
        orch = AriaOrchestrator()
    round1 = run_round(orch, goal, 1, override_kind, demo_mode)
    override = record_override(goal, round1["metrics"]["avg_quality"], override_kind=override_kind, demo_mode=demo_mode)
    round2 = run_round(orch, goal, 2, override_kind, demo_mode)
    snapshot = build_dashboard_snapshot(goal, [round1, round2], override, demo_mode=demo_mode)
    write_research_record(snapshot)
    write_json(RUNTIME_DASHBOARD, snapshot)
    return snapshot


def ensure_runtime_available() -> None:
    return


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
