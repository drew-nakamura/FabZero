import unittest
import hashlib
import subprocess
import tempfile
from pathlib import Path
from siliconos.engine import DEFAULT, validate, explore, simulate

class EngineTests(unittest.TestCase):
    def test_budget_never_certified_without_reports(self):
        data=explore({**DEFAULT,"max_dsps":0})
        self.assertIsNone(data['hardware_recommendation'])
        self.assertTrue(all(c['dsp'] is None and not c['dsp_budget_verified'] for c in data['candidates']))

    def test_export_can_replay_without_repository_sources(self):
        result=simulate(DEFAULT,4)
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            for name,source in result['source_files'].items():
                raw=source.encode('utf-8')
                self.assertEqual(hashlib.sha256(raw).hexdigest(),result['source_sha256'][name])
                (root/name).write_bytes(raw)
            values=result['inputs']['a']+result['inputs']['b']
            (root/'inputs.hex').write_text('\n'.join(f'{x&255:02x}' for x in values)+'\n')
            subprocess.run(['iverilog','-g2012','-s','tb','-Ptb.N=8','-Ptb.LANES=4',
                            '-o','sim','matmul.sv','tb.sv'],cwd=root,check=True,capture_output=True,timeout=20)
            replay=subprocess.run(['vvp','sim'],cwd=root,check=True,capture_output=True,text=True,timeout=20)
            self.assertEqual(replay.stdout,result['simulator_stdout'])

    def test_constraints(self):
        self.assertEqual(explore({**DEFAULT,"max_lanes":1})['provisional'],'mac1')
        for patch in ({'size':9},{'size':True},{'operation':'convolution'},{'precision':'fp32'},{'frequency_mhz':0},{'max_dsps':-1},{'objective':'minimize_power'}):
            with self.assertRaises(ValueError): validate({**DEFAULT,**patch})

    def test_rtl_against_reference(self):
        for n in (8,16):
            for lanes in (1,4):
                for seed in range(25):
                    with self.subTest(n=n,lanes=lanes,seed=seed):
                        r=simulate({**DEFAULT,'size':n},lanes,seed)
                        self.assertTrue(r['correct'])
                        self.assertEqual(r['cycles'],n**3//lanes)
                        self.assertFalse(r['physical_fpga'])
                vectors=[([0]*(n*n),[-128]*(n*n)),([-128]*(n*n),[-128]*(n*n)),([127]*(n*n),[-128]*(n*n)),([int(i//n==i%n) for i in range(n*n)],list(range(-128,-128+n*n)))]
                for a,b in vectors:
                    self.assertTrue(simulate({**DEFAULT,'size':n},lanes,vectors=(a,b))['correct'])

if __name__=='__main__': unittest.main()
