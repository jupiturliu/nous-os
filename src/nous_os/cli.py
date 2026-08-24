"""Unified NOUS OS command Interface."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import uuid
from pathlib import Path

from nous_os.artifacts import publish_site_data, stage_site
from nous_os.assurance import InvariantViolation
from nous_os.checks import CHECK_MODES, run_check
from nous_os.contracts.domain_compilation import validate_contract_bundle, validate_full_contract_bundle
from nous_os.contracts.harness_inventory import validate_inventory
from nous_os.core import EvidenceEvent, EventStore, Harness, HarnessContext, RuntimePaths, load_profile
from nous_os.core.project import find_project_root
from nous_os.specs import (
    approve_change,
    gate_range,
    gate_staged,
    initialize_change,
    status_change,
    validate_change,
    verify_change,
)
from nous_os.security import PermissionDenied
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

    check = commands.add_parser("check")
    check.add_argument("--mode", choices=CHECK_MODES, default="quick")
    check.add_argument("--json", action="store_true", dest="json_output")
    check.add_argument("--max-workers", type=int)
    check.add_argument("--record-snapshots", action="store_true")
    check.set_defaults(function=_check)

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

    diagnose = commands.add_parser("diagnose")
    _profile_argument(diagnose, "student")
    diagnose.add_argument("--json", action="store_true", dest="json_output")
    diagnose.set_defaults(function=_diagnose)

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

    spec = commands.add_parser("spec")
    spec_commands = spec.add_subparsers(dest="spec_action", required=True)
    spec_init = spec_commands.add_parser("init")
    spec_init.add_argument("change_id")
    spec_init.add_argument("--title", required=True)
    spec_init.set_defaults(function=_spec_init)
    spec_validate = spec_commands.add_parser("validate")
    spec_validate.add_argument("change_id")
    spec_validate.set_defaults(function=_spec_validate)
    spec_approve = spec_commands.add_parser("approve")
    spec_approve.add_argument("change_id")
    spec_approve.add_argument("--by", dest="approver", required=True)
    spec_approve.add_argument("--reason", required=True)
    spec_approve.add_argument("--channel", choices=("local", "pull-request"), default="local")
    spec_approve.add_argument("--reference")
    spec_approve.set_defaults(function=_spec_approve)
    spec_status = spec_commands.add_parser("status")
    spec_status.add_argument("change_id")
    spec_status.set_defaults(function=_spec_status)
    spec_verify = spec_commands.add_parser("verify")
    spec_verify.add_argument("change_id")
    spec_verify.set_defaults(function=_spec_verify)
    spec_gate = spec_commands.add_parser("gate")
    gate_source = spec_gate.add_mutually_exclusive_group(required=True)
    gate_source.add_argument("--staged", action="store_true")
    gate_source.add_argument("--range", dest="revision_range")
    spec_gate.add_argument("--message-file", type=Path)
    spec_gate.add_argument("--require-remote-approval", action="store_true")
    spec_gate.set_defaults(function=_spec_gate)

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


def _check(args) -> int:
    report = run_check(
        _root(),
        args.mode,
        max_workers=args.max_workers,
        record_snapshots=args.record_snapshots,
        runtime_home=args.runtime_home,
    )
    if args.json_output:
        print(json.dumps(report.as_dict(), ensure_ascii=False, indent=2))
    else:
        for result in report.results:
            suffix = f" ({result.duration_ms} ms)"
            if result.skipped_because:
                suffix += f" needs={','.join(result.skipped_because)}"
            print(f"[{result.status.upper():7}] {result.gate_id}: {result.label}{suffix}")
            if result.status == "failed":
                for diagnostic in (result.error, result.stderr.strip(), result.stdout.strip()):
                    if diagnostic:
                        print(diagnostic, file=sys.stderr)
        print(f"check {report.mode}: {report.status} ({report.duration_ms} ms)")
    return 0 if report.ok else 1


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
        harness.check()
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
        harness.check()
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


def _diagnose(args) -> int:
    profile = _profile(args.profile)
    context = HarnessContext(profile_name=profile.name, paths=_paths(args))
    harness = Harness(profile, context)
    try:
        harness.start()
    except PermissionDenied as error:
        return _print_diagnose_failure(args, profile.name, {
            "code": error.code,
            "plugin": error.plugin_id,
            "denied_effects": list(error.denied_effects),
        })
    except InvariantViolation as error:
        return _print_diagnose_failure(args, profile.name, {
            "code": error.code,
            "owner": error.owner,
            "invariant": error.invariant,
            "phase": error.phase,
        })
    try:
        report = harness.diagnose()
        _print_diagnose_report(args, report)
    finally:
        harness.stop()
    return 0 if report["readiness"]["ready"] else 1


def _print_diagnose_failure(args, profile_name: str, failure: dict) -> int:
    report = {
        "schema_version": 1,
        "profile": {"name": profile_name},
        "readiness": {
            "ready": False,
            "status": "failed",
            "reasons": [failure["code"]],
            "profile": profile_name,
        },
        "failure": failure,
    }
    _print_diagnose_report(args, report)
    return 1


def _print_diagnose_report(args, report: dict) -> None:
    if args.json_output:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return
    profile = report["profile"]
    schema = f" schema={profile['schema_version']}" if "schema_version" in profile else ""
    telemetry = f" telemetry={report['telemetry']['mode']}" if "telemetry" in report else ""
    print(f"profile={profile['name']}{schema}")
    print(f"readiness={report['readiness']['status']}{telemetry}")
    if "plugin_order" in report:
        print(f"plugins={','.join(item['id'] for item in report['plugin_order'])}")
        print(f"capabilities={','.join(report['capabilities'])}")
        for credential in report["credentials"]:
            print(
                f"credential={credential['reference']} configured={str(credential['configured']).lower()} "
                f"source={credential['source'] or 'none'} writable={str(credential['writable']).lower()}"
            )
    if "failure" in report:
        print(f"failure={report['failure']['code']}")


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


def _spec_init(args) -> int:
    print(initialize_change(_root(), args.change_id, args.title))
    return 0


def _spec_validate(args) -> int:
    result = validate_change(_root(), args.change_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


def _spec_approve(args) -> int:
    result = approve_change(
        _root(), args.change_id, approver=args.approver, reason=args.reason,
        channel=args.channel, reference=args.reference, runtime_home=args.runtime_home,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def _spec_status(args) -> int:
    result = status_change(_root(), args.change_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


def _spec_verify(args) -> int:
    result = verify_change(_root(), args.change_id, runtime_home=args.runtime_home)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["verdict"] == "pass" else 1


def _spec_gate(args) -> int:
    if args.staged:
        if not args.message_file:
            raise ValueError("--staged requires --message-file")
        result = gate_staged(_root(), args.message_file)
    else:
        if args.message_file:
            raise ValueError("--message-file is only valid with --staged")
        result = gate_range(_root(), args.revision_range, require_remote_approval=args.require_remote_approval)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


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
