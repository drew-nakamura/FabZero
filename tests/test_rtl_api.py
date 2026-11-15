import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import server
from siliconos.engine import DEFAULT
from test_rtl_simulation import SOURCE, SLOW_SOURCE


class GeneratedRtlApiTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.db_patch = patch.object(server, 'DB', Path(folder.name) / 'test.db')
        self.db_patch.start()
        self.addCleanup(self.db_patch.stop)
        with server.connect(): pass
        self.body = {'spec': DEFAULT, 'prompt': 'Multiply signed INT8 matrices', 'lanes': 4}

    def post(self, body=None, origin=None, length=None):
        payload = json.dumps(self.body if body is None else body).encode()
        handler = object.__new__(server.Handler)
        handler.path = '/api/generate-rtl'
        handler.server = SimpleNamespace(server_port=8000)
        handler.headers = {'Content-Length': str(length if length is not None else len(payload))}
        if origin: handler.headers['Origin'] = origin
        handler.rfile = io.BytesIO(payload)
        replies = []
        handler.reply = lambda status, data: replies.append((status, data))
        handler.do_POST()
        self.assertEqual(len(replies), 1)
        return replies[0]

    def counts(self):
        with server.connect() as db:
            return tuple(db.execute('SELECT COUNT(*) FROM ' + table).fetchone()[0] for table in ('runs', 'events'))

    def test_success_persists_only_verified_generated_source(self):
        with patch('server.ai.generate_rtl', return_value=SLOW_SOURCE) as provider:
            status, result = self.post(origin='http://127.0.0.1:8000')
        self.assertEqual(status, 200, result)
        provider.assert_called_once_with(DEFAULT, self.body['prompt'])
        self.assertEqual(result['evidence'], 'ai_generated_rtl')
        self.assertEqual(result['cycles'], 129)
        self.assertEqual(self.counts(), (1, 1))
        self.assertFalse(server.RUN_LOCK.locked())
        with server.connect() as db:
            self.assertEqual(json.loads(db.execute('SELECT payload FROM runs').fetchone()[0]), result)

    def test_asic_runs_real_synthesis_and_keeps_evidence_separate(self):
        with patch('server.ai.generate_rtl', return_value=SLOW_SOURCE):
            status, result = self.post({**self.body, 'spec': {**DEFAULT, 'target': 'asic'}})
        self.assertEqual(status, 200, result)
        self.assertEqual(result['evidence'], 'ai_generated_rtl')
        self.assertEqual(result['synthesis']['evidence'], 'generic_synthesis')
        self.assertEqual(result['synthesis']['source_origin'], 'ai_generated_rtl')
        self.assertEqual(result['source_sha256'], result['synthesis']['source_sha256'])
        self.assertEqual(self.counts(), (1, 1))

    def test_generation_gate_compile_and_oracle_failures_persist_nothing(self):
        cases = [ValueError('Provider refused generation'), SOURCE + '`include "x"',
                 SOURCE.replace('integer row,', 'nonsense;\n integer row,'),
                 SOURCE.replace('c[address]', "32'sd0"), SOURCE.replace('cycles<=cycles+1;', 'cycles<=1;')]
        for candidate in cases:
            provider = patch('server.ai.generate_rtl', side_effect=candidate) if isinstance(candidate, Exception) else patch('server.ai.generate_rtl', return_value=candidate)
            with self.subTest(candidate=cases.index(candidate)), provider, patch('server.ai.repair_rtl', side_effect=ValueError('Repair rejected')):
                status, result = self.post()
            self.assertEqual(status, 400, result)
            self.assertEqual(set(result), {'error'})
            self.assertEqual(self.counts(), (0, 0))
            self.assertFalse(server.RUN_LOCK.locked())

    def test_one_failed_candidate_can_be_repaired_before_atomic_acceptance(self):
        incorrect = SOURCE.replace('c[address]', "32'sd0")
        with patch('server.ai.generate_rtl', return_value=incorrect), patch('server.ai.repair_rtl', return_value=SLOW_SOURCE) as repair:
            status, result = self.post()
        self.assertEqual(status, 200, result)
        repair.assert_called_once()
        self.assertEqual(result['generation_attempts'], 2)
        self.assertEqual(result['source_files']['matmul.sv'], SLOW_SOURCE)
        self.assertEqual(self.counts(), (1, 1))

    def test_synthesis_failure_does_not_save_successful_rtl_stage(self):
        for error in (ValueError('Netlist oracle rejected'), RuntimeError('unexpected tool failure')):
            with patch('server.ai.generate_rtl', return_value=SOURCE), patch('server.asic.synthesize', side_effect=error):
                status, result = self.post({**self.body, 'spec': {**DEFAULT, 'target': 'asic'}})
            self.assertIn(status, (400, 502))
            self.assertEqual(set(result), {'error'})
            self.assertEqual(self.counts(), (0, 0))
            self.assertFalse(server.RUN_LOCK.locked())

    def test_static_failure_never_invokes_simulator(self):
        with patch('server.ai.generate_rtl', return_value='module evil; endmodule'), patch('server.simulate') as simulator:
            self.assertEqual(self.post()[0], 400)
            simulator.assert_not_called()

    def test_invalid_requests_and_missing_tools_precede_provider(self):
        cases = [{**self.body, 'spec': {'size': 32}}, {**self.body, 'spec': None},
                 {**self.body, 'prompt': ''}, {**self.body, 'prompt': 'a'*4001},
                 {**self.body, 'seed': True}, {**self.body, 'seed': -1},
                 {**self.body, 'lanes': True}, {**self.body, 'lanes': 3}, []]
        with patch('server.ai.generate_rtl') as provider:
            for body in cases: self.assertEqual(self.post(body)[0], 400)
            with patch('server.shutil.which', return_value=None):
                self.assertEqual(self.post()[0], 400)
            provider.assert_not_called()
        self.assertEqual(self.counts(), (0, 0))

    def test_two_lanes_are_accepted_for_ai_generation(self):
        with patch('server.ai.generate_rtl', return_value=SOURCE) as provider:
            status, result = self.post({**self.body, 'lanes': 2})
        self.assertEqual(status, 200, result)
        self.assertEqual(result['lanes'], 2)
        provider.assert_called_once()

    def test_configuration_origin_size_and_lock_gates(self):
        with patch.dict('os.environ', GROQ_API_KEY='', GROQ_MODEL=''):
            status, result = self.post()
            self.assertEqual(status, 400)
            self.assertIn('not configured', result['error'])
        with patch('server.ai.generate_rtl') as provider:
            self.assertEqual(self.post(origin='https://evil.invalid')[0], 403)
            self.assertEqual(self.post(length=16385)[0], 400)
            self.assertEqual(self.post(length=0)[0], 400)
            with server.RUN_LOCK: self.assertEqual(self.post()[0], 409)
            provider.assert_not_called()
        self.assertEqual(self.counts(), (0, 0))

    def test_atomic_rollback_if_event_write_fails(self):
        with server.connect() as db:
            db.execute("CREATE TRIGGER fail_event BEFORE INSERT ON events BEGIN SELECT RAISE(ABORT, 'test rollback'); END")
        with patch('server.ai.generate_rtl', return_value=SOURCE):
            self.assertEqual(self.post()[0], 502)
        self.assertEqual(self.counts(), (0, 0))

    def test_omitted_lanes_follow_reviewed_objective(self):
        with patch('server.ai.generate_rtl', return_value=SOURCE):
            body = {'spec': {**DEFAULT, 'objective': 'minimize_lanes'}, 'prompt': self.body['prompt']}
            status, result = self.post(body)
        self.assertEqual(status, 200, result)
        self.assertEqual(result['lanes'], 1)
