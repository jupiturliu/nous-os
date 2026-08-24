"""Keyless installed-wheel scenario, deliberately independent of the checkout."""

from __future__ import annotations

import json
import tempfile

from nous_os.core import Harness, HarnessContext, RuntimePaths
from nous_os.core.profiles import load_named_profile


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="nous-os-wheel-scenario-") as directory:
        profile = load_named_profile("student")
        context = HarnessContext(profile_name=profile.name, paths=RuntimePaths.resolve(directory))
        harness = Harness(profile, context).start()
        try:
            record = context.resolve("student-sandbox").save({
                "session_id": "packaged-smoke",
                "worksheet": {
                    "question": "Compare two synthetic explanations.",
                    "boundary": "No final answer.",
                    "revised_plan": "Check evidence and reflect.",
                },
                "reflection": {"reflect_next": "Compare evidence."},
            })
            harness.check()
            status = "passed" if record["session_id"] == "packaged-smoke" else "failed"
        finally:
            harness.stop()
    print(json.dumps({"schema_version": 1, "status": status, "profile": "student"}, sort_keys=True))
    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
