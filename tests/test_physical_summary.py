import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('physical_summary',Path(__file__).resolve().parents[1]/'hardware/physical/summarize.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class SummaryTests(unittest.TestCase):
    def test_missing_and_failed_checks_never_claim_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'final').mkdir();(root/'source.v').write_text('module m; endmodule')
            (root/'resolved.json').write_text(json.dumps({'PDK':'sky130A','CLOCK_PERIOD':20,'VERILOG_FILES':[str(root/'source.v')]}))
            (root/'final/metrics.json').write_text(json.dumps({'timing__setup__ws':-0.01,'timing__hold__ws':0.1}))
            report=module.summarize(root)
            self.assertFalse(report['all_listed_checks_pass'])
            self.assertFalse(report['checks']['timing__setup__ws'])
            self.assertIsNone(report['checks']['design__max_cap_violation__count'])
            self.assertFalse(report['fabrication_ready'])
