"""Profile Permission Policy capability Plugin."""

from __future__ import annotations

from typing import Any

from nous_os.core.context import HarnessContext


class PermissionPolicyPlugin:
    id = "permission-policy"
    requires: tuple[str, ...] = ()
    provides = ("permission-policy",)
    effects: tuple[str, ...] = ()

    def start(self, context: HarnessContext, config: dict[str, Any]) -> None:
        if config:
            raise ValueError("permission-policy Plugin has no configuration fields")
        context.register("permission-policy", context.permission_policy)

    def stop(self, context: HarnessContext) -> None:
        context.unregister("permission-policy")


plugin = PermissionPolicyPlugin()
