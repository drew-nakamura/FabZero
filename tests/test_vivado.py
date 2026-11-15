import unittest
import json
import hashlib
from pathlib import Path

from siliconos.vivado import parse_utilization, parse_import


class VivadoUtilizationTests(unittest.TestCase):
    def test_import_remains_unverified_ooc_evidence(self):
        metadata = "evidence=out_of_context_synthesis\nvivado=2025.2\ntop=matmul\npart=xck26\nN=16\nLANES=2\nsource=matmul.sv\nphysical_fpga=false\ntiming_closed=false\n"
        result = parse_import("| DSPs | 2 | 1248 |", metadata)
        self.assertEqual(result['resources']['dsp'], 2)
        self.assertEqual(result['parameters'], {'N': 16, 'LANES': 2})
        self.assertFalse(result['source_binding_verified'])
        self.assertFalse(result['timing_closed'])
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            parse_import("| DSPs | 2 | 1248 |", "N=16\nLANES=2")

    def test_routed_manifest_binds_report_and_current_sources(self):
        report = "| DSPs | 0 | 1248 |\n| CLB LUTs | 100 | 117120 |"
        root = Path(__file__).resolve().parent.parent / 'hardware'
        manifest = {'schema': 'fabzero.matmul_board.implementation_manifest/1',
                    'parameters': {'N': 8, 'LANES': 1}, 'logical_top': 'matmul_axi',
                    'board_top': 'matmul_board_top', 'target_part': 'xck26-sfvc784-2LV-c',
                    'vivado_version': '2025.2', 'timing': {'timing_met': True},
                    'report_sha256': {'utilization.rpt': hashlib.sha256(report.encode()).hexdigest()},
                    'rtl': {'sha256': {name: hashlib.sha256((root/name).read_bytes()).hexdigest()
                                       for name in ('matmul.sv', 'matmul_axi.sv')}}}
        result = parse_import(report, json.dumps(manifest))
        self.assertEqual(result['resources']['dsp'], 0)
        self.assertTrue(result['source_binding_verified'])
        manifest['report_sha256']['utilization.rpt'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'does not match'):
            parse_import(report, json.dumps(manifest))

    def test_summary_and_primitives(self):
        report = """+----------------+------+-----------+
| Site Type      | Used | Available |
| CLB LUTs       | 1,234| 117120    |
| CLB Registers  | 345  | 234240    |
| Block RAM Tile | 2    | 144       |
| DSPs           | 8    | 1248      |
| DSP48E2        | 8    | 1248      |
"""
        self.assertEqual(parse_utilization(report), {"dsp": 8, "lut": 1234, "ff": 345, "bram": 2})

    def test_primitive_only_and_zero_are_real_counts(self):
        self.assertEqual(parse_utilization("| DSP48E1 | 0 | 220 |"), {"dsp": 0, "lut": None, "ff": None, "bram": None})

    def test_no_explicit_dsp_row_rejected(self):
        with self.assertRaisesRegex(ValueError, "no explicit DSP"):
            parse_utilization("| CLB LUTs | 12 | 100 |")

    def test_conflicting_rows_rejected(self):
        for report in ("| DSPs | 4 | 100 |\n| DSP48E2 | 3 | 100 |",
                       "| DSPs | 4 | 100 |\n| DSPs | 5 | 100 |"):
            with self.subTest(report=report), self.assertRaisesRegex(ValueError, "disagree|Conflicting"):
                parse_utilization(report)

    def test_non_table_text_is_not_evidence(self):
        with self.assertRaisesRegex(ValueError, "no explicit DSP"):
            parse_utilization("DSP48E2 4")


if __name__ == "__main__":
    unittest.main()
