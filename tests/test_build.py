import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import server
from siliconos.engine import DEFAULT

class BuildTests(unittest.TestCase):
    def setUp(self):
        folder=tempfile.TemporaryDirectory(); self.addCleanup(folder.cleanup)
        patcher=patch.object(server,'DB',Path(folder.name)/'test.db')
        patcher.start();self.addCleanup(patcher.stop)
    def post(self,spec):
        h=object.__new__(server.Handler);h.path='/api/build'
        h.server=SimpleNamespace(server_port=8000)
        body=json.dumps({'spec':spec}).encode()
        h.headers={'Content-Length':str(len(body))};h.rfile=io.BytesIO(body)
        replies=[];h.reply=lambda code,result:replies.append((code,result))
        h.do_POST();return replies[0]
    def test_real_kv260_bundle_and_removed_asic_target(self):
        code,result=self.post({**DEFAULT,'max_lanes':1})
        self.assertEqual(code,200,result)
        self.assertNotIn('synthesis',result)
        self.assertEqual(result['cycles'],512)
        code,result=self.post({**DEFAULT,'target':'asic'})
        self.assertEqual(code,400)
        self.assertIn('KV260',result['error'])
        self.assertFalse(server.RUN_LOCK.locked())
        with server.connect() as db:
            self.assertEqual(db.execute('select count(*) from runs').fetchone()[0],1)
            self.assertEqual(db.execute('select count(*) from events').fetchone()[0],1)
    def test_source_change_rejected(self):
        with patch('server.simulate',return_value={'source_sha256':{}}):
            self.assertEqual(self.post(DEFAULT)[0],400)
        self.assertFalse(server.RUN_LOCK.locked())
    def test_busy_rejected(self):
        server.RUN_LOCK.acquire()
        try:self.assertEqual(self.post(DEFAULT)[0],409)
        finally:server.RUN_LOCK.release()
