"""Protocol regression runs the actual RTL independently of application runner."""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("iverilog") and shutil.which("vvp"), "Icarus Verilog required")
class HardwareLifecycleTests(unittest.TestCase):
    def test_lifecycle(self):
        for n in (8, 16):
            for lanes in (1, 4):
                with self.subTest(n=n, lanes=lanes), tempfile.TemporaryDirectory() as td:
                    binary = str(Path(td) / "lifecycle")
                    subprocess.run([
                        "iverilog", "-g2012", "-s", "tb_lifecycle",
                        f"-Ptb_lifecycle.N={n}", f"-Ptb_lifecycle.LANES={lanes}",
                        "-o", binary, str(ROOT / "hardware/matmul.sv"),
                        str(ROOT / "hardware/tb_lifecycle.sv"),
                    ], check=True, capture_output=True, text=True, timeout=30)
                    result = subprocess.run(["vvp", binary], check=True, capture_output=True,
                                            text=True, timeout=30)
                    self.assertIn(f"PASS lifecycle N={n} LANES={lanes}", result.stdout)
