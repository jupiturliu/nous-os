"""Unified NOUS OS command Interface."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import uuid
from pathlib import Path

from nous_os.artifacts import publish_site_data, stage_site
from nous_os.contracts.domain_compilation import validate_contract_bundle, validate_full_contract_bundle
from nous_os.contracts.harness_inventory import validate_inventory
from nous_os.core import EvidenceEvent, EventStore, Harness, HarnessContext, RuntimePaths, load_profile
from nous_os.core.project import find_project_root
from nous_os.web import serve


def main(argv: list[str] | None = None) -> None:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        status = args.function(args)
    except (FileNotFoundError, ValueError, KeyError) as error:
        parser.exit(2, f"nous-os: {error}\n")
    raise SystemExit(status or 0)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nous-os", description="NOUS OS evidence-backed Harness")
    parser.add_argument("--runtime-home", help="override NOUS_OS_HOME")
    commands = parser.add_subparsers(dest="command", required=True)

    run = commands.add_parser("run")
    run_commands = run.add_subparsers(dest="workflow", required=True)
    heartbeat = run_commands.add_parser("heartbeat")
    _profile_argument(heartbeat, "research")
    heartbeat.add_argument("--goal")
    heartbeat.add_argument("--override-kind")
    heartbeat.add_argument("--demo-mode")
    heartbeat.set_defaults(function=_run_heartbeat)
    research = run_commands.add_parser("research-line")
    _profile_argument(research, "research")
    research.add_argument("--capture-date")
    research.add_argument("--max-age-days", type=int, default=2)
    research.add_argument("--dry-run", action="store_true")
    research.set_defaults(function=_run_research_line)

    serve_parser = commands.add_parser("serve")
    serve_commands = serve_parser.add_subparsers(dest="composition", required=True)
    web = serve_commands.add_parser("web")
    _profile_argument(web, "student")
    web.add_argument("--host")
    web.add_argument("--port", type=int)
    web.set_defaults(function=_serve_web)

    validate = commands.add_parser("validate")
    validate_commands = validate.add_subparsers(dest="validation", required=True)
    profile = validate_commands.add_parser("profile")
    _profile_argument(profile, "student")
    profile.set_defaults(function=_validate_profile)
    contracts = validate_commands.add_parser("contracts")
    contracts.set_defaults(function=_validate_contracts)
    harness = validate_commands.add_parser("harness")
    harness.add_argument("--inventory", type=Path)
    harness.set_defaults(function=_validate_harness)

    contract = commands.add_parser("contract")
    contract_commands = contract.add_subparsers(dest="contract_action", required=True)
    contract_validate = contract_commands.add_parser("validate")
    contract_validate.add_argument("spec", type=Path)
    contract_validate.add_argument("report", type=Path)
    contract_validate.add_argument("--target", type=Path)
    contract_validate.add_argument("--platform-config", type=Path)
    contract_validate.set_defaults(function=_contract_validate)
    contract_generate = contract_commands.add_parser("generate")
    contract_generate.add_argument("destination", type=Path)
    contract_generate.set_defaults(function=_contract_generate)

    publish = commands.add_parser("publish-site-data")
    _profile_argument(publish, "research")
    publish.add_argument("--site-public", type=Path)
    publish.set_defaults(function=_publish)

    site = commands.add_parser("site")
    site_commands = site.add_subparsers(dest="site_action", required=True)
    site_stage = site_commands.add_parser("stage")
    site_stage.add_argument("--destination", type=Path)
    site_stage.set_defaults(function=_stage)

    migrate = commands.add_parser("migrate")
    migrate_commands = migrate.add_subparsers(dest="migration", required=True)
    legacy = migrate_commands.add_parser("legacy-runtime")
    legacy.add_argument("--from", dest="source", type=Path, required=True)
    legacy.add_argument("--profile", default="migration")
    legacy.set_defaults(function=_migrate_legacy)
    return parser


def _profile_argument(parser: argparse.ArgumentParser, default: str) -> None:
    parser.add_argument("--profile", default=default, help="Profile name or YAML path")


def _root() -> Path:
    return find_project_root()


def _profile(value: str):
    candidate = Path(value)
    if not candidate.exists():
        candidate = _root() / "config" / "profiles" / f"{value}.yaml"
    return load_profile(candidate)


def _paths(args) -> RuntimePaths:
    return RuntimePaths.resolve(args.runtime_home)


def _run_heartbeat(args) -> int:
    profile = _profile(args.profile)
    context = HarnessContext(profile_name=profile.name, paths=_paths(args))
    harness = Harness(profile, context).start()
    try:
        snapshot = context.resolve("heartbeat").run(
            goal=args.goal,
            override_kind=args.override_kind,
            demo_mode=args.demo_mode,
        )
    finally:
        harness.stop()
    print(json.dumps(snapshot["metrics"], ensure_ascii=False, indent=2))
    print(context.paths.projections / "dashboard-data.json")
    return 0


def _run_research_line(args) -> int:
    profile = _profile(args.profile)
    context = HarnessContext(profile_name=profile.name, paths=_paths(args))
    harness = Harness(profile, context).start()
    try:
        module = context.resolve("research-line")
        capture_date, markdown = module.capture(
            max_age_days=args.max_age_days,
            capture_date=args.capture_date,
        )
        if args.dry_run:
            print(markdown)
        else:
            print(module.write_inbox_file(capture_date, markdown))
    finally:
        harness.stop()
    return 0


def _serve_web(args) -> int:
    profile = _profile(args.profile)
    context = HarnessContext(profile_name=profile.name, paths=_paths(args))
    harness = Harness(profile, context).start()
    try:
        root = _root()
        staged = stage_site(root)
        host = args.host or profile.web.get("host", "127.0.0.1")
        port = args.port or int(profile.web.get("port", 8787))
        serve(context, static_root=staged, host=host, port=port)
    finally:
        harness.stop()
    return 0


def _validate_profile(args) -> int:
    profile = _profile(args.profile)
    context = HarnessContext(profile_name=profile.name, paths=_paths(args))
    harness = Harness(profile, context).start()
    harness.stop()
    print(f"profile ok name={profile.name} plugins={len(profile.plugins)}")
    return 0


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _default_contract_paths() -> tuple[Path, Path, Path, Path]:
    directory = _root() / "contracts" / "domain-compilation"
    return (
        directory / "research-source-intake-spec-v0.json",
        directory / "research-source-intake-target-description-v0.json",
        directory / "research-source-intake-platform-config-v0.json",
        directory / "research-source-intake-verification-report-v0.json",
    )


def _validate_contracts(args) -> int:
    spec, target, config, report = _default_contract_paths()
    result = validate_full_contract_bundle(*map(_load_json, (spec, target, config, report)))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


def _validate_harness(args) -> int:
    result = validate_inventory(args.inventory or _root() / "contracts" / "harness" / "inventory.json")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


def _contract_validate(args) -> int:
    if bool(args.target) != bool(args.platform_config):
        raise ValueError("--target and --platform-config must be supplied together")
    if args.target:
        result = validate_full_contract_bundle(
            _load_json(args.spec), _load_json(args.target), _load_json(args.platform_config), _load_json(args.report)
        )
    else:
        result = validate_contract_bundle(_load_json(args.spec), _load_json(args.report))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


def _contract_generate(args) -> int:
    destination = args.destination.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    for source in _default_contract_paths():
        shutil.copy2(source, destination / source.name)
    print(destination)
    return 0


def _publish(args) -> int:
    profile = _profile(args.profile)
    public = args.site_public or _root() / "apps" / "web" / "public"
    targets = publish_site_data(_paths(args), public)
    print(f"published profile={profile.name}")
    for target in targets:
        print(target)
    return 0


def _stage(args) -> int:
    print(stage_site(_root(), args.destination))
    return 0


def _migrate_legacy(args) -> int:
    source = args.source.resolve()
    if not source.is_dir():
        raise FileNotFoundError(f"legacy runtime directory not found: {source}")
    store = EventStore(_paths(args))
    run_id = f"migration-{uuid.uuid4().hex[:12]}"
    count = 0
    for path in sorted(source.rglob("*")):
        if not path.is_file() or path.suffix not in {".json", ".jsonl"}:
            continue
        payload = {"legacy_path": path.relative_to(source).as_posix(), "content": path.read_text(encoding="utf-8")}
        artifact = store.write_artifact("legacy-runtime", payload)
        store.append(EvidenceEvent(
            event_type="migration.legacy-artifact-imported",
            run_id=run_id,
            profile=args.profile,
            producer="legacy-runtime-migration",
            payload={"legacy_path": payload["legacy_path"]},
            evidence_refs=(artifact,),
            privacy="private",
        ))
        count += 1
    print(f"migrated files={count} run_id={run_id}")
    return 0
