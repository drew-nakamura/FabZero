"""Artifact-bound conversion of partner board evidence."""
import json
import tempfile
import unittest
from pathlib import Path

from siliconos.board_adapter import adapt_drew_result

ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / 'hw/matmul_board'
ZIPS = ROOT / 'data/handoff_exports'
KEY = 'test-only-runner-secret-' * 2


class BoardAdapterTests(unittest.TestCase):
    def fixture(self, lanes):
        parent, stamp = {
            1: ('6bccf63e-f83a-4e12-88e6-78b20d120b65', '20261115T011930Z_n8_l1'),
            4: ('3abe54e6-25d2-4eb7-90bf-dd3b39f3a4e9', '20261115T012007Z_n8_l4'),
        }[lanes]
        return (BOARD / 'results' / stamp / 'board-result.json',
                BOARD / 'build' / f'n8_l{lanes}',
                next(ZIPS.glob(f'*{parent}*handoff.zip')))

    def adapt(self, paths):
        return adapt_drew_result(*paths, runner_key=KEY, runner_key_id='test')

    def test_real_result_chains_convert(self):
        for lanes in (1, 4):
            with self.subTest(lanes=lanes):
                signed = self.adapt(self.fixture(lanes))
                self.assertEqual(signed['evidence'], 'board_measured')
                self.assertEqual(signed['run']['cycles'], 512 // lanes)
                self.assertEqual(signed['runner_auth']['key_id'], 'test')

    def test_crossed_bitstream_and_zip_fail(self):
        a, b = self.fixture(1), self.fixture(4)
        with self.assertRaises(ValueError):
            self.adapt((a[0], b[1], a[2]))
        with self.assertRaises(ValueError):
            self.adapt((a[0], a[1], b[2]))

    def test_tampered_raw_output_fails_before_signing(self):
        result, build, handoff = self.fixture(1)
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            (temp / 'inputs.json').write_bytes((result.parent / 'inputs.json').read_bytes())
            (temp / 'xsdb.log').write_bytes((result.parent / 'xsdb.log').read_bytes())
            raw = json.loads(result.read_bytes())
            raw['run']['outputs'][0] += 1
            copy = temp / 'board-result.json'
            copy.write_text(json.dumps(raw))
            with self.assertRaisesRegex(ValueError, 'Board run vectors'):
                self.adapt((copy, build, handoff))

    def test_transcript_must_match_result(self):
        result, build, handoff = self.fixture(1)
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            (temp / 'inputs.json').write_bytes((result.parent / 'inputs.json').read_bytes())
            (temp / 'board-result.json').write_bytes(result.read_bytes())
            (temp / 'xsdb.log').write_text('MM BEGIN n=8 base=0xA0000000\nMM END\n')
            with self.assertRaisesRegex(ValueError, 'transcript'):
                self.adapt((temp / 'board-result.json', build, handoff))


if __name__ == '__main__':
    unittest.main()
