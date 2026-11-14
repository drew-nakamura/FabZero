#!/usr/bin/env python3
"""Map the supported kernel to a supplied SKY130 HD Liberty; not physical design."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, cwd, name, timeout=120):
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    (cwd / name).write_text(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(f'{command[0]} failed; see {cwd / name}')
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--liberty', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--size', type=int, choices=(8, 16), default=8)
    parser.add_argument('--lanes', type=int, choices=(1, 4), default=1)
    args = parser.parse_args()
    liberty = args.liberty.expanduser().resolve(strict=True)
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / 'build'):
        parser.error('--output must be beneath this repository build/ directory')
    if output.exists() and any(output.iterdir()):
        parser.error('--output must be empty to avoid overwriting evidence')
    output.mkdir(parents=True, exist_ok=True)
    for name in ('matmul.sv', 'tb.sv'):
        shutil.copyfile(ROOT / 'hardware' / name, output / name)
    shutil.copyfile(liberty, output / 'cells.lib')
    script = (f'read_verilog -sv matmul.sv\nchparam -set N {args.size} -set LANES {args.lanes} matmul\n'
              'synth -top matmul -noabc\ndfflibmap -liberty cells.lib\n'
              'abc -liberty cells.lib\nclean\n'
              'read_liberty -lib -ignore_miss_func cells.lib\ncheck -assert\n'
              'tee -o statistics.json stat -json -liberty cells.lib\n'
              'write_verilog -noattr mapped.v\n')
    (output / 'map.ys').write_text(script)
    version = run(['yosys', '-V'], output, 'version.log', 5).strip()
    run(['yosys', '-s', 'map.ys'], output, 'mapping.log')
    stats = json.loads((output / 'statistics.json').read_text())
    module = stats['modules']['\\matmul']
    counts = module['num_cells_by_type']
    if not counts or any(not name.startswith('sky130_fd_sc_hd__') for name in counts):
        raise RuntimeError('Unmapped or unexpected cells remain; no mapping accepted')
    report = dict(evidence='technology_mapped', pdk='sky130A', library=liberty.name,
                  size=args.size, lanes=args.lanes, yosys_version=version,
                  source_sha256=digest(output / 'matmul.sv'), liberty_sha256=digest(output / 'cells.lib'),
                  netlist_sha256=digest(output / 'mapped.v'), cell_count=module['num_cells'],
                  cell_counts=counts, standard_cell_area_um2=module.get('area'),
                  physical_area_um2=None, achieved_timing_ns=None, power_mw=None,
                  physical_ready=False, mapped_netlist_verified=False,
                  limitations=['Area is the sum of Liberty cell areas, excluding floorplan, routing and utilization.',
                               'No placement, routing, static timing analysis, power analysis, DRC, LVS or GDSII.'])
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    models = liberty.parent.parent / 'verilog'
    if all((models / name).is_file() for name in ('primitives.v', 'sky130_fd_sc_hd.v')):
        for name in ('primitives.v', 'sky130_fd_sc_hd.v'):
            shutil.copyfile(models / name, output / name)
        report['model_sha256'] = {name: digest(output / name) for name in ('primitives.v', 'sky130_fd_sc_hd.v')}
        tb = (output / 'tb.sv').read_text().replace('matmul #(.N(N),.LANES(LANES)) dut(.*);', 'matmul dut(.*);')
        (output / 'mapped_tb.sv').write_text(tb)
        rng = random.Random(42)
        n = args.size
        a, b = [[rng.randrange(-128, 128) for _ in range(n*n)] for _ in range(2)]
        (output / 'inputs.hex').write_text('\n'.join(f'{x & 255:02x}' for x in a+b) + '\n')
        run(['iverilog', '-g2012', '-DFUNCTIONAL', '-s', 'tb', f'-Ptb.N={n}',
             '-o', 'mapped_sim', 'primitives.v', 'sky130_fd_sc_hd.v', 'mapped.v', 'mapped_tb.sv'], output, 'compile.log')
        result = run(['vvp', 'mapped_sim'], output, 'simulation.log', 60)
        values = [int(line.split()[1]) for line in result.splitlines() if line.startswith('OUT ')]
        cycles = [int(line.split()[1]) for line in result.splitlines() if line.startswith('CYCLES ')]
        expected = [sum(a[i*n+k]*b[k*n+j] for k in range(n)) for i in range(n) for j in range(n)]
        if values != expected or cycles != [n**3 // args.lanes]:
            raise RuntimeError('Mapped netlist arithmetic/cycle verification failed')
        report.update(mapped_netlist_verified=True, verified_outputs=len(values), cycles=cycles[0],
                      verification='Zero-delay official cell models; deterministic signed random vector, seed 42')
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
