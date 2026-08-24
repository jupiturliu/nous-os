"""Trading Proof evaluator capability Plugin."""

from __future__ import annotations

from functools import partial
from typing import Any

from nous_os.core.context import HarnessContext
from nous_os.evaluation.trading import TradingEvaluator


class TradingEvaluatorPlugin:
    id = "trading-evaluator"
    requires = ("evidence-store",)
    provides = ("domain-evaluator-factory",)
    effects = ("filesystem-read",)

    def start(self, context: HarnessContext, config: dict[str, Any]) -> None:
        workspace = config.get("workspace")
        username = config.get("username")
        if not workspace or not username:
            context.register("domain-evaluator-factory", TradingEvaluator)
            return
        context.register("domain-evaluator-factory", partial(TradingEvaluator, workspace, username))

    def stop(self, context: HarnessContext) -> None:
        context.unregister("domain-evaluator-factory")


plugin = TradingEvaluatorPlugin()
