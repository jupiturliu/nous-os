# ADR 0003: Spec-Driven Development for Software Changes

## Status

Accepted

## Decision

Behavior-changing repository work is governed by the Software Change Spec Module under `src/nous_os/specs`. Each Software Change has a tracked package under `specs/changes/<change-id>/`: YAML `manifest.yaml`, `spec.yaml`, and `implementation.yaml`; JSON `approval.json` and `verification.json`.

Approval must be a separate human decision recorded before implementation. It binds the Spec and Implementation Plan by SHA-256. Protected implementation commits carry exactly one `Spec-Ref` trailer and stay within planned paths. Verification runs only named unittest or built-in Harness checks; arbitrary shell from a Spec is forbidden. A passing VerificationReport is both tracked in Git and stored as an Artifact referenced by a `spec.verification-recorded` Evidence Event.

The Module is separate from Domain Compilation. Domain Compilation decides whether a domain target is feasible; the Software Change Spec Module governs how this repository changes.

## Consequences

Local `commit-msg` and `pre-push` hooks plus CI enforce the lifecycle immediately for protected paths. Pure documentation and metadata changes remain exempt except `AGENTS.md` and `CONTEXT.md`. Approved Spec and Implementation Plan files are immutable; changed intent or paths require a new change ID with `supersedes` provenance. Existing commits are not retroactively governed.

The Module provides a small command Interface while Git-history inspection, strict schemas, path policy, safe check execution, approval verification, and evidence write-back remain local to its implementation.
