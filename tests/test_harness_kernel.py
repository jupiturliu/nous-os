from __future__ import annotations

import json
import sys
import tempfile
import threading
import types
import unittest
from pathlib import Path

from nous_os.core import EvidenceEvent, EventStore, Harness, HarnessContext, PluginConfig, Profile, RuntimePaths, load_profile
from nous_os.artifacts.projections import project_latest_heartbeat
from nous_os.workflows.student_sandbox import StudentSandboxStore


class _FakePlugin:
    def __init__(self, plugin_id, *, requires=(), provides=(), trace=None):
        self.id = plugin_id
        self.requires = tuple(requires)
        self.provides = tuple(provides)
        self.trace = trace if trace is not None else []

    def start(self, context, config):
        self.trace.append(f"start:{self.id}")
        for name in self.provides:
            context.register(name, {"plugin": self.id, "config": config})

    def stop(self, context):
        self.trace.append(f"stop:{self.id}")
        for name in self.provides:
            context.unregister(name)


class HarnessKernelTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.paths = RuntimePaths.resolve(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def _module(self, name, plugin):
        module = types.ModuleType(name)
        module.plugin = plugin
        sys.modules[name] = module
        self.addCleanup(sys.modules.pop, name, None)

    def test_profile_loader_is_strict(self):
        for name in ("student", "research", "trading-proof"):
            profile = load_profile(f"config/profiles/{name}.yaml")
            self.assertEqual(profile.name, name)
        invalid = Path(self.temp.name) / "invalid.yaml"
        invalid.write_text("schema_version: 1\nname: bad\nplugins: []\nsurprise: true\n")
        with self.assertRaisesRegex(ValueError, "unknown profile fields"):
            load_profile(invalid)

    def test_harness_orders_plugins_and_stops_in_reverse(self):
        trace = []
        self._module("test.provider", _FakePlugin("provider", provides=("clock",), trace=trace))
        self._module("test.consumer", _FakePlugin("consumer", requires=("clock",), provides=("workflow",), trace=trace))
        profile = Profile(1, "test", (
            PluginConfig("consumer", "test.consumer"),
            PluginConfig("provider", "test.provider"),
        ))
        context = HarnessContext(profile_name="test", paths=self.paths)
        harness = Harness(profile, context).start()
        self.assertEqual(trace, ["start:provider", "start:consumer"])
        self.assertTrue(context.has("workflow"))
        harness.stop()
        self.assertEqual(trace[-2:], ["stop:consumer", "stop:provider"])

    def test_harness_rejects_missing_duplicate_and_cycle(self):
        self._module("test.missing", _FakePlugin("missing", requires=("absent",)))
        context = HarnessContext(profile_name="test", paths=self.paths)
        with self.assertRaisesRegex(ValueError, "missing capability"):
            Harness(Profile(1, "test", (PluginConfig("missing", "test.missing"),)), context).start()

        self._module("test.a", _FakePlugin("a", requires=("b-cap",), provides=("a-cap",)))
        self._module("test.b", _FakePlugin("b", requires=("a-cap",), provides=("b-cap",)))
        cycle = Profile(1, "test", (PluginConfig("a", "test.a"), PluginConfig("b", "test.b")))
        with self.assertRaisesRegex(ValueError, "cycle"):
            Harness(cycle, context).start()

        self._module("test.c", _FakePlugin("c", provides=("same",)))
        self._module("test.d", _FakePlugin("d", provides=("same",)))
        duplicate = Profile(1, "test", (PluginConfig("c", "test.c"), PluginConfig("d", "test.d")))
        with self.assertRaisesRegex(ValueError, "duplicate capability"):
            Harness(duplicate, context).start()


class EvidencePlaneTests(unittest.TestCase):
    def test_event_and_artifact_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = RuntimePaths.resolve(directory)
            store = EventStore(paths)
            artifact = store.write_artifact("test", {"answer": 42}, "artifact-1")
            event = EvidenceEvent(
                event_type="test.completed",
                run_id="run-1",
                profile="test",
                producer="unit-test",
                payload={"ok": True},
                evidence_refs=(artifact,),
            )
            store.append(event)
            records = tuple(store.events())
            self.assertEqual(records[0]["event_id"], event.event_id)
            artifact_path = paths.home / artifact.path
            self.assertEqual(json.loads(artifact_path.read_text()), {"answer": 42})
            self.assertEqual(artifact_path.stat().st_mode & 0o777, 0o600)

    def test_student_records_are_redacted_and_event_backed(self):
        with tempfile.TemporaryDirectory() as directory:
            context = HarnessContext(profile_name="student", paths=RuntimePaths.resolve(directory))
            store = StudentSandboxStore(context)
            record = store.save({
                "session_id": "student-session-1",
                "worksheet": {"question": "Email me at learner@example.com", "boundary": "No final answers"},
                "reflection": {},
            })
            self.assertIn("[redacted-email]", record["worksheet"]["question"])
            self.assertTrue(record["privacy"]["private_pattern_detected"])
            self.assertEqual(store.read("student-session-1")["session_id"], "student-session-1")
            self.assertEqual(store.list()[0]["session_id"], "student-session-1")

    def test_heartbeat_projection_replays_deterministically_from_event_and_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = RuntimePaths.resolve(directory)
            store = EventStore(paths)
            snapshot = {"research_record": {"run_id": "run-1", "privacy": {"contains_private_student_data": False}}}
            artifact = store.write_artifact("heartbeat", snapshot, "run-1")
            store.append(EvidenceEvent(
                event_type="heartbeat.completed",
                run_id="run-1",
                profile="research",
                producer="heartbeat",
                evidence_refs=(artifact,),
            ))
            dashboard, latest = project_latest_heartbeat(store)
            first_dashboard = dashboard.read_bytes()
            first_latest = latest.read_bytes()
            dashboard.unlink()
            latest.unlink()
            project_latest_heartbeat(store)
            self.assertEqual(dashboard.read_bytes(), first_dashboard)
            self.assertEqual(latest.read_bytes(), first_latest)

    def test_concurrent_appends_keep_jsonl_intact(self):
        with tempfile.TemporaryDirectory() as directory:
            store = EventStore(RuntimePaths.resolve(directory))
            threads = [threading.Thread(target=store.append, args=(EvidenceEvent(
                event_type="test.concurrent",
                run_id=f"run-{index}",
                profile="test",
                producer="unit-test",
            ),)) for index in range(24)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            records = tuple(store.events())
            self.assertEqual(len(records), 24)
            self.assertEqual(len({record["event_id"] for record in records}), 24)


if __name__ == "__main__":
    unittest.main()
