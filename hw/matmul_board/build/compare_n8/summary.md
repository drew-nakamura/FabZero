# matmul_board N=8: 1 lane vs 4 lanes (post-route)

Generated 2026-11-14T16:06:01-08:00 by hw/tools/vivado_summary.py from Vivado report files. This restates tool estimates; it is not evidence of bitstream loading or board execution.

## Comparison

| Metric | N=8 LANES=1 | N=8 LANES=4 |
|---|---|---|
| Evidence stage | Post-route | Post-route |
| N / LANES | 8 / n/a | 8 / n/a |
| LUTs | 354 | 3612 |
| FFs | 318 | 2470 |
| LUTRAM | 60 | 50 |
| BRAM36 / BRAM18 | 0 / 0 | 0 / 0 |
| DSP | 0 | 0 |
| Timing met | yes | yes |
| WNS / WHS (ns) | 4.757 / 0.001 | 3.885 / 0.035 |
| Fmax estimate (MHz) | 190.7 | 163.5 |
| Power total (W) | 2.723 | 2.736 |
| Cycles | 512 | 128 |
| Compute time (us) | 5.12 | 1.28 |

Area columns describe each folder's area scope; check each section before comparing.

## N=8 LANES=1

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

</details>

## N=8 LANES=4

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

</details>
