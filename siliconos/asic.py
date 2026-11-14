"""Reproducible generic logic synthesis; deliberately no fabricated ASIC PPA.

Yosys reference: https://yosyshq.readthedocs.io/projects/yosys/en/stable/cmd/index_techlibs_common.html
Generic cells are not foundry standard cells or physical area measurements.
"""
import hashlib
import json
import random
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from .engine import ROOT, reference, validate


def _hash(content):
    return hashlib.sha256(content).hexdigest()


def _run(command, cwd, timeout):
    try:
        return subprocess.run(command, cwd=cwd, check=True, capture_output=True,
                              text=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise ValueError(f"{Path(command[0]).name} exceeded its {timeout}s limit; no synthesis result accepted.") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "No diagnostic output")[-4000:]
        raise ValueError(f"{Path(command[0]).name} failed; no synthesis result accepted.\n{detail}") from exc


def synthesize(spec, lanes):
    spec = validate(spec)
    if spec['target'] != 'asic':
        raise ValueError('Generic ASIC synthesis requires target=asic.')
    if type(lanes) is not int or lanes not in (1, 4) or lanes > spec['max_lanes']:
        raise ValueError('Candidate exceeds the lane limit or is unsupported.')
    binaries = {name: shutil.which(name) for name in ('yosys', 'iverilog', 'vvp')}
    missing = [name for name, path in binaries.items() if not path]
    if missing:
        raise ValueError('Generic synthesis and netlist verification require: ' + ', '.join(missing))
    n = spec['size']
    sources = {name: (ROOT / 'hardware' / name).read_bytes() for name in ('matmul.sv', 'tb.sv')}
    # Yosys specializes the kernel parameters; the harness still needs N for input loading.
    tb = sources['tb.sv'].decode().replace('matmul #(.N(N),.LANES(LANES)) dut(.*);', 'matmul dut(.*);')
    if tb == sources['tb.sv'].decode():
        raise ValueError('Netlist testbench specialization failed; no result accepted.')
    script = (f'read_verilog -sv matmul.sv\nchparam -set N {n} -set LANES {lanes} matmul\n'
              'synth -top matmul\ncheck -assert\ntee -o statistics.json stat -json\n'
              'write_verilog -noattr netlist.v\n')
    seed = 42
    rng = random.Random(seed)
    a = [rng.randrange(-128, 128) for _ in range(n*n)]
    b = [rng.randrange(-128, 128) for _ in range(n*n)]
    expected = reference(a, b, n)
    begin = time.monotonic()
    with tempfile.TemporaryDirectory(prefix='siliconos-asic-') as td:
        path = Path(td)
        for name, content in sources.items():
            (path / name).write_bytes(content)
        (path / 'netlist_tb.sv').write_text(tb)
        (path / 'synth.ys').write_text(script)
        (path / 'inputs.hex').write_text('\n'.join(f'{x & 255:02x}' for x in a+b) + '\n')
        version = _run([binaries['yosys'], '-V'], td, 5).stdout.strip()
        synthesis = _run([binaries['yosys'], '-s', 'synth.ys'], td, 120)
        synthesis_seconds = time.monotonic() - begin
        statistics = json.loads((path / 'statistics.json').read_text())
        module = statistics['modules']['\\matmul']
        cell_counts = module['num_cells_by_type']
        cell_count = module['num_cells']
        if not cell_count or sum(cell_counts.values()) != cell_count:
            raise ValueError('Invalid generic cell statistics; no result accepted.')
        netlist = (path / 'netlist.v').read_text()
        compilation = _run([binaries['iverilog'], '-g2012', '-s', 'tb', f'-Ptb.N={n}',
                           f'-Ptb.LANES={lanes}', '-o', 'netlist_sim', 'netlist.v', 'netlist_tb.sv'], td, 30)
        simulation = _run([binaries['vvp'], 'netlist_sim'], td, 60)
        outputs = [int(line.split()[1]) for line in simulation.stdout.splitlines() if line.startswith('OUT ')]
        cycles = [int(line.split()[1]) for line in simulation.stdout.splitlines() if line.startswith('CYCLES ')]
        if outputs != expected or cycles != [n**3 // lanes]:
            raise ValueError('Synthesized-netlist correctness/cycle check failed; no synthesis result accepted.')
        simulator = _run([binaries['iverilog'], '-V'], td, 5).stdout.splitlines()[0]
    return dict(
        evidence='generic_synthesis', correct=True, spec=spec, lanes=lanes, seed=seed,
        cycles=cycles[0], parameters={'N': n, 'LANES': lanes},
        cell_count=cell_count, cell_counts=cell_counts,
        resources={'generic_cells': cell_count, 'cell_types': cell_counts, 'dsp': None, 'lut': None, 'bram': None},
        tool='Yosys', tool_version=version, simulator=simulator,
        synthesis_wall_seconds=synthesis_seconds, total_wall_seconds=time.monotonic()-begin,
        source_files={name: content.decode() for name, content in sources.items()},
        source_sha256={name: _hash(content) for name, content in sources.items()},
        synthesis_script=script, synthesis_log=synthesis.stdout+synthesis.stderr,
        statistics=statistics, netlist_verilog=netlist, netlist_sha256=_hash(netlist.encode()),
        netlist_testbench=tb, verification_log=compilation.stdout+compilation.stderr+simulation.stdout+simulation.stderr,
        netlist_verified=True, verification='seeded functional netlist simulation against Python integer oracle',
        inputs={'a': a, 'b': b}, outputs=outputs,
        input_sha256=_hash(bytes(x & 255 for x in a+b)),
        output_sha256=_hash(json.dumps(outputs).encode()),
        timing=None, area=None, power=None, timing_closed=False,
        physical_fpga=False, physical_asic=False,
        limitations=[
            'Generic Yosys/ABC logic cells only; no PDK or foundry standard-cell library was used.',
            'Generic cell counts are not silicon area, cost, FPGA resource usage, or timing evidence.',
            'No placement, routing, static timing analysis, parasitics, power analysis, DRC/LVS, or tapeout.',
            'Netlist verification is one seeded functional simulation, not formal equivalence or timing simulation.',
            'Operand/output arrays map to generic logic; no SRAM macros are inferred or characterized.',
            'Requested frequency is an unverified specification; no achieved ASIC clock is claimed.',
        ])
