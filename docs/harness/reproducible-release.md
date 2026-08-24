# Reproducible Python Release

The Release Builder Module proves that one clean source commit can become an auditable Python wheel and sdist. It does not publish, tag, sign, or choose a version.

## Interface

Install the exact build environment in Python 3.11, then run the canonical Gate:

```bash
python3.11 -m pip install --requirement requirements/build.lock
python3.11 -m pip install --editable .
nous-os --runtime-home /tmp/nous-os-release check --mode release
```

Release mode runs the complete `ci` graph, then this serial chain:

```text
release-build -> release-inspect -> installed-wheel
```

- `release-build` requires a clean checkout, exports `HEAD` twice, uses the Git commit timestamp as `SOURCE_DATE_EPOCH`, and rejects non-identical artifact bytes.
- `release-inspect` verifies SHA-256 provenance, archive paths and modes, Profile mirrors, package metadata, privacy constraints, and the runtime dependency/license contract.
- `installed-wheel` creates a disposable environment outside the checkout, removes source `PYTHONPATH` and secret-shaped variables, installs the wheel, validates all Profiles, runs diagnose, and executes a synthetic Student Sandbox scenario.

The resulting external directory contains one wheel, one sdist, and `release-manifest.json`. The manifest uses repository-relative artifact names and contains no local paths or credential values.

## Canonical Profiles

Packaged Profile YAML is canonical under `src/nous_os/resources/profiles`. Files under `config/profiles` are developer-visible mirrors. Tests and archive inspection require exact bytes, preventing the installed composition from drifting away from checkout behavior.

## Dependency and license closure

`pyproject.toml` declares the runtime closure. `contracts/release/runtime-dependencies.json` is its machine-readable allowlist, and `THIRD_PARTY_NOTICES.md` is the reviewed human notice. Release inspection fails if wheel metadata or either notice differs.

Build-only packages are exact-pinned in `requirements/build.lock`; they do not become runtime dependencies. Dependabot proposes grouped monthly updates, but it cannot merge or bypass Software Change Approval.

## GitHub artifacts

`.github/workflows/release-artifacts.yml` runs only on manual dispatch or a human-created `v*` tag. It has `contents: read`, runs the same release Gate, and uploads workflow artifacts for 30 days. It has no registry write permission and performs no publication.

## Human authority

Artifact hashes prove identity, not publisher identity. A human still chooses the commit, version, tag, signing approach, and whether a verified artifact is released. Registry upload and signing require a later approved Spec.
