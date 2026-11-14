# KV260 board bring-up (hello world + programmable-logic proof)

This folder holds the bring-up work that proved our Kria KV260 works and that we can build a design, load it into the FPGA and read correct results back. It is diagnostic scaffolding, not product logic. The future customer design will reuse the same structure.

Status: verified on Drew's KV260 on 2026-11-14, including again after a power cycle.

## What was proven

| Milestone | Evidence |
|---|---|
| 1. Board hello world | The factory boot firmware (U-Boot 2023.01, dated May 10 2024) in the board's QSPI flash answered `echo hello world` with `hello world` over the USB serial console. |
| 2. FPGA logic runs our design | Our bitstream was loaded over JTAG, and the CPU-side debugger read back the expected build ID `0xFAB00001`, a counter that changes over time (about 100 MHz), and `y = 3x + 1` correct for x = 0, 1, 7, 0x12345678 and 0xFFFFFFFF. |

Build results (Vivado 2025.2): synthesis and implementation completed; timing met (worst setup slack +6.079 ns, worst hold slack +0.018 ns at 100 MHz); routed DRC had 4 warnings (PDCN-1569 x3, RTSTAT-10 x1) and no errors; about 1.3% of the chip used. Bitstream SHA256 `67c8294e7a956d6d0f637ec95f224da8e1a54330ecb1da10af2a83926323710d`. A rebuild may produce a different hash.

What we did not do: no Ubuntu/Linux, no SD card, no changes to the board's flash, no compiled CPU program (the ARM compiler is not installed), and no use of the board's external pins.

## How it works

- `pl_probe.sv`: the tiny test logic. It computes `y = 3x + 1` and runs a free-running counter.
- `bringup_top.sv`: the top-level SystemVerilog wrapper. It connects `pl_probe` to the processor block design. The customer's verified modules will go here in place of `pl_probe`.
- `build.tcl`: builds everything in Vivado batch mode (no GUI). It creates the processor block design with the KV260 board preset, plus two AXI GPIO blocks so the processor side can write `x` and read `y`, the counter and the ID. Then it runs synthesis, implementation and bitstream generation and writes the reports.
- `run_pl_probe.tcl`: an `xsdb` script. It switches the board to JTAG boot (temporary; a power cycle undoes it), initialises the processor, loads the bitstream and checks the results. It prints `PL_PROBE_RESULT: PASS` or `FAIL`.
- `serial_capture.ps1`: logs the board's serial console on Windows.

Register map: GPIO0 at `0xA0000000` (`+0x0` writes x, `+0x8` reads y); GPIO1 at `0xA0010000` (`+0x0` reads the counter, `+0x8` reads the build ID).

## Reproduce it

Needs: Vivado 2025.2 with KV260 board files, a 12 V 3 A supply on J12, and a micro-USB data cable on J4. No SD card is needed.

```
cd hw/bringup
vivado -mode batch -source build.tcl          # about 10 minutes; outputs in build/
xsdb run_pl_probe.tcl                         # Vivado/bin/xsdb.bat on Windows
```

The serial console is the second of the board's four USB serial interfaces (COM8 on Drew's PC), at 115200 baud. With no SD card or network, U-Boot repeatedly tries to network-boot; press Ctrl+C repeatedly to get the `ZynqMP>` prompt.

## Gotchas we hit

- `apply_bd_automation ... intc_ip New` is rejected by Vivado 2025.2; `intc_ip Auto` works.
- On Windows, `xsdb.bat` is in `Vivado/bin`, not `Vitis/bin`.
- `xsdb` refuses to read FPGA (PL) addresses until they are declared with `memmap ... -flags 3`.
- The KV260 has no boot-mode switches. JTAG boot is selected by writing `0x0100` to `0xFF5E0200` (BOOT_MODE_USER) and resetting. This is volatile, so a power cycle restores the factory boot.
