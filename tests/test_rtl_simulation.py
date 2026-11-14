import hashlib
import subprocess
import unittest
from unittest.mock import patch

from siliconos.engine import DEFAULT, ROOT, simulate, reference

SOURCE = (ROOT / 'hardware/matmul.sv').read_text()
# A test fixture with a real extra start bubble; never presented as a live AI call.
SLOW_SOURCE = SOURCE.replace('integer row,', 'reg bubble;\n integer row,').replace(
    'busy<=1; done<=0;', 'busy<=1; done<=0; bubble<=1;').replace(
    'cycles<=cycles+1;', 'cycles<=cycles+1;\n if(bubble) bubble<=0; else begin').replace(
    'end\n end\nendmodule', 'end\n end\n end\nendmodule')


class GeneratedSimulationTests(unittest.TestCase):
    def test_generated_source_is_simulated_hashed_and_checked(self):
        for n, lanes in ((8, 1), (8, 4), (16, 1), (16, 4)):
            with self.subTest(n=n, lanes=lanes):
                r = simulate({**DEFAULT, 'size': n}, lanes, seed=73, source_override=SLOW_SOURCE)
                self.assertEqual(r['evidence'], 'ai_generated_rtl')
                self.assertEqual(r['cycles'], n**3 // lanes + 1)
                self.assertEqual(r['outputs'], reference(r['inputs']['a'], r['inputs']['b'], n))
                self.assertEqual(r['source_files']['matmul.sv'], SLOW_SOURCE)
                self.assertEqual(r['source_sha256']['matmul.sv'], hashlib.sha256(SLOW_SOURCE.encode()).hexdigest())
                self.assertEqual(r['source_files']['tb.sv'].encode(), (ROOT / 'hardware/tb.sv').read_bytes())
                self.assertIn('rtl_monitor.sv', r['source_files'])
                self.assertEqual(r['resources'], {'dsp': None, 'lut': None, 'bram': None})

    def test_default_path_matches_explicit_none(self):
        a, b = simulate(DEFAULT, 4), simulate(DEFAULT, 4, source_override=None)
        a.pop('simulator_wall_seconds'); b.pop('simulator_wall_seconds')
        self.assertEqual(a, b)
        self.assertEqual(a['evidence'], 'rtl_simulation')
        self.assertEqual(set(a['source_files']), {'matmul.sv', 'tb.sv'})
        self.assertEqual(a['source_files']['matmul.sv'], SOURCE)

    def test_gate_rejects_before_any_process(self):
        with patch('siliconos.engine.subprocess.run') as tool:
            with self.assertRaisesRegex(ValueError, 'before tool execution'):
                simulate(DEFAULT, 4, source_override=SOURCE + '\nmodule evil; endmodule')
            tool.assert_not_called()

    def test_compile_arithmetic_unknown_and_counter_failures_are_rejected(self):
        cases = [(SOURCE.replace('integer row,', 'nonsense;\n integer row,'), 'compilation/simulation failed'),
                 (SOURCE.replace('a[row*N+k] * b[k*N+col+g]', "16'sd0"), 'correctness failed'),
                 (SOURCE.replace('c[address]', "32'bx"), 'unknown or malformed'),
                 (SOURCE.replace('cycles<=cycles+1;', 'cycles<=1;'), 'disagrees with observed clocks'),
                 (SOURCE.replace('done<=1;', 'done<=0;'), 'execution protocol failed')]
        for source, error in cases:
            with self.subTest(error=error), self.assertRaisesRegex(ValueError, error):
                simulate(DEFAULT, 4, source_override=source)
        with patch('siliconos.engine.subprocess.run', side_effect=subprocess.TimeoutExpired('iverilog', 20)):
            with self.assertRaisesRegex(ValueError, 'timed out'):
                simulate(DEFAULT, 4, source_override=SOURCE)

    def test_generated_extremes_zero_identity_and_seeded_inputs(self):
        n = 8
        vectors = [([0]*64, [-128]*64), ([-128]*64, [-128]*64),
                   ([127]*64, [-128]*64), ([int(i//n == i%n) for i in range(64)], list(range(-64, 0)))]
        for a, b in vectors:
            self.assertEqual(simulate(DEFAULT, 4, vectors=(a, b), source_override=SOURCE)['outputs'], reference(a, b, n))
