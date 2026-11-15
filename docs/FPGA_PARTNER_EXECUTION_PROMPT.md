# FPGA partner execution prompt

Copy everything under **Prompt** into the FPGA partner's Kiro, Codex, or other coding-agent session.

---

## Prompt

You are the FPGA/Vivado owner for the SiliconOS hackathon demo.

Work independently and in parallel with the product/backend owner. Do not modify `server.py`, `siliconos/`, `web/`, or product documentation unless we explicitly coordinate a contract change. Own `hardware/`, Vivado project/build artifacts, board-runner code, and hardware-specific tests.

Read these files before changing anything:

1. `AGENTS.md`
2. `docs/DEMO_PRODUCT_AND_FPGA_SPEC.md`
3. `hardware/BRINGUP.md`
4. `docs/PARTNER_FPGA_GAMEPLAN.md`
5. `hardware/matmul.sv`
6. `hardware/matmul_axi.sv`
7. `hardware/synth.tcl`
8. `hardware/tb_axi.sv`
9. `hardware/tb_lifecycle.sv`

## Primary objective

Produce one reproducible, physically verified KV260 execution of the existing signed INT8 matrix-multiplication accelerator.

Start with:

- Board: AMD SK-KV260-G
- Tools: Vivado/Vitis 2025.2 on Windows 11
- Top-level accelerator wrapper: `matmul_axi`
- Matrix size: `N=8`
- Arithmetic lanes: `LANES=1`
- Requested clock: 100 MHz / 10 ns, subject to actual timing closure
- Expected kernel cycles: 512

Do not begin the four-lane physical build until the one-lane artifact has passed identity, arithmetic, repeated-run, reset/recovery, and evidence-capture tests.

The application already accepts a signed `board-result.json` import and validates it
against the immutable simulation parent. Do not wait for a direct website-to-board
connection: return physical evidence as files and structured JSON.

## Non-negotiable evidence rules

- Do not claim physical FPGA success until the exact artifact runs correctly on the KV260.
- Out-of-context synthesis is not a board bitstream.
- Synthesis is not implementation or timing closure.
- A generated bitstream is not evidence that it was loaded or executed.
- The requested 100 MHz clock is an assumption until the implemented design and board clock configuration are verified.
- Kernel cycles exclude operand loading, polling, result readback, programming, and host transfer.
- `LANES=1` is not a measured DSP count.
- Keep unknown DSP/LUT/BRAM values unknown until matching Vivado reports exist.
- `LANES=4` uses more arithmetic capacity. It is not a fixed-resource optimization.
- Do not change the kernel workload, precision, schedule, register map, or API/evidence semantics without coordinating with the product owner.
- Do not replace `hardware/matmul.sv` or bypass the existing `matmul_axi.sv` behavior with unrelated generated IP.
- Preserve the working boot image and firmware.
- Do not guess the MMIO base address.
- Do not put passwords, API keys, or private credentials in Git, logs, screenshots, or result files.

## Phase 1: Inventory and tool discovery

Record the exact output of:

```tcl
version -short
get_board_parts *kv260*
get_parts *xck26*
```

Confirm:

- Exact installed part matching the physical KV260
- Exact board preset
- Physical board revision if visible
- Vivado and Vitis versions
- Board operating-system/runtime image
- Kernel version
- Boot firmware identity
- Existing loader/runtime method
- Whether PYNQ, `xmutil`, XRT, Linux FPGA manager, UIO, `/dev/mem`, or another verified path is available
- How the host will access the AXI-Lite registers

Useful board-side read-only commands may include:

```sh
cat /etc/os-release
uname -a
```

Do not upgrade tools, replace firmware, or rewrite boot media before recording and preserving the known state.

Immediately send the product owner:

1. Exact FPGA part
2. Board revision
3. Board image/kernel/firmware identity
4. Intended loading method
5. Intended MMIO-access method

If K26 support or the board preset is missing, report the exact missing component. Do not synthesize for a substitute device.

## Phase 2: Run existing simulations

Before Vivado implementation, run the existing hardware regressions if Icarus is available:

```sh
python -m unittest discover -s tests -p test_hardware.py -v
python -m unittest discover -s tests -p test_axi.py -v
```

Preserve logs.

Do not modify the oracle or expected cycle count to make a failing implementation pass.

## Phase 3: Out-of-context synthesis checkpoint

From the repository root, substitute the exact installed part:

```bat
vivado -mode batch -source hardware/synth.tcl -tclargs EXACT_INSTALLED_PART 8 1 10 build/axi1 matmul_axi
```

If time permits after the first checkpoint:

```bat
vivado -mode batch -source hardware/synth.tcl -tclargs EXACT_INSTALLED_PART 8 4 10 build/axi4 matmul_axi
```

Preserve:

- Vivado console log
- `utilization_synth.rpt`
- `timing_synth.rpt`
- `drc_synth.rpt`
- `matmul_synth.dcp`
- `build_metadata.txt`

Record source hashes:

```powershell
Get-FileHash hardware/matmul.sv -Algorithm SHA256
Get-FileHash hardware/matmul_axi.sv -Algorithm SHA256
```

Report actual inferred resources and warnings. Do not equate a lane with a DSP.

This checkpoint is real synthesis evidence only. It does not establish placement, routing, timing closure, bitstream generation, or board execution.

## Phase 4: Build the KV260 block design

Start with `N=8`, `LANES=1`.

Create or reuse a board-matched Vivado project compatible with the board's actual runtime image.

The block design must include:

- Correctly configured Zynq UltraScale+ processing system
- Supported PS-to-PL AXI master
- Required AXI interconnect or protocol conversion
- `matmul_axi` as a module reference or packaged custom IP
- One intended AXI clock domain
- Correctly synchronized peripheral reset
- Non-overlapping AXI address segment

The wrapper uses:

- `aclk`
- synchronous active-low `aresetn`
- 32-bit AXI data
- 8-bit byte address
- independent AW and W handshakes
- no internal clock-domain crossing

In Address Editor:

- assign an accessible non-overlapping address segment;
- record the actual base address;
- export or screenshot the address map;
- send the base address to the product owner as soon as it is known.

Validate the block design. Resolve relevant errors and warnings involving:

- clock associations;
- reset polarity/synchronization;
- AXI interface inference;
- address decoding;
- unconnected signals;
- unconstrained paths.

Do not change the tested register map merely to simplify integration without coordinating first.

## Phase 5: Implement and generate the deployment artifact

Run the complete board flow:

1. Generate output products.
2. Generate the HDL wrapper.
3. Synthesize the whole design.
4. Implement/place and route.
5. Review timing.
6. Review utilization.
7. Review DRC and unconstrained paths.
8. Generate the bitstream.
9. Produce all metadata required by the confirmed loader/runtime.

Preserve:

- Project or reproducible project-generation Tcl
- Block-design export
- HDL wrapper
- Whole-design utilization report
- Kernel hierarchy utilization report if available
- Final timing summary
- DRC report
- Clock report
- Actual address map
- Bitstream/deployment package
- Required XSA, XCLBIN, DTBO, HWH, shell metadata, or other runtime files as applicable
- Full logs

Reject a timing failure before making a physical speed claim. If 100 MHz does not close, report the actual failure. Coordinate before lowering the target or altering RTL.

Hash the final bitstream and relevant metadata:

```powershell
Get-FileHash PATH_TO_BITSTREAM -Algorithm SHA256
```

Also produce an implementation manifest binding:

- source hashes;
- exact part;
- top module;
- N and LANES;
- requested clock;
- timing-report hashes;
- utilization-report hashes;
- bitstream hash;
- Vivado version;
- build timestamp.

## Phase 6: Load the board

Use only the loading flow confirmed to match the current board image.

Do not assume that `xmutil`, PYNQ, XRT, FPGA manager, or a raw `.bit` load is universally compatible.

Record:

- loader and version;
- exact command or procedure;
- artifact loaded;
- timestamp;
- board image and firmware identity;
- successful or failed loader output.

After loading, verify the physical register interface before arithmetic.

## Phase 7: Register smoke test

Use the actual base address from Address Editor.

Required reads:

- `base + 0x00` → `0x53494c01`
- `base + 0x20` → `8`
- `base + 0x24` → `1`

Require the accelerator to be idle.

Test a harmless writable register:

1. Write `5` to `base + 0x0c`.
2. Read it back and require `5`.
3. Write `0`.
4. Read it back and require `0`.

Stop and debug identity, clock, reset, address, or loader issues if this fails. Do not continue to arithmetic using a guessed address or stale result.

Send the product owner:

- actual base address;
- observed identity;
- observed N;
- observed LANES;
- MMIO method;
- pass/fail status.

## Phase 8: First arithmetic acceptance

Use:

- A = 8×8 identity matrix
- B element `i = i - 32` for `i=0..63`

For each A element:

1. Write index to `0x0c`.
2. Write low signed byte to `0x10`.

For each B element:

1. Write `0x10000 | index` to `0x0c`.
2. Write `(i - 32) & 0xff` to `0x10`.

Then:

1. Write `1` to `0x04`.
2. Poll `0x08` with a finite timeout.
3. Completion condition is `(status & 3) == 2`.
4. Do not require observing busy; the kernel may complete between host polls.
5. For each output index, write the index to `0x0c`.
6. Read signed INT32 from `0x14`.
7. Require output `i = i - 32`.
8. Read cycle low from `0x18`.
9. Read cycle high from `0x1c`.
10. Combine them into one 64-bit count.
11. Require exactly 512 cycles.

Do not read outputs while busy.

Run the same job again without reloading and require the same outputs and cycle count.

Then test reset/recovery:

1. Assert the supported reset sequence.
2. Confirm busy/done/cycles reset behavior.
3. Reload operands.
4. Run the complete job again.
5. Require correct outputs and 512 cycles.

## Phase 9: SiliconOS exported-vector acceptance

Obtain an actual `handoff.zip` from a verified SiliconOS run.

Verify every file hash in its manifest.

Execute the exact exported vectors on the board.

Require:

- input hash matches the parent SiliconOS run;
- all 64 outputs match `expected.json`;
- output hash matches;
- physical cycle count is 512;
- source hashes match the implemented artifact;
- compiled N/LANES match;
- artifact identity and timestamp are recorded.

Do not alter the exported expected output.

## Phase 10: Produce the website return result

Create `board-result.json` matching the contract in:

`docs/DEMO_PRODUCT_AND_FPGA_SPEC.md`

At minimum include:

- schema version;
- unique runner result UUID;
- parent run UUID;
- `evidence: "board_measured"`;
- physical timestamp;
- exact parent source hashes;
- bitstream and wrapper hashes;
- Vivado version and exact part;
- top, N/LANES, and configured clock;
- the complete implementation manifest;
- canonical implementation-manifest hash;
- hashes for timing, utilization, and DRC reports;
- board SKU and revision;
- image, kernel, firmware, and loader identity;
- interface identity/N/LANES reads;
- parent input hash;
- all initial-run outputs, canonical output hash, cycles, and timing boundary;
- all repeat-without-reload outputs, canonical output hash, and cycles;
- all reset-recovery outputs, canonical output hash, and cycles;
- host/programming timing only if actually measured.

Output hashes use compact JSON UTF-8 with no spaces. The full canonical rules and a fixed hash vector are in `docs/DEMO_PRODUCT_AND_FPGA_SPEC.md`.

Configure the same runner-only secret and non-secret key ID in the runner and server process environments. Use at least 32 random bytes for the secret. Never put it in Git, chat, logs, JSON, or screenshots.

Sign the completed unsigned file:

```powershell
$env:SILICONOS_RUNNER_KEY = "locally-generated-secret"
$env:SILICONOS_RUNNER_KEY_ID = "demo-runner-v1"
python -m siliconos.board unsigned-board-result.json board-result.json
```

The command prints only the key ID, never the secret. The website/server will authenticate the HMAC, recompute the implementation-manifest hash, independently recompute every expected output, and reject incorrect, stale, incomplete, unsigned, or mismatched evidence.

Never mark `timing_met: true` unless the complete matching implementation manifest and retained report hashes support it.

## Phase 11: Record the successful run

After physical acceptance passes, record a genuine demonstration showing:

1. Exact artifact identity
2. Board connection
3. Artifact load
4. Identity/N/LANES reads
5. Job execution
6. Complete output match
7. Cycle count
8. Result file returned to SiliconOS

The video may be time-compressed, but label it:

- “Recorded real run”
- “Time-compressed”
- Actual elapsed duration
- Matching artifact/run identity

Do not record or present a simulated or failed run as physical success.

## Phase 12: Four-lane stretch

Only after all one-lane evidence and recording are secure:

1. Reuse the stable board design.
2. Set `LANES=4`.
3. Re-run synthesis and implementation.
4. Review timing, utilization, and DRC.
5. Generate and hash a distinct artifact.
6. Load it.
7. Verify identity/N/LANES.
8. Run identical inputs.
9. Require all outputs to match.
10. Require 128 cycles.
11. Produce a second separate board result.

The four-lane result spends more arithmetic capacity. Do not call it a fixed-resource optimization.

## Required updates to the product owner

Send an update at each gate.

### Gate A: Inventory complete

- Tool version
- Exact part
- Board image
- Loader/MMIO plan
- Blocker, if any

### Gate B: Synthesis complete

- Pass/fail
- Report locations
- Resource summary
- Timing warnings
- Source hashes

### Gate C: Implementation complete

- Timing pass/fail
- Actual clock constraint
- Address map
- Bitstream hash
- Report paths

### Gate D: Register smoke test

- Identity/N/LANES
- Read/write result
- Actual base address
- MMIO method

### Gate E: Physical arithmetic

- All-output pass/fail
- Cycle count
- Repeat/reset result
- Result JSON and evidence locations

Report the first exact error and surrounding log when blocked. Do not spend hours silently retrying speculative changes.

## Definition of done

The one-lane FPGA task is complete only when:

- Vivado implementation has completed;
- relevant timing and DRC checks have been reviewed;
- the deployed artifact is hashed;
- its actual base address is recorded;
- identity/N/LANES reads match;
- all outputs pass the independent oracle;
- cycle count is exactly 512;
- repeat and reset/recovery pass;
- the exported SiliconOS vector passes;
- `board-result.json` is complete;
- the product owner can import and display it;
- a genuine backup recording exists.

If physical deployment does not complete, return the highest truthful evidence reached: OOC synthesis, implementation reports, generated bitstream, loader failure, or register-access failure. Never upgrade that evidence label.
