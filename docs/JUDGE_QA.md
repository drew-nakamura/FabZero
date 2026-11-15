# Judge Q&A

These answers describe the committed SiliconOS scope and current evidence status. They deliberately distinguish simulation, generic synthesis, tool reports, and physical board measurement.

## Why not Vivado alone?

Vivado remains necessary for the FPGA build, implementation, timing, and utilization evidence. SiliconOS does not claim to replace it. Its narrow role is to connect a reviewed supported requirement, deterministic candidate selection, RTL/oracle verification, and the identifiers needed to relate a vendor-tool artifact and later board result to the same experiment.

## Why is AI necessary?

It is not necessary for arithmetic correctness or measurement. AI helps turn a natural-language requirement into an editable, provenance-labeled draft and explain supported versus unsupported requests. Deterministic code validates the specification, chooses from the supported catalog, runs checks, and records evidence. If AI is unavailable, manual entry remains usable and is labeled accordingly.

## Is this arbitrary RTL generation?

No. The primary path selects an allowlisted parameterized matrix-multiply recipe. The supported contract is signed INT8 square matrix multiply, N=8 or 16, INT32 accumulation, and one or four lanes. An optional generated-RTL path is gated and must pass source restrictions, unchanged-testbench simulation, an independent oracle, and a trusted cycle monitor before it can be retained. Unsupported requests stay unsupported.

## Is four lanes an optimization or simply more hardware?

It is more arithmetic capacity: four lanes use four times the parallel arithmetic of one lane. For the documented N=8 schedule, the compute-cycle counts are 512 for one lane and 128 for four lanes, excluding loading and host work. That is not a fixed-resource optimization, and a lane count is not a mapped-DSP count.

## Are DSP/LUT/BRAM numbers measured?

No matching Vivado utilization report has been verified at this time. DSP, LUT, and BRAM fields must stay unknown/null until a matching synthesized or implemented artifact report is recorded. A requested DSP budget and a lane count do not measure resources.

## Is latency measured or projected?

The recorded RTL simulation has execution-cycle evidence. Converting those cycles using a requested clock produces a projected kernel time, not hardware latency. It excludes loading, launch, host communication, polling, result readback, and programming. Hardware latency requires an identified artifact, actual configured clock, a defined timing boundary, and board measurement; full-job latency must be reported separately.

## Did you build federated learning or fleet management?

No. An edge-device fleet is a motivating scenario only. SiliconOS does not provide federated learning, camera processing, fleet control, over-the-air updates, or a complete neural-inference application.

## Who has this problem?

The hypothesis is that FPGA, embedded, robotics, accelerator, and hardware engineers who revise supported accelerator configurations may need a trustworthy link between parameters, correctness checks, artifacts, and deployment. We have not yet completed a qualified customer interview or observed session, so we do not claim this hypothesis is validated.

## Who would pay?

The buyer hypothesis is an engineering manager, hardware lead, technical founder, or FPGA-consultancy owner who is responsible for repeated, reliable hardware experiments. No buyer has been interviewed, no price has been validated, and no paid commitment exists. The next test asks a qualified participant who approves a pilot and what evidence would justify it.

## Why not use a CPU or Raspberry Pi?

For a small matrix kernel, a CPU may be simpler or faster end-to-end; SiliconOS does not claim otherwise. The prototype explores a reproducible FPGA-accelerator workflow on the KV260 target. No matched CPU or Raspberry Pi benchmark, speedup, power measurement, or deployment comparison is currently claimed.

## What exactly ran on the KV260?

The partner has saved routed KV260 build reports, bitstreams, and board-result artifacts for N=8 INT8 one- and four-lane designs. The local comparison verifies report and RTL hashes; a separate adapter validates the saved board artifacts, oracle outputs, and lifecycle evidence before an authenticated import to a matching parent run. A saved partner artifact alone is not an accepted app board measurement, and there is no direct live runner connection yet.

## What does the ASIC branch prove?

The app's ASIC branch proves generic Yosys synthesis and netlist-oracle verification for an accepted source. Separately, a recorded N=8/LANES=1 INT8 baseline was mapped to SKY130 HD standard cells and taken through physical implementation experiments. The latest saved route has positive extracted setup/hold slack and zero reported detailed-route DRC, Magic DRC, KLayout DRC and LVS errors, but still has slew, capacitance, fanout and antenna violations. This is real PDK-specific implementation evidence, not signoff, fabrication readiness or a product power/performance claim. FPGA resource budgets do not apply to the generic ASIC result.

## What does the receipt contain?

For the supported workflow, it binds the reviewed specification, provenance, selected recipe, source/testbench and vector identities, correctness result, execution-cycle record, and limitations. A future FPGA receipt must keep parent RTL simulation, implementation artifact, and `board_measured` child result separate rather than relabeling simulation as hardware.

## What happens after the demo?

The next test is a consented, one-to-one observed session with a relevant engineer. We will ask about their most recent configuration change before showing the product, observe an uncoached supported workflow attempt, record failure points and required evidence, and ask for a non-confidential follow-up workload and second session. Refusal or lack of follow-up will be recorded alongside positive feedback.
