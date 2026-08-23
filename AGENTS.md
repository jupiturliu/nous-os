# Repository instructions

- Python 3.11 is the supported runtime.
- Product Python code belongs under `src/nous_os`; do not add `sys.path` manipulation.
- Mutable runtime data belongs under `$NOUS_OS_HOME`, never in tracked source directories.
- Workflows write Evidence Events and Artifacts; public website data changes only through `nous-os publish-site-data`.
- Keep existing website URLs and `/api/*` route contracts stable.
- Use `PYTHONPATH=src python3 -m unittest discover -s tests` for the full test suite before installation, or `python3 -m unittest discover -s tests` after `pip install -e .`.
- Keep architectural decisions in `docs/adr` and domain vocabulary in `CONTEXT.md`.
