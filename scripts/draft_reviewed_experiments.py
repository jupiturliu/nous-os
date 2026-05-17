#!/usr/bin/env python3
"""Draft ReviewedExperiment artifacts from existing trading-agent proof packs.

This is a NOUS OS helper that stays strictly read-only on its own. It scans
``<workspace>/trading-agent/data/users/<user>/promotion_reviews/proof_packs/``,
extracts a real hypothesis + source pointer from each pack, and prints draft
ReviewedExperiment payloads for human sign-off.

The drafts can be committed to the trading-agent ledger via the
``--apply <candidate_id>`` flag, which delegates to trading-agent's own
``scripts/record_reviewed_experiment.py``. That script is the one true
writer: it enforces the capital_boundary=review_only invariant, refuses
capital-action verbs, and writes atomically into
``data/users/<user>/proof_loop/reviewed_experiments/``.

This helper never writes to the ledger itself. It only proposes drafts.

Hypothesis sourcing: drafts pull from the proof pack's own
``required_human_decision`` and ``why_review_ready`` fields so the resulting
hypothesis reflects what the system actually flagged, not invented text.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


DEFAULT_WORKSPACE = Path(__file__).resolve().parents[2]
DEFAULT_USER = "feige"
DEFAULT_REVIEW_STATE = "pending"
DEFAULT_SOURCE_TYPE = "operator_review"

# Hypothesis text must not contain capital-action verbs — same guardrail
# trading-agent's record_reviewed_experiment.py enforces. Mirrored here so
# we never emit a draft that the writer would reject.
_FORBIDDEN_FRAGMENTS = (
    " buy ", " sell ", " execute ", " approve ", " place_order ",
    " cancel_order ", " change_risk_config ", " promote_live ",
)


def _proof_packs_dir(workspace: Path, user: str) -> Path:
    return (
        workspace
        / "trading-agent"
        / "data"
        / "users"
        / user
        / "promotion_reviews"
        / "proof_packs"
    )


def _load_packs(packs_dir: Path) -> list[tuple[Path, dict]]:
    if not packs_dir.exists():
        return []
    packs: list[tuple[Path, dict]] = []
    for path in sorted(packs_dir.glob("*.json")):
        if path.name == "index.json":
            continue
        try:
            with open(path, "r", encoding="utf-8") as fh:
                pack = json.load(fh)
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(pack, dict) or "candidate_id" not in pack:
            continue
        packs.append((path, pack))
    return packs


def _build_hypothesis(pack: dict) -> str:
    """Compose a real hypothesis from the proof pack's own fields.

    The hypothesis describes what the system itself flagged as the
    review-worthy claim. Falls back through several pack fields so the
    text is always grounded in artifact content rather than fabricated.
    """
    candidate = pack.get("candidate_id", "candidate")
    decision = pack.get("required_human_decision")
    why = pack.get("why_review_ready")
    blocking = pack.get("blocking_states") or []

    if isinstance(decision, str) and decision.strip():
        text = (
            f"Reviewing {candidate}: the system flagged "
            f"{decision.strip()!r}. Confirm whether the recalibration or "
            f"deferral the proof pack proposes would tighten the realized-rate "
            f"gap without re-introducing the blocked states "
            f"{blocking!r}."
        )
    elif isinstance(why, str) and why.strip():
        text = (
            f"Reviewing {candidate}: the system surfaced this as review-ready "
            f"with rationale {why.strip()!r}. Confirm whether the cited "
            f"rationale holds and what follow-on evidence the next cycle "
            f"should gather."
        )
    else:
        text = (
            f"Reviewing {candidate}: the system surfaced this candidate "
            f"with blocking_states {blocking!r}. Confirm whether the cited "
            f"blockers reflect current state and what the next cycle should "
            f"gather."
        )
    return _sanitize_hypothesis(text)


def _sanitize_hypothesis(text: str) -> str:
    """Strip capital-action verb tokens so the downstream writer accepts the
    text. Replaces with bracketed labels rather than dropping silently."""
    haystack = f" {text.lower()} "
    if not any(bad in haystack for bad in _FORBIDDEN_FRAGMENTS):
        return text
    cleaned = text
    for bad in _FORBIDDEN_FRAGMENTS:
        token = bad.strip()
        if not token:
            continue
        cleaned = re.sub(
            rf"\b{re.escape(token)}\b",
            f"[{token}_redacted]",
            cleaned,
            flags=re.IGNORECASE,
        )
    return cleaned


def build_draft(pack_path: Path, pack: dict, *, user: str, source_type: str, review_state: str) -> dict:
    # source_ref must be relative to the trading-agent repo root because that
    # is the cwd record_reviewed_experiment.py will run from. pack_path is
    # <ta_root>/data/users/<user>/promotion_reviews/proof_packs/<id>.json so
    # parents[5] is <ta_root>.
    rel = pack_path.relative_to(pack_path.parents[5])
    return {
        "candidate_id": pack["candidate_id"],
        "user": user,
        "source_type": source_type,
        "source_ref": str(rel),
        "hypothesis": _build_hypothesis(pack),
        "review_state": review_state,
        "applied": False,
        "summary_fields": {
            "ticker": pack.get("ticker"),
            "theme": pack.get("theme"),
            "blocking_states": pack.get("blocking_states"),
            "capital_action_authorized": pack.get("capital_action_authorized"),
            "validated_claims_count": (
                len(pack["validated_claims"]) if isinstance(pack.get("validated_claims"), list) else None
            ),
            "missing_evidence_count": (
                len(pack["missing_evidence"]) if isinstance(pack.get("missing_evidence"), list) else None
            ),
            "required_human_decision": pack.get("required_human_decision"),
        },
    }


def _draft_record_command(draft: dict, *, trading_agent_root: Path) -> list[str]:
    return [
        "venv/bin/python3",
        "scripts/record_reviewed_experiment.py",
        "--user", draft["user"],
        "--source-type", draft["source_type"],
        "--source-ref", draft["source_ref"],
        "--hypothesis", draft["hypothesis"],
        "--review-state", draft["review_state"],
    ]


def apply_draft(draft: dict, *, workspace: Path, dry_run: bool = False) -> dict:
    trading_agent_root = workspace / "trading-agent"
    if not trading_agent_root.exists():
        raise SystemExit(f"trading-agent repo not found at {trading_agent_root}")
    cmd = _draft_record_command(draft, trading_agent_root=trading_agent_root)
    if dry_run:
        cmd = cmd + ["--dry-run"]
    result = subprocess.run(
        cmd,
        cwd=trading_agent_root,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return {
        "candidate_id": draft["candidate_id"],
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "applied": result.returncode == 0 and not dry_run,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=str(DEFAULT_WORKSPACE))
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--source-type", default=DEFAULT_SOURCE_TYPE)
    parser.add_argument("--review-state", default=DEFAULT_REVIEW_STATE)
    parser.add_argument(
        "--limit", type=int, default=5,
        help="Cap on drafts emitted (default 5). Use 0 for no cap.",
    )
    parser.add_argument(
        "--apply", default=None, metavar="CANDIDATE_ID",
        help=(
            "After printing drafts, invoke trading-agent's "
            "record_reviewed_experiment.py for this specific candidate_id. "
            "Repeat the flag for multiple. Without --apply nothing is written."
        ),
        action="append",
    )
    parser.add_argument(
        "--apply-dry-run", action="store_true",
        help="When applying, pass --dry-run to the downstream writer.",
    )
    args = parser.parse_args(argv)

    workspace = Path(args.workspace).resolve()
    packs_dir = _proof_packs_dir(workspace, args.user)
    packs = _load_packs(packs_dir)
    drafts = [
        build_draft(
            path, pack,
            user=args.user,
            source_type=args.source_type,
            review_state=args.review_state,
        )
        for path, pack in packs
    ]
    if args.limit and args.limit > 0:
        drafts = drafts[: args.limit]

    output = {
        "workspace": str(workspace),
        "user": args.user,
        "scanned": len(packs),
        "drafts_emitted": len(drafts),
        "drafts": drafts,
        "applied": [],
    }

    if args.apply:
        wanted = set(args.apply)
        unknown = wanted - {d["candidate_id"] for d in drafts}
        if unknown:
            raise SystemExit(
                f"--apply ids not in scanned drafts: {sorted(unknown)}"
            )
        for draft in drafts:
            if draft["candidate_id"] not in wanted:
                continue
            output["applied"].append(
                apply_draft(draft, workspace=workspace, dry_run=args.apply_dry_run)
            )

    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
