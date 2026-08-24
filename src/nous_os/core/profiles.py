"""Strict YAML Profile loader."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from nous_os.security.permissions import ProfilePermissionPolicy


@dataclass(frozen=True)
class PluginConfig:
    id: str
    module: str
    config: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Profile:
    schema_version: int
    name: str
    plugins: tuple[PluginConfig, ...]
    workflows: tuple[str, ...] = ()
    web: dict[str, Any] = field(default_factory=dict)
    allowed_effects: tuple[str, ...] = ()


def load_profile(path: str | Path) -> Profile:
    source = Path(path)
    raw = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("profile must be a YAML mapping")
    allowed = {"schema_version", "name", "plugins", "workflows", "web", "allowed_effects"}
    unknown = set(raw) - allowed
    if unknown:
        raise ValueError(f"unknown profile fields: {', '.join(sorted(unknown))}")
    if raw.get("schema_version") == 1:
        raise ValueError("Profile schema_version 1 must migrate: add allowed_effects and set schema_version to 2")
    if raw.get("schema_version") != 2:
        raise ValueError("profile schema_version must be 2")
    name = raw.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("profile name must be a non-empty string")
    plugin_values = raw.get("plugins", [])
    if not isinstance(plugin_values, list):
        raise ValueError("profile plugins must be a list")
    plugins: list[PluginConfig] = []
    for index, value in enumerate(plugin_values):
        if not isinstance(value, dict) or set(value) - {"id", "module", "config"}:
            raise ValueError(f"invalid plugin configuration at index {index}")
        if not isinstance(value.get("id"), str) or not isinstance(value.get("module"), str):
            raise ValueError(f"plugin id and module must be strings at index {index}")
        config = value.get("config", {})
        if not isinstance(config, dict):
            raise ValueError(f"plugin config must be a mapping at index {index}")
        plugins.append(PluginConfig(value["id"], value["module"], config))
    workflows = raw.get("workflows", [])
    if not isinstance(workflows, list) or not all(isinstance(item, str) for item in workflows):
        raise ValueError("profile workflows must be a list of strings")
    web = raw.get("web", {})
    if not isinstance(web, dict):
        raise ValueError("profile web must be a mapping")
    allowed_effects = raw.get("allowed_effects")
    if not isinstance(allowed_effects, list) or not all(isinstance(item, str) for item in allowed_effects):
        raise ValueError("profile allowed_effects must be a list of strings")
    policy = ProfilePermissionPolicy(allowed_effects)
    return Profile(2, name.strip(), tuple(plugins), tuple(workflows), web, policy.allowed_effects)
