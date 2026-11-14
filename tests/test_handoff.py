import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import zipfile
from siliconos.engine import DEFAULT,simulate
from siliconos.handoff import archive

class HandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=simulate(DEFAULT,4)
        cls.report['id']='00000000-0000-0000-0000-000000000001'
    def test_archive_replays_exact_source_and_records_distinct_aids(self):
        with zipfile.ZipFile(io.BytesIO(archive(self.report))) as bundle:
            manifest=json.loads(bundle.read('manifest.json'))
            self.assertFalse(manifest['physical_fpga'])
            for name,digest in manifest['files_sha256'].items():
                self.assertEqual(hashlib.sha256(bundle.read(name)).hexdigest(),digest)
            with tempfile.TemporaryDirectory() as folder:
                bundle.extractall(folder)
                subprocess.run(['iverilog','-g2012','-s','tb','-Ptb.N=8','-Ptb.LANES=4','-o','sim','hardware/matmul.sv','hardware/tb.sv'],cwd=folder,check=True,capture_output=True,timeout=20)
                run=subprocess.run(['vvp','sim'],cwd=folder,check=True,capture_output=True,text=True,timeout=20)
                outputs=[int(line.split()[1]) for line in run.stdout.splitlines() if line.startswith('OUT ')]
                self.assertEqual(outputs,self.report['outputs'])
    def test_tampered_missing_or_false_evidence_rejected(self):
        for key,value in [('correct',False),('source_files',{}),('outputs',[0]),('lanes',True),('inputs',{})]:
            report=copy.deepcopy(self.report);report[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):archive(report)
        report=copy.deepcopy(self.report);report['source_files']['matmul.sv']+='// changed'
        with self.assertRaises(ValueError):archive(report)

    def test_generated_archive_preserves_and_replays_cycle_monitor(self):
        from test_rtl_simulation import SLOW_SOURCE
        report=simulate(DEFAULT,4,source_override=SLOW_SOURCE)
        with zipfile.ZipFile(io.BytesIO(archive(report))) as bundle, tempfile.TemporaryDirectory() as folder:
            self.assertIn('hardware/rtl_monitor.sv',bundle.namelist())
            self.assertIn('-s rtl_monitor',bundle.read('README.md').decode())
            bundle.extractall(folder)
            subprocess.run(['iverilog','-g2012','-s','tb','-s','rtl_monitor','-Ptb.N=8','-Ptb.LANES=4',
                            '-o','sim','hardware/matmul.sv','hardware/tb.sv','hardware/rtl_monitor.sv'],
                           cwd=folder,check=True,capture_output=True,timeout=20)
            run=subprocess.run(['vvp','sim'],cwd=folder,check=True,capture_output=True,text=True,timeout=20)
            outputs=[int(line.split()[1]) for line in run.stdout.splitlines() if line.startswith('OUT ')]
            cycles=[int(line.split()[1]) for line in run.stdout.splitlines() if line.startswith('CYCLES ')]
            self.assertEqual(outputs,report['outputs'])
            self.assertEqual(cycles,[report['cycles']])
        report['source_files'].pop('rtl_monitor.sv')
        with self.assertRaisesRegex(ValueError,'source snapshot'):archive(report)

    def test_download_endpoint_and_missing_run(self):
        from unittest.mock import patch
        import server
        with tempfile.TemporaryDirectory() as folder, patch.object(server,'DB',Path(folder)/'runs.db'):
            with server.connect() as db:
                db.execute('INSERT INTO runs VALUES (?,?)',(self.report['id'],json.dumps(self.report)))
            handler=object.__new__(server.Handler)
            handler.path='/api/runs/'+self.report['id']+'/handoff.zip'
            handler.wfile=io.BytesIO();statuses=[];headers={}
            handler.send_response=statuses.append
            handler.send_header=lambda k,v:headers.update({k:v})
            handler.end_headers=lambda:None
            handler.reply=lambda status,payload:statuses.append(status)
            handler.do_GET()
            self.assertEqual(statuses,[200])
            self.assertEqual(headers['Content-Type'],'application/zip')
            self.assertTrue(zipfile.is_zipfile(handler.wfile))
            handler.path='/api/runs/00000000-0000-0000-0000-000000000002/handoff.zip'
            handler.do_GET();self.assertEqual(statuses[-1],404)
