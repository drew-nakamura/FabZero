# Generate, verify and synthesize candidate RTL

**Generate & verify RTL** requests a new SystemVerilog matrix-multiply implementation from Groq and accepts it only after actual tool execution and Python integer-oracle checks. The supported workload remains signed INT8 square matrix multiplication with INT32 accumulation, N=8/16 and LANES=1/2/4. This is a student prototype; a successful run does not establish board operation or a physical ASIC implementation.

## Use

Set `GROQ_API_KEY` and `GROQ_MODEL` in the server process environment, and install Icarus `iverilog`/`vvp`. ASIC requests also require Yosys. The key stays on the server; `.env` is not automatically loaded. The button is enabled only when AI configuration and the required tools are available and the prompt is nonempty. Configuration availability does not prove a live provider connection.

Enter the workload, review the editable supported specification, select KV260 or ASIC, then click **Generate & verify RTL**. The prompt provides context for that reviewed specification; this endpoint does not extract a new specification or compile arbitrary workloads. The provider is instructed to refuse unsupported operations or conflicting requirements. A successful GEMM check does not prove that a camera pipeline or full neural model was implemented.

The selected objective chooses a requested lane parameter: one lane for `minimize_lanes`, otherwise the lane limit. This does not prove that the new implementation is optimal or uses a particular number of physical arithmetic resources. Existing checked-in architecture projections describe the checked-in RTL schedule only.

## Acceptance sequence

1. `POST /api/generate-rtl` validates the supported `spec` and a `prompt` of 1–4000 characters after trimming surrounding whitespace. Optional `lanes` must be 1, 2, or 4 within the lane limit; optional `seed` is an integer from 0 through 2147483647, default 42. The existing same-origin check, 16 KiB request-body cap and shared nonblocking `RUN_LOCK` apply.
2. `ai.generate_rtl(spec, prompt)` requests raw source, with no testbench, Markdown or measurement fields. Missing configuration, refusal, incomplete responses and provider errors reject the request.
3. `rtlgen.gate(source)` accepts only one ANSI `module matmul` with exactly the required N/LANES parameters and port names, directions, signedness and widths. Its conservative subset forbids directives such as `` `include ``, external modules, hierarchical references, attributes, initial/final blocks, delays, strings and system tasks/file I/O. Only the pure system functions `$signed`, `$unsigned` and `$clog2` are permitted. Source is limited to 64 KiB of ASCII text. It is rejected rather than repaired or stripped, before any compiler or simulator is run.
4. `engine.simulate(..., source_override=source)` writes the exact candidate into an isolated temporary directory and compiles it with the **unmodified** `hardware/tb.sv`. That trusted testbench loads inputs while idle, starts the job, reads every output and prints the `CYCLES`/`OUT` lines. The generated module cannot print those lines. A separate trusted `rtl_monitor.sv` checks the observed reset/start/busy/done/counter behavior and counts execution clocks independently.
5. Real Icarus execution must finish, produce valid outputs/cycles, and match every value from `reference(a, b, n)`. Compilation failures, timeouts, unknown outputs, protocol/counter failures and arithmetic mismatches reject the request. A different correct schedule is allowed; reported cycles must match observation.
6. For `target=asic`, `asic.synthesize(..., source_override=source)` gates and re-simulates that exact source, runs Yosys generic synthesis, then simulates the netlist against the integer oracle. Netlist verification uses seed 42 and must match the verified RTL's cycles. The exported netlist testbench adjusts only the module instantiation because Yosys has already specialized N/LANES. The repository testbench stays unchanged.
7. Only after every required stage passes does one transaction save the accepted result and success event. On any failure, the API returns `{"error":"..."}` and saves neither a new run nor a success event. The UI shows the rejection and retains any previously verified report. Editing the spec or prompt marks that earlier generated report stale; export continues to identify the displayed report.

## Evidence and replay

| Result | Evidence label | What it establishes |
|---|---|---|
| Checked-in default simulation | `rtl_simulation` | Correct checked-in RTL outputs for the recorded inputs/configuration |
| Accepted generated-source simulation | `ai_generated_rtl` | AI-generated RTL, verified by simulation against an integer oracle |
| Nested generated-source synthesis | `generic_synthesis`, `source_origin=ai_generated_rtl` | Actual generic synthesis and seeded netlist verification of that candidate |

Generated simulation exports include the prompt, reviewed spec, parameters, seed, actual input/output vectors, input/output hashes, simulator version/stdout, observed cycles and exact `source_files`/`source_sha256` entries for `matmul.sv`, `tb.sv` and `rtl_monitor.sv`. ASIC exports additionally retain the synthesis script/log, tool version, generic cell statistics, netlist/hash, specialized testbench and verification log. The top-level generated evidence label is preserved when synthesis is nested; it is never relabeled as checked-in RTL or board evidence.

Matched comparisons require the same evidence type, spec, simulator, source hashes, input hash and output hash. Independently generated source revisions are not presented as a matched lane comparison. The default `source_override=None` path continues to use the checked-in sources and its existing `rtl_simulation` evidence contract.

To replay an accepted generated simulation, save its complete JSON export as `report.json` and run the following in a scratch directory. Both `tb` and `rtl_monitor` must be simulation roots; omitting the second root drops the independent protocol/counter checks. This recreates source and inputs from the export rather than using current repository RTL.

```sh
python3 - <<'PY'
import hashlib
import json
import subprocess
from pathlib import Path

r = json.loads(Path('report.json').read_text())
assert r['evidence'] == 'ai_generated_rtl' and r['correct'] is True
p = Path('rtl-replay')
p.mkdir(exist_ok=True)
for name in ('matmul.sv', 'tb.sv', 'rtl_monitor.sv'):
    source = r['source_files'][name].encode('utf-8')
    assert hashlib.sha256(source).hexdigest() == r['source_sha256'][name]
    (p / name).write_bytes(source)
a, b = r['inputs']['a'], r['inputs']['b']
(p / 'inputs.hex').write_text('\n'.join(f'{x & 255:02x}' for x in a + b) + '\n')
n, lanes = r['parameters']['N'], r['parameters']['LANES']
subprocess.run(['iverilog', '-g2012', '-s', 'tb', '-s', 'rtl_monitor',
                f'-Ptb.N={n}', f'-Ptb.LANES={lanes}', '-o', 'sim',
                'matmul.sv', 'tb.sv', 'rtl_monitor.sv'], cwd=p, check=True, timeout=20)
run = subprocess.run(['vvp', 'sim'], cwd=p, check=True, timeout=20,
                     capture_output=True, text=True)
outputs = [int(line.split()[1]) for line in run.stdout.splitlines() if line.startswith('OUT ')]
cycles = [int(line.split()[1]) for line in run.stdout.splitlines() if line.startswith('CYCLES ')]
expected = [sum(a[i*n+k] * b[k*n+j] for k in range(n)) for i in range(n) for j in range(n)]
assert outputs == expected == r['outputs'] and cycles == [r['cycles']]
print(run.stdout)
PY
```

This replays the recorded RTL vectors, not the separate synthesized netlist. Simulator diagnostic text such as the `$finish` source path can differ with directory layout; compare actual outputs and cycles, not whole stdout strings.

## Boundaries

Each accepted candidate has passed the recorded seeded vectors and selected configuration. Separate developer regression tests exercise success and rejection paths; they do not make each new candidate exhaustively verified across all inputs, sizes, lanes or lifecycle sequences. Neither RTL nor netlist simulation is formal equivalence or timing simulation.

The static gate deliberately rejects some otherwise valid SystemVerilog. It is an interface/construct filter, not an operating-system sandbox for hostile compiler inputs. The service remains a local loopback prototype.

DSP/LUT/BRAM remain `null`. Generic cells are not silicon area, foundry standard-cell counts, FPGA resources or cost. Target MHz is an assumption, so cycles divided by it are projected microseconds. Kernel cycles exclude loading and communication. No generated report establishes placement/routing, timing closure, power, board deployment or signoff. Separate physical research reports apply only to their own recorded artifacts.
