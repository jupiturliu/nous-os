from __future__ import annotations

import json
import threading
import time
import unittest
from pathlib import Path

from nous_os.checks import Gate, ProcessOutcome, gates_for_mode, run_check, run_gates


ROOT = Path(__file__).resolve().parents[1]


class GateGraphTests(unittest.TestCase):
    def test_modes_have_one_canonical_validated_graph(self):
        expected = {
            "quick": {"harness", "contracts", "site", "profile-student", "profile-research", "profile-trading-proof"},
            "full": {"harness", "contracts", "site", "profile-student", "profile-research", "profile-trading-proof", "scenarios", "unit-tests"},
            "ci": {"harness", "contracts", "site", "profile-student", "profile-research", "profile-trading-proof", "scenarios", "unit-tests", "source-clean"},
            "release": {"harness", "contracts", "site", "profile-student", "profile-research", "profile-trading-proof", "scenarios", "unit-tests", "source-clean", "entrypoint"},
        }
        for mode, ids in expected.items():
            gates = gates_for_mode(mode)
            self.assertEqual({gate.id for gate in gates}, ids)
            results = run_gates(gates, lambda _: ProcessOutcome(0), max_workers=3)
            self.assertEqual([result.gate_id for result in results], [gate.id for gate in gates])
            self.assertTrue(all(result.status == "passed" for result in results))

    def test_invalid_dependencies_duplicates_and_cycles_fail_before_execution(self):
        invalid_graphs = (
            (Gate("a", "A", ("true",), needs=("missing",)),),
            (Gate("a", "A", ("true",)), Gate("a", "Again", ("true",))),
            (Gate("a", "A", ("true",), needs=("b",)), Gate("b", "B", ("true",), needs=("a",))),
        )
        for gates in invalid_graphs:
            with self.assertRaises(ValueError):
                run_gates(gates, lambda _: self.fail("executor must not run"))

    def test_failure_skips_dependents_but_independent_gate_continues(self):
        gates = (
            Gate("failed", "Failed", ("false",)),
            Gate("dependent", "Dependent", ("true",), needs=("failed",)),
            Gate("independent", "Independent", ("true",)),
        )

        def execute(gate):
            return ProcessOutcome(9, stderr="expected failure") if gate.id == "failed" else ProcessOutcome(0)

        results = run_gates(gates, execute, max_workers=2)
        self.assertEqual([result.status for result in results], ["failed", "skipped", "passed"])
        self.assertEqual(results[1].skipped_because, ("failed",))
        self.assertEqual(results[0].exit_code, 9)
        self.assertEqual(results[0].stderr, "expected failure")

    def test_scheduler_honors_worker_bound_and_keeps_report_order_stable(self):
        gates = tuple(Gate(f"gate-{index}", f"Gate {index}", ("true",)) for index in range(6))
        lock = threading.Lock()
        current = 0
        peak = 0

        def execute(_):
            nonlocal current, peak
            with lock:
                current += 1
                peak = max(peak, current)
            time.sleep(0.01)
            with lock:
                current -= 1
            return ProcessOutcome(0)

        results = run_gates(gates, execute, max_workers=2)
        self.assertEqual(peak, 2)
        self.assertEqual([result.gate_id for result in results], [gate.id for gate in gates])

    def test_results_have_machine_readable_independent_outcomes(self):
        gate = Gate("signal", "Signal", ("fixture",))
        result = run_gates(
            (gate,),
            lambda _: ProcessOutcome(None, stdout="out", stderr="err", signal=15, error="terminated"),
        )[0]
        encoded = json.loads(json.dumps(result.as_dict()))
        self.assertEqual(encoded["status"], "failed")
        self.assertEqual(encoded["signal"], 15)
        self.assertIsNone(encoded["exit_code"])
        self.assertEqual(encoded["error"], "terminated")

    def test_real_quick_report_normalizes_machine_specific_roots(self):
        report = run_check(ROOT, "quick", max_workers=2)
        serialized = json.dumps(report.as_dict())
        self.assertTrue(report.ok)
        self.assertNotIn(str(ROOT), serialized)
        self.assertIn("<project-root>", serialized)


if __name__ == "__main__":
    unittest.main()
