"""Prepare a fresh SKY130 baseline workspace; does not claim physical success."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
def prepare(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    source = (ROOT/'hardware/matmul.sv').read_bytes()
    if b'parameter N=8, parameter LANES=1' not in source:
        raise ValueError('Baseline defaults changed: review the physical configuration first.')
    config = (Path(__file__).parent/'sky130.json').read_bytes()
    (output/'matmul.sv').write_bytes(source)
    (output/'config.json').write_bytes(config)
    (output/'manifest.json').write_text(json.dumps({
        'evidence':'physical_build_plan', 'parameters':{'N':8,'LANES':1},
        'pdk':'sky130A','library':'sky130_fd_sc_hd',
        'clock_period_ns_assumed':20,
        'source_sha256':hashlib.sha256(source).hexdigest(),
        'config_sha256':hashlib.sha256(config).hexdigest(),
        'physical_ready':False,
        'limitations':['No physical results until the external flow completes.',
                       'Default flow I/O assumptions require review for real integration.',
                       'Register-based operand storage; no SRAM macros.']},indent=2))
    return output/'config.json'
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True)
    print(prepare(parser.parse_args().output))
