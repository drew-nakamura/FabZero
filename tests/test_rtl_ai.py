import io
import json
import unittest
from unittest.mock import patch

from siliconos import ai
from siliconos.engine import DEFAULT, ROOT


class RtlAiTests(unittest.TestCase):
    def call_with(self, payload):
        return patch('urllib.request.urlopen', return_value=io.BytesIO(json.dumps(payload).encode()))

    def test_raw_source_and_server_side_contract(self):
        source = (ROOT / 'hardware/matmul.sv').read_text()
        with patch.dict('os.environ', GROQ_API_KEY='test-only-key', GROQ_MODEL='test-model'):
            with self.call_with({'choices': [{'finish_reason': 'stop', 'message': {'content': source}}]}) as request:
                self.assertEqual(ai.generate_rtl(DEFAULT, 'Multiply signed matrices'), source)
                sent = request.call_args.args[0]
                body = json.loads(sent.data)
                self.assertEqual(body['model'], 'test-model')
                self.assertEqual(body['messages'][1]['content'], 'Multiply signed matrices')
                self.assertIn('output reg [63:0] cycles', body['messages'][0]['content'])
                self.assertIn('UNMODIFIED external tb.sv', body['messages'][0]['content'])
                self.assertNotIn('test-only-key', json.dumps(body))
                self.assertEqual(sent.get_header('Authorization'), 'Bearer test-only-key')

    def test_rejects_incomplete_refused_and_malformed_responses(self):
        cases = [None, {}, {'choices': []}, {'choices': [None]},
                 {'choices': [{'message': None}]},
                 {'choices': [{'finish_reason': 'length', 'message': {'content': 'module matmul;'}}]},
                 {'choices': [{'finish_reason': 'stop', 'message': {'refusal': 'declined'}}]},
                 {'choices': [{'finish_reason': 'stop', 'message': {'content': 42}}]},
                 {'choices': [{'finish_reason': 'stop', 'message': {'content': ' '}}]}]
        with patch.dict('os.environ', GROQ_API_KEY='test-only-key', GROQ_MODEL='test-model'):
            for payload in cases:
                with self.subTest(payload=payload), self.call_with(payload), self.assertRaises(ValueError):
                    ai.generate_rtl(DEFAULT, 'matrix multiply')
            with patch('urllib.request.urlopen', side_effect=OSError('secret-provider-detail')):
                with self.assertRaisesRegex(ValueError, 'provider unavailable') as error:
                    ai.generate_rtl(DEFAULT, 'matrix multiply')
                self.assertNotIn('secret-provider-detail', str(error.exception))

    def test_rejects_inputs_before_network(self):
        with patch('urllib.request.urlopen') as request:
            with patch.dict('os.environ', {}, clear=True), self.assertRaisesRegex(ValueError, 'not configured'):
                ai.generate_rtl(DEFAULT, 'matrix multiply')
            with patch.dict('os.environ', GROQ_API_KEY='test-only-key', GROQ_MODEL='test-model'):
                for prompt in (None, '', ' ', 'a' * 4001):
                    with self.assertRaises(ValueError): ai.generate_rtl(DEFAULT, prompt)
                with self.assertRaises(ValueError):
                    ai.generate_rtl({**DEFAULT, 'operation': 'object_detection'}, 'detect objects')
            request.assert_not_called()
