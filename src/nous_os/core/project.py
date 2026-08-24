"""Repository source-root discovery for developer and deployment commands."""

from __future__ import annotations

from importlib import resources
from pathlib import Path


def find_project_root(start: str | Path | None = None) -> Path:
    candidate = Path(start or Path.cwd()).resolve()
    if candidate.is_file():
        candidate = candidate.parent
    for directory in (candidate, *candidate.parents):
        if (directory / "pyproject.toml").exists() and (directory / "apps" / "web").exists():
            return directory
    packaged = resources.files("nous_os.resources")
    try:
        return Path(packaged).resolve()
    except TypeError as error:
        raise FileNotFoundError("NOUS OS project root not found; run inside a source checkout") from error
