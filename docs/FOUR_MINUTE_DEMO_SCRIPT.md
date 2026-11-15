# Four-minute SiliconOS demo script

**Evidence status for this version:** verified RTL simulation and app-based generic ASIC synthesis are available. A separate SKY130 research flow has technology mapping and physical-run artifacts, with unresolved electrical and antenna violations. Vivado synthesis, implementation, timing closure, bitstream loading, and KV260 execution are unverified. Keep these evidence tracks distinct.

## Before presenting

Open the prepared supported specification, candidate comparison, a real RTL-simulation run, and its receipt. Put `docs/DEMO_PRODUCT_AND_FPGA_SPEC.md` evidence-state language in presenter notes. If the live AI provider is unavailable, use manual specification entry and say so. Do not use a fabricated board screen, resource report, quote, or customer count.

## Timed narration

| Time | Show | Say |
|---|---|---|
| 0:00–0:30 | Problem statement and current evidence status | “Changing an accelerator parameter is easy. The expensive, error-prone part is proving the resulting variant is correct and knowing exactly what was deployed. SiliconOS is a narrow workbench for an edge-hardware engineer: configure a supported accelerator, prove it against an independent oracle, prepare an identified FPGA handoff, and export a reproducible receipt. We have not yet completed a qualified customer session, so this problem is a hypothesis we are testing—not customer demand.” |
| 0:30–1:05 | Plain-language request, editable typed specification, field provenance | “An engineer can describe the requirement in plain language. AI drafts an editable specification and identifies what it inferred or defaulted. The engineer reviews it; deterministic validation decides what is supported. Today, that scope is signed INT8 square matrix multiplication, N=8 or 16, with INT32 accumulation and one or four lanes. It does not silently turn an unsupported camera, FP16, or arbitrary RTL request into a demo.” |
| 1:05–1:40 | One-lane and four-lane comparison; change max lanes to one, then restore it | “This is the capacity decision. For the same N=8 kernel schedule, one lane has 512 compute clocks and four lanes has 128 compute clocks. Those are analytical/simulated kernel compute cycles; loading, launch, host communication, readback, and programming are excluded. Four lanes use four times the arithmetic parallelism. That is capacity scaling, not a fixed-resource optimization, and it is not proof of four mapped DSPs. At a requested clock, any microseconds shown are projected until timing and clock configuration are verified.” |
| 1:40–2:30 | Fresh or archived real RTL simulation; output/oracle match; hashes and cycle record | “Now we run the checked-in SystemVerilog path and compare every signed INT32 output with an independent Python integer oracle. A pass means these recorded vectors matched, with source and input/output hashes plus an observed execution-cycle record. This is `rtl_simulation` evidence—not FPGA execution, universal formal proof, or a resource measurement. The receipt keeps the exact specification and artifacts together so another engineer can inspect and replay the decision.” |
| 2:30–3:15 | FPGA evidence panel / handoff manifest with explicit status | “Our partner has saved routed KV260 builds and board-result artifacts for the one- and four-lane N=8 INT8 designs. SiliconOS checks build reports against exact RTL and bitstream hashes, and the board-result adapter checks outputs and lifecycle evidence before importing a signed child result. Show each artifact at its accepted evidence level: a saved file is not automatically an app-validated board run. The direct live runner connection remains pending.” |
| 3:15–3:30 | ASIC branch and SKY130 research evidence, if shown | “The app verifies RTL and its generic synthesized netlist. We also ran a separate SKY130 technology mapping and physical design experiment for the one-lane N=8 baseline. It produced inspectable mapping and route artifacts, but electrical and antenna violations remain. This is physical-design progress, not signoff or fabrication readiness.” |
| 3:30–4:00 | Evidence receipt and customer-test slide | “The receipt is the product: reviewed requirement, selected recipe, source and vectors, correctness result, and clearly separated evidence levels. Our next customer test is one observed session with a relevant engineer, starting from their most recent configuration change and then having them use this narrow workflow without coaching. We will ask what evidence they require before reuse or deployment, and whether they will bring a non-confidential workload for a second session. Until that happens, demand and willingness to pay remain unvalidated.” |

## Conditional substitutions

Use these only when the referenced artifact exists and is displayed.

- **Live AI:** “This draft came from the configured server-side AI adapter.” Otherwise: “AI is unavailable in this session; the same typed specification is entered manually.”
- **Physical FPGA:** Replace the 2:30–3:15 wording only with the artifact hash, board identity, tool version, configured clock, matching implementation report, complete oracle result, measurement boundary, and timestamp from an accepted `board_measured` child result. Show full-job timing separately from hardware compute cycles.
- **Customer learning:** Add a participant's role, a concrete incident, or a quote only after their explicit consent permits that use. State the number of qualified sessions with its denominator; one session is directional only.

## Claims to keep out of the pitch

- A deployed fleet, federated learning, camera processing, FP16, arbitrary RTL deployment, or fleet management.
- Measured DSP/LUT/BRAM, latency, throughput, savings, or speedup without matching physical/tool artifacts.
- Customer demand, willingness to pay, or named attribution without a real, consented conversation.
- ASIC signoff, fabrication readiness, or timing closure from a generic synthesis report or a physical run with unresolved checks.
