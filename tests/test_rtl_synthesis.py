import subprocess
import unittest
from unittest.mock import patch

from siliconos import asic
from siliconos.engine import DEFAULT
from test_rtl_simulation import SOURCE, SLOW_SOURCE

SPEC = {**DEFAULT, 'target': 'asic'}


class GeneratedSynthesisTests(unittest.TestCase):
    def test_real_generated_synthesis_and_netlist_oracle(self):
        result = asic.synthesize(SPEC, 4, source_override=SLOW_SOURCE)
        self.assertEqual(result['evidence'], 'generic_synthesis')
        self.assertEqual(result['source_origin'], 'ai_generated_rtl')
        self.assertEqual(result['rtl_verification']['evidence'], 'ai_generated_rtl')
        self.assertEqual(result['cycles'], 129)
        self.assertTrue(result['netlist_verified'])
        self.assertEqual(result['output_sha256'], result['rtl_verification']['output_sha256'])
        self.assertEqual(result['source_files']['matmul.sv'], SLOW_SOURCE)
        self.assertEqual(result['cell_count'], sum(result['cell_counts'].values()))
        self.assertIn('rtl_monitor.sv', result['source_files'])
        self.assertIsNone(result['area'])
        self.assertIsNone(result['timing'])
        self.assertIsNone(result['power'])
        self.assertTrue(all(result['resources'][k] is None for k in ('dsp', 'lut', 'bram')))
        self.assertIn('Generic cell counts are not silicon area, cost, FPGA resource usage, or timing evidence.', result['limitations'])

    def test_static_and_rtl_failures_precede_yosys(self):
        with patch('siliconos.asic._run') as yosys:
            with self.assertRaisesRegex(ValueError, 'before tool execution'):
                asic.synthesize(SPEC, 4, source_override=SOURCE + '`include "x"')
            with self.assertRaisesRegex(ValueError, 'correctness failed'):
                asic.synthesize(SPEC, 4, source_override=SOURCE.replace('c[address]', "32'sd0"))
            yosys.assert_not_called()

    def test_rejects_netlist_oracle_failure_after_real_synthesis(self):
        real_run = asic._run
        def corrupt_output(command, cwd, timeout):
            result = real_run(command, cwd, timeout)
            if command[0].endswith('/vvp') or command[0] == 'vvp':
                return subprocess.CompletedProcess(command, 0, stdout='CYCLES 128\nOUT 0\n', stderr='')
            return result
        with patch('siliconos.asic._run', side_effect=corrupt_output):
            with self.assertRaisesRegex(ValueError, 'Synthesized-netlist correctness/cycle check failed'):
                asic.synthesize(SPEC, 4, source_override=SOURCE)

    def test_yosys_failure_and_timeout_have_no_result(self):
        for exc in (subprocess.TimeoutExpired('yosys', 120),
                    subprocess.CalledProcessError(1, 'yosys', stderr='fixture synthesis error')):
            with patch('siliconos.asic.subprocess.run', side_effect=exc), self.assertRaises(ValueError):
                asic._run(['yosys', '-s', 'synth.ys'], '.', 120)
