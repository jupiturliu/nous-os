"""Read-only DomainEvaluator for trading-agent proof artifacts.

Implements the DomainEvaluator contract from
docs/domain-evaluator-interface.md by consuming existing trading-agent
artifacts under data/users/<username>/{market_proof,promotion_reviews}/.

Hard boundary (do not violate):
- pure read; the evaluator opens no write handles anywhere
- no import of trading-agent modules; filesystem access only
- no broker / order / risk / promotion / live-state mutation
- evidence_refs contain stable file pointers only — no secrets, no live state

Mapped CLS v2 components:
- boundary_integrity        -> fraction of artifacts whose execution_boundary
                               block attests zero live effect
- human_agency_preservation -> fraction of proof_packs where
                               capital_action_authorized is False
- outcome_quality_delta     -> rate of outperformed_benchmark over resolved
                               (non neutral_no_entry) baseline comparisons
- repeatability_gain        -> clamp(brier_improvement_over_baseline, 0, 1)
                               from forecast_ledger_summary.json
- correction_absorption     -> fraction of proof_packs where the system
                               flagged human_review_required AND filed a
                               concrete required_human_decision string
- memory_reuse_precision    -> average per-pack
                               validated_claims / (validated_claims +
                               missing_evidence) across packs that carry
                               either signal

Components that cannot be computed from the available artifacts still
return 0.0 with an explicit ``pending:<name>`` marker in evidence_refs.
This follows the ground-truth-first principle: unimplemented or
unmeasurable signals must be visible, not papered over with optimistic
defaults.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


CLS_V2_FIELDS = (
    "outcome_quality_delta",
    "correction_absorption",
    "memory_reuse_precision",
    "repeatability_gain",
    "boundary_integrity",
    "human_agency_preservation",
)

_HUMAN_HANDOFF_BLOCKING_STATES = ("human_review_required",)

_BOUNDARY_FLAGS_MUST_BE_FALSE = (
    "broker_action_allowed",
    "creates_order_or_draft",
    "creates_promotion_or_approval",
    "mutates_runtime_live_state",
    "production_config_changed",
)


class TradingEvaluator:
    """Map trading-agent proof artifacts into CLS v2 components.

    Args:
        workspace: directory containing a ``trading-agent/`` repo sibling.
        username: account namespace under
            ``trading-agent/data/users/<username>/`` to evaluate.
    """

    def __init__(self, workspace: Path | str, username: str) -> None:
        self.workspace = Path(workspace)
        self.username = username
        self._user_root = (
            self.workspace
            / "trading-agent"
            / "data"
            / "users"
            / username
        )

    def evaluate(self, run_context: dict, outcome_artifacts: dict | None = None) -> dict:
        if not self._user_root.exists():
            return self._empty_result(reason="missing:trading_agent_workspace")

        proof_packs = list(self._load_proof_packs())
        if not proof_packs:
            return self._empty_result(reason="missing:proof_packs")

        comparisons = self._load_baseline_comparisons()
        summary = self._load_forecast_summary()

        outcome_quality_delta, outcome_resolved = self._outcome_quality_delta(comparisons)
        repeatability_gain, repeatability_available = self._repeatability_gain(summary)
        correction_absorption, correction_available = self._correction_absorption(proof_packs)
        memory_reuse_precision, memory_available = self._memory_reuse_precision(proof_packs)

        evidence_refs = self._evidence_refs(proof_packs)
        evidence_refs.extend(self._market_evidence_refs(outcome_resolved, repeatability_available))
        if not outcome_resolved:
            evidence_refs.append("pending:outcome_quality_delta")
        if not repeatability_available:
            evidence_refs.append("pending:repeatability_gain")
        if not correction_available:
            evidence_refs.append("pending:correction_absorption")
        if not memory_available:
            evidence_refs.append("pending:memory_reuse_precision")

        result = {field: 0.0 for field in CLS_V2_FIELDS}
        result["boundary_integrity"] = self._boundary_integrity(proof_packs)
        result["human_agency_preservation"] = self._human_agency_preservation(proof_packs)
        result["outcome_quality_delta"] = outcome_quality_delta
        result["repeatability_gain"] = repeatability_gain
        result["correction_absorption"] = correction_absorption
        result["memory_reuse_precision"] = memory_reuse_precision
        result["evidence_refs"] = evidence_refs
        return result

    def _empty_result(self, *, reason: str) -> dict:
        return {
            **{field: 0.0 for field in CLS_V2_FIELDS},
            "evidence_refs": [reason],
        }

    def _proof_packs_dir(self) -> Path:
        return self._user_root / "promotion_reviews" / "proof_packs"

    def _load_proof_packs(self) -> Iterable[tuple[Path, dict]]:
        directory = self._proof_packs_dir()
        if not directory.exists():
            return []
        packs = []
        for path in sorted(directory.glob("*.json")):
            if path.name == "index.json":
                continue
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    pack = json.load(fh)
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(pack, dict):
                continue
            if "candidate_id" not in pack and "experiment_id" not in pack:
                continue
            packs.append((path, pack))
        return packs

    def _boundary_integrity(self, proof_packs: list[tuple[Path, dict]]) -> float:
        if not proof_packs:
            return 0.0
        clean = 0
        for _, pack in proof_packs:
            boundary = pack.get("execution_boundary", {})
            if all(boundary.get(flag) is False for flag in _BOUNDARY_FLAGS_MUST_BE_FALSE):
                clean += 1
        return round(clean / len(proof_packs), 4)

    def _human_agency_preservation(self, proof_packs: list[tuple[Path, dict]]) -> float:
        if not proof_packs:
            return 0.0
        preserved = sum(
            1 for _, pack in proof_packs if pack.get("capital_action_authorized") is False
        )
        return round(preserved / len(proof_packs), 4)

    def _load_baseline_comparisons(self) -> list[dict]:
        path = self._user_root / "market_proof" / "baseline_comparisons.jsonl"
        if not path.exists():
            return []
        rows: list[dict] = []
        try:
            with open(path, "r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rows.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except OSError:
            return []
        return rows

    def _load_forecast_summary(self) -> dict | None:
        path = self._user_root / "market_proof" / "forecast_ledger_summary.json"
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (OSError, json.JSONDecodeError):
            return None

    def _outcome_quality_delta(self, comparisons: list[dict]) -> tuple[float, bool]:
        resolved = [
            row for row in comparisons
            if row.get("outcome_label") and row["outcome_label"] != "neutral_no_entry"
        ]
        if not resolved:
            return 0.0, False
        wins = sum(1 for row in resolved if row.get("outperformed_benchmark") is True)
        return round(wins / len(resolved), 4), True

    def _repeatability_gain(self, summary: dict | None) -> tuple[float, bool]:
        if not summary or "brier_improvement_over_baseline" not in summary:
            return 0.0, False
        raw = summary.get("brier_improvement_over_baseline")
        if not isinstance(raw, (int, float)):
            return 0.0, False
        clamped = max(0.0, min(1.0, float(raw)))
        return round(clamped, 4), True

    def _correction_absorption(self, proof_packs: list[tuple[Path, dict]]) -> tuple[float, bool]:
        if not proof_packs:
            return 0.0, False
        absorbed = 0
        for _, pack in proof_packs:
            blocking = pack.get("blocking_states") or []
            decision = pack.get("required_human_decision")
            handed_to_human = any(state in _HUMAN_HANDOFF_BLOCKING_STATES for state in blocking)
            has_decision = isinstance(decision, str) and decision.strip()
            if handed_to_human and has_decision:
                absorbed += 1
        return round(absorbed / len(proof_packs), 4), True

    def _memory_reuse_precision(self, proof_packs: list[tuple[Path, dict]]) -> tuple[float, bool]:
        if not proof_packs:
            return 0.0, False
        ratios: list[float] = []
        for _, pack in proof_packs:
            validated = pack.get("validated_claims")
            missing = pack.get("missing_evidence")
            validated_count = len(validated) if isinstance(validated, list) else 0
            missing_count = len(missing) if isinstance(missing, list) else 0
            total = validated_count + missing_count
            if total == 0:
                continue
            ratios.append(validated_count / total)
        if not ratios:
            return 0.0, False
        return round(sum(ratios) / len(ratios), 4), True

    def _evidence_refs(self, proof_packs: list[tuple[Path, dict]]) -> list[str]:
        refs = []
        for path, _ in proof_packs:
            refs.append(self._relative_ref(path))
        return refs

    def _market_evidence_refs(self, outcome_resolved: bool, repeatability_available: bool) -> list[str]:
        refs = []
        if outcome_resolved:
            refs.append(self._relative_ref(self._user_root / "market_proof" / "baseline_comparisons.jsonl"))
        if repeatability_available:
            refs.append(self._relative_ref(self._user_root / "market_proof" / "forecast_ledger_summary.json"))
        return refs

    def _relative_ref(self, path: Path) -> str:
        try:
            base = self.workspace.resolve()
            return str(path.resolve().relative_to(base))
        except (OSError, ValueError):
            return path.name
