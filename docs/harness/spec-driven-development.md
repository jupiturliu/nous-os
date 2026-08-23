# Spec-Driven Development

The Software Change Spec Module turns an intended repository behavior change into reviewable, executable evidence:

```text
draft Spec + Implementation Plan
  → separate human Approval
  → implementation commits carrying Spec-Ref
  → named safe checks
  → tracked VerificationReport + runtime Artifact + Evidence Event
```

It governs software changes; it does not replace the Domain Compilation Module or define a universal domain DSL.

## Protected scope

`config/spec-policy.yaml` is authoritative. Product source, tests, configuration, contracts, apps, deployment/scripts, CI/hooks, runtime configuration, `AGENTS.md`, and `CONTEXT.md` require a Spec. Pure files under `docs/` plus `README.md`, `ARCHITECTURE.md`, `LICENSE`, and `.gitignore` are exempt unless combined with a protected change; then every changed path must be in the Implementation Plan.

## Standard workflow

Create and complete a draft package:

```bash
nous-os spec init 0002-short-change-name --title "Short change title"
nous-os spec validate 0002-short-change-name
git add specs/changes/0002-short-change-name
git commit -m "spec: define short change"
```

After independent review, record Approval in a separate commit:

```bash
NOUS_OS_HOME=/tmp/nous-os-spec nous-os spec approve 0002-short-change-name \
  --by github-login \
  --reason "Requirements and acceptance criteria approved"
git add specs/changes/0002-short-change-name
git commit -m "spec: approve short change"
```

For GitHub's dual channel, use `--channel pull-request --reference https://github.com/OWNER/REPO/pull/NUMBER`. CI verifies that the PR was merged and that the named approver submitted an `APPROVED` review.

Implementation commits use exactly one trailer:

```text
feat: implement short change

Spec-Ref: 0002-short-change-name
```

On the clean latest implementation commit, run verification. It executes only checks named in `implementation.yaml`:

```bash
NOUS_OS_HOME=/tmp/nous-os-spec nous-os spec verify 0002-short-change-name
git add specs/changes/0002-short-change-name/verification.json
git commit -m "spec: verify short change" -m "Spec-Ref: 0002-short-change-name"
```

`unittest` targets and built-in `harness`, `profiles`, `contracts`, and `site` checks are allowed. Arbitrary shell commands, globs, parent paths, same-commit approval, dirty-worktree final verification, and stale reports are rejected.

## Gate commands

The hooks call these commands automatically:

```bash
nous-os spec gate --staged --message-file .git/COMMIT_EDITMSG
nous-os spec gate --range BASE..HEAD
```

The `commit-msg` hook checks approval timing and path coverage. The `pre-push` hook and CI require a passing VerificationReport bound to the latest implementation commit. There is no emergency bypass.

Approval and VerificationReport events are written below `$NOUS_OS_HOME`. Keep that runtime outside the repository.
