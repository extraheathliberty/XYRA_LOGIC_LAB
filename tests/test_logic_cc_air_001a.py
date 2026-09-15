import unittest

from xyra_logic import (
    And,
    Atom,
    Implies,
    Not,
    Or,
    ReasoningAssurancePacketError,
    expression_from_wire,
    expression_to_wire,
    replay_reasoning_assurance_packet,
)


class TestLogicCcAir001A(unittest.TestCase):
    def setUp(self):
        self.P = Atom("P")
        self.Q = Atom("Q")

    def test_atom_round_trip(self):
        wire = expression_to_wire(self.P)

        self.assertEqual(
            wire,
            {
                "type": "ATOM",
                "name": "P",
            },
        )
        self.assertEqual(expression_from_wire(wire), self.P)

    def test_nested_expression_round_trip(self):
        expression = Implies(
            And(self.P, Not(self.Q)),
            Or(self.Q, self.P),
        )

        wire = expression_to_wire(expression)
        restored = expression_from_wire(wire)

        self.assertEqual(restored, expression)

    def test_valid_modus_ponens_packet_replay(self):
        packet = {
            "schema_id": "XYRA_LOGIC_REASONING_ASSURANCE_REQUEST_V1",
            "correlation_id": "CC-TASK-001",
            "object_registry": {
                "D1": {
                    "type": "ATOM",
                    "name": "P",
                },
                "D2": {
                    "type": "IMPLIES",
                    "left": {"type": "ATOM", "name": "P"},
                    "right": {"type": "ATOM", "name": "Q"},
                },
            },
            "step": {
                "step_id": "D3",
                "input_object_ids": ["D1", "D2"],
                "rule_id": "PROP-MP-001",
                "proposed_output": {
                    "type": "ATOM",
                    "name": "Q",
                },
            },
        }

        result = replay_reasoning_assurance_packet(packet)

        self.assertEqual(
            result["schema_id"],
            "XYRA_LOGIC_REASONING_ASSURANCE_RESULT_V1",
        )
        self.assertEqual(result["correlation_id"], "CC-TASK-001")
        self.assertEqual(result["step_id"], "D3")
        self.assertEqual(result["input_object_ids"], ["D1", "D2"])
        self.assertEqual(result["rule_id"], "PROP-MP-001")
        self.assertEqual(result["status"], "VALID_STEP")
        self.assertEqual(
            result["derived_output"],
            {
                "type": "ATOM",
                "name": "Q",
            },
        )
        self.assertIsNone(result["failure_reason"])

    def test_invalid_rule_application_remains_invalid(self):
        packet = {
            "schema_id": "XYRA_LOGIC_REASONING_ASSURANCE_REQUEST_V1",
            "correlation_id": "CC-TASK-002",
            "object_registry": {
                "D1": {
                    "type": "IMPLIES",
                    "left": {"type": "ATOM", "name": "P"},
                    "right": {"type": "ATOM", "name": "Q"},
                },
                "D2": {
                    "type": "ATOM",
                    "name": "Q",
                },
            },
            "step": {
                "step_id": "D3",
                "input_object_ids": ["D1", "D2"],
                "rule_id": "PROP-MP-001",
                "proposed_output": {
                    "type": "ATOM",
                    "name": "P",
                },
            },
        }

        result = replay_reasoning_assurance_packet(packet)

        self.assertEqual(result["status"], "INVALID_STEP")
        self.assertEqual(
            result["failure_reason"],
            "RULE_INPUT_MISMATCH",
        )
        self.assertIsNone(result["derived_output"])

    def test_declared_input_order_is_preserved(self):
        packet = {
            "schema_id": "XYRA_LOGIC_REASONING_ASSURANCE_REQUEST_V1",
            "correlation_id": "CC-TASK-003",
            "object_registry": {
                "D1": {
                    "type": "ATOM",
                    "name": "P",
                },
                "D2": {
                    "type": "IMPLIES",
                    "left": {"type": "ATOM", "name": "P"},
                    "right": {"type": "ATOM", "name": "Q"},
                },
            },
            "step": {
                "step_id": "D3",
                "input_object_ids": ["D2", "D1"],
                "rule_id": "PROP-MP-001",
                "proposed_output": {
                    "type": "ATOM",
                    "name": "Q",
                },
            },
        }

        result = replay_reasoning_assurance_packet(packet)

        self.assertEqual(
            result["input_object_ids"],
            ["D2", "D1"],
        )
        self.assertEqual(result["status"], "INVALID_STEP")
        self.assertEqual(
            result["failure_reason"],
            "RULE_INPUT_MISMATCH",
        )

    def test_missing_dependency_fails_closed(self):
        packet = {
            "schema_id": "XYRA_LOGIC_REASONING_ASSURANCE_REQUEST_V1",
            "correlation_id": "CC-TASK-004",
            "object_registry": {
                "D1": {
                    "type": "ATOM",
                    "name": "P",
                },
            },
            "step": {
                "step_id": "D3",
                "input_object_ids": ["D1", "D2"],
                "rule_id": "PROP-MP-001",
                "proposed_output": {
                    "type": "ATOM",
                    "name": "Q",
                },
            },
        }

        result = replay_reasoning_assurance_packet(packet)

        self.assertEqual(result["status"], "INVALID_STEP")
        self.assertEqual(
            result["failure_reason"],
            "MISSING_DEPENDENCY",
        )
        self.assertIsNone(result["derived_output"])

    def test_unknown_expression_type_fails_closed(self):
        with self.assertRaises(ReasoningAssurancePacketError):
            expression_from_wire(
                {
                    "type": "MAGIC_THINKING",
                    "name": "P",
                }
            )

    def test_unknown_schema_fails_closed(self):
        packet = {
            "schema_id": "NOT-A-REAL-SCHEMA",
            "correlation_id": "CC-TASK-005",
            "object_registry": {
                "D1": {
                    "type": "ATOM",
                    "name": "P",
                },
            },
            "step": {
                "step_id": "D2",
                "input_object_ids": ["D1"],
                "rule_id": "PROP-AND-E-L-001",
                "proposed_output": {
                    "type": "ATOM",
                    "name": "P",
                },
            },
        }

        with self.assertRaises(ReasoningAssurancePacketError):
            replay_reasoning_assurance_packet(packet)

    def test_repeated_packet_replay_is_identical(self):
        packet = {
            "schema_id": "XYRA_LOGIC_REASONING_ASSURANCE_REQUEST_V1",
            "correlation_id": "CC-TASK-006",
            "object_registry": {
                "D1": {
                    "type": "ATOM",
                    "name": "P",
                },
                "D2": {
                    "type": "IMPLIES",
                    "left": {"type": "ATOM", "name": "P"},
                    "right": {"type": "ATOM", "name": "Q"},
                },
            },
            "step": {
                "step_id": "D3",
                "input_object_ids": ["D1", "D2"],
                "rule_id": "PROP-MP-001",
                "proposed_output": {
                    "type": "ATOM",
                    "name": "Q",
                },
            },
        }

        first = replay_reasoning_assurance_packet(packet)
        second = replay_reasoning_assurance_packet(packet)

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
