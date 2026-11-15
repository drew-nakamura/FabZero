# Compare real KV260 builds

On the FPGA target, click **Compare real KV260 builds** above the architecture cards.
The local API (`GET /api/kv260/builds`) reads the fixed `build/drew-branch/n8_l1`
and `n8_l4` directories. Each needs `implementation_manifest.json`,
`reports/utilization.rpt`, and `reports/timing_summary.rpt`.

The reader verifies exact report bytes against the manifest SHA-256 values and
both `hardware/matmul.sv` and `hardware/matmul_axi.sv` against the manifest RTL
hashes. It also checks parameters, routed stage, design name, device and Vivado
version. Both builds must pass before any values are returned. A changed source,
missing file or altered report clears the comparison and shows an actionable error.

The table shows whole-design LUTs, flip-flops and DSPs, plus setup, hold and
pulse-width timing margins parsed from the routed report. Clicking a value opens
its original report. These numbers are separate from simulated cycles and do not
establish physical board execution. The board-result JSON is not read by this view.

Drew's downloaded builds use the original INT8 RTL at commit
`84fcae1000f056f869b6b84a28804b98cb7b6a48`. Concurrent precision changes in the working
tree invalidate that source match. Do not overwrite those edits or relax the check
to make old metrics apply to a new design: use the original checkout for the old
builds, or rebuild the new RTL and supply matching manifests and reports.

Focused checks:

```
python3 -m unittest tests.test_build_compare -v
node --test tests/test_kv260_builds_web.js
```
