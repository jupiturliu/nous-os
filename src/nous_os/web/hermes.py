"""Hermes Gateway Adapter for the Student Sandbox."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


MAX_MESSAGE_CHARS = 1200
DEFAULT_MODEL = "hermes-agent"
DEFAULT_URL = "http://127.0.0.1:8642/v1/chat/completions"


def load_local_env(path: Path | None = None) -> None:
    source = path or Path.home() / ".hermes" / ".env"
    if not source.exists():
        return
    for line in source.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))
    if "HERMES_API_SERVER_KEY" not in os.environ and "API_SERVER_KEY" in os.environ:
        os.environ["HERMES_API_SERVER_KEY"] = os.environ["API_SERVER_KEY"]


def resolve_url(env: dict[str, str] | os._Environ[str] = os.environ) -> str:
    direct = env.get("HERMES_API_SERVER_URL", "").strip()
    if direct:
        return direct
    gateway = env.get("HERMES_GATEWAY_URL", DEFAULT_URL.removesuffix("/v1/chat/completions")).rstrip("/")
    return f"{gateway}/v1/chat/completions"


def system_prompt() -> str:
    return "\n".join((
        "You are Hermes, the NOUS OS Student Sandbox learning agent.",
        "Preserve the gateway as the model/tool/provider seam.",
        "Help a student think better with AI while preserving human agency.",
        "Do not write the final answer, essay, or finished homework.",
        "Give hints, subquestions, source checks, boundaries, and reflection prompts.",
        "Do not request or store private student data.",
        "End with one concrete next action in the worksheet.",
    ))


def build_messages(message: str, body: dict[str, Any]) -> list[dict[str, str]]:
    worksheet = body.get("worksheet", {})
    compact = {key: str(worksheet.get(key, ""))[:limit] for key, limit in {
        "question": 500, "prior_belief": 500, "boundary": 300,
        "ai_plan_notes": 700, "source_notes": 700, "revised_plan": 700,
    }.items()}
    return [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": json.dumps({
            "student_message": message,
            "worksheet": compact,
            "sandbox_policy": body.get("policy", {}),
        }, ensure_ascii=False)},
    ]


def ask_hermes(body: dict[str, Any], env: dict[str, str] | os._Environ[str] = os.environ) -> dict[str, Any]:
    message = str(body.get("message", "")).strip()[:MAX_MESSAGE_CHARS]
    if not message:
        raise ValueError("Missing student message.")
    model = env.get("HERMES_API_SERVER_MODEL") or env.get("HERMES_GATEWAY_MODEL") or DEFAULT_MODEL
    headers = {"Content-Type": "application/json", "X-Hermes-Session-Key": "nous-os-student-sandbox-v1"}
    key = env.get("HERMES_API_SERVER_KEY") or env.get("HERMES_GATEWAY_API_KEY")
    if key:
        headers["Authorization"] = f"Bearer {key}"
    request = urllib.request.Request(resolve_url(env), method="POST", headers=headers, data=json.dumps({
        "model": model,
        "messages": build_messages(message, body),
        "temperature": 0.3,
        "max_tokens": 500,
        "stream": False,
    }).encode("utf-8"))
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.loads(response.read())
    except urllib.error.HTTPError as error:
        try:
            payload = json.loads(error.read())
        except Exception:
            payload = {}
        message = payload.get("error", {}).get("message") or "Hermes Gateway request failed."
        raise HermesGatewayError(error.code, message) from error
    choice = (payload.get("choices") or [{}])[0]
    content = choice.get("message", {}).get("content", "")
    if isinstance(content, list):
        content = "\n".join(str(part.get("text") or part.get("content") or "") for part in content)
    reply = str(content).strip() or "Hermes Gateway returned an empty reply. Try again with a shorter question."
    return {"reply": reply, "model": model, "agent": "hermes-student-agent", "route": "hermes-gateway"}


class HermesGatewayError(RuntimeError):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
