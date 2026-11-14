import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which('iverilog') and shutil.which('vvp'), 'Icarus Verilog required')
class AxiTests(unittest.TestCase):
    def test_register_slave(self):
        for n in (8, 16):
            for lanes in (1, 4):
                with self.subTest(n=n, lanes=lanes), tempfile.TemporaryDirectory() as td:
                    binary = str(Path(td) / 'axi')
                    subprocess.run([
                        'iverilog', '-g2012', '-s', 'tb_axi', f'-Ptb_axi.N={n}',
                        f'-Ptb_axi.LANES={lanes}', '-o', binary,
                        *[str(ROOT / 'hardware' / name) for name in
                          ('matmul.sv', 'matmul_axi.sv', 'tb_axi.sv')],
                    ], check=True, capture_output=True, text=True, timeout=30)
                    run = subprocess.run(['vvp', binary], check=True, capture_output=True,
                                         text=True, timeout=30)
                    self.assertIn(f'PASS AXI N={n} LANES={lanes}', run.stdout)
