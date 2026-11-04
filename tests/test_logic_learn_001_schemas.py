import json
import unittest
from pathlib import Path

from xyra_logic.learn_validation import validate_learning_packet

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
FIXTURES = ROOT / "fixtures"


class TestLogicLearn001Schemas(unittest.TestCase):
    def load_json(self, path):
        return json.loads(path.read_text(encoding="utf-8"))

    def test_request_schema_declares_required_contract(self):
        schema = self.load_json(SCHEMAS / "logic_learn_001_request.schema.json")
        required = set(schema["required"])
        expected = {
            "schema_version",
            "learner_id",
            "source_work_id",
            "source_authority_ref",
            "task",
            "observed_facts",
            "not_established",
            "competing_hypotheses",
            "source_dependencies",
            "information_gaps",
            "next_collection",
            "premises",
            "disconfirming_evidence",
            "claimed_conclusion",
            "terminal_state",
        }
        self.assertEqual(required, expected)
        self.assertEqual(
            schema["properties"]["schema_version"]["const"],
            "LOGIC-LEARN-001/request/v1",
        )

    def test_all_request_fixtures_match_required_contract(self):
        schema = self.load_json(SCHEMAS / "logic_learn_001_request.schema.json")
        required = schema["required"]
        for name in [
            "logic_learn_001_student001_four_book.json",
            "logic_learn_001_good.json",
            "logic_learn_001_bad.json",
            "logic_learn_001_blind.json",
        ]:
            with self.subTest(name=name):
                data = self.load_json(FIXTURES / name)
                self.assertEqual(data["schema_version"], "LOGIC-LEARN-001/request/v1")
                for key in required:
                    self.assertIn(key, data)

    def test_response_contract_matches_validator_output(self):
        request = self.load_json(FIXTURES / "logic_learn_001_good.json")
        response = validate_learning_packet(request)
        schema = self.load_json(SCHEMAS / "logic_learn_001_response.schema.json")
        self.assertEqual(
            response["schema_version"],
            schema["properties"]["schema_version"]["const"],
        )
        for key in schema["required"]:
            self.assertIn(key, response)


if __name__ == "__main__":
    unittest.main()
