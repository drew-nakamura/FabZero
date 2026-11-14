# KV260 hardware handoff

Current evidence: portable SystemVerilog kernel, tested with Icarus Verilog. Includes a generic AXI4-Lite wrapper tested in simulation. Not yet synthesized, timed, mapped to DSP/BRAM, integrated into a board design, or executed on KV260. Do not deploy this file alone as an accelerator.

## Partner on Windows

1. Use the user-confirmed **Vivado/Vitis 2025.2** installation on **Windows 11** (approximately **32 GB RAM**); this supersedes the earlier 2026.1.1 report. The KV260 preset is reported visible. Capture actual tool output with `version -short` for the build record. Reported hardware is **SK-KV260-G** with accessory pack **HW-BACCP01-SK-G**; still confirm board revision and exact FPGA part against the physical board and installed preset.
2. Run the supplied `hardware/matmul.sv` and `hardware/tb.sv` in Vivado simulation, with matching N=8 and LANES=1 or 4. Generate inputs using the Python simulation runner or use the exported report's signed input values converted to two-digit hex. The testbench expects `inputs.hex`, A then B in row-major order.
3. Create a board-matched block design with Zynq PS, clock/reset and AXI interconnect. Integrate `matmul_axi.sv`, the generic AXI4-Lite wrapper, using Vivado interface mapping or IP packaging. Connect the 8-bit byte-addressed slave into an allocated PS address segment. Verify reset polarity and clock domain; this wrapper does not cross clock domains.
4. Implemented generic register contract: see the AXI section below. There is still no allocated physical base address or usable board driver until the PS block design and board image are built.
5. The initial RTL uses local arrays with asynchronous reads. Inspect memory inference and critical paths. For a real BRAM implementation, bank B by output lane and account for synchronous read latency in the schedule/counter. Regenerate simulation expectations whenever the schedule changes.
6. Implement separate 1- and 4-lane images. Save whole-design and kernel utilization, timing, part, actual clock configuration, tool versions, source/bitstream hashes. Reject timing failures. Do not equate lane count to DSP allocation.
7. When the board is available, identify its Linux image, kernel and boot firmware versions; these remain unknown. Select a compatible loading flow only after that check (for example, the image-specific PYNQ or xmutil flow). Package matching metadata/device-tree artifacts. Prove a scratch register before arithmetic. Check identical exported inputs and outputs with the Python oracle.

No board connection or FPGA run button is enabled in the web app until this path exists. No physical measurements may be imported as live without artifact identity, correctness, clock and provenance validation.

## Kernel synthesis handoff (available now)

`hardware/synth.tcl` is a non-project, out-of-context synthesis entry point for the kernel. It requires an explicit installed part; it intentionally does not assume a board part or pin assignment. **The script has not been executed here because Vivado is unavailable.** It creates synthesis utilization/timing/DRC reports and a checkpoint, not a deployable bitstream. The requested clock only constrains synthesis timing analysis; it does not establish an achieved board clock. External data ports have no board timing constraints at this stage.

On the Windows build computer, open the Vivado Tcl Shell, change directory to the repository, and inspect the installed tool/parts:

```tcl
version -short
get_board_parts *kv260*
get_parts *xck26*
```

Use the exact part validated against the physical board and installed board preset. An empty board-parts result requires checking board-file installation; an empty parts result requires checking device support. Do not substitute a merely similar part.

In a Windows command prompt with `vivado` on PATH, replace `EXACT_INSTALLED_PART` below and run both candidates into separate output directories (10 ns is a requested 100 MHz clock):

```bat
vivado -mode batch -source hardware/synth.tcl -tclargs EXACT_INSTALLED_PART 8 1 10 build/mac1
vivado -mode batch -source hardware/synth.tcl -tclargs EXACT_INSTALLED_PART 8 4 10 build/mac4
```

If Vivado is not on PATH, launch its supplied command environment or use the full installed path to `vivado.bat`. Preserve the console log and each output directory. Record source identity with PowerShell:

```powershell
Get-FileHash hardware/matmul.sv -Algorithm SHA256
```

Review `utilization_synth.rpt`, `timing_synth.rpt`, `drc_synth.rpt`, and `build_metadata.txt`. Synthesis resource estimates can inform the next implementation, but do not satisfy physical measurements or timing closure. A failing Tcl command should stop the build; do not present missing/stale reports as fresh evidence. The next step remains wrapper integration into a board-matched block design, followed by full implementation and hardware validation.

## Kernel contract and regression

- Valid configurations in this project: N=8/16, LANES=1/4. N must be divisible by LANES; arbitrary parameter values are unsupported.
- Inputs are signed INT8 and outputs are signed INT32. A complete A and B must be loaded before launch. Address selects an element, not a byte; A and B are each row-major N×N arrays.
- Assert `load` while idle for a clock edge to write `data_in` at `address`, selecting A with `operand_b=0` or B with `operand_b=1`. Out-of-range loads are ignored; reads return zero.
- Pulse `start` for one clock while idle. Busy starts and loads are ignored. Holding start high can initiate another run after completion; the future host wrapper must generate a pulse.
- `done` stays high until the next start or reset. `cycles` excludes loading and launch and counts exactly N³/LANES compute clocks. Read outputs only after done; output memory is progressively overwritten during a new run.
- Synchronous active-high reset aborts work and clears busy/done/cycles. Operand/output memories are not cleared; outputs are invalid until a completed run. Reload operands after reset for a reproducible host sequence.

Run the independent protocol regression with `python3 -m unittest discover -s tests -p test_hardware.py -v`. It checks all four supported configurations against its own arithmetic oracle, including signed extremes, repeated runs, busy write/start rejection, reset during execution and recovery, invalid reads, cycle counts, and sticky completion. Existing engine tests separately exercise seeded random and directed vectors through the application runner. Neither test constitutes FPGA execution.

## Implemented AXI4-Lite wrapper

`matmul_axi.sv` provides a 32-bit data bus and 8-bit byte address bus. `aresetn` is synchronous and active low. AW and W are captured independently, with one outstanding write and one outstanding read supported. Responses remain stable until accepted; the intentionally conservative implementation inserts bubbles between transactions. Unknown, unaligned, and read-only write addresses return SLVERR (2); valid transactions return OKAY (0). Unsupported upper address bits must be decoded by the external interconnect.

| Offset | Register | Behavior |
|---|---|---|
| 0x00 | Identity | Read-only `0x53494c01` |
| 0x04 | Control | Write bit 0 with low-byte strobe to pulse start; reads zero |
| 0x08 | Status | Read-only bit 0 busy, bit 1 sticky done |
| 0x0c | Address | Read/write; element index bits 15:0; operand B select bit 16; all byte strobes honored |
| 0x10 | Operand | Low-byte write loads signed INT8 at selected index; only strobe 0 triggers a load; read returns last operand byte zero extended |
| 0x14 | Result | Signed INT32 at selected index; SLVERR until completion or while busy |
| 0x18 | Cycles low | Read-only; SLVERR while busy |
| 0x1c | Cycles high | Read-only; SLVERR while busy |
| 0x20 | Compiled N | Read-only matrix dimension, 8 or 16 |
| 0x24 | Compiled LANES | Read-only lane count, 1 or 4 |

While busy, effective start/address/operand writes return SLVERR and do not change the job. Zero-strobe writes to writable registers are no-ops. An operand write with an out-of-range element index returns SLVERR. The host must load every input before starting; the wrapper does not track operand completeness. Counter halves are stable after completion until a new job; serialize access to avoid another host initiating work between reads. Read results only after polling done. Reset flushes partial AXI transactions and aborts work; the interconnect/master must share an appropriate reset sequence.

Before loading operands, read identity, compiled N and compiled LANES; reject a mismatch against the expected build. These registers identify the interface/configuration, not a cryptographic bitstream identity. For one job: write address then operand for each A/B element; write control=1; poll status until done; write each output index to address and read result; read both cycle halves. This register-loading approach prioritizes bring-up simplicity, and its transfer overhead must be measured separately from kernel cycles.

To synthesize the wrapper plus kernel, append `matmul_axi` to the batch arguments:

```bat
vivado -mode batch -source hardware/synth.tcl -tclargs EXACT_INSTALLED_PART 8 4 10 build/axi4 matmul_axi
```

`python3 -m unittest discover -s tests -p test_axi.py -v` tests all four supported parameter configurations with AW-before-W, W-before-AW, simultaneous AW/W, partial and zero strobes, stalled B/R responses, invalid registers, read-only build configuration, busy write rejection, full arithmetic readback, counters, and reset flushing of a partial write. This is directed simulation, not formal AXI compliance or board validation. The script's optional wrapper synthesis mode is also unexecuted here.
