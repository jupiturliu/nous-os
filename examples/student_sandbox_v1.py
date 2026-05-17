#!/usr/bin/env python3
"""Student Sandbox v1 packet builder for NOUS OS.

Local-only scaffolding for a 20-minute high-school research learning loop.
It deliberately returns hints, checks, and reflection prompts instead of final
answers, so the student keeps verification and responsibility.
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
    now_local,
    redact_demo_text,
    write_json,
)
from student_sandbox_v0 import detect_private_detail  # noqa: E402


DEFAULT_RESEARCH_QUESTION = DEFAULT_GOAL


def _phase(
    phase_id: str,
    minutes: int,
    student_action: str,
    ai_help: str,
    human_keeps: str,
    artifact: str,
) -> Dict:
    return {
        "id": phase_id,
        "minutes": minutes,
        "student_action": student_action,
        "ai_help": ai_help,
        "human_keeps": human_keeps,
        "artifact": artifact,
    }


def build_twenty_minute_loop() -> Dict:
    """Return the fixed v1 learning loop schedule.

    The loop is intentionally short enough for a real student trial and explicit
    enough for parent/teacher/researcher observation.
    """

    phases: List[Dict] = [
        _phase(
            "intent",
            3,
            "Write the research question in your own words and name what you already believe.",
            "Suggest clearer subquestions without choosing the thesis.",
            "goal, curiosity, and initial judgment",
            "one-sentence question + prior-belief note",
        ),
        _phase(
            "ai_first_pass",
            4,
            "Ask for a learning plan, not an answer paragraph.",
            "Offer concepts, vocabulary, possible source types, and common traps.",
            "which path to explore first",
            "three possible subquestions",
        ),
        _phase(
            "human_boundary",
            3,
            "Choose one boundary: privacy, facts, learning, decision, or values.",
            "Restate the boundary and adapt the plan around it.",
            "values, privacy choices, and assignment constraints",
            "boundary card",
        ),
        _phase(
            "source_check",
            4,
            "Check at least two reviewable sources for author, date, evidence, and uncertainty.",
            "Provide a checklist and critique weak evidence.",
            "verification and source acceptance",
            "source checklist",
        ),
        _phase(
            "ai_second_pass",
            3,
            "Ask AI to revise the research plan using the chosen boundary and source notes.",
            "Improve next steps, practice questions, and uncertainty notes.",
            "the final claim and whether evidence is enough",
            "revised learning plan",
        ),
        _phase(
            "reflection",
            3,
            "Answer the reflection card before writing any final assignment text.",
            "Help compare first-pass vs second-pass behavior.",
            "responsibility for final work and next learning move",
            "reflection card",
        ),
    ]
    return {"total_minutes": sum(phase["minutes"] for phase in phases), "phases": phases}


def build_reflection_card() -> Dict:
    return {
        "student_prompts": [
            "What did AI help with?",
            "What did I verify?",
            "What remains my responsibility?",
            "What would I ask differently next time?",
        ],
        "parent_teacher_prompts": [
            "Could the student explain the question without AI?",
            "Did the student identify a source-quality issue?",
            "Did the student preserve their own judgment before drafting?",
        ],
    }


def build_source_checklist() -> List[str]:
    return [
        "Original source found, not only a summary.",
        "Author or institution is identifiable.",
        "Date is current enough for the topic.",
        "Evidence is separated from opinion.",
        "Student writes what would change their mind.",
    ]


def build_research_study_protocol() -> Dict:
    """Return the lightweight privacy-first observation protocol."""

    return {
        "version": "research_study_v0",
        "session_length_minutes": 20,
        "collects_student_identity": False,
        "collects_school_name": False,
        "collects_raw_private_prompt": False,
        "consent_language": "Student/parent may stop anytime; record learning-process observations, not identity.",
        "observer_packet": {
            "before_session": [
                "topic chosen by student",
                "student states what they already know",
                "allowed source types noted",
            ],
            "during_session": [
                "boundary selected",
                "source checklist attempted",
                "AI first pass changed after human boundary",
            ],
            "after_session": [
                "student reflection completed",
                "parent/teacher review comments optional",
                "next-run improvement noted",
            ],
            "confusion_notes": [],
        },
        "parent_or_teacher_review": {
            "questions": [
                "Was the AI acting like a tutor instead of a ghostwriter?",
                "Could you see what the student verified themselves?",
                "What boundary or instruction was unclear?",
            ]
        },
        "success_criteria": [
            "student_can_explain_ai_help",
            "student_can_name_verified_source_check",
            "student_can_name_human_responsibility",
            "student_has_next_learning_move",
        ],
    }


def build_learning_loop_packet(
    research_question: str = DEFAULT_RESEARCH_QUESTION,
    student_level: str = "high_school",
) -> Dict:
    detected = detect_private_detail(research_question or "")
    sanitized_question = redact_demo_text(research_question or DEFAULT_RESEARCH_QUESTION)
    if detected:
        sanitized_question = "[redacted-by-policy]"
    return {
        "version": "student_sandbox_v1",
        "generated_at": now_local(),
        "student_level": student_level,
        "student_intent": sanitized_question,
        "ai_support_policy": "hints_not_answers",
        "privacy": {
            "local_only": True,
            "external_model_calls": False,
            "contains_private_student_data": False,
            "redaction_applied": True,
            "private_detail_detected": detected,
            "policy": "Do not store names, school identifiers, emails, family details, or account data.",
        },
        "twenty_minute_loop": build_twenty_minute_loop(),
        "source_checklist": build_source_checklist(),
        "reflection_card": build_reflection_card(),
        "research_study": build_research_study_protocol(),
    }


def run_student_sandbox_v1(
    research_question: str = DEFAULT_RESEARCH_QUESTION,
    student_level: str = "high_school",
    output_dir: Path | None = None,
) -> Dict:
    packet = build_learning_loop_packet(research_question, student_level)
    artifact_dir = output_dir or RUNTIME_RESEARCH_RECORDS
    output_path = artifact_dir / "student-sandbox-v1-latest.json"
    packet["artifact_path"] = str(output_path)
    write_json(output_path, packet)
    return packet


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a local-only NOUS OS Student Sandbox v1 packet.")
    parser.add_argument("--question", default=DEFAULT_RESEARCH_QUESTION)
    parser.add_argument("--student-level", default="high_school")
    args = parser.parse_args()

    packet = run_student_sandbox_v1(args.question, args.student_level)
    print(json.dumps({
        "version": packet["version"],
        "generated_at": packet["generated_at"],
        "artifact_path": packet["artifact_path"],
        "local_only": packet["privacy"]["local_only"],
        "total_minutes": packet["twenty_minute_loop"]["total_minutes"],
        "ai_support_policy": packet["ai_support_policy"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
