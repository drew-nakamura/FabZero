# Windows partner: FPGA gameplan

**Goal: one verified N=8 hardware run first, then compare one and four lanes.** Tonight's synthesis work does not need the board. Board deployment does require its exact hardware, running image and supported loading flow. Our kernel and AXI wrapper pass directed simulation; Vivado synthesis, implementation and physical execution are still unverified.

## Send back these facts first — 10 minutes

- Vivado and Vitis versions from Help → About. Keep the installed versions initially.
- Exact board model/revision when available; an existing working board project is especially useful.
- In Vivado Tcl Console: run `version -short`, `get_board_parts *kv260*`, and `get_parts *xck26*`; copy results. Matching names are discovery results, not permission to select an unverified part.
- Tomorrow: board Linux image/distribution, kernel version, SSH hostname/login (no password), and any already-working overlay/application example. `cat /etc/os-release` and `uname -a` are useful read-only checks. Is this a PYNQ image, an AMD accelerated-application image, or something else?

Do not spend the first hour upgrading tools. If device support or a board preset is missing, identify the exact missing component. Vitis is not needed for our existing RTL synthesis path; its role depends on the eventual host/boot flow.

## Tonight: synthesis checkpoint — aim for 45–60 minutes

1. Obtain the current repository. For a fresh checkout after this branch is pushed:

```bat
git clone --branch codex/siliconos-demo https://github.com/drew-nakamura/FabZero.git
cd FabZero
```

For an existing clean clone, fetch origin and switch to the matching branch; preserve any local work before switching. Confirm the checkout includes `hardware/matmul.sv`, `hardware/matmul_axi.sv`, and `hardware/synth.tcl`.
2. Verify the exact installed device part against the board/preset. If unavailable tonight, complete tool discovery and simulation; do not invent the part.
3. In a command prompt where `vivado` is available, run these commands from the repository root, replacing `EXACT_INSTALLED_PART`:

```bat
vivado -mode batch -source hardware/synth.tcl -tclargs EXACT_INSTALLED_PART 8 1 10 build/axi1 matmul_axi
vivado -mode batch -source hardware/synth.tcl -tclargs EXACT_INSTALLED_PART 8 4 10 build/axi4 matmul_axi
```

The 10 ns period requests 100 MHz for analysis; it is not an achieved hardware clock. This out-of-context flow produces no board bitstream. The script has not yet been exercised in Vivado; send the first error and surrounding log if it fails.

4. Keep both output directories: `utilization_synth.rpt`, `timing_synth.rpt`, `drc_synth.rpt`, `matmul_synth.dcp`, and `build_metadata.txt`. Save the Vivado console log. Report actual mapped resources; lanes are not DSP counts. Memories currently use asynchronous reads, so inspect inference and address/multiplexer paths.
5. Hash both source files in PowerShell:

```powershell
Get-FileHash hardware/matmul.sv -Algorithm SHA256
Get-FileHash hardware/matmul_axi.sv -Algorithm SHA256
```

**Exit condition:** one reproducible synthesis result or a precise blocker. Do not burn the evening trying speculative RTL optimizations before a baseline exists. If Icarus is installed, `python -m unittest discover -s tests -p test_axi.py -v` exercises all four configurations; otherwise the supplied `tb_axi.sv` is a self-contained simulation top with no input file dependency.

## Tomorrow: board integration — start with N=8, LANES=1

Use an existing working project matched to this board and software image when possible. Otherwise establish the correct PS configuration before creating a new design.

1. Add the two RTL sources to a Vivado project using the verified device/board. Create an IP Integrator block design containing the correctly configured Zynq UltraScale+ processing system. AMD documents processor Block Automation and Connection Automation; available presets depend on installed board support. [AMD UG994: designer assistance](https://docs.amd.com/r/2024.1-English/ug994-vivado-ip-subsystems/Using-the-Designer-Assistance-Feature)
2. Add `matmul_axi` as a module reference with N=8 and LANES=1. Check that the `s_axi_*` ports form one AXI4-Lite slave interface. AMD supports interface inference from conventional port names; if inference is incomplete, package the existing RTL as custom IP and explicitly map its ports. Do not replace its tested logic with an unrelated generated peripheral. [AMD UG994: AXI inference](https://docs.amd.com/r/en-US/ug994-vivado-ip-subsystems/Inferring-AXI-Interfaces), [AMD UG1118: custom IP](https://docs.amd.com/r/2026.1-English/ug1118-vivado-creating-packaging-custom-ip/Introduction)
3. Connect an enabled PS-to-PL AXI master through the appropriate interconnect/conversion to the slave. Connect wrapper, interconnect and associated PS AXI clock inputs to the intended clock domain. Drive the wrapper's synchronous active-low `aresetn` from the correctly synchronized peripheral reset. This RTL has no clock-domain crossing logic. Review clock/reset associations instead of assuming automatic inference completed them.
4. In Address Editor, assign an accessible non-overlapping segment and **record the actual base address**. The slave exposes 8 address bits, with implemented offsets through 0x24; use the allocated segment's documented accesses only. Do not guess a base address or treat an alias as another peripheral.
5. Validate the design; resolve errors and relevant clock/reset/address warnings. Generate output products and the HDL wrapper, then synthesize, implement and generate the bitstream. Inspect final timing and design-rule reports. A successful synthesis alone is insufficient. These are standard IP Integrator stages; match documentation to the installed release. [AMD UG994](https://docs.amd.com/r/2024.1-English/ug994-vivado-ip-subsystems)
6. Export the hardware/metadata required by the **confirmed** board software flow. Select loading only after checking the running image. AMD accelerated applications use matching firmware/application packages; `xmutil loadapp` is an application loader, not a universal command for an arbitrary `.bit`. If using PYNQ, verify that image's overlay/metadata requirements first. Preserve the working board image. [AMD KV260 application deployment](https://xilinx.github.io/kria-apps-docs/kv260/2022.1/bist/1_2/build/html/docs/run.html)

## Exact register smoke test

Use a host MMIO facility supported by the actual image and mapped base address. The notation below means ordered 32-bit accesses at **verified base + offset**; it is an algorithm, not a ready-to-run driver. Confirm accesses complete successfully. Do not read results/counters while busy because those accesses can return SLVERR.

1. Read 0x00 → expect `0x53494c01`. Read 0x20 → 8. Read 0x24 → selected lane count. Reject mismatches.
2. Read status 0x08 and require busy bit 0 clear. Write 0x0c = `0x00000005`, read back 5; write 0x0c = 0, read back 0. This tests a harmless writable register before arithmetic.
3. Set A to the 8×8 identity and B element `i` to `i - 32` for i=0…63. For every A element i, write 0x0c=i then 0x10=(1 if row==column else 0). For every B element i, write 0x0c=`0x10000 | i`, then 0x10=`(i - 32) & 0xff`. All 128 operands must be loaded.
4. Write 0x04=1. Poll 0x08 until **`(status & 3) == 2`**, meaning busy=0 and done=1. Use a finite host timeout, for example one second for bring-up; timeout is a failure, not a latency measurement. Do not require observing busy because the kernel may finish between host polls.
5. For each output i, write 0x0c=i and read 0x14. Interpret the result as signed INT32; expect `i - 32` exactly for every element.
6. Read low cycles 0x18 and high cycles 0x1c while idle; combine as `(high << 32) | low`. Expect **512** for one lane or **128** for four lanes. These counts exclude register loading, host polling and readback.
7. Run the same operands again without reloading, repeat the completion predicate and verify every result/counter. Then test an exported seeded application dataset against the Python oracle.

Only after the one-lane image passes should we build/load the four-lane version and repeat the identical inputs. Label the comparison as added arithmetic parallelism. It is not a fixed-resource optimization claim.

## Evidence, timeboxes and fallback

Keep the Vivado version, exact part, source hashes, project/block-design export, address map, clock configuration, bitstream hash, deployment metadata, full utilization/timing reports, board image/kernel identification, inputs, all outputs, cycles and host timestamps. Preserve separate one-/four-lane artifacts. Convert cycles to time only using a verified actual clock configuration; report host end-to-end timing separately.

- **First 30 minutes with the board:** establish SSH/image identity and a known working hardware access path.
- **Next 60–90 minutes:** target identity plus address-register round-trip. If blocked, isolate clock/reset/address/loader issues before arithmetic.
- **Next 30 minutes after register access:** complete one-lane correctness and repeated execution. Get a short recording and immutable evidence copy.
- **Then:** attempt the four-lane image and UI evidence integration. Drop optional optimization work if this threatens the working demo.

If only synthesis works, demonstrate the app's genuine RTL simulation plus clearly labeled synthesis reports. If only one physical configuration works, demonstrate it and keep the other labeled simulated. Neither fallback is a completed physical acceleration comparison. Do not replace missing board evidence with projected microseconds.
