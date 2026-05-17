#!/usr/bin/env python3
"""Validate the NOUS OS harness inventory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INVENTORY = ROOT / "docs" / "harness" / "HARNESS_INVENTORY.json"
REQUIRED_SURFACE_KEYS = {"id", "path", "kind", "owner", "published", "verification"}


def validate_inventory(inventory_path: Path = DEFAULT_INVENTORY) -> dict:
    inventory = json.loads(inventory_path.read_text())
    issues: list[str] = []
    seen_ids: set[str] = set()

    if inventory.get("schema_version") != 1:
        issues.append("schema_version must be 1")
    if inventory.get("project") != "nous-os":
        issues.append("project must be nous-os")
    if not inventory.get("default_boundary"):
        issues.append("default_boundary is required")

    surfaces = inventory.get("surfaces")
    if not isinstance(surfaces, list) or not surfaces:
        issues.append("surfaces must be a non-empty list")
        surfaces = []

    for index, surface in enumerate(surfaces):
        missing = sorted(REQUIRED_SURFACE_KEYS - set(surface))
        if missing:
            issues.append(f"surface[{index}] missing keys: {', '.join(missing)}")
            continue

        surface_id = surface["id"]
        if surface_id in seen_ids:
            issues.append(f"duplicate surface id: {surface_id}")
        seen_ids.add(surface_id)

        rel_path = Path(surface["path"])
        if rel_path.is_absolute() or ".." in rel_path.parts:
            issues.append(f"{surface_id} path must be repo-relative: {surface['path']}")
            continue
        if not (ROOT / rel_path).exists():
            issues.append(f"{surface_id} path does not exist: {surface['path']}")
        if not str(surface.get("verification", "")).strip():
            issues.append(f"{surface_id} verification command is required")

    required_ids = {
        "harness_readme",
        "harness_context_index",
        "next_development_plan",
        "heartbeat_demo_dashboard",
        "heartbeat_runtime",
        "domain_evaluator_interface",
        "trading_evaluator",
        "first_vertical_wiring_plan",
        "harness_handoffs",
        "student_sandbox_v0",
        "latest_research_record",
        "review_template",
        "cross_repo_release_gate",
        "documentation_reproducibility_test",
        "github_pages_workflow",
    }
    missing_ids = sorted(required_ids - seen_ids)
    if missing_ids:
        issues.append(f"missing required surface ids: {', '.join(missing_ids)}")

    return {
        "ok": not issues,
        "inventory": str(inventory_path),
        "surface_count": len(surfaces),
        "issues": issues,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate NOUS OS harness inventory.")
    parser.add_argument("--inventory", default=str(DEFAULT_INVENTORY))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = validate_inventory(Path(args.inventory))
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"harness inventory ok={result['ok']} surfaces={result['surface_count']}")
        for issue in result["issues"]:
            print(f"- {issue}")
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
