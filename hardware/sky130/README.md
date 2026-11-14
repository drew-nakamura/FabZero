# SKY130 standard-cell mapping

This optional command maps the existing supported INT8 GEMM kernel to a locally
installed SKY130 high-density standard-cell Liberty library. It requires Yosys;
Icarus Verilog and `vvp` are required when the corresponding official cell models
are present. It downloads nothing and does not modify the PDK.

```sh
python3 hardware/sky130/map.py \
  --liberty /absolute/path/to/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib \
  --output build/sky130-mapped-n8-l1 --size 8 --lanes 1
```

Use an empty output directory. Each tool invocation is bounded to 120 seconds or
less. The output includes source and library snapshots, synthesis script, raw
logs, technology-mapped netlist, statistics, and `report.json` with hashes.
If sibling `verilog/primitives.v` and `verilog/sky130_fd_sc_hd.v` files exist,
the command simulates the mapped netlist using those official models and checks
all outputs against an independent Python matrix multiplication and cycle count.
This is one deterministic random vector set, not exhaustive equivalence proof.
Failures return nonzero; a report with `mapped_netlist_verified: false` must not
be presented as verified.

`standard_cell_area_um2` is a Liberty-derived sum of mapped cell areas. It is not
the physical core/die area and excludes utilization, placement, wiring and
physical-only cells. Functional simulation uses zero-delay models, so it does
not verify achievable frequency. Physical timing, power, DRC, LVS and GDSII are
outside this command. The library corner is encoded by its filename; the
example uses typical process, 25 °C and 1.80 V.

The PDK and standard-cell model licenses remain their upstream licenses;
snapshotted models retain upstream copyright headers. This script does not
represent foundry qualification or tapeout approval.
