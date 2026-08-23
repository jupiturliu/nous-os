# Repository instructions

- Python 3.11 is the supported runtime.
- Product Python code belongs under `src/nous_os`; do not add `sys.path` manipulation.
- Mutable runtime data belongs under `$NOUS_OS_HOME`, never in tracked source directories.
- Workflows write Evidence Events and Artifacts; public website data changes only through `nous-os publish-site-data`.
- Keep existing website URLs and `/api/*` route contracts stable.
- Use `PYTHONPATH=src python3 -m unittest discover -s tests` for the full test suite before installation, or `python3 -m unittest discover -s tests` after `pip install -e .`.
- Keep architectural decisions in `docs/adr` and domain vocabulary in `CONTEXT.md`.
- Before changing behavior under protected paths, create and commit a Software Change Spec with `nous-os spec init`, obtain a separate explicit Approval with `nous-os spec approve`, and keep implementation inside its approved paths.
- Put exactly one `Spec-Ref: <change-id>` trailer on every protected implementation commit. Run `nous-os spec verify <change-id>` on the clean latest implementation commit and commit the generated VerificationReport separately.
- Pure documentation changes are exempt, except changes to `AGENTS.md` and `CONTEXT.md`. There is no bypass for protected changes; revise the Spec through a superseding change when approved intent or paths change.
