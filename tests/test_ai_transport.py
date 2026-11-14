import io
import json
import unittest
import urllib.error
from unittest.mock import patch
from siliconos import ai


class TransportTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict('os.environ', GROQ_API_KEY='private-test-key', GROQ_MODEL='test-model')
        self.env.start()
        self.addCleanup(self.env.stop)

    def error(self, code, headers=None):
        return urllib.error.HTTPError(ai.GROQ_URL, code, 'secret diagnostic', headers or {}, io.BytesIO(b'secret body'))

    def test_transient_retry_then_success(self):
        for error in (self.error(429), self.error(503), urllib.error.URLError('secret network detail')):
            with self.subTest(error=type(error)), patch('siliconos.ai.time.sleep') as sleep, patch('urllib.request.urlopen', side_effect=[error, io.BytesIO(b'{"choices": []}')]) as call:
                self.assertEqual(ai._completion({'model': 'test-model'}), {'choices': []})
                self.assertEqual(call.call_count, 2)
                self.assertEqual(call.call_args.kwargs['timeout'], 20)
                sleep.assert_called_once()

    def test_permanent_errors_not_retried_and_sanitized(self):
        for code, expected in ((401, 'authentication'), (403, 'authentication'), (404, 'model'), (400, 'JSON-schema'), (422, 'JSON-schema')):
            with self.subTest(code=code), patch('urllib.request.urlopen', side_effect=self.error(code)) as call, self.assertRaisesRegex(ValueError, expected) as caught:
                ai._completion({})
            self.assertEqual(call.call_count, 1)
            self.assertNotIn('secret', str(caught.exception))
            self.assertNotIn('private-test-key', str(caught.exception))

    def test_retry_is_bounded_and_honors_long_retry_after(self):
        with patch('siliconos.ai.time.sleep'), patch('urllib.request.urlopen', side_effect=[self.error(503), self.error(503)]) as call, self.assertRaisesRegex(ValueError, 'provider unavailable'):
            ai._completion({})
        self.assertEqual(call.call_count, 2)
        with patch('urllib.request.urlopen', side_effect=self.error(429, {'Retry-After': '60'})) as call, self.assertRaisesRegex(ValueError, 'rate limit'):
            ai._completion({})
        self.assertEqual(call.call_count, 1)

    def test_malformed_provider_data_is_not_retried(self):
        for data in (b'not-json', b'null', b'[]'):
            with patch('urllib.request.urlopen', return_value=io.BytesIO(data)) as call, self.assertRaises(ValueError):
                ai._completion({})
            self.assertEqual(call.call_count, 1)

    def test_spec_bad_envelope_is_actionable(self):
        for choices in ([None], [{'message': None}], [{'message': {'content': '{'}, 'finish_reason': 'stop'}]):
            with patch('urllib.request.urlopen', return_value=io.BytesIO(json.dumps({'choices': choices}).encode())), self.assertRaises(ValueError):
                ai.generate('multiply matrices')
