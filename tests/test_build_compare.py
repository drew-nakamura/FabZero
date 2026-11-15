import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from siliconos import build_compare
from siliconos.build_compare import compare_builds


class BuildComparisonTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.rtl = self.root/'hardware'
        self.rtl.mkdir()
        for name in ('matmul.sv','matmul_axi.sv'):
            (self.rtl/name).write_text('fixture '+name)
        hashes = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in self.rtl.iterdir()}
        self.builds = self.root/'builds'
        for lane in (1,4):
            folder = self.builds/f'n8_l{lane}'
            (folder/'reports').mkdir(parents=True)
            header = '| Tool Version : Vivado v.2025.2 (win64)\r\n| Design : matmul_board_top\r\n| Device : xck26-sfvc784-2LV-c\r\n| Design State : Routed\r\n'
            reports = {'utilization.rpt':header+f'| CLB LUTs | {100*lane} |\n| CLB Registers | {200*lane} |\n| DSPs | 0 |\n',
                       'timing_summary.rpt':header+' WNS(ns) TNS(ns) TNS Failing Endpoints TNS Total Endpoints WHS(ns) THS(ns) THS Failing Endpoints THS Total Endpoints WPWS(ns) TPWS(ns) TPWS Failing Endpoints TPWS Total Endpoints\r\n --------\r\n 4.757 0.000 0 3488 0.001 0.000 0 3488 3.500 0.000 0 1230\r\n'}
            report_hashes = {}
            for name,text in reports.items():
                raw=text.encode();(folder/'reports'/name).write_bytes(raw)
                report_hashes[name]=hashlib.sha256(raw).hexdigest()
            manifest = dict(schema='fabzero.matmul_board.implementation_manifest/1', parameters={'N':8,'LANES':lane},
                            rtl={'sha256':hashes},board_top='matmul_board_top',logical_top='matmul_axi',
                            report_sha256=report_hashes,vivado_version='2025.2',target_part='xck26-sfvc784-2LV-c')
            (folder/'implementation_manifest.json').write_text(json.dumps(manifest))

    def test_comparison_uses_whole_design_reports_and_preserves_raw_evidence(self):
        result=compare_builds(self.builds,self.rtl)
        self.assertEqual(result['scope'],'whole design')
        self.assertEqual([x['resources']['lut'] for x in result['builds']],[100,400])
        self.assertEqual(result['builds'][0]['timing']['wns_ns'],4.757)
        self.assertNotIn('cycles',result['builds'][0])
        self.assertIn('\r\n',result['builds'][0]['reports']['timing_summary.rpt'])

    def test_changed_report_rejects_entire_pair(self):
        with (self.builds/'n8_l4/reports/timing_summary.rpt').open('ab') as f:f.write(b'changed')
        with self.assertRaisesRegex(ValueError,'timing_summary.rpt hash mismatch'):
            compare_builds(self.builds,self.rtl)

    def test_changed_checked_in_rtl_rejects_entire_pair(self):
        (self.rtl/'matmul.sv').write_text('changed source')
        with self.assertRaisesRegex(ValueError,'RTL hash mismatch'):
            compare_builds(self.builds,self.rtl)

    def test_archived_build_remains_visible_when_active_rtl_changes(self):
        archived = self.root/'hw/matmul_board/rtl'
        archived.mkdir(parents=True)
        for source in self.rtl.iterdir():
            shutil.copy2(source, archived/source.name)
        shutil.copytree(self.builds, self.root/'build/drew-branch')
        (self.rtl/'matmul.sv').write_text('new unimplemented source')
        with patch.object(build_compare, 'ROOT', self.root):
            result = compare_builds()
        self.assertFalse(result['current_rtl_matches_build'])
        self.assertEqual(result['builds'][0]['resources']['lut'], 100)
