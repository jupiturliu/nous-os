"""Plugin lifecycle and deterministic capability composition."""

from __future__ import annotations

import importlib
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from nous_os.assurance import InvariantViolation
from nous_os.security import ProfilePermissionPolicy

from .context import HarnessContext
from .profiles import Profile


@runtime_checkable
class Plugin(Protocol):
    id: str
    requires: tuple[str, ...]
    provides: tuple[str, ...]
    effects: tuple[str, ...]

    def start(self, context: HarnessContext, config: dict[str, Any]) -> None: ...

    def stop(self, context: HarnessContext) -> None: ...


@dataclass(frozen=True)
class LifecycleFailure:
    plugin_id: str
    phase: str
    error_class: str


class HarnessStopError(RuntimeError):
    code = "HARNESS_STOP"

    def __init__(self, failures: tuple[LifecycleFailure, ...]):
        self.failures = failures
        facts = ", ".join(f"{item.plugin_id}:{item.phase}:{item.error_class}" for item in failures)
        super().__init__(f"{self.code}: {facts}")


class Harness:
    def __init__(self, profile: Profile, context: HarnessContext):
        self.profile = profile
        self.context = context
        if profile.schema_version != 2:
            raise ValueError("Harness requires Profile schema_version 2")
        self.context.permission_policy = ProfilePermissionPolicy(profile.allowed_effects)
        self._started: list[tuple[str, Plugin]] = []
        self._order: tuple[str, ...] = ()
        self._plugins: dict[str, tuple[Plugin, dict[str, Any]]] = {}

    def start(self) -> "Harness":
        if self._started or self.context.readiness()["status"] == "ready":
            raise RuntimeError("Harness is already started")
        plugins = {config.id: (_load_plugin(config.module), config.config) for config in self.profile.plugins}
        if len(plugins) != len(self.profile.plugins):
            raise ValueError("profile contains duplicate plugin ids")
        providers: dict[str, str] = {}
        for plugin_id, (plugin, _) in plugins.items():
            if plugin.id != plugin_id:
                raise ValueError(f"profile id {plugin_id!r} does not match plugin id {plugin.id!r}")
            self.context.permission_policy.authorize(plugin_id, plugin.effects)
            for capability in plugin.provides:
                if capability in providers:
                    raise ValueError(f"duplicate capability provider: {capability}")
                providers[capability] = plugin_id
        dependencies: dict[str, set[str]] = defaultdict(set)
        for plugin_id, (plugin, _) in plugins.items():
            for capability in plugin.requires:
                provider = providers.get(capability)
                if provider is None:
                    raise ValueError(f"missing capability {capability!r} required by {plugin_id!r}")
                dependencies[plugin_id].add(provider)
        order: list[str] = []
        remaining = set(plugins)
        while remaining:
            ready = sorted(item for item in remaining if not (dependencies[item] & remaining))
            if not ready:
                raise ValueError("plugin dependency cycle detected")
            order.extend(ready)
            remaining.difference_update(ready)
        self._order = tuple(order)
        self._plugins = plugins
        self.context.mark_starting()
        try:
            for plugin_id in order:
                plugin, config = plugins[plugin_id]
                self._started.append((plugin_id, plugin))
                started = time.monotonic()
                plugin.start(self.context, config)
                missing = [name for name in plugin.provides if name not in self.context._capabilities]
                if missing:
                    raise RuntimeError(f"plugin {plugin_id!r} did not register: {', '.join(missing)}")
                self.context.emit_telemetry(
                    "plugin-start", "start", "passed", plugin_id=plugin_id,
                    duration_ms=_duration_ms(started),
                )
            self.context.run_invariants("after-start")
            self.context.mark_ready()
        except Exception as error:
            cleanup_failures = self._stop(run_invariants=False, raise_errors=False)
            if cleanup_failures:
                error.cleanup_failures = cleanup_failures
            self.context.mark_failed(_failure_reason(error))
            raise
        return self

    def check(self) -> tuple[str, ...]:
        try:
            executed = self.context.run_invariants("workflow-complete")
        except InvariantViolation as error:
            self.context.mark_unready(f"invariant:{error.owner}.{error.invariant}")
            self.context.emit_telemetry("invariant", "run", "failed", error_class=type(error).__name__)
            raise
        self.context.emit_telemetry("invariant", "run", "passed")
        return executed

    def stop(self) -> None:
        self._stop(run_invariants=True, raise_errors=True)

    def _stop(self, *, run_invariants: bool, raise_errors: bool) -> tuple[LifecycleFailure, ...]:
        if not self._started:
            if self.context.readiness()["status"] not in {"failed", "stopped"}:
                self.context.mark_stopped()
            return ()
        self.context.mark_stopping()
        failures: list[LifecycleFailure] = []
        if run_invariants:
            try:
                self.context.run_invariants("before-stop")
            except Exception as error:
                failures.append(LifecycleFailure("harness", "before-stop", type(error).__name__))
                self.context.emit_telemetry("invariant", "before-stop", "failed", error_class=type(error).__name__)
        while self._started:
            plugin_id, plugin = self._started.pop()
            started = time.monotonic()
            try:
                plugin.stop(self.context)
                outcome = "passed"
                error_class = None
            except Exception as error:
                outcome = "failed"
                error_class = type(error).__name__
                failures.append(LifecycleFailure(plugin_id, "stop", error_class))
            finally:
                for capability in plugin.provides:
                    self.context.unregister(capability)
                self.context.emit_telemetry(
                    "plugin-stop", "stop", outcome, plugin_id=plugin_id,
                    duration_ms=_duration_ms(started), error_class=error_class,
                )
        self.context.clear_capabilities()
        self.context.mark_stopped()
        if failures and raise_errors:
            raise HarnessStopError(tuple(failures))
        return tuple(failures)

    def diagnose(self) -> dict[str, Any]:
        credentials = self.context.resolve("credential-provider") if self.context.has("credential-provider") else None
        references = []
        if credentials is not None:
            for plugin_id in self._order:
                config = self._plugins[plugin_id][1]
                for key, value in sorted(config.items()):
                    if key.endswith("_ref") and isinstance(value, str):
                        from nous_os.security import CredentialRef
                        info = credentials.describe(CredentialRef(value))
                        references.append({
                            "plugin": plugin_id,
                            "reference": value,
                            "configured": info.configured,
                            "source": info.source,
                            "writable": info.writable,
                        })
        registry = self.context.resolve("invariants") if self.context.has("invariants") else None
        telemetry = self.context.resolve("telemetry") if self.context.has("telemetry") else None
        return {
            "schema_version": 1,
            "profile": {"name": self.profile.name, "schema_version": self.profile.schema_version},
            "plugin_order": [
                {
                    "id": plugin_id,
                    "effects": list(self._plugins[plugin_id][0].effects),
                    "provides": list(self._plugins[plugin_id][0].provides),
                }
                for plugin_id in self._order
            ],
            "allowed_effects": list(self.context.permission_policy.allowed_effects),
            "capabilities": list(self.context.capability_names()),
            "invariants": [item.as_dict() for item in registry.registrations()] if registry else [],
            "runtime_home": {
                "location": "<runtime-home>",
                "ready": self.context.paths.home.is_dir(),
                "directories": {
                    name: path.is_dir()
                    for name, path in (
                        ("artifacts", self.context.paths.artifacts),
                        ("cache", self.context.paths.cache),
                        ("projections", self.context.paths.projections),
                        ("state", self.context.paths.state),
                    )
                },
            },
            "credentials": references,
            "telemetry": telemetry.describe() if telemetry else {"mode": "unavailable"},
            "readiness": self.context.readiness(),
        }


def _load_plugin(module_name: str) -> Plugin:
    module = importlib.import_module(module_name)
    plugin = getattr(module, "plugin", None)
    if plugin is None or not isinstance(plugin, Plugin):
        raise ValueError(f"module {module_name!r} does not export a valid plugin")
    return plugin


def _duration_ms(started: float) -> int:
    return max(0, round((time.monotonic() - started) * 1000))


def _failure_reason(error: Exception) -> str:
    if isinstance(error, InvariantViolation):
        return f"invariant:{error.owner}.{error.invariant}"
    return type(error).__name__
