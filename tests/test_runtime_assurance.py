from __future__ import annotations

import json
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from types import SimpleNamespace

from nous_os.assurance import InvariantRegistry, InvariantViolation
from nous_os.cli import _diagnose
from nous_os.core import Harness, HarnessContext, HarnessStopError, PluginConfig, Profile, RuntimePaths, load_profile
from nous_os.security import CredentialRef, EnvironmentCredentialProvider, PermissionDenied, ProfilePermissionPolicy
from nous_os.telemetry import JsonlTelemetrySink, OperationalTelemetry, TelemetryRecord


class RuntimeAssuranceUnitTests(unittest.TestCase):
    def test_credential_provider_is_dynamic_absence_aware_and_redacted(self):
        environment = {"FEATURE_KEY": "first-secret", "EMPTY_KEY": "  "}
        provider = EnvironmentCredentialProvider(environment)
        reference = CredentialRef("FEATURE_KEY")
        resolved = provider.resolve(reference)
        self.assertEqual(resolved.value, "first-secret")
        self.assertNotIn("first-secret", repr(resolved))
        environment["FEATURE_KEY"] = "rotated-secret"
        self.assertEqual(provider.resolve(reference).value, "rotated-secret")
        self.assertIsNone(provider.resolve(CredentialRef("EMPTY_KEY")))
        self.assertFalse(provider.describe(CredentialRef("MISSING_KEY")).configured)
        with self.assertRaises(ValueError):
            CredentialRef("not a ref")

    def test_permission_policy_is_closed_and_fails_before_start(self):
        ProfilePermissionPolicy(("filesystem-read",)).authorize("reader", ("filesystem-read",))
        with self.assertRaises(PermissionDenied):
            ProfilePermissionPolicy(()).authorize("writer", ("filesystem-write",))
        with self.assertRaisesRegex(ValueError, "unknown effects"):
            ProfilePermissionPolicy(("shell-anything",))

    def test_invariants_have_exact_selection_stable_attribution_and_no_duplicates(self):
        registry = InvariantRegistry(owner_allowlist=("selected",), owner_blocklist=("blocked",))
        registry.register("selected", "healthy", ("after-start",), lambda: None)
        registry.register("blocked", "ignored", ("after-start",), lambda: "failure")
        self.assertEqual(registry.check("after-start"), ("selected.healthy",))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            registry.register("selected", "healthy", ("after-start",), lambda: None)

        failing = InvariantRegistry()
        failing.register("evidence", "artifact-resolves", ("workflow-complete",), lambda: "missing")
        with self.assertRaises(InvariantViolation) as raised:
            failing.check("workflow-complete")
        self.assertEqual(
            (raised.exception.owner, raised.exception.invariant, raised.exception.phase),
            ("evidence", "artifact-resolves", "workflow-complete"),
        )

    def test_profile_v1_has_an_explicit_migration_error(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "v1.yaml"
            source.write_text("schema_version: 1\nname: old\nplugins: []\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must migrate"):
                load_profile(source)

    def test_real_profile_diagnosis_is_ready_and_contains_no_values_or_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            profile = load_profile("config/profiles/research.yaml")
            context = HarnessContext(profile_name=profile.name, paths=RuntimePaths.resolve(directory))
            harness = Harness(profile, context).start()
            try:
                report = harness.diagnose()
            finally:
                harness.stop()
            encoded = json.dumps(report, sort_keys=True)
            self.assertTrue(report["readiness"]["ready"])
            self.assertEqual(report["telemetry"]["mode"], "disabled")
            self.assertFalse(report["credentials"][0]["configured"])
            self.assertEqual(report["runtime_home"]["location"], "<runtime-home>")
            self.assertNotIn(directory, encoded)

    def test_diagnose_reports_unauthorized_effect_without_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            profile_path = Path(directory) / "denied.yaml"
            profile_path.write_text(
                "schema_version: 2\n"
                "name: denied\n"
                "allowed_effects: []\n"
                "plugins:\n"
                "  - id: telemetry\n"
                "    module: nous_os.plugins.telemetry\n",
                encoding="utf-8",
            )
            output = StringIO()
            with redirect_stdout(output):
                status = _diagnose(SimpleNamespace(
                    profile=str(profile_path), runtime_home=directory, json_output=True,
                ))
            report = json.loads(output.getvalue())
            self.assertEqual(status, 1)
            self.assertEqual(report["failure"], {
                "code": "PERMISSION_DENIED",
                "plugin": "telemetry",
                "denied_effects": ["filesystem-write"],
            })
            self.assertEqual(report["readiness"]["status"], "failed")

    def test_telemetry_is_best_effort_and_jsonl_contains_only_safe_fields(self):
        class BrokenSink:
            mode = "broken"

            def emit(self, record):
                raise OSError("disk unavailable")

            def shutdown(self):
                raise OSError("disk unavailable")

        telemetry = OperationalTelemetry("research", BrokenSink())
        self.assertFalse(telemetry.emit("workflow", "run", "passed"))
        self.assertFalse(telemetry.shutdown())
        self.assertEqual(telemetry.failures, 2)

        with tempfile.TemporaryDirectory() as directory:
            paths = RuntimePaths.resolve(directory).ensure()
            sink = JsonlTelemetrySink(paths)
            sink.emit(TelemetryRecord("plugin-start", "start", "passed", "research", plugin_id="evidence"))
            record = json.loads(sink.path.read_text(encoding="utf-8"))
            self.assertEqual(set(record), {"event", "phase", "outcome", "profile", "plugin_id"})
            self.assertEqual(sink.path.stat().st_mode & 0o777, 0o600)
            with self.assertRaisesRegex(ValueError, "unsafe telemetry"):
                TelemetryRecord("workflow", "run", "failed", "research", error_class="https://secret.invalid")


class RuntimeAssuranceLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.paths = RuntimePaths.resolve(self.temp.name)
        self.modules = []

    def tearDown(self):
        for name in self.modules:
            sys.modules.pop(name, None)
        self.temp.cleanup()

    def plugin(self, name, *, provides=(), start_error=None, stop_error=None, trace=None, effects=()):
        trace = trace if trace is not None else []

        class Plugin:
            id = name
            requires = ()

            def start(self, context, config):
                trace.append(f"start:{name}")
                for capability in provides:
                    context.register(capability, self)
                if start_error:
                    raise start_error

            def stop(self, context):
                trace.append(f"stop:{name}")
                if stop_error:
                    raise stop_error

        Plugin.provides = tuple(provides)
        Plugin.effects = tuple(effects)
        module_name = f"runtime_assurance_test.{name}"
        module = types.ModuleType(module_name)
        module.plugin = Plugin()
        sys.modules[module_name] = module
        self.modules.append(module_name)
        return PluginConfig(name, module_name)

    def test_partial_start_failure_cleans_every_started_plugin_in_reverse(self):
        trace = []
        first = self.plugin("first", provides=("first-cap",), trace=trace)
        second = self.plugin(
            "second",
            provides=("second-cap",),
            start_error=RuntimeError("boom"),
            stop_error=ValueError("cleanup"),
            trace=trace,
        )
        context = HarnessContext(profile_name="test", paths=self.paths)
        with self.assertRaisesRegex(RuntimeError, "boom") as raised:
            Harness(Profile(2, "test", (first, second)), context).start()
        self.assertEqual(trace, ["start:first", "start:second", "stop:second", "stop:first"])
        self.assertEqual(raised.exception.cleanup_failures[0].plugin_id, "second")
        self.assertEqual(context.capability_names(), ())
        self.assertEqual(context.readiness()["status"], "failed")

    def test_stop_continues_after_failure_and_is_idempotent(self):
        trace = []
        first = self.plugin("first", provides=("first-cap",), stop_error=RuntimeError("one"), trace=trace)
        second = self.plugin("second", provides=("second-cap",), stop_error=ValueError("two"), trace=trace)
        harness = Harness(
            Profile(2, "test", (first, second)),
            HarnessContext(profile_name="test", paths=self.paths),
        ).start()
        with self.assertRaises(HarnessStopError) as raised:
            harness.stop()
        self.assertEqual([failure.plugin_id for failure in raised.exception.failures], ["second", "first"])
        self.assertEqual(harness.context.capability_names(), ())
        harness.stop()
        self.assertEqual(trace.count("stop:first"), 1)
        self.assertEqual(trace.count("stop:second"), 1)

    def test_effect_denial_happens_before_any_plugin_starts(self):
        trace = []
        writer = self.plugin("writer", effects=("filesystem-write",), trace=trace)
        harness = Harness(Profile(2, "test", (writer,)), HarnessContext(profile_name="test", paths=self.paths))
        with self.assertRaises(PermissionDenied):
            harness.start()
        self.assertEqual(trace, [])


if __name__ == "__main__":
    unittest.main()
