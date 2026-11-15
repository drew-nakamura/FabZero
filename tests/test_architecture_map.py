import io
import json
import unittest
from unittest.mock import patch

from siliconos import ai
from siliconos.engine import DEFAULT


def provider(payload):
    return io.BytesIO(json.dumps({"choices": [{"finish_reason": "stop", "message": {"content": json.dumps(payload)}}]}).encode())


class ArchitectureMapTests(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict("os.environ", GROQ_API_KEY="test-key", GROQ_MODEL="test-model")
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def test_constrained_explanation_is_accepted(self):
        answer = {"title": "A conceptual compute path", "summary": "Four lanes trade added arithmetic capacity for fewer modeled compute cycles.", "selection_reason": "The reviewed objective prefers lower modeled compute cycles.", "assumptions": ["The requested clock is not a measured board clock."]}
        with patch("urllib.request.urlopen", return_value=provider(answer)) as call:
            result = ai.generate_architecture_map(DEFAULT)
        self.assertEqual(result, answer)
        body = json.loads(call.call_args.args[0].data)
        self.assertEqual(body["response_format"]["json_schema"]["name"], "architecture_map_explanation")
        self.assertIn("may not invent blocks", body["messages"][0]["content"])

    def test_untrusted_explanation_is_rejected(self):
        bad = {"title": "A", "summary": "B", "selection_reason": "C", "assumptions": []}
        with patch("urllib.request.urlopen", return_value=provider(bad)):
            with self.assertRaisesRegex(ValueError, "assumptions"):
                ai.generate_architecture_map(DEFAULT)

        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(ValueError, "not configured"):
                ai.generate_architecture_map(DEFAULT)


if __name__ == "__main__":
    unittest.main()
