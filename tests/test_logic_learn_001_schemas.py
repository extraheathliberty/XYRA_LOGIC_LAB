import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
FIXTURES = ROOT / "fixtures"


class TestLogicLearn001Schemas(unittest.TestCase):
    def load_json(self, path):
        return json.loads(path.read_text(encoding="utf-8"))

    def test_request_fixtures_validate(self):
        schema = self.load_json(SCHEMAS / "logic_learn_001_request.schema.json")
        validator = Draft202012Validator(schema)
        for name in [
            "logic_learn_001_student001_four_book.json",
            "logic_learn_001_good.json",
            "logic_learn_001_bad.json",
            "logic_learn_001_blind.json",
        ]:
            with self.subTest(name=name):
                validator.validate(self.load_json(FIXTURES / name))

    def test_response_schema_accepts_validator_output(self):
        from xyra_logic.learn_validation import validate_learning_packet

        request = self.load_json(FIXTURES / "logic_learn_001_good.json")
        response = validate_learning_packet(request)
        schema = self.load_json(SCHEMAS / "logic_learn_001_response.schema.json")
        Draft202012Validator(schema).validate(response)


if __name__ == "__main__":
    unittest.main()
