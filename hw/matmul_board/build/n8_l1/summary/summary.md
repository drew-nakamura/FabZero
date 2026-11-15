# matmul_board N=8 LANES=1 post-route

Generated 2026-11-14T15:53:17-08:00 by hw/tools/vivado_summary.py from Vivado report files. This restates tool estimates; it is not evidence of bitstream loading or board execution.

## N=8 LANES=1 post-route

- **Evidence stage:** Post-route (implemented design)
- **Tool / device:** Vivado v.2025.2 (win64) Build 6299465 Fri Nov 14 19:35:11 GMT 2025 / xck26-sfvc784-2LV-c
- **Configuration:** N=8, LANES=n/a, top=matmul_board_top

### Area (instance u_matmul (matmul_axi))

| Resource | Used |
|---|---|
| Total LUTs | 354 |
| Logic LUTs | 294 |
| LUTRAMs | 60 |
| SRLs | 0 |
| FFs | 318 |
| RAMB36 | 0 |
| RAMB18 | 0 |
| URAM | 0 |
| DSP Blocks | 0 |

### Timing

- **Constraints:** MET
- **Setup (WNS / TNS):** 4.757 ns / 0 ns (0 failing of 3488 endpoints)
- **Hold (WHS / THS):** 0.001 ns / 0 ns (0 failing)
- **Clock clk_pl_0:** 10 ns (100 MHz constrained)
- **Clock clk_pl_1:** 10 ns (100 MHz constrained)
- **Fmax estimate clk_pl_0:** about 190.7 MHz (1 / (period - WNS); a rough guide, not a verified frequency)
- **Worst setup path:** slack 4.757 ns, 13 logic levels (CARRY8=6 LUT2=3 LUT4=1 LUT6=2 RAMD64E=1), `.../kernel/k_reg[0]/C` -> `.../c_reg_0_63_28_31/RAMB/I`
- **Worst kernel path:** slack 4.948 ns, 13 logic levels (CARRY8=6 LUT2=3 LUT4=1 LUT6=2 RAMD64E=1), `.../kernel/k_reg[0]/C` -> `.../kernel/acc_reg[0][31]/D`

### Power (Vivado estimate)

- **Total:** 2.723 W (dynamic 2.422 W, static 0.3 W), junction 31.3 C, confidence Medium
- **Kernel (u_matmul):** 0.002 W
- **By component:** Clocks 0.003 W; CLB Logic 0.002 W; Signals 0.002 W; PS8 2.415 W; Static Power 0.3 W
- Default activity estimate unless a simulation activity file was loaded; not a board measurement.

### Design rule checks

- **DRC:** none found
- **METHODOLOGY:** none found

### Synthesis inference

- **Synthesis messages:** 0 errors, 0 critical warnings, 0 warnings
- **Inferred RTL components:** Adders: 2 Input 32 Bit Adders x5; Registers: 32 Bit Registers x5; Registers: 8 Bit Registers x2; Registers: 4 Bit Registers x1; Registers: 2 Bit Registers x2; Registers: 1 Bit Registers x8; RAMs: 2K Bit (64 X 32 bit) RAMs x1; RAMs: 512 Bit (64 X 8 bit) RAMs x2; Muxes: 2 Input 32 Bit Muxes x8; Muxes: 4 Input 32 Bit Muxes x1; Muxes: 3 Input 2 Bit Muxes x2; Muxes: 2 Input 2 Bit Muxes x2; Muxes: 2 Input 1 Bit Muxes x14; Muxes: 4 Input 1 Bit Muxes x3
- **Mapped primitives:** matmul_board_bd_rst_pl_clk0 1, matmul_board_bd_smartconnect_0 1, matmul_board_bd_zynq_ultra_ps_e_0 1, CARRY8 40, LUT1 7, LUT2 151, LUT3 48, LUT4 74, LUT5 40, LUT6 134, RAM64M8 7, RAM64X1D 2, FDRE 318

**Distributed RAM: Preliminary Mapping Report (see note below)**

| Module Name | RTL Object | Inference | Size (Depth x Width) | Primitives |
|---|---|---|---|---|
| matmul_board_top | u_matmul/kernel/b_reg | Implied | 64 x 8 | RAM64M8 x 2 |
| matmul_board_top | u_matmul/kernel/a_reg | Implied | 64 x 8 | RAM64M8 x 2 |
| matmul_board_top | u_matmul/kernel/c_reg | Implied | 64 x 32 | RAM64M8 x 5 |

**Distributed RAM: Final Mapping Report**

| Module Name | RTL Object | Inference | Size (Depth x Width) | Primitives |
|---|---|---|---|---|
| matmul_board_top | u_matmul/kernel/b_reg | Implied | 64 x 8 | RAM64M8 x 2 |
| matmul_board_top | u_matmul/kernel/a_reg | Implied | 64 x 8 | RAM64M8 x 2 |
| matmul_board_top | u_matmul/kernel/c_reg | Implied | 64 x 32 | RAM64M8 x 5 |

### Kernel cycles

- **Cycles:** 512 (source: expected)
- **Compute time at constrained clock:** 5.12 us (cycles x constrained clock period (not a measured time))
- **Work:** 512 multiply-accumulates; 1 per cycle; 0.1 GMAC/s at constrained clock
- Excludes operand loading, polling, readback and host transfer.

<details><summary>Input files and SHA256</summary>

- `design_info.txt` (design_info): `cc51b6b70a894a7479cf734cddc491c88c4d2061f13387027cfe27dbc9f54c78`
- `drc.rpt` (drc): `e2d60ffec186b5452a84fe83d59d9bd81a0439906b10c5225158418848f18949`
- `kernel_paths.rpt` (timing_paths): `833bd119e7dc86553389cb926522ada38ba66edd0f930cfb800f73598397863e`
- `methodology.rpt` (methodology): `fe582684c930b3177009a01a03037a46c0d144a065681d20d8cba714e5caea96`
- `power.rpt` (power): `ab67349c4a44b60726546c30026fef79aa6b44103eb1bb5ed81c2b91284dc224`
- `timing_summary.rpt` (timing_summary): `d115f86467eeac8a8e6171688ae7297388dba7b1cc17a103c2fe21a09f78707f`
- `utilization.rpt` (utilization): `a7ebc104967218632caa8be16db4ea6643aa9afbf3c3c23e7fd32e50ad56f2f9`
- `utilization_hier.rpt` (utilization_hier): `7c718602263f11645caa5bba383f44c639e0a7e444a6748fe3641c4e7e2ca35d`
- `runme.log` (synth_log): `cad9c5da9b6402f9386d018c77c669c393f8e82d53cf53f74a2ca401f7164ff9`

</details>
