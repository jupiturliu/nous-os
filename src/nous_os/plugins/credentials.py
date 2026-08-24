"""Environment Credential Provider capability Plugin."""

from __future__ import annotations

from typing import Any

from nous_os.core.context import HarnessContext
from nous_os.security import EnvironmentCredentialProvider


class CredentialsPlugin:
    id = "credentials"
    requires = ("permission-policy",)
    provides = ("credential-provider",)
    effects: tuple[str, ...] = ()

    def start(self, context: HarnessContext, config: dict[str, Any]) -> None:
        if config:
            raise ValueError("credentials Plugin has no configuration fields")
        context.register("credential-provider", EnvironmentCredentialProvider())

    def stop(self, context: HarnessContext) -> None:
        context.unregister("credential-provider")


plugin = CredentialsPlugin()
