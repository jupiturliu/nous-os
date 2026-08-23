"""Privacy-first Student Sandbox record workflow."""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from typing import Any

from nous_os.core.context import HarnessContext
from nous_os.core.events import EvidenceEvent


MAX_TURNS = 24
MAX_SOURCE_CARDS = 4
FIELD_LIMITS = {
    "question": 500,
    "prior_belief": 800,
    "boundary": 400,
    "ai_plan_notes": 1400,
    "source_notes": 1400,
    "revised_plan": 1400,
    "reflect_help": 900,
    "reflect_verify": 900,
    "reflect_responsibility": 900,
    "reflect_next": 900,
    "summary": 2000,
}
PRIVATE_PATTERNS = (
    re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I),
    re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b"),
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"\b\d{9}\b"),
)
REPLACEMENTS = ("[redacted-email]", "[redacted-phone]", "[redacted-ssn]", "[redacted-id]")


def redact_private_text(value: Any) -> str:
    text = str(value or "")
    for pattern, replacement in zip(PRIVATE_PATTERNS, REPLACEMENTS):
        text = pattern.sub(replacement, text)
    return text


def contains_private_pattern(value: Any) -> bool:
    text = str(value or "")
    return any(pattern.search(text) for pattern in PRIVATE_PATTERNS)


def safe_text(value: Any, limit: int = 2000) -> str:
    return redact_private_text(value).strip()[:limit]


def safe_session_id(value: Any) -> str:
    candidate = str(value or "").strip()
    return candidate if re.fullmatch(r"[A-Za-z0-9_-]{8,80}", candidate) else f"session-{uuid.uuid4().hex[:16]}"


def _safe_fields(source: dict[str, Any], limits: dict[str, int]) -> dict[str, str]:
    return {key: safe_text(source.get(key), limit) for key, limit in limits.items()}


def build_record(body: dict[str, Any]) -> dict[str, Any]:
    worksheet = _safe_fields(body.get("worksheet", {}), {key: FIELD_LIMITS[key] for key in (
        "question", "prior_belief", "boundary", "ai_plan_notes", "source_notes", "revised_plan"
    )})
    reflection = _safe_fields(body.get("reflection", {}), {key: FIELD_LIMITS[key] for key in (
        "reflect_help", "reflect_verify", "reflect_responsibility", "reflect_next"
    )})
    source_cards = []
    for index, card in enumerate(body.get("source_cards", [])[:MAX_SOURCE_CARDS]):
        source_cards.append({
            "id": safe_text(card.get("id"), 40) or f"source-{index + 1}",
            "title": safe_text(card.get("title"), 240),
            "url": safe_text(card.get("url"), 500),
            "author": safe_text(card.get("author"), 240),
            "date": safe_text(card.get("date"), 120),
            "evidence": safe_text(card.get("evidence"), 700),
            "uncertainty": safe_text(card.get("uncertainty"), 700),
            "decision": safe_text(card.get("decision"), 80),
        })
    turns = [{
        "role": "agent" if turn.get("role") == "agent" else "student",
        "text": safe_text(turn.get("text"), 1600),
        "created_at": safe_text(turn.get("created_at"), 80),
    } for turn in body.get("chat_turns", [])[-MAX_TURNS:]]
    observer = _safe_fields(body.get("observer", {}), {
        "student_explained_question": 20,
        "named_source_issue": 20,
        "kept_human_responsibility": 20,
        "used_ai_for_hints": 20,
        "note": 1200,
    })
    complete_sources = sum(bool(card["title"] and card["author"] and card["date"] and card["evidence"] and card["uncertainty"]) for card in source_cards)
    complete_reflection = sum(bool(value) for value in reflection.values())
    observer_checks = sum(value == "yes" for key, value in observer.items() if key != "note")
    signals = {
        "source_cards_total": len(source_cards),
        "source_cards_complete": complete_sources,
        "accepted_sources": sum(card["decision"] == "accepted" for card in source_cards),
        "reflection_fields_complete": complete_reflection,
        "chat_turns_total": len(turns),
        "has_human_boundary": bool(worksheet["boundary"]),
        "has_revised_plan": bool(worksheet["revised_plan"]),
        "observer_check_count": observer_checks,
    }
    serialized = repr({key: body.get(key) for key in ("worksheet", "reflection", "source_cards", "observer", "summary", "chat_turns")})
    return {
        "version": "student_sandbox_session_v1",
        "session_id": safe_session_id(body.get("session_id")),
        "saved_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "storage": {"backend": "nous-os-artifact-store", "browser_storage": False, "local_only": True},
        "privacy": {
            "contains_private_student_data": False,
            "private_pattern_detected": contains_private_pattern(serialized),
            "redaction": "email_phone_ssn_and_numeric_id_patterns",
            "reminder": "Do not enter full names, school names, teacher names, addresses, or family details.",
        },
        "worksheet": worksheet,
        "source_cards": source_cards,
        "reflection": reflection,
        "observer": observer,
        "research_signals": signals,
        "readiness": {
            "ready_for_first_pass": signals["has_human_boundary"],
            "ready_for_second_pass": signals["has_human_boundary"] and complete_sources >= 1,
            "ready_for_review": signals["has_human_boundary"] and signals["has_revised_plan"] and complete_sources >= 2 and complete_reflection >= 4,
            "source_cards_complete": complete_sources,
            "reflection_fields_complete": complete_reflection,
            "observer_check_count": observer_checks,
        },
        "summary": safe_text(body.get("summary"), FIELD_LIMITS["summary"]),
        "chat_turns": turns,
    }


class StudentSandboxStore:
    def __init__(self, context: HarnessContext):
        self.context = context

    def save(self, body: dict[str, Any]) -> dict[str, Any]:
        record = build_record(body)
        artifact = self.context.events.write_artifact("student-sessions", record)
        self.context.emit(EvidenceEvent(
            event_type="student-sandbox.session-saved",
            run_id=record["session_id"],
            profile=self.context.profile_name,
            producer="student-sandbox",
            payload={
                "session_id": record["session_id"],
                "saved_at": record["saved_at"],
                "private_pattern_detected": record["privacy"]["private_pattern_detected"],
                "research_signals": record["research_signals"],
                "readiness": record["readiness"],
            },
            evidence_refs=(artifact,),
            privacy="private-redacted",
        ))
        return record

    def read(self, session_id: str) -> dict[str, Any] | None:
        safe_id = safe_session_id(session_id)
        if safe_id != session_id:
            return None
        for event in reversed(tuple(self.context.events.events())):
            if event.get("event_type") != "student-sandbox.session-saved":
                continue
            if event.get("payload", {}).get("session_id") != safe_id:
                continue
            references = event.get("evidence_refs") or []
            if not references:
                return None
            path = self.context.paths.home / references[0]["path"]
            if not path.exists():
                return None
            import json
            return json.loads(path.read_text(encoding="utf-8"))
        return None

    def list(self, limit: int = 20) -> list[dict[str, Any]]:
        result = []
        for event in reversed(tuple(self.context.events.events())):
            if event.get("event_type") != "student-sandbox.session-saved":
                continue
            result.append(event["payload"])
            if len(result) >= max(1, min(50, limit)):
                break
        return result
