#!/usr/bin/env python3
"""Local-only student learning sandbox for NOUS OS.

This sandbox does not call external models or collect private student data. It
simulates a constrained learning loop and emits the same research-record shape
used by the heartbeat demo.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nousos_heartbeat_demo import (  # noqa: E402
    DEFAULT_GOAL,
    RUNTIME_RESEARCH_RECORDS,
    build_research_record,
    now_local,
    normalize_override_kind,
    redact_demo_text,
    write_json,
)


DEFAULT_SCENARIO = DEFAULT_GOAL


def detect_private_detail(text: str) -> bool:
    return redact_demo_text(text) != (text or "")


def build_first_pass(intent: str) -> Dict:
    return {
        "summary": (
            "Before answering, ask what the student already knows, what sources are allowed, "
            "what the project rubric requires, and which parts should remain the student's own thinking."
        ),
        "risks": [
            "answering too early can replace learning",
            "unsupported claims can look confident",
            "private details should be removed or anonymized",
        ],
        "clarifying_questions": [
            "What is the research question in your own words?",
            "What does your teacher's rubric require?",
            "Which sources are you allowed to use?",
            "What part do you want hints for, not answers for?",
        ],
    }


def build_second_pass(intent: str, boundary_kind: str) -> Dict:
    hints = [
        "Write a one-sentence research question before asking AI for sources.",
        "Ask AI for three possible subquestions, then choose one yourself.",
        "Keep a source checklist: author, date, evidence, and uncertainty.",
    ]
    practice = [
        "Draft two possible thesis statements and mark which evidence would support each one.",
        "Ask AI to challenge your weakest assumption instead of writing the final paragraph.",
    ]
    if boundary_kind == "facts":
        hints.append("Do not accept claims until you can point to at least two reviewable sources.")
    if boundary_kind == "learning":
        hints.append("Ask for hints, examples, and practice questions before any final answer.")
    if boundary_kind == "privacy":
        hints.append("Remove names, school identifiers, family details, and account information before saving notes.")

    return {
        "summary": "The sandbox returns a learning plan with hints, practice, source checks, and a reflection prompt instead of a final answer.",
        "behavior_changed": True,
        "hints": hints,
        "practice": practice,
        "source_check": [
            "Find the original source, not only a summary.",
            "Check whether the source is current enough for the topic.",
            "Write what would change your mind.",
        ],
    }


def build_sandbox_research_record(intent: str, boundary_kind: str = "learning") -> Dict:
    boundary_kind = normalize_override_kind(boundary_kind, "student")
    sanitized_intent = redact_demo_text(intent or DEFAULT_SCENARIO)
    private_detail_detected = detect_private_detail(intent or "")

    round1 = {
        "round": 1,
        "completed": [
            {
                "topic": "student_sandbox",
                "output": {
                    "agent": "student-sandbox-v0",
                    "summary": build_first_pass(sanitized_intent)["summary"],
                    "quality_score": 0.72,
                    "memory_hits": 0,
                },
            }
        ],
        "metrics": {"tasks_dispatched": 1, "tasks_completed": 1, "avg_quality": 0.72, "memory_hit_rate": 0.0},
    }
    round2 = {
        "round": 2,
        "completed": [
            {
                "topic": "student_sandbox",
                "output": {
                    "agent": "student-sandbox-v0",
                    "summary": build_second_pass(sanitized_intent, boundary_kind)["summary"],
                    "quality_score": 0.9,
                    "memory_hits": 1,
                },
            }
        ],
        "metrics": {"tasks_dispatched": 1, "tasks_completed": 1, "avg_quality": 0.9, "memory_hit_rate": 1.0},
    }
    override = {
        "kind": boundary_kind,
        "label": f"{boundary_kind.replace('_', ' ').title()} boundary",
        "reason": "Student sandbox boundary: keep learning, verification, privacy, and final responsibility with the student.",
    }
    benchmark = {
        "cls_v2": {
            "components": {
                "correction_absorption": 1.0,
                "memory_reuse_precision": 1.0,
                "boundary_integrity": 1.0,
                "human_agency_preservation": 1.0,
                "repeatability_gain": 0.0,
            },
            "evidence_refs": ["student_sandbox://first_pass", "student_sandbox://second_pass", "student_sandbox://boundary"],
        }
    }
    record = build_research_record(sanitized_intent, [round1, round2], override, benchmark, "student")
    record["run_id"] = f"{record['run_id']}-sandbox-v0"
    record["sandbox"] = {
        "name": "student_sandbox_v0",
        "local_only": True,
        "external_model_calls": False,
        "clarifying_questions": build_first_pass(sanitized_intent)["clarifying_questions"],
        "hints": build_second_pass(sanitized_intent, boundary_kind)["hints"],
        "practice": build_second_pass(sanitized_intent, boundary_kind)["practice"],
        "source_check": build_second_pass(sanitized_intent, boundary_kind)["source_check"],
        "refuses_private_storage_without_anonymization": True,
        "private_detail_detected": private_detail_detected,
    }
    record["privacy"]["contains_private_student_data"] = False
    record["privacy"]["redaction_applied"] = True
    record["privacy"]["policy"] = "local-only sandbox; private details are redacted before record emission"
    return record


def run_student_sandbox(intent: str = DEFAULT_SCENARIO, boundary_kind: str = "learning") -> Dict:
    record = build_sandbox_research_record(intent, boundary_kind)
    output_path = RUNTIME_RESEARCH_RECORDS / "student-sandbox-latest.json"
    write_json(output_path, record)
    record["artifact_path"] = str(output_path)
    write_json(output_path, record)
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local-only NOUS OS student sandbox v0.")
    parser.add_argument("--intent", default=DEFAULT_SCENARIO)
    parser.add_argument("--boundary", default="learning")
    args = parser.parse_args()

    record = run_student_sandbox(intent=args.intent, boundary_kind=args.boundary)
    print(json.dumps({
        "run_id": record["run_id"],
        "generated_at": now_local(),
        "artifact_path": record["artifact_path"],
        "local_only": record["sandbox"]["local_only"],
        "boundary": record["human_boundary"]["kind"],
        "reflection": record["reflection"]["prompt"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
