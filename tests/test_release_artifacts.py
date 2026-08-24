from __future__ import annotations

import hashlib
import io
import json
import subprocess
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path

from nous_os.core.profiles import load_named_profile
from nous_os.release import ReleaseError, build_release, inspect_release
from nous_os.release.artifacts import MANIFEST_NAME, PROFILE_NAMES, assert_release_payload_safe


ROOT = Path(__file__).resolve().parents[1]


class ReleaseArtifactTests(unittest.TestCase):
    def test_packaged_profiles_are_canonical_and_checkout_mirrors_match(self):
        for name in PROFILE_NAMES:
            packaged = ROOT / "src" / "nous_os" / "resources" / "profiles" / f"{name}.yaml"
            checkout = ROOT / "config" / "profiles" / f"{name}.yaml"
            self.assertEqual(packaged.read_bytes(), checkout.read_bytes())
            self.assertEqual(load_named_profile(name).name, name)

    def test_builder_exports_head_twice_and_records_identical_artifacts(self):
        with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as output_dir:
            source = Path(source_dir)
            lock = source / "requirements"
            lock.mkdir()
            lock.joinpath("build.lock").write_text(
                "build==1.5.0\npackaging==25.0\npyproject_hooks==1.2.0\n"
                "setuptools==84.0.0\nwheel==0.48.0\n",
                encoding="utf-8",
            )
            calls = []

            def runner(command, **kwargs):
                calls.append(tuple(command))
                if command[:3] == ("git", "status", "--porcelain"):
                    return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
                if command[:3] == ("git", "rev-parse", "HEAD"):
                    return subprocess.CompletedProcess(command, 0, stdout="a" * 40 + "\n", stderr="")
                if command[:3] == ("git", "show", "-s"):
                    return subprocess.CompletedProcess(command, 0, stdout="1700000000\n", stderr="")
                if command[:3] == ("git", "archive", "--format=tar"):
                    buffer = io.BytesIO()
                    with tarfile.open(fileobj=buffer, mode="w") as archive:
                        info = tarfile.TarInfo("pyproject.toml")
                        payload = b"[build-system]\n"
                        info.size = len(payload)
                        archive.addfile(info, io.BytesIO(payload))
                    return subprocess.CompletedProcess(command, 0, stdout=buffer.getvalue(), stderr=b"")
                if "-c" in command:
                    code = command[command.index("-c") + 1]
                    if "platform.python_version" in code:
                        output = "3.11.15\n"
                    else:
                        output = json.dumps({
                            "build": "1.5.0", "packaging": "25.0", "pyproject-hooks": "1.2.0",
                            "setuptools": "84.0.0", "wheel": "0.48.0",
                        }) + "\n"
                    return subprocess.CompletedProcess(command, 0, stdout=output, stderr="")
                if command[1:4] == ("-m", "build", "--no-isolation"):
                    destination = Path(command[command.index("--outdir") + 1])
                    destination.joinpath("nous_os-0.2.0-py3-none-any.whl").write_bytes(b"wheel")
                    destination.joinpath("nous_os-0.2.0.tar.gz").write_bytes(b"sdist")
                    return subprocess.CompletedProcess(command, 0, stdout="built\n", stderr="")
                self.fail(f"unexpected command: {command}")

            manifest = build_release(source, output_dir, python="python3.11", runner=runner)
            self.assertTrue(manifest["reproducible"])
            self.assertEqual(manifest["source_commit"], "a" * 40)
            self.assertEqual(len(manifest["artifacts"]), 2)
            self.assertEqual(sum(command[1:3] == ("-m", "build") for command in calls), 2)
            self.assertTrue((Path(output_dir) / MANIFEST_NAME).is_file())

    def test_inspector_accepts_allowlisted_archives_and_dependency_notice(self):
        with tempfile.TemporaryDirectory() as directory:
            release = Path(directory)
            wheel = release / "nous_os-0.2.0-py3-none-any.whl"
            sdist = release / "nous_os-0.2.0.tar.gz"
            self._wheel(wheel)
            self._sdist(sdist)
            facts = [self._fact(path) for path in (wheel, sdist)]
            (release / MANIFEST_NAME).write_text(json.dumps({
                "schema_version": 1,
                "project": "nous-os",
                "source_commit": "a" * 40,
                "reproducible": True,
                "artifacts": facts,
            }), encoding="utf-8")
            report = inspect_release(ROOT, release)
            self.assertEqual(report["status"], "passed")
            self.assertEqual({item["kind"] for item in report["artifacts"]}, {"wheel", "sdist"})

    def test_privacy_and_archive_path_fail_closed(self):
        unsafe = (
            ("fixture.json", b'{"password":"private-value"}'),
            ("fixture.yaml", b'path: /Users/example/private.txt'),
            ("fixture.txt", b'token=private-value'),
        )
        for name, payload in unsafe:
            with self.subTest(name), self.assertRaises(ReleaseError):
                assert_release_payload_safe(name, payload)

    def _wheel(self, path):
        with zipfile.ZipFile(path, "w") as archive:
            for name in PROFILE_NAMES:
                archive.write(
                    ROOT / "src" / "nous_os" / "resources" / "profiles" / f"{name}.yaml",
                    f"nous_os/resources/profiles/{name}.yaml",
                )
            archive.writestr("nous_os-0.2.0.dist-info/METADATA", (
                "Metadata-Version: 2.4\nName: nous-os\nVersion: 0.2.0\n"
                "License-Expression: MIT\nRequires-Python: >=3.11\n"
                "Requires-Dist: PyYAML<7.0,>=6.0\n\n"
            ))

    def _sdist(self, path):
        with tarfile.open(path, "w:gz") as archive:
            for name in PROFILE_NAMES:
                payload = (ROOT / "src" / "nous_os" / "resources" / "profiles" / f"{name}.yaml").read_bytes()
                info = tarfile.TarInfo(f"nous_os-0.2.0/src/nous_os/resources/profiles/{name}.yaml")
                info.mode = 0o644
                info.size = len(payload)
                archive.addfile(info, io.BytesIO(payload))

    @staticmethod
    def _fact(path):
        payload = path.read_bytes()
        return {"filename": path.name, "sha256": hashlib.sha256(payload).hexdigest(), "size": len(payload)}


if __name__ == "__main__":
    unittest.main()
