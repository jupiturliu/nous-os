"""Command Interface for reproducible release artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from nous_os.core.project import find_project_root

from .artifacts import build_release, inspect_release, smoke_installed_wheel


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m nous_os.release")
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build")
    build.add_argument("--root", type=Path)
    build.add_argument("--output", type=Path, required=True)
    inspect = commands.add_parser("inspect")
    inspect.add_argument("--root", type=Path)
    inspect.add_argument("--directory", type=Path, required=True)
    smoke = commands.add_parser("smoke")
    smoke.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "build":
        report = build_release(args.root or find_project_root(), args.output)
    elif args.command == "inspect":
        report = inspect_release(args.root or find_project_root(), args.directory)
    else:
        report = smoke_installed_wheel(args.directory)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
