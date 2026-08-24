"""Evidence capability Plugin."""

from __future__ import annotations

import hashlib
from typing import Any

from nous_os.core.context import HarnessContext


class EvidencePlugin:
    id = "evidence"
    requires = ("permission-policy", "invariants", "telemetry")
    provides = ("evidence-store",)
    effects = ("filesystem-write",)

    def start(self, context: HarnessContext, config: dict[str, Any]) -> None:
        context.register("evidence-store", context.events)
        context.resolve("invariants").register(
            self.id,
            "artifact-references-resolve",
            ("workflow-complete", "before-stop"),
            lambda: _validate_artifact_references(context),
        )

    def stop(self, context: HarnessContext) -> None:
        context.unregister("evidence-store")


plugin = EvidencePlugin()


def _validate_artifact_references(context: HarnessContext) -> str | None:
    """Check the observable Event-to-Artifact relationship without exposing content."""

    for event_index, event in enumerate(context.events.events(), 1):
        for reference_index, reference in enumerate(event.get("evidence_refs") or (), 1):
            relative = reference.get("path")
            if not isinstance(relative, str):
                return f"event {event_index} reference {reference_index} has no relative path"
            path = (context.paths.home / relative).resolve()
            if context.paths.home != path and context.paths.home not in path.parents:
                return f"event {event_index} reference {reference_index} escapes Runtime Home"
            if not path.is_file():
                return f"event {event_index} reference {reference_index} is missing"
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != reference.get("sha256"):
                return f"event {event_index} reference {reference_index} digest differs"
    return None
