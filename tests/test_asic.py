import shutil
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import server
from siliconos.asic import synthesize
from siliconos.engine import DEFAULT


class AsicValidationTests(unittest.TestCase):
    def test_rejects_wrong_target_and_lane_types(self):
        with self.assertRaises(ValueError):
            synthesize(DEFAULT, 1)
        for lanes in (True, 0, 2, 4):
            with self.subTest(lanes=lanes), self.assertRaises(ValueError):
                synthesize({**DEFAULT, 'target': 'asic', 'max_lanes': 1}, lanes)

    def test_missing_tools_do_not_fabricate_evidence(self):
        with patch('siliconos.asic.shutil.which', return_value=None), self.assertRaisesRegex(ValueError, 'require:'):
            synthesize({**DEFAULT, 'target': 'asic'}, 1)


class AsicApiPersistenceTests(unittest.TestCase):
    def test_event_failure_rolls_back_direct_synthesis_run(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(server, 'DB', Path(folder) / 'test.db'):
            with server.connect() as db:
                db.execute("CREATE TRIGGER fail_event BEFORE INSERT ON events BEGIN SELECT RAISE(ABORT, 'test rollback'); END")
            payload=json.dumps({'spec':{**DEFAULT,'target':'asic'},'lanes':1}).encode()
            handler=object.__new__(server.Handler)
            handler.path='/api/asic/synthesize'
            handler.server=SimpleNamespace(server_port=8000)
            handler.headers={'Content-Length':str(len(payload))}
            handler.rfile=io.BytesIO(payload)
            replies=[]
            handler.reply=lambda status,data: replies.append((status,data))
            with patch('server.asic.synthesize',return_value={'spec':{**DEFAULT,'target':'asic'},'lanes':1}):
                handler.do_POST()
            self.assertEqual(replies[0][0],502)
            with server.connect() as db:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM runs').fetchone()[0],0)
                self.assertEqual(db.execute('SELECT COUNT(*) FROM events').fetchone()[0],0)


@unittest.skipUnless(all(shutil.which(t) for t in ('yosys', 'iverilog', 'vvp')), 'Yosys and Icarus required')
class ActualAsicSynthesisTests(unittest.TestCase):
    def test_generic_netlists(self):
        for lanes in (1, 4):
            with self.subTest(lanes=lanes):
                result = synthesize({**DEFAULT, 'target': 'asic', 'size': 8}, lanes)
                self.assertTrue(result['netlist_verified'])
                self.assertEqual(result['cycles'], 512 // lanes)
                self.assertEqual(result['cell_count'], sum(result['cell_counts'].values()))
                self.assertGreater(result['cell_count'], 0)
                self.assertIn('module matmul', result['netlist_verilog'])
                for key in ('timing', 'area', 'power'):
                    self.assertIsNone(result[key])
                self.assertFalse(result['physical_asic'])
                self.assertFalse(result['timing_closed'])
