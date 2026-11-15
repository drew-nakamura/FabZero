# matmul_axi on the KV260 (board build + JTAG runner)

This folder puts the teammate's **unchanged** `matmul_axi` (signed INT8 matrix multiply behind an AXI4-Lite register interface) next to the Zynq processor on the Kria KV260. It builds one bitstream per configuration and holds the runner that will test it on the board over JTAG. Task record: MATMUL-BOARD-001 (local, `docs/team/tasks/`).

Status (2026-11-14): both N=8 builds meet timing, and both **passed on Drew's KV260** with the identity/ramp workload: all 64 outputs correct on the first run, on a repeat, and after reset + reload. Cycles were 512 for LANES=1 and 128 for LANES=4. Results: `results/20261115T001327Z_n8_l1/`, `results/20261115T001604Z_n8_l4/`. The app's own handoff ZIPs (parents `6bccf63e…` L1 and `3abe54e6…` L4) also passed: `results/20261115T011930Z_n8_l1/` and `results/20261115T012007Z_n8_l4/`. For the app side, start with `APP_SIDE_UPDATE.md`.

## What is in here

| File | Purpose |
|---|---|
| `rtl/matmul.sv`, `rtl/matmul_axi.sv` | Byte-exact copies from teammate commit `84fcae1000f056f869b6b84a28804b98cb7b6a48` (`hardware/`). `build.py` refuses to build if their SHA256 changes. Do not edit. |
| `matmul_board_top.sv` | Board top: block-design wrapper + `matmul_axi #(N, LANES)`. Uses no package pins. |
| `build.tcl` | Vivado batch flow: block design, synthesis, place and route, bitstream, XSA, `psu_init.tcl`, reports. |
| `build.py` | One-command build: verifies RTL hashes, runs `build.tcl`, collects reports (`hw/tools/collect_reports.tcl`), summarizes them (`hw/tools/vivado_summary.py`), judges timing/DRC, writes `implementation_manifest.json`. |
| `run_matmul.tcl` | xsdb script: JTAG boot, load bitstream, then register reads/writes. Prints raw `MM ...` readings only. |
| `run_board.py` | The fixed runner: checks hashes, runs `run_matmul.tcl`, judges every value against a Python reference model, writes the result folder per `docs/spec/BOARD_RESULT_FILE.md`. |
| `tests/` | Offline checks for the runner (no board): canned transcripts and an xsdb register-model mock. |

## Design

- Block design: Zynq UltraScale+ PS (KV260 board preset), one AXI master (HPM0_FPD), an AXI SmartConnect (converts the PS AXI4 master to 32-bit AXI4-Lite) and a `proc_sys_reset`. It exports port `M_AXI` plus `pl_clk0` and `pl_rst_n`. `matmul_axi` is instantiated in the hand-written SystemVerilog top, not inside the block design, because Vivado module references do not accept `.sv` files and the RTL must not change.
- Clock: `pl_clk0` from the PS, 99,999,001 Hz as configured by the board preset (the PS PLL cannot make exactly 100 MHz). The constraint comes from the PS IP. Nothing measures the real board frequency.
- Reset: `peripheral_aresetn` from `proc_sys_reset`, synchronous to `pl_clk0` (matmul_axi expects synchronous active-low reset).
- Address map (read back from the block design, written to `build/<cfg>/addresses.tcl`): base `0xA0000000`, range 4 KB. `matmul_axi` decodes only address bits 7:0, so the register map repeats every `0x100` within the 4 KB window. The SmartConnect answers DECERR outside the window.
- Registers (teammate contract): `0x00` ID `0x53494c01`, `0x04` start, `0x08` status (bit0 busy, bit1 done), `0x0c` element index (bit16 = B), `0x10` operand, `0x14` result, `0x18`/`0x1c` cycles, `0x20` N, `0x24` LANES.

## Build

Needs Vivado 2025.2 with the KV260 board files and Python 3. No board needed.

```
python hw/matmul_board/build.py --lanes 1      # ~15-20 min -> build/n8_l1/
python hw/matmul_board/build.py --lanes 4      # separate artifact -> build/n8_l4/
python hw/matmul_board/build.py --compare      # build/compare_n8/summary.md
```

`python hw/matmul_board/build.py --handoff app.zip` builds from the RTL **inside an app handoff ZIP** instead of `rtl/`. It verifies the ZIP and writes `hardware/matmul.sv` and `integration/matmul_axi.sv` to `build/n8_l<LANES>/rtl/`. The manifest records the ZIP hash, the parent run and the parent source map. A clean-room rebuild from the app's ZIPs on 2026-11-14 gave the same circuit: identical timing and area, and only the bitstream header timestamp differs.

`python hw/matmul_board/tests/product_fit_check.py RESULT_DIR ZIP BUILD_DIR` is an independent check (it does not import the runner) that a result fits the app's import rules and is bound to the actual `.bit`, reports and ZIP.

`--force` rebuilds an existing folder; `--stage bd` stops after the block design (quick check). A rebuild may produce a different bitstream hash; the manifest records the one actually built. Each `build/n8_l<LANES>/` holds the `.bit`, `.xsa`, `psu_init.tcl`, `addresses.tcl`, `reports/`, `summary/`, `implementation_manifest.json` (+ `.sha256`) and the Vivado logs. `build/` is git-ignored.

`build.py` prints `BUILD_RESULT ...: PASS` only if the post-route timing report says all user constraints are met, WNS/WHS/pulse-width slack are not negative with no failing endpoints, routing has no errors, and DRC has no errors or critical warnings.

## Build results (2026-11-14, Vivado 2025.2)

Post-route, both configurations: all user timing constraints met, 0 failing setup/hold/pulse-width endpoints, routed DRC and methodology 0 checks, `check_timing` all zero, 0 routing errors, 0 critical warnings.

| | N=8 LANES=1 | N=8 LANES=4 |
|---|---|---|
| WNS / WHS (ns) | 4.757 / 0.001 | 3.885 / 0.035 |
| matmul_axi LUT / FF / DSP / BRAM | 354 / 318 / 0 / 0 | 3612 / 2470 / 0 / 0 |
| Expected compute cycles | 512 (5.12 µs at 100 MHz) | 128 (1.28 µs) |
| Bitstream SHA256 | `63c19180…1909bfc` | `500cc93b…55ce770` |

Full hashes are in each `build/n8_l<LANES>/implementation_manifest.json`. These rows are implementation results; the board results are in `results/`.

## Board run (later task; needs the board)

Same physical setup as `hw/bringup`: micro-USB data cable on J4, 12 V supply on J12, **no SD card**. Close any Vivado Hardware Manager session first.

```
python hw/matmul_board/run_board.py --lanes 1    # one-lane first
python hw/matmul_board/run_board.py --lanes 4    # only after one lane passes
```

It refuses to load unless the build manifest says timing met and DRC clean and the bitstream, `psu_init.tcl` and `addresses.tcl` hashes match the manifest. Then over JTAG it does the following:
- Boots the board into JTAG mode (volatile; a power cycle restores factory boot) and loads the bitstream.
- Reads ID/N/LANES and checks that status is idle, then does the address-register write 5, read 5, write 0, read 0 test.
- Loads A = identity and B[i] = i − 32 and starts the kernel.
- Polls up to 2000 times for `(status & 3) == 2`, then reads all 64 signed outputs and the cycle counter.
- Repeats the job without reloading.
- Pulses the PL reset, then requires status 0 and cycle counter 0, reloads and reruns.

Pass requires every output to equal the Python reference, cycles = N³/LANES (512 or 128) on all three jobs, and the comparator self-check. Output:

```
hw/matmul_board/results/<UTC time>_n8_l<LANES>/{board-result.json, inputs.json, xsdb.log}
MATMUL_BOARD_RESULT: PASS|FAIL (...) <folder>
```

**SiliconeOS handoff ZIP:** `python hw/matmul_board/run_board.py --handoff run.zip` runs the app's exported vectors and links the result to the ZIP's parent run.
- **Checks before loading the board:** every ZIP entry must match its manifest hash; N=8 and LANES 1 or 4; the expected outputs must agree with our reference model and the cycles with the schedule. Then the ZIP's `hardware/matmul.sv` and `integration/matmul_axi.sv` must be byte-identical to the RTL the bitstream was built from. Otherwise it refuses. A CRLF checkout on the app side changes the hash.
- **The result adds:**
  - `parent_run_id`;
  - the parent's `source_sha256` map (`matmul.sv`, `tb.sv`);
  - `wrapper_sha256`;
  - a `handoff` block (ZIP hash, parent-output match);
  - the outputs of all three runs.

**Board presence:** `python hw/matmul_board/run_board.py --check` lists the JTAG chain only, with no reset or programming. It writes `results/board_check.json` with a timestamp.

`input_sha256` follows the app's rule: SHA256 of the raw bytes `x & 255` for A then B. The two 2026-11-14 identity runs predate this and used the earlier JSON rule.

Failed runs are written too (`"status": "fail"`, `"evidence": null`). A second run in the same second gets a `-2` suffix rather than overwriting. Only one run at a time (`results/.runner.lock`). `--inputs file.json` runs other signed INT8 vectors, for example archived SiliconeOS vectors.

## Offline checks (no board)

```
python -B hw/matmul_board/tests/test_run_board.py
```

These checks feed canned transcripts (good, wrong output, wrong cycles, timeout, bad identity/LANES, truncated, xsdb error, reset not cleared) through the result writer. They also run the real `run_matmul.tcl` in xsdb against `tests/mock_board.tcl`, a register-level model of `matmul_axi`, with injected faults. Replay results are labelled `replay_test_not_board` and cannot be written into `results/`.

## Known limitations

- `host_elapsed_ns` is JTAG load + poll + readback time (seconds). It is not kernel speed. Kernel time is `cycles` at the configured clock, and that clock is not measured.
- `board_revision` is null (not readable over this path without extra I2C work).
- The 8x8 multiplies map to LUTs, not DSPs, in this RTL. This is reported, not changed.
- The pass/fail decision uses the default identity/ramp workload unless `--inputs` is given. The accepted parent run and its archived vectors do not exist yet.
