# matmul_board N=8 LANES=4 post-route

Generated 2026-11-14T18:09:56-08:00 by hw/tools/vivado_summary.py from Vivado report files. This restates tool estimates; it is not evidence of bitstream loading or board execution.

## N=8 LANES=4 post-route

- **Evidence stage:** Post-route (implemented design)
- **Tool / device:** Vivado v.2025.2 (win64) Build 6299465 Fri Nov 14 19:35:11 GMT 2025 / xck26-sfvc784-2LV-c
- **Configuration:** N=8, LANES=n/a, top=matmul_board_top

### Area (instance u_matmul (matmul_axi))

| Resource | Used |
|---|---|
| Total LUTs | 3612 |
| Logic LUTs | 3562 |
| LUTRAMs | 50 |
| SRLs | 0 |
| FFs | 2470 |
| RAMB36 | 0 |
| RAMB18 | 0 |
| URAM | 0 |
| DSP Blocks | 0 |

### Timing

- **Constraints:** MET
- **Setup (WNS / TNS):** 3.885 ns / 0 ns (0 failing of 7822 endpoints)
- **Hold (WHS / THS):** 0.035 ns / 0 ns (0 failing)
- **Clock clk_pl_0:** 10 ns (100 MHz constrained)
- **Clock clk_pl_1:** 10 ns (100 MHz constrained)
- **Fmax estimate clk_pl_0:** about 163.5 MHz (1 / (period - WNS); a rough guide, not a verified frequency)
- **Worst setup path:** slack 3.885 ns, 3 logic levels (CARRY8=1 LUT4=1 LUT5=1), `.../kernel/col_reg[2]/C` -> `.../kernel/c_reg[50][5]/D`
- **Worst kernel path:** slack 3.885 ns, 3 logic levels (CARRY8=1 LUT4=1 LUT5=1), `.../kernel/col_reg[2]/C` -> `.../kernel/c_reg[50][5]/D`

### Power (Vivado estimate)

- **Total:** 2.736 W (dynamic 2.436 W, static 0.301 W), junction 31.4 C, confidence Medium
- **Kernel (u_matmul):** 0.016 W
- **By component:** Clocks 0.007 W; CLB Logic 0.007 W; Signals 0.006 W; PS8 2.415 W; Static Power 0.301 W
- Default activity estimate unless a simulation activity file was loaded; not a board measurement.

### Design rule checks

- **DRC:** none found
- **METHODOLOGY:** none found

### Synthesis inference

- **Synthesis messages:** 0 errors, 0 critical warnings, 0 warnings
- **Inferred RTL components:** Adders: 2 Input 32 Bit Adders x9; Adders: 2 Input 6 Bit Adders x1; Registers: 32 Bit Registers x72; Registers: 8 Bit Registers x2; Registers: 4 Bit Registers x1; Registers: 2 Bit Registers x2; Registers: 1 Bit Registers x8; RAMs: 512 Bit (64 X 8 bit) RAMs x2; Muxes: 2 Input 32 Bit Muxes x9; Muxes: 4 Input 32 Bit Muxes x1; Muxes: 3 Input 2 Bit Muxes x2; Muxes: 2 Input 2 Bit Muxes x2; Muxes: 2 Input 1 Bit Muxes x14; Muxes: 4 Input 1 Bit Muxes x3
- **Mapped primitives:** matmul_board_bd_rst_pl_clk0 1, matmul_board_bd_smartconnect_0 1, matmul_board_bd_zynq_ultra_ps_e_0 1, CARRY8 89, LUT1 10, LUT2 383, LUT3 45, LUT4 1180, LUT5 1096, LUT6 1025, MUXF7 384, MUXF8 148, RAM64M8 5, RAM64X1D 5, FDRE 2470

**Distributed RAM: Preliminary Mapping Report (see note below)**

| Module Name | RTL Object | Inference | Size (Depth x Width) | Primitives |
|---|---|---|---|---|
| matmul_board_top | b_reg | Implied | 64 x 8 | RAM64M8 x 8 |
| matmul_board_top | a_reg | Implied | 64 x 8 | RAM64M8 x 2 |

**Distributed RAM: Final Mapping Report**

| Module Name | RTL Object | Inference | Size (Depth x Width) | Primitives |
|---|---|---|---|---|
| matmul_board_top | b_reg | Implied | 64 x 8 | RAM64M8 x 8 |
| matmul_board_top | a_reg | Implied | 64 x 8 | RAM64M8 x 2 |

### Kernel cycles

- **Cycles:** 128 (source: expected)
- **Compute time at constrained clock:** 1.28 us (cycles x constrained clock period (not a measured time))
- **Work:** 512 multiply-accumulates; 4 per cycle; 0.4 GMAC/s at constrained clock
- Excludes operand loading, polling, readback and host transfer.

<details><summary>Input files and SHA256</summary>

- `design_info.txt` (design_info): `6e8aa4a67778af02a84a014adee3bbd13029afc1feecd60e4a300d25ed2d7f66`
- `drc.rpt` (drc): `cbb301fcf35f855272f515d6d90ca83dce5d9cccacf474e61923f56f8a2257ad`
- `kernel_paths.rpt` (timing_paths): `48523f75e2e41b1887500c03e00a53ed1d09c4a51d37d59c9c27ab8e10dc0832`
- `methodology.rpt` (methodology): `291c28cc20a3b6112142201e9bb968715a57733e0fa3f59356cb418be8236013`
- `power.rpt` (power): `8c530a2739fdb6f2b06a6af1ed3ecc6d9611342f2e3e1fbf1f4912b2ed54e5ba`
- `timing_summary.rpt` (timing_summary): `3599c386387203c51b0bcc839a3e7d61aeeae1faa7f3c920110fe91c75390bdf`
- `utilization.rpt` (utilization): `f15b395f365002623282766484599760dbb627a139c68051ce60506922809752`
- `utilization_hier.rpt` (utilization_hier): `4055c6fe242f968974532456b3858aba93a1b5162cd09057d0ef42b4138e223d`
- `runme.log` (synth_log): `00834e14adce05d8139f521700286b915091fca14aaea0462f76deca667b215b`

</details>
