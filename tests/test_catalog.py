import json
import io
from unittest.mock import patch
import subprocess
import tempfile
import unittest
from pathlib import Path
from siliconos.catalog import blocks,plan,ROOT
from siliconos.engine import DEFAULT

class CatalogTests(unittest.TestCase):
    def test_selection_and_identity(self):
        a=plan(DEFAULT)
        self.assertEqual(a['parameters']['LANES'],4)
        self.assertEqual(a['recipe_sha256'],plan(dict(reversed(list(DEFAULT.items()))))['recipe_sha256'])
        self.assertNotEqual(a['recipe_sha256'],plan(DEFAULT,1)['recipe_sha256'])
        self.assertEqual(plan({**DEFAULT,'max_lanes':1})['parameters']['LANES'],1)
        self.assertEqual(plan({**DEFAULT,'max_lanes':2})['parameters']['LANES'],2)
        self.assertEqual(plan({**DEFAULT,'objective':'minimize_lanes'})['parameters']['LANES'],1)
    def test_fail_closed(self):
        for block in ('../../evil','zipcpu.skidbuffer.registered8.v1','unknown'):
            with self.assertRaises(ValueError):plan(DEFAULT,block_id=block)
        for lanes in (True,3,0,'4'):
            with self.assertRaises(ValueError):plan(DEFAULT,lanes)
        with self.assertRaises(ValueError):plan(DEFAULT,1,'siliconos.matmul.parallel4.v1')
    def test_ai_rejects_invalid_envelope_and_target_drift(self):
        from siliconos import ai
        good={'supported':True,'explanation':'fixture','spec':DEFAULT,
              'provenance':{k:'default' for k in DEFAULT},'unresolved':[]}
        cases=[{**good,'supported':'true'}, {**good,'provenance':{}},
               {**good,'unresolved':'none'}, {**good,'spec':{'size':8}}]
        with patch.dict('os.environ',{'GROQ_API_KEY':'fixture','GROQ_MODEL':'fixture'}):
            for value in cases:
                response=io.BytesIO(json.dumps({'choices':[{'finish_reason':'stop','message':{'content':json.dumps(value)}}]}).encode())
                with patch('urllib.request.urlopen',return_value=response):
                    with self.assertRaises(ValueError): ai.generate('matrix')
            response=io.BytesIO(json.dumps({'choices':[{'finish_reason':'stop','message':{'content':json.dumps(good)}}]}).encode())
            with patch('urllib.request.urlopen',return_value=response):
                with self.assertRaisesRegex(ValueError,'target'): ai.generate('matrix',target='asic')

    def test_vendor_integrity_and_protocol(self):
        self.assertTrue(blocks()[-1]['source_integrity'])
        with tempfile.TemporaryDirectory() as td:
            subprocess.run(['iverilog','-g2012','-s','tb','-o',td+'/sim',
                str(ROOT/'hardware/vendor/wb2axip/skidbuffer.v'),str(ROOT/'hardware/tb_skidbuffer.sv')],check=True,capture_output=True,timeout=20)
            result=subprocess.run(['vvp',td+'/sim'],check=True,capture_output=True,text=True,timeout=20)
            self.assertIn('PASS skidbuffer',result.stdout)
