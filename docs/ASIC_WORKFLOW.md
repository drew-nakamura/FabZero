# ASIC workflow: what we can finish now

SiliconOS can use the installed Yosys 0.57 to synthesize the existing signed INT8 matrix kernel into a **generic logic netlist** while the FPGA is unavailable. That is a useful ASIC front-end deliverable: inspect the generated structure, compare one- and four-lane variants, and export reproducible artifacts. It is not a manufactured chip, a physical layout, or technology-qualified area/timing/power evidence. No OpenROAD/PDK installation or physical-design run is established in this workspace.

## Stage gates

| Stage | Required work and evidence | Current boundary |
|---|---|---|
| Verified RTL | Simulate arithmetic, reset and transaction behavior; preserve sources, parameters and test vectors | Existing RTL tests provide behavioral evidence; record the exact tested revision |
| Generic synthesis | Elaborate fixed N/LANES, synthesize, check structural errors, export netlist, cell statistics and complete log | Available with installed Yosys; each successful run must be recorded before claiming completion |
| Technology mapping | Select compatible process/library; map sequential and combinational logic; apply real constraints | Needs a chosen PDK/platform and library. Generic cell counts do not pass this gate |
| Floorplan → place → clock tree → route | Define die/core/I/O/power and memory strategy; place cells, build clock distribution, route | Needs a configured physical-design flow and physical library views |
| Post-route checks | Extract parasitics; run static timing analysis (STA), design-rule checks (DRC), and layout-versus-schematic checks (LVS); resolve violations | No results yet. A generated layout alone does not establish correctness |
| Signoff / fabrication handoff | Meet the chosen process's qualified checks and delivery requirements, including relevant power/reliability, test and integration requirements | Outside the completed prototype; fabrication acceptance is process-specific |

Yosys distinguishes generic synthesis from mapping into a supplied library; its documented example uses `dfflibmap -liberty` for registers and `abc -liberty` for combinational mapping. A Liberty file supplies cell models, but does not replace all physical-design inputs. [Yosys official documentation](https://github.com/YosysHQ/yosys)

OpenROAD Flow Scripts documents the floorplan, placement, clock-tree, routing and finishing stages. Its physical-verification tool integration and platform configuration must be selected and checked; do not assume every run meets foundry signoff requirements. [OpenROAD flow overview](https://openroad-flow-scripts.readthedocs.io/en/latest/mainREADME.html), [official flow tutorial](https://openroad-flow-scripts.readthedocs.io/en/latest/tutorials/FlowTutorial.html)

## Reproducible generic run

A local illustrative script, run from the repository root, is:

```tcl
# Save as a .ys file and execute with: yosys -l synthesis.log script.ys
read_verilog -sv hardware/matmul.sv
chparam -set N 8 -set LANES 1 matmul
hierarchy -check -top matmul
synth -top matmul
check -assert
stat
write_verilog -noattr generic_netlist.v
write_json generic_netlist.json
```

Use a separate output directory for every size/lane configuration and preserve the script itself. The application integration may generate an equivalent script; its exported script and raw log are authoritative. `check -assert` is a structural check, not a functional-equivalence proof. Retain the independent RTL simulation result; synthesized-netlist simulation or formal equivalence would add separate evidence.

Export tool version, exact source text/hash, N/LANES, commands, full synthesis log, netlist, cell statistics and warnings. A failed run must not leave a success badge or replace a prior result silently. Label counts **generic synthesized cells** and show their cell-type breakdown. Do not label them square micrometers, gates of a specific fabrication process, FPGA LUTs/DSPs, power, clock frequency, or production cost. Compare results only when tool settings, workload and evidence stages match.

The current local operand arrays may become logic/register structures under generic synthesis. Their resulting size is useful feedback on this RTL implementation; it is not a compiled SRAM design. Replacing them with memory macros requires a real macro/interface strategy and suitable timing/physical views. One- versus four-lane comparison shows capacity scaling, not equal-resource optimization.

## Next inputs for a physical ASIC experiment

Choose a supported **research/demo platform** and compatible tool versions first. Obtain its standard-cell Liberty files and physical LEF/GDS views, technology routing rules, extraction data and configured verification decks. Define clock/I/O constraints, reset assumptions, power intent, floorplan targets, and whether operand storage remains registers or uses supported SRAM macros. Use the platform's documented flow rather than combining unrelated library versions.

Then install/configure a compatible OpenROAD Flow Scripts environment and the platform's verification tools; run a tiny reference design to establish the installation before porting the kernel. Save mapped utilization/timing separately from post-route area/timing. Record corners and constraints with every metric. DRC/LVS/STA failures are actionable findings, not completed stages.

For the current demo, finish the generic synthesis/export loop and show the stage boundary directly in the UI. A concise claim is: **“We simulated the kernel and synthesized its RTL to an inspectable generic netlist. Technology mapping and physical implementation are the next stages.”** Do not spend the remaining FPGA preparation time on an unpinned physical-design installation unless the team deliberately expands scope.


## Selected physical platform: SKY130

The selected process is **SkyWater SKY130A**, using **sky130_fd_sc_hd** standard cells. LibreLane 2.4.10 and a Ciel-managed PDK revision `0fe599b2afb6708d281543108caf8310912f54af` were found locally. The first physical baseline uses the existing default N=8, LANES=1 kernel, a provisional 20 ns clock period and 35% target core utilization. These are flow inputs, not achieved metrics. Storage remains flip-flops rather than SRAM macros.

Prepare a new isolated source/config snapshot:

```sh
python3 hardware/physical/prepare.py --output build/sky130-baseline
librelane --manual-pdk --pdk-root /path/to/pinned/pdk-parent --run-tag baseline -j 4 build/sky130-baseline/config.json
```

The PDK parent must contain `sky130A`; retain its SOURCES/version information with reports. `librelane` may need to be invoked from the installed Nix environment. Do not install a Python-only package and assume the EDA tools are included. The prepared manifest hashes the RTL/config; retain LibreLane's resolved config, tool versions, logs, metrics, netlists, DEF/GDS, DRC and LVS outputs. Review interface delays, output loads, operating corners and switching assumptions before presenting timing or power as representative of a product.

Mapping alone gives a sum of library cell areas, not routed core/die area. A failed later stage does not establish a finished physical design. Generic app builds remain generic; the standalone SKY130 flow does not retroactively change their evidence.

References: [LibreLane official repository](https://github.com/librelane/librelane), [PDK management](https://librelane.readthedocs.io/en/stable/usage/about_pdks.html).

### First technology-mapped baseline

The standalone mapper completed N=8/LANES=1 using SKY130 HD TT 25°C 1.80 V Liberty: 6,899 cells, summed cell area 121,722.992 µm². Official zero-delay cell-model simulation matched 64 outputs and 512 cycles for seed 42. See `docs/evidence/sky130-n8-l1.json` for hashes and qualifications, and `hardware/sky130/README.md` for reproduction. This single-vector mapped-netlist check supplements the existing RTL regression; it is not exhaustive equivalence or timing simulation. This mapped area must not be compared directly to generic Yosys cell counts.
