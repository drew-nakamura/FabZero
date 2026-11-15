# matmul_board N=8 LANES=4 post-route

Generated 2026-11-14T16:05:31-08:00 by hw/tools/vivado_summary.py from Vivado report files. This restates tool estimates; it is not evidence of bitstream loading or board execution.

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

- `design_info.txt` (design_info): `d0c58be4c38fb3d74bceada20100ba5769a01496ff307b7c221673152523f8de`
- `drc.rpt` (drc): `be4b9888ca33bdb04dd01013b880cf24d68afea6196e4219ea23da47b9243a35`
- `kernel_paths.rpt` (timing_paths): `3c3e12e46e946d253af1c5d1dc5ff39b177c1cd337acdfaf066a9715b2aa6b4b`
- `methodology.rpt` (methodology): `1ef12799299437cc46f0f66077114ddefa4dbfbf72e7748b9d8a7bd4f8d26489`
- `power.rpt` (power): `4b6533c34244c8e9fa99c964da53f34a56328bce4ef1bcb2820a8bcc1142cd90`
- `timing_summary.rpt` (timing_summary): `4af09be7e103b484a0734882a6b50060d07192f981c6f7b8cb9926c75f71b259`
- `utilization.rpt` (utilization): `6fb971a2ac216476271863ee263804af74484b55c0859b54566eae05d18c5277`
- `utilization_hier.rpt` (utilization_hier): `443cfce06c44591f087e3525b9b56a091b898c3249d0b276fbf3ca34bd53831b`
- `runme.log` (synth_log): `818a56161bda1d87bcee1327d0e19937a43f008ea16d0853cce44f7b8602946f`

</details>
