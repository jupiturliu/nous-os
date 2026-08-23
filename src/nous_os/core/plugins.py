"""Plugin lifecycle and deterministic capability composition."""

from __future__ import annotations

import importlib
from collections import defaultdict
from typing import Any, Protocol, runtime_checkable

from .context import HarnessContext
from .profiles import Profile


@runtime_checkable
class Plugin(Protocol):
    id: str
    requires: tuple[str, ...]
    provides: tuple[str, ...]

    def start(self, context: HarnessContext, config: dict[str, Any]) -> None: ...

    def stop(self, context: HarnessContext) -> None: ...


class Harness:
    def __init__(self, profile: Profile, context: HarnessContext):
        self.profile = profile
        self.context = context
        self._started: list[Plugin] = []

    def start(self) -> "Harness":
        plugins = {config.id: (_load_plugin(config.module), config.config) for config in self.profile.plugins}
        if len(plugins) != len(self.profile.plugins):
            raise ValueError("profile contains duplicate plugin ids")
        providers: dict[str, str] = {}
        for plugin_id, (plugin, _) in plugins.items():
            if plugin.id != plugin_id:
                raise ValueError(f"profile id {plugin_id!r} does not match plugin id {plugin.id!r}")
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
        try:
            for plugin_id in order:
                plugin, config = plugins[plugin_id]
                plugin.start(self.context, config)
                missing = [name for name in plugin.provides if name not in self.context._capabilities]
                if missing:
                    raise RuntimeError(f"plugin {plugin_id!r} did not register: {', '.join(missing)}")
                self._started.append(plugin)
        except Exception:
            self.stop()
            raise
        return self

    def stop(self) -> None:
        while self._started:
            self._started.pop().stop(self.context)


def _load_plugin(module_name: str) -> Plugin:
    module = importlib.import_module(module_name)
    plugin = getattr(module, "plugin", None)
    if plugin is None or not isinstance(plugin, Plugin):
        raise ValueError(f"module {module_name!r} does not export a valid plugin")
    return plugin
