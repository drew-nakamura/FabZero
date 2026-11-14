# Reusable RTL shortlist

Reviewed 2026-11-13. These are research candidates, not integrated or locally qualified components. Upstream tests are evidence about upstream configurations, not proof of our integration. No third-party RTL was imported in this review.

| Source | Candidate use | License / integration considerations | Priority |
|---|---|---|---|
| [ZipCPU/wb2axip](https://github.com/ZipCPU/wb2axip) | AXI-Lite bridges, buffering and protocol-verification examples | README states Apache-2.0 and describes formal verification. Review the exact selected files and proof assumptions; retain notices. Do not replace our tested slave without a demonstrated need. | First review for bus infrastructure |
| [PULP common_cells](https://github.com/pulp-platform/common_cells) | FIFO, arbitration, reset and CDC utilities | [License](https://github.com/pulp-platform/common_cells/blob/master/LICENSE): Solderpad 0.51 with an Apache-2.0 option in its text. Check active vs deprecated modules, includes, packages and supported parameter ranges. CDC still requires physical constraints. | First review for small utilities |
| [lowRISC OpenTitan primitives](https://github.com/lowRISC/opentitan/tree/master/hw/ip/prim) | FIFO, counters, synchronizers and register utilities | Apache-2.0 at repository level; exact dependencies and technology-specific implementations need inspection. Import a dependency closure, not a whole SoC. | Second choice for utilities |
| [Alex Forencich verilog-axi](https://github.com/alexforencich/verilog-axi) | AXI adapters, FIFOs, DMA and cocotb test references | [COPYING](https://github.com/alexforencich/verilog-axi/blob/master/COPYING) is MIT. Repository explicitly deprecated in favor of Taxi; no future upstream fixes promised. A pinned legacy module needs local regression coverage. | Evaluate only for a specific need |
| [FPGA Ninja Taxi](https://github.com/fpganinja/taxi) | Current AXI/stream transport ecosystem with Cocotb/Verilator tests | Upstream offers CERN-OHL-S-2.0 or paid commercial licensing. Do not assume the legacy library's MIT terms carry over. Review obligations before adoption. | Defer pending license and integration choice |
| [EnjoyDigital LiteX](https://github.com/enjoy-digital/litex) | SoC integration, buses and reusable peripheral ecosystem | Framework states BSD-2-Clause; dependencies have their own licenses. Python/Migen generation adds a different build path. Not a quick replacement for our KV260 PS integration. | Post-demo platform option |
| [Berkeley HardFloat](https://github.com/ucb-bar/berkeley-hardfloat) | Future floating-point arithmetic | Chisel generation and recoded floating-point representation; README warns about maturity. Exact source license must be reviewed before importing. FP is outside current INT8 contract. | Defer |

## First integration decision

Retain our verified INT8 compute engines and AXI wrapper for the presentation baseline. If buffering is needed, evaluate one synchronous FIFO utility first. If protocol adaptation is needed, evaluate one AXI utility. Add neither merely to increase the number of catalog entries. Do not add CPUs, floating-point units or DMA before the current physical job works.

## Qualification gate

1. Select exact module and immutable upstream commit; collect license files, copyright notices, dependencies and source hashes.
2. Record supported parameters, ports, signedness, clock/reset behavior, handshake and latency contract. Distinguish FPGA primitives from portable RTL and ASIC technology cells.
3. Compile in our actual toolchain. Run upstream relevant tests plus local reset, full/empty, backpressure and arithmetic/protocol integration cases as applicable.
4. Synthesize the selected configurations; preserve logs, warnings and source identity. Netlist simulation adds evidence; upstream formal claims do not transfer automatically.
5. Compare against the existing baseline using the same workload and constraints. Enable the block in the runnable catalog only after these gates pass.
6. Credit upstream in UI/export manifests and retain required notices with redistributed source. No claim of affiliation or endorsement.

## Compact catalog for Groq

Give the model metadata, not entire repositories: block ID, version, purpose, legal parameter values, interface, dependencies and qualified targets. The model emits an allowlisted block ID and validated parameter values. Deterministic code resolves pinned files and generates wrappers from reviewed templates. Reject unknown IDs, unsupported compositions and arbitrary paths/commands.

Each catalog entry should record: repository URL, pinned commit, source paths and hashes, license/notices, parameter schema, interface/clock/reset contract, tool versions, test reports, synthesis reports and qualification status. Research candidates remain separate from executable blocks. Cache builds using the full dependency hashes, parameters, tool versions and constraints. Never reuse a cached report after changing its inputs.
