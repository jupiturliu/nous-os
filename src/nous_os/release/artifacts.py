"""Build, inspect, and smoke-test release artifacts behind one deep Interface."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import venv
import zipfile
from email.parser import BytesParser
from importlib import metadata
from pathlib import Path, PurePosixPath
from typing import Callable, Iterable


BUILD_LOCK = "requirements/build.lock"
DEPENDENCY_CONTRACT = "contracts/release/runtime-dependencies.json"
MANIFEST_NAME = "release-manifest.json"
PROFILE_NAMES = ("student", "research", "trading-proof")
PRIVATE_PATTERNS = (
    re.compile(r"(?:^|[\s\"'])/(?:Users|home|private)/"),
    re.compile(r"[A-Za-z]:\\"),
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"[\"']?(?:password|secret|token|access[_-]?token|webhook[_-]?url)[\"']?\s*[:=]\s*[^\s<]+", re.I),
)
TEXT_DATA_SUFFIXES = frozenset({".json", ".jsonl", ".md", ".txt", ".yaml", ".yml"})
CommandRunner = Callable[..., subprocess.CompletedProcess]


class ReleaseError(RuntimeError):
    """Stable release validation failure."""


def build_release(
    root: str | Path,
    output: str | Path,
    *,
    python: str = sys.executable,
    runner: CommandRunner = subprocess.run,
) -> dict:
    """Build the clean HEAD twice, require byte identity, and write provenance."""

    project = Path(root).resolve()
    destination = Path(output).resolve()
    if destination == project or project in destination.parents:
        raise ReleaseError("release output must be outside the source checkout")
    _require_clean_head(project, runner)
    tools = _locked_tool_versions(project / BUILD_LOCK)
    _require_installed_tools(tools, python, runner)
    commit = _git(project, ("rev-parse", "HEAD"), runner).strip()
    source_date_epoch = int(_git(project, ("show", "-s", "--format=%ct", "HEAD"), runner).strip())

    with tempfile.TemporaryDirectory(prefix="nous-os-release-build-") as temporary:
        temporary_root = Path(temporary)
        builds = []
        for sequence in ("first", "second"):
            source = temporary_root / f"source-{sequence}"
            artifacts = temporary_root / f"artifacts-{sequence}"
            _export_head(project, source, runner)
            artifacts.mkdir()
            environment = os.environ.copy()
            environment["SOURCE_DATE_EPOCH"] = str(source_date_epoch)
            environment["PYTHONHASHSEED"] = "0"
            _run(
                (python, "-m", "build", "--no-isolation", "--sdist", "--wheel", "--outdir", str(artifacts)),
                cwd=source,
                env=environment,
                runner=runner,
            )
            _normalize_built_archives(artifacts, source_date_epoch)
            builds.append(_artifact_facts(artifacts))
        if builds[0] != builds[1]:
            raise ReleaseError("normalized builds are not byte-for-byte reproducible")

        if destination.exists():
            if any(destination.iterdir()):
                raise ReleaseError("release output directory must be empty")
        else:
            destination.mkdir(parents=True)
        first = temporary_root / "artifacts-first"
        for fact in builds[0]:
            shutil.copy2(first / fact["filename"], destination / fact["filename"])

    manifest = {
        "schema_version": 1,
        "project": "nous-os",
        "source_commit": commit,
        "source_date_epoch": source_date_epoch,
        "python": _python_version(python, runner),
        "build_tools": tools,
        "reproducible": True,
        "artifacts": list(builds[0]),
    }
    _write_json(destination / MANIFEST_NAME, manifest)
    return manifest


def inspect_release(root: str | Path, directory: str | Path) -> dict:
    """Validate provenance, archive membership, metadata, privacy, and Profile mirrors."""

    project = Path(root).resolve()
    release = Path(directory).resolve()
    manifest = json.loads((release / MANIFEST_NAME).read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or manifest.get("project") != "nous-os":
        raise ReleaseError("invalid release manifest identity")
    if manifest.get("reproducible") is not True:
        raise ReleaseError("release manifest does not attest reproducibility")
    facts = manifest.get("artifacts")
    if not isinstance(facts, list) or len(facts) != 2:
        raise ReleaseError("release manifest must contain one sdist and one wheel")
    suffixes = {"wheel": 0, "sdist": 0}
    reports = []
    for fact in facts:
        path = release / _safe_filename(fact.get("filename"))
        actual = _file_fact(path)
        if actual != fact:
            raise ReleaseError(f"artifact differs from manifest: {path.name}")
        if path.suffix == ".whl":
            suffixes["wheel"] += 1
            reports.append(_inspect_wheel(project, path))
        elif path.name.endswith(".tar.gz"):
            suffixes["sdist"] += 1
            reports.append(_inspect_sdist(project, path))
        else:
            raise ReleaseError(f"unsupported release artifact: {path.name}")
    if suffixes != {"wheel": 1, "sdist": 1}:
        raise ReleaseError("release must contain exactly one wheel and one sdist")
    _validate_dependency_notice(project)
    return {
        "schema_version": 1,
        "status": "passed",
        "source_commit": manifest["source_commit"],
        "artifacts": reports,
        "runtime_dependencies": ["PyYAML"],
    }


def smoke_installed_wheel(
    directory: str | Path,
    *,
    python: str = sys.executable,
    runner: CommandRunner = subprocess.run,
) -> dict:
    """Install the wheel outside the checkout and exercise its public runtime Interface."""

    release = Path(directory).resolve()
    wheels = tuple(release.glob("*.whl"))
    if len(wheels) != 1:
        raise ReleaseError("installed smoke requires exactly one wheel")
    with tempfile.TemporaryDirectory(prefix="nous-os-installed-smoke-") as temporary:
        root = Path(temporary)
        environment_path = root / "venv"
        venv.EnvBuilder(with_pip=True, clear=True).create(environment_path)
        executable = environment_path / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        cli = environment_path / ("Scripts/nous-os.exe" if os.name == "nt" else "bin/nous-os")
        _run((str(executable), "-m", "pip", "install", "--disable-pip-version-check", str(wheels[0])), runner=runner)
        work = root / "outside-checkout"
        work.mkdir()
        runtime_home = root / "runtime"
        environment = os.environ.copy()
        environment.pop("PYTHONPATH", None)
        for name in tuple(environment):
            if any(token in name.upper() for token in ("PASSWORD", "SECRET", "TOKEN", "WEBHOOK")):
                environment.pop(name, None)
        environment["NOUS_OS_HOME"] = str(runtime_home)
        commands = [(str(cli), "--help")]
        commands.extend((str(cli), "validate", "profile", "--profile", name) for name in PROFILE_NAMES)
        commands.extend((
            (str(cli), "diagnose", "--profile", "student", "--json"),
            (str(executable), "-m", "nous_os.release.installed_smoke"),
        ))
        outputs = []
        for command in commands:
            completed = _run(command, cwd=work, env=environment, runner=runner)
            outputs.append(completed.stdout)
        joined = "\n".join(outputs)
        if str(work) in joined or str(runtime_home) in joined:
            raise ReleaseError("installed smoke output exposed a machine path")
        diagnosis = json.loads(outputs[-2])
        scenario = json.loads(outputs[-1])
        if diagnosis.get("readiness", {}).get("ready") is not True or scenario.get("status") != "passed":
            raise ReleaseError("installed wheel did not become ready")
    return {"schema_version": 1, "status": "passed", "profiles": list(PROFILE_NAMES), "scenario": "student"}


def assert_release_payload_safe(name: str, payload: bytes) -> None:
    """Reject private or machine-local text from shipped data and documentation."""

    suffix = Path(name).suffix.lower()
    if suffix not in TEXT_DATA_SUFFIXES:
        return
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ReleaseError(f"release text payload is not UTF-8: {name}") from error
    if any(pattern.search(text) for pattern in PRIVATE_PATTERNS):
        raise ReleaseError(f"unsafe release payload: {name}")


def _inspect_wheel(root: Path, path: Path) -> dict:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        dist_info = _wheel_dist_info(names)
        for info in archive.infolist():
            name = _safe_member(info.filename)
            if not (name == "nous_os" or name.startswith("nous_os/") or name == dist_info or name.startswith(f"{dist_info}/")):
                raise ReleaseError(f"unexpected wheel member: {name}")
            if _forbidden_member(name):
                raise ReleaseError(f"forbidden wheel member: {name}")
            mode = (info.external_attr >> 16) & 0o777
            if not info.is_dir() and mode & 0o111:
                raise ReleaseError(f"unexpected executable wheel member: {name}")
            if not info.is_dir():
                assert_release_payload_safe(name, archive.read(info))
        _verify_profile_members(root, lambda name: archive.read(name), set(names), "nous_os/resources/profiles")
        metadata_bytes = archive.read(f"{dist_info}/METADATA")
        _validate_wheel_metadata(root, metadata_bytes)
    return {"filename": path.name, "kind": "wheel", "members": len(names), "status": "passed"}


def _inspect_sdist(root: Path, path: Path) -> dict:
    with tarfile.open(path, "r:gz") as archive:
        members = archive.getmembers()
        roots = {PurePosixPath(member.name).parts[0] for member in members if member.name}
        if len(roots) != 1:
            raise ReleaseError("sdist must contain one top-level directory")
        prefix = next(iter(roots))
        payloads: dict[str, bytes] = {}
        for member in members:
            name = _safe_member(member.name)
            relative = PurePosixPath(name).relative_to(prefix).as_posix()
            if relative == ".":
                continue
            if member.issym() or member.islnk():
                raise ReleaseError(f"sdist links are not allowed: {name}")
            if not _allowed_sdist_member(relative) or _forbidden_member(relative):
                raise ReleaseError(f"unexpected sdist member: {relative}")
            if member.isfile() and member.mode & 0o111:
                raise ReleaseError(f"unexpected executable sdist member: {relative}")
            if member.isfile():
                extracted = archive.extractfile(member)
                if extracted is None:
                    raise ReleaseError(f"could not read sdist member: {relative}")
                payload = extracted.read()
                payloads[relative] = payload
                assert_release_payload_safe(relative, payload)
        _verify_profile_members(root, payloads.__getitem__, set(payloads), "src/nous_os/resources/profiles")
    return {"filename": path.name, "kind": "sdist", "members": len(members), "status": "passed"}


def _validate_wheel_metadata(root: Path, payload: bytes) -> None:
    message = BytesParser().parsebytes(payload)
    if message.get("Name") != "nous-os" or message.get("License-Expression") != "MIT":
        raise ReleaseError("wheel metadata identity or license differs")
    if message.get("Requires-Python") != ">=3.11":
        raise ReleaseError("wheel Requires-Python differs")
    expected = _dependency_contract(root)
    observed = tuple(message.get_all("Requires-Dist") or ())
    if {_normalized_requirement(value) for value in observed} != {
        _normalized_requirement(item["requirement"]) for item in expected
    }:
        raise ReleaseError("wheel runtime dependency closure differs")


def _validate_dependency_notice(root: Path) -> None:
    notice = (root / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    for item in _dependency_contract(root):
        if item["notice_heading"] not in notice or item["license"] not in notice or item["requirement"] not in notice:
            raise ReleaseError(f"third-party notice differs for {item['name']}")


def _dependency_contract(root: Path) -> tuple[dict, ...]:
    value = json.loads((root / DEPENDENCY_CONTRACT).read_text(encoding="utf-8"))
    dependencies = value.get("dependencies")
    if value.get("schema_version") != 1 or not isinstance(dependencies, list) or not dependencies:
        raise ReleaseError("invalid runtime dependency contract")
    return tuple(dependencies)


def _verify_profile_members(root: Path, reader: Callable[[str], bytes], names: set[str], prefix: str) -> None:
    for profile_name in PROFILE_NAMES:
        member = f"{prefix}/{profile_name}.yaml"
        if member not in names:
            raise ReleaseError(f"artifact is missing packaged Profile: {profile_name}")
        expected = (root / "src" / "nous_os" / "resources" / "profiles" / f"{profile_name}.yaml").read_bytes()
        mirror = (root / "config" / "profiles" / f"{profile_name}.yaml").read_bytes()
        if expected != mirror:
            raise ReleaseError(f"Profile checkout mirror differs: {profile_name}")
        if reader(member) != expected:
            raise ReleaseError(f"packaged Profile differs: {profile_name}")


def _allowed_sdist_member(name: str) -> bool:
    roots = {
        "LICENSE", "MANIFEST.in", "PKG-INFO", "README.md", "THIRD_PARTY_NOTICES.md", "pyproject.toml", "setup.cfg",
    }
    directories = {"src", "src/nous_os", "src/nous_os.egg-info"}
    return (
        name in roots
        or name in directories
        or name.startswith("src/nous_os/")
        or name.startswith("src/nous_os.egg-info/")
    )


def _forbidden_member(name: str) -> bool:
    parts = {part.lower() for part in PurePosixPath(name).parts}
    forbidden = {".env", ".git", "__pycache__", "artifacts", "events", "projections", "tests", "_site"}
    return bool(parts & forbidden) or name.endswith((".pyc", ".pyo"))


def _wheel_dist_info(names: Iterable[str]) -> str:
    values = {name.split("/", 1)[0] for name in names if ".dist-info/" in name}
    if len(values) != 1:
        raise ReleaseError("wheel must contain one dist-info directory")
    return next(iter(values))


def _safe_member(value: str) -> str:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or "\\" in value:
        raise ReleaseError(f"unsafe archive member: {value!r}")
    return path.as_posix().rstrip("/")


def _safe_filename(value) -> str:
    if not isinstance(value, str) or Path(value).name != value or value in {"", ".", ".."}:
        raise ReleaseError("unsafe artifact filename")
    return value


def _artifact_facts(directory: Path) -> tuple[dict, ...]:
    facts = tuple(_file_fact(path) for path in sorted(directory.iterdir()) if path.is_file())
    if len(facts) != 2:
        raise ReleaseError("build must produce exactly one wheel and one sdist")
    return facts


def _normalize_built_archives(directory: Path, source_date_epoch: int) -> None:
    for path in sorted(directory.iterdir()):
        if path.suffix == ".whl":
            _normalize_wheel(path, source_date_epoch)
        elif path.name.endswith(".tar.gz"):
            _normalize_sdist(path, source_date_epoch)
        elif path.is_file():
            raise ReleaseError(f"build produced an unsupported artifact: {path.name}")


def _normalize_wheel(path: Path, source_date_epoch: int) -> None:
    timestamp = time.gmtime(max(source_date_epoch, 315532800))[:6]
    with zipfile.ZipFile(path) as source:
        entries = tuple((info.filename, info.is_dir(), source.read(info) if not info.is_dir() else b"")
                        for info in source.infolist())
    temporary = path.with_suffix(path.suffix + ".normalized")
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as destination:
        for name, is_directory, payload in sorted(entries):
            info = zipfile.ZipInfo(name, date_time=timestamp)
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = ((0o40755 if is_directory else 0o100644) << 16) | (0x10 if is_directory else 0)
            destination.writestr(info, payload)
    temporary.replace(path)


def _normalize_sdist(path: Path, source_date_epoch: int) -> None:
    entries = []
    with tarfile.open(path, "r:gz") as source:
        for member in source.getmembers():
            if member.issym() or member.islnk():
                raise ReleaseError(f"build produced an archive link: {member.name}")
            extracted = source.extractfile(member) if member.isfile() else None
            entries.append((member.name, member.isdir(), extracted.read() if extracted is not None else b""))
    temporary = path.with_suffix(path.suffix + ".normalized")
    with temporary.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=raw, mtime=source_date_epoch) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as destination:
                for name, is_directory, payload in sorted(entries):
                    info = tarfile.TarInfo(name)
                    info.type = tarfile.DIRTYPE if is_directory else tarfile.REGTYPE
                    info.mode = 0o755 if is_directory else 0o644
                    info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    info.mtime = source_date_epoch
                    info.size = 0 if is_directory else len(payload)
                    destination.addfile(info, None if is_directory else io.BytesIO(payload))
    temporary.replace(path)


def _file_fact(path: Path) -> dict:
    if not path.is_file():
        raise ReleaseError(f"release artifact does not exist: {path.name}")
    payload = path.read_bytes()
    return {"filename": path.name, "sha256": hashlib.sha256(payload).hexdigest(), "size": len(payload)}


def _require_clean_head(root: Path, runner: CommandRunner) -> None:
    if _git(root, ("status", "--porcelain"), runner).strip():
        raise ReleaseError("release build requires a clean source checkout")


def _export_head(root: Path, destination: Path, runner: CommandRunner) -> None:
    completed = runner(("git", "archive", "--format=tar", "HEAD"), cwd=root, capture_output=True, check=False)
    if completed.returncode != 0:
        raise ReleaseError("could not export the source commit")
    destination.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(completed.stdout), mode="r:") as archive:
        for member in archive.getmembers():
            _safe_member(member.name)
            if member.issym() or member.islnk():
                raise ReleaseError("source export contains a link")
        archive.extractall(destination)


def _locked_tool_versions(path: Path) -> dict[str, str]:
    result = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.fullmatch(r"([A-Za-z0-9_.-]+)==([A-Za-z0-9_.+!-]+)", line)
        if not match:
            raise ReleaseError(f"build lock entry is not exact: {line}")
        result[match.group(1).lower().replace("_", "-")] = match.group(2)
    if set(result) != {"build", "packaging", "pyproject-hooks", "setuptools", "wheel"}:
        raise ReleaseError("build lock closure differs from the approved tool set")
    return dict(sorted(result.items()))


def _require_installed_tools(tools: dict[str, str], python: str, runner: CommandRunner) -> None:
    code = (
        "import json,importlib.metadata as m;"
        "print(json.dumps({n:m.version(n) for n in " + repr(tuple(tools)) + "},sort_keys=True))"
    )
    completed = _run((python, "-c", code), runner=runner)
    observed = {key.lower().replace("_", "-"): value for key, value in json.loads(completed.stdout).items()}
    if observed != tools:
        raise ReleaseError("installed build tools differ from requirements/build.lock")


def _python_version(python: str, runner: CommandRunner) -> str:
    completed = _run(
        (python, "-c", "import platform; print(platform.python_version())"),
        runner=runner,
    )
    version = completed.stdout.strip()
    if tuple(int(item) for item in version.split(".")[:2]) < (3, 11):
        raise ReleaseError("release build requires Python 3.11 or newer")
    return version


def _normalized_requirement(value: str) -> tuple[str, tuple[str, ...]]:
    match = re.fullmatch(r"\s*([A-Za-z0-9_.-]+)\s*(.*)", value)
    if not match:
        raise ReleaseError(f"invalid runtime requirement: {value}")
    name = match.group(1).lower().replace("_", "-")
    clauses = tuple(sorted(item.replace(" ", "") for item in match.group(2).split(",") if item.strip()))
    return name, clauses


def _git(root: Path, arguments: tuple[str, ...], runner: CommandRunner) -> str:
    return _run(("git", *arguments), cwd=root, runner=runner).stdout


def _run(command: tuple[str, ...], *, cwd: Path | None = None, env: dict | None = None,
         runner: CommandRunner = subprocess.run) -> subprocess.CompletedProcess:
    completed = runner(command, cwd=cwd, env=env, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "command failed").strip().splitlines()[-1]
        raise ReleaseError(f"release command failed ({Path(command[0]).name}): {detail[:240]}")
    return completed


def _write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
