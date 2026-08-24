"""Run real Profiles and compare their privacy-safe observable snapshots."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable

from nous_os.core import Harness, HarnessContext, RuntimePaths, load_profile
from nous_os.core.project import find_project_root


SCHEMA_VERSION = 1
SNAPSHOT_NAMES = ("student", "research", "trading-proof")
FORBIDDEN_KEYS = frozenset({
    "body", "content", "credential", "credentials", "link", "markdown",
    "password", "secret", "summary", "token", "url", "webhook", "webhook_url",
})
PRIVATE_PATTERNS = (
    re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I),
    re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b"),
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"(?:https?|file)://", re.I),
    re.compile(r"(?:^|[\s\"'])/(?:Users|home|private|tmp|var)/"),
    re.compile(r"[A-Za-z]:\\"),
)


def replay_scenarios(
    root: Path | None = None,
    *,
    snapshot_dir: Path | None = None,
    record: bool = False,
) -> dict[str, dict[str, Any]]:
    """Run every canonical scenario and compare or record reviewed snapshots."""

    project = (root or find_project_root()).resolve()
    destination = snapshot_dir or project / "tests" / "snapshots"
    builders: dict[str, Callable[[Path, Path], dict[str, Any]]] = {
        "student": _student_scenario,
        "research": _research_scenario,
        "trading-proof": _trading_scenario,
    }
    observed: dict[str, dict[str, Any]] = {}
    with _without_external_credentials():
        for name in SNAPSHOT_NAMES:
            with tempfile.TemporaryDirectory(prefix=f"nous-os-{name}-") as directory:
                snapshot = builders[name](project, Path(directory))
            assert_snapshot_safe(snapshot)
            observed[name] = snapshot
            expected_path = destination / f"{name}.json"
            if record:
                expected_path.parent.mkdir(parents=True, exist_ok=True)
                expected_path.write_text(_json(snapshot), encoding="utf-8")
                continue
            if not expected_path.exists():
                raise FileNotFoundError(f"scenario snapshot does not exist: {expected_path}")
            expected = json.loads(expected_path.read_text(encoding="utf-8"))
            if snapshot != expected:
                raise AssertionError(
                    f"scenario snapshot changed: {name}; review with "
                    "nous-os check --mode full --record-snapshots"
                )
    return observed


def assert_snapshot_safe(snapshot: Any) -> None:
    """Reject private content, secret-shaped fields, endpoints, and machine paths."""

    def visit(value: Any, location: str) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                normalized = str(key).lower().replace("-", "_")
                if normalized in FORBIDDEN_KEYS or any(
                    token in normalized for token in ("password", "secret", "token", "webhook")
                ):
                    raise ValueError(f"unsafe snapshot field at {location}.{key}")
                visit(item, f"{location}.{key}")
            return
        if isinstance(value, (list, tuple)):
            for index, item in enumerate(value):
                visit(item, f"{location}[{index}]")
            return
        if isinstance(value, str):
            for pattern in PRIVATE_PATTERNS:
                if pattern.search(value):
                    raise ValueError(f"unsafe snapshot value at {location}")

    visit(snapshot, "snapshot")


def _student_scenario(root: Path, home: Path) -> dict[str, Any]:
    profile, context, harness, cli_output = _start(root, home, "student")
    try:
        record = context.resolve("student-sandbox").save({
            "session_id": "scenario-student-001",
            "worksheet": {
                "question": "Compare two explanations of photosynthesis.",
                "boundary": "Hints and source checks only; no final answer.",
                "revised_plan": "Check evidence, revise the outline, then reflect.",
            },
            "source_cards": [
                {
                    "id": "source-1",
                    "title": "Synthetic source card",
                    "author": "Scenario fixture",
                    "date": "2026-01-01",
                    "evidence": "A synthetic observation for deterministic verification.",
                    "uncertainty": "No external source was contacted.",
                    "decision": "accepted",
                }
            ],
            "reflection": {
                "reflect_help": "The outline became clearer.",
                "reflect_verify": "I still need a second source.",
                "reflect_responsibility": "The conclusion remains mine.",
                "reflect_next": "Compare the evidence.",
            },
        })
        world = {
            "saved_session": record["session_id"],
            "redaction_detected": record["privacy"]["private_pattern_detected"],
            "ready_for_second_pass": record["readiness"]["ready_for_second_pass"],
        }
        return _snapshot(profile.name, cli_output, context, world)
    finally:
        harness.stop()


def _research_scenario(root: Path, home: Path) -> dict[str, Any]:
    profile, context, harness, cli_output = _start(root, home, "research")
    try:
        runner = context.resolve("research-line")
        source = {
            "id": "fixture-feed",
            "title": "Scenario feed",
            "url": "fixture-feed",
            "bucket": "scenario",
        }
        capture_date, markdown = runner.capture(
            sources=[source],
            keywords=["human agency"],
            max_age_days=2,
            capture_date="2026-01-02",
            fetcher=lambda _: _fixture_feed(),
        )
        output = runner.write_inbox_file(capture_date, markdown, inbox_dir=context.paths.state / "scenario-inbox")
        world = {
            "capture_date": capture_date,
            "inbox_file": output.relative_to(context.paths.home).as_posix(),
            "inbox_exists": output.exists(),
            "notification_status": tuple(context.events.events())[-1]["payload"]["delivery_status"],
        }
        return _snapshot(profile.name, cli_output, context, world)
    finally:
        harness.stop()


def _trading_scenario(root: Path, home: Path) -> dict[str, Any]:
    profile, context, harness, cli_output = _start(root, home, "trading-proof")
    try:
        evaluator = context.resolve("domain-evaluator-factory")(home / "external", "scenario-user")
        result = evaluator.evaluate({"demo_mode": "trading_vertical"})
        world = {
            "evidence_refs": result["evidence_refs"],
            "all_components_zero": all(
                result[name] == 0.0
                for name in (
                    "boundary_integrity", "human_agency_preservation", "outcome_quality_delta",
                    "repeatability_gain", "correction_absorption", "memory_reuse_precision",
                )
            ),
        }
        return _snapshot(profile.name, cli_output, context, world)
    finally:
        harness.stop()


def _start(root: Path, home: Path, name: str):
    profile = load_profile(root / "config" / "profiles" / f"{name}.yaml")
    cli_output = _profile_cli_output(root, home, name)
    context = HarnessContext(profile_name=profile.name, paths=RuntimePaths.resolve(home))
    harness = Harness(profile, context).start()
    return profile, context, harness, cli_output


def _profile_cli_output(root: Path, home: Path, name: str) -> str:
    environment = os.environ.copy()
    source = str(root / "src")
    environment["PYTHONPATH"] = source + (os.pathsep + environment["PYTHONPATH"] if environment.get("PYTHONPATH") else "")
    completed = subprocess.run(
        (
            sys.executable, "-m", "nous_os", "--runtime-home", str(home),
            "validate", "profile", "--profile", name,
        ),
        cwd=root,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"Profile CLI failed for {name}: {completed.stderr.strip()}")
    return completed.stdout.strip()


def _snapshot(profile_name: str, cli_output: str, context: HarnessContext, world: dict[str, Any]) -> dict[str, Any]:
    events = []
    artifacts: dict[tuple[str, str], dict[str, Any]] = {}
    for event in context.events.events():
        normalized_payload = _normalize(event.get("payload", {}))
        events.append({
            "event_type": event["event_type"],
            "profile": event["profile"],
            "producer": event["producer"],
            "privacy": event["privacy"],
            "payload": normalized_payload,
        })
        for reference in event.get("evidence_refs", []):
            path = context.paths.home / reference["path"]
            key = (reference["kind"], reference["path"])
            artifacts[key] = {
                "kind": reference["kind"],
                "path": _normalize_artifact_path(reference["path"]),
                "sha256": "<sha256>",
                "exists": path.is_file(),
                "mode": f"{path.stat().st_mode & 0o777:03o}" if path.exists() else None,
            }
    projections = sorted(
        path.relative_to(context.paths.home).as_posix()
        for path in context.paths.projections.rglob("*")
        if path.is_file()
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "profile": profile_name,
        "cli_output": cli_output,
        "events": events,
        "artifacts": list(artifacts.values()),
        "projections": projections,
        "world": _normalize(world),
    }


def _normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: ("<timestamp>" if key in {"saved_at", "occurred_at", "created_at"} else _normalize(item))
            for key, item in sorted(value.items())
        }
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    if isinstance(value, tuple):
        return [_normalize(item) for item in value]
    return value


def _normalize_artifact_path(value: str) -> str:
    path = Path(value)
    return (path.parent / "<artifact-id>.json").as_posix()


def _fixture_feed() -> bytes:
    return b"""<?xml version="1.0"?><rss><channel><item>
      <title>Fixture observation</title><link>fixture-entry</link>
      <pubDate>Fri, 02 Jan 2026 12:00:00 GMT</pubDate>
      <description>A synthetic human agency observation.</description>
    </item></channel></rss>"""


@contextmanager
def _without_external_credentials():
    names = ("NOUS_OS_RESEARCH_NOTIFICATION_WEBHOOK_URL", "HERMES_API_KEY", "OPENAI_API_KEY")
    previous = {name: os.environ.pop(name, None) for name in names}
    try:
        yield
    finally:
        for name, value in previous.items():
            if value is not None:
                os.environ[name] = value


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Replay canonical NOUS OS Harness scenarios")
    parser.add_argument("--record", action="store_true", help="write reviewed expected snapshots")
    parser.add_argument("--snapshot-dir", type=Path)
    args = parser.parse_args(argv)
    observed = replay_scenarios(snapshot_dir=args.snapshot_dir, record=args.record)
    print(_json({"ok": True, "recorded": args.record, "scenarios": list(observed)}), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
