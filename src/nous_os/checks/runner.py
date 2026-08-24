"""Validated Gate graphs with bounded scheduling and stable diagnostics."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Mapping


CHECK_MODES = ("quick", "full", "ci", "release")
TERMINAL_STATUSES = frozenset({"passed", "failed", "skipped"})


@dataclass(frozen=True)
class Gate:
    """One command and its dependencies inside a named check mode."""

    id: str
    label: str
    command: tuple[str, ...]
    needs: tuple[str, ...] = ()
    env: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ProcessOutcome:
    """Independent subprocess outcomes; none is hidden behind another."""

    exit_code: int | None
    stdout: str = ""
    stderr: str = ""
    signal: int | None = None
    error: str | None = None


@dataclass(frozen=True)
class GateResult:
    gate_id: str
    label: str
    status: str
    duration_ms: int
    exit_code: int | None
    signal: int | None
    stdout: str = ""
    stderr: str = ""
    error: str | None = None
    skipped_because: tuple[str, ...] = ()

    def as_dict(self) -> dict:
        result = {
            "id": self.gate_id,
            "label": self.label,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "exit_code": self.exit_code,
            "signal": self.signal,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "error": self.error,
        }
        if self.skipped_because:
            result["skipped_because"] = list(self.skipped_because)
        return result


@dataclass(frozen=True)
class CheckReport:
    mode: str
    status: str
    duration_ms: int
    results: tuple[GateResult, ...]

    @property
    def ok(self) -> bool:
        return self.status == "passed"

    def as_dict(self) -> dict:
        return {
            "schema_version": 1,
            "mode": self.mode,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "summary": {
                status: sum(result.status == status for result in self.results)
                for status in ("passed", "failed", "skipped")
            },
            "gates": [result.as_dict() for result in self.results],
        }


GateExecutor = Callable[[Gate], ProcessOutcome]


def gates_for_mode(mode: str, *, record_snapshots: bool = False) -> tuple[Gate, ...]:
    """Return the canonical Gate graph for one public mode."""

    if mode not in CHECK_MODES:
        raise ValueError(f"check mode must be one of: {', '.join(CHECK_MODES)}")
    if record_snapshots and mode not in {"full", "ci", "release"}:
        raise ValueError("--record-snapshots requires full, ci, or release mode")

    python = sys.executable
    harness = Gate("harness", "Harness contracts", (python, "-m", "nous_os", "validate", "harness"))
    contracts = Gate("contracts", "Domain contracts", (python, "-m", "nous_os", "validate", "contracts"))
    site = Gate(
        "site",
        "Static site staging",
        (python, "-m", "nous_os", "site", "stage", "--destination", "{project_root}/_site/check"),
        needs=("harness",),
    )
    profiles = tuple(
        Gate(
            f"profile-{name}",
            f"Profile {name}",
            (python, "-m", "nous_os", "validate", "profile", "--profile", name),
            needs=("harness",),
        )
        for name in ("student", "research", "trading-proof")
    )
    quick = (harness, contracts, site, *profiles)
    if mode == "quick":
        return quick

    scenario_command = [python, "-m", "nous_os.scenarios.replay"]
    if record_snapshots:
        scenario_command.append("--record")
    scenarios = Gate(
        "scenarios",
        "Assembled Profile scenarios",
        tuple(scenario_command),
        needs=tuple(gate.id for gate in profiles),
    )
    unit = Gate(
        "unit-tests",
        "Python unit tests",
        (python, "-m", "unittest", "discover", "-s", "tests", "-v"),
        needs=("harness", "contracts", "site", "scenarios") if record_snapshots else ("harness", "contracts", "site"),
    )
    full = (*quick, scenarios, unit)
    if mode == "full":
        return full

    if record_snapshots:
        ci = full
    else:
        clean = Gate(
            "source-clean",
            "Source checkout unchanged",
            ("git", "diff", "--exit-code"),
            needs=("scenarios", "unit-tests"),
        )
        ci = (*full, clean)
    if mode == "ci":
        return ci

    release_needs = (ci[-1].id,)
    entrypoint = Gate(
        "entrypoint",
        "Installed CLI entry path",
        ("nous-os", "--help"),
        needs=release_needs,
    )
    return (*ci, entrypoint)


def run_check(
    root: Path,
    mode: str,
    *,
    max_workers: int | None = None,
    record_snapshots: bool = False,
    runtime_home: Path | str | None = None,
) -> CheckReport:
    """Run one named repository check mode from its source root."""

    root = root.resolve()
    gates = gates_for_mode(mode, record_snapshots=record_snapshots)
    started = time.monotonic()
    temporary_home = tempfile.TemporaryDirectory(prefix="nous-os-check-") if runtime_home is None else None
    selected_home = Path(temporary_home.name if temporary_home else runtime_home).resolve()

    def execute(gate: Gate) -> ProcessOutcome:
        environment = os.environ.copy()
        source = str(root / "src")
        existing = environment.get("PYTHONPATH")
        environment["PYTHONPATH"] = source if not existing else os.pathsep.join((source, existing))
        environment["NOUS_OS_HOME"] = str(selected_home)
        environment.update(gate.env)
        try:
            command = tuple(
                argument.replace("{project_root}", str(root)).replace("{runtime_home}", str(selected_home))
                for argument in gate.command
            )
            completed = subprocess.run(
                command,
                cwd=root,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )
        except OSError as error:
            return ProcessOutcome(None, error=f"{type(error).__name__}: {error}")
        signal = -completed.returncode if completed.returncode < 0 else None
        exit_code = completed.returncode if completed.returncode >= 0 else None
        return ProcessOutcome(
            exit_code,
            _normalize_diagnostics(completed.stdout, root, selected_home),
            _normalize_diagnostics(completed.stderr, root, selected_home),
            signal,
        )

    try:
        results = run_gates(gates, execute, max_workers=max_workers)
        status = "passed" if all(result.status == "passed" for result in results) else "failed"
        return CheckReport(mode, status, _milliseconds_since(started), results)
    finally:
        if temporary_home is not None:
            temporary_home.cleanup()


def run_gates(
    gates: Iterable[Gate],
    executor: GateExecutor,
    *,
    max_workers: int | None = None,
) -> tuple[GateResult, ...]:
    """Validate and execute a Gate dependency graph with bounded concurrency."""

    ordered = tuple(gates)
    _validate_graph(ordered)
    if not ordered:
        return ()
    if max_workers is not None and max_workers < 1:
        raise ValueError("max_workers must be a positive integer")
    worker_count = max_workers if max_workers is not None else min(4, len(ordered), os.cpu_count() or 1)

    by_id = {gate.id: gate for gate in ordered}
    pending = set(by_id)
    results: dict[str, GateResult] = {}
    running: dict[Future[GateResult], str] = {}

    with ThreadPoolExecutor(max_workers=worker_count, thread_name_prefix="nous-os-gate") as pool:
        while pending or running:
            progressed = False
            for gate in ordered:
                if gate.id not in pending:
                    continue
                failed_needs = tuple(
                    need for need in gate.needs
                    if need in results and results[need].status != "passed"
                )
                if failed_needs:
                    results[gate.id] = GateResult(
                        gate.id,
                        gate.label,
                        "skipped",
                        0,
                        None,
                        None,
                        skipped_because=failed_needs,
                    )
                    pending.remove(gate.id)
                    progressed = True
                    continue
                if all(need in results for need in gate.needs) and len(running) < worker_count:
                    future = pool.submit(_run_gate, gate, executor)
                    running[future] = gate.id
                    pending.remove(gate.id)
                    progressed = True
            if running:
                completed, _ = wait(tuple(running), return_when=FIRST_COMPLETED)
                for future in completed:
                    gate_id = running.pop(future)
                    results[gate_id] = future.result()
                continue
            if pending and not progressed:
                raise RuntimeError("Gate scheduler made no progress")

    return tuple(results[gate.id] for gate in ordered)


def _run_gate(gate: Gate, executor: GateExecutor) -> GateResult:
    started = time.monotonic()
    try:
        outcome = executor(gate)
    except Exception as error:  # A Gate implementation defect is reported, not raised across the scheduler.
        outcome = ProcessOutcome(None, error=f"{type(error).__name__}: {error}")
    status = "passed" if outcome.exit_code == 0 and outcome.signal is None and outcome.error is None else "failed"
    return GateResult(
        gate.id,
        gate.label,
        status,
        _milliseconds_since(started),
        outcome.exit_code,
        outcome.signal,
        outcome.stdout,
        outcome.stderr,
        outcome.error,
    )


def _validate_graph(gates: tuple[Gate, ...]) -> None:
    ids = [gate.id for gate in gates]
    if any(not gate_id or gate_id.strip() != gate_id for gate_id in ids):
        raise ValueError("Gate ids must be non-empty and whitespace-trimmed")
    if len(set(ids)) != len(ids):
        raise ValueError("Gate ids must be unique")
    known = set(ids)
    for gate in gates:
        unknown = set(gate.needs) - known
        if unknown:
            raise ValueError(f"Gate {gate.id!r} has unknown dependencies: {', '.join(sorted(unknown))}")
        if gate.id in gate.needs:
            raise ValueError(f"Gate {gate.id!r} cannot depend on itself")

    visiting: set[str] = set()
    visited: set[str] = set()
    by_id = {gate.id: gate for gate in gates}

    def visit(gate_id: str) -> None:
        if gate_id in visiting:
            raise ValueError("Gate dependency cycle detected")
        if gate_id in visited:
            return
        visiting.add(gate_id)
        for dependency in by_id[gate_id].needs:
            visit(dependency)
        visiting.remove(gate_id)
        visited.add(gate_id)

    for gate_id in ids:
        visit(gate_id)


def _milliseconds_since(started: float) -> int:
    return max(0, round((time.monotonic() - started) * 1000))


def _normalize_diagnostics(value: str, root: Path, runtime_home: Path) -> str:
    """Keep Gate reports useful without embedding machine-specific roots."""

    replacements = sorted(
        ((str(runtime_home), "<runtime-home>"), (str(root), "<project-root>")),
        key=lambda item: len(item[0]),
        reverse=True,
    )
    result = value
    for source, replacement in replacements:
        result = result.replace(source, replacement)
    return result
