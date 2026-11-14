# SiliconOS implementation contract

This document separates the current software/RTL prototype from tomorrow's proposed board integration. It is a handoff contract, not evidence that synthesis, deployment, or customer validation succeeded. The current two-person team has a Windows Vivado/Vitis host of unknown version and expects KV260 access tomorrow.

## Supported experiment

Signed INT8 square matrix multiplication, C=A×B with INT32 accumulation; sizes 8 and 16; one or four arithmetic lanes. Inputs are row-major. No bias, scaling, saturation, activation, neural network, camera pipeline, dynamic matrix dimensions, or model compilation is included. Size and lane count are compile-time RTL parameters: changing either requires the matching build, unless a later implementation explicitly supports runtime selection.

The API accepts the following specification. Defaults are assumptions to review, not extracted user requirements:

```json
{
  "operation": "matrix_multiply",
  "size": 8,
  "precision": "int8",
  "target": "kv260",
  "frequency_mhz": 100,
  "max_dsps": 16,
  "max_lanes": 4,
  "objective": "minimize_latency"
}
```

`frequency_mhz` is a requested target, not achieved frequency. `max_dsps` is a budget whose feasibility remains unknown until implementation reports are associated with the exact candidate. `max_lanes` limits architecture enumeration, not the FPGA's allocated DSP count. Supported alternate objective: `minimize_lanes`; this is not a power objective. `minimize_latency` currently ranks projected kernel cycles, not full application latency.

AI extraction must preserve unsupported explicit requirements. “Detect defects from a camera at 60 FPS” is unsupported; offer an explicitly acknowledged GEMM experiment separately. Never silently turn that request into a functioning detector. Each field should retain provenance (`user`, `inferred`, `default`, or `unresolved`). Unresolved requirements need review before a run can be presented as satisfying the original request. Manual spec editing remains a complete path when credits or credentials are unavailable.

## Evidence contract

| State | Permitted claim | Required provenance |
|---|---|---|
| Analytical | Ideal schedule projection | Spec, lane count, equation, assumed frequency |
| RTL simulation | RTL produced correct outputs for these vectors and counted these cycles | Simulator version, source hashes, input/output vectors and hashes, seed, correctness |
| Implemented | This exact design mapped to these resources and met this clock constraint | Vivado version, target part, source/build hashes, top/parameters, clock constraint, timing and utilization reports |
| Board measured | This artifact executed correctly on this physical board | Prior build identity plus board/image identity, bitstream hash, run timestamp, complete output check, cycles, actual configured clock, timing boundaries |

Missing values remain unknown (`null`), not zero. A simulated microsecond value is a cycle count divided by an assumed clock. It is not measured FPGA latency. An implementation report is not proof of deployment. A successful historical run is labeled recorded when the board is disconnected.

For the existing schedule, ideal kernel cycles are N³/L; the run's RTL counter is authoritative for simulation. Four lanes spend more arithmetic capacity. They do not demonstrate a fixed-resource optimization. Full-job timing must include operand staging and result retrieval; keep programming time separately visible. CPU comparisons require identical numerical semantics and explicit timing boundaries.

## Critical implementation gaps and gates

1. **Physical communication:** a generic AXI-Lite wrapper is now simulated, but still needs PS/block-design integration; derive its physical base address from exported hardware metadata. Before GEMM, load the new design and demonstrate identity/address-register read/write. A stock overlay proves only the deployment infrastructure.
2. **Tool/image compatibility:** record Windows Vivado/Vitis versions, exact target part/board definition, board Linux image/kernel and existing loader. Prefer an already working platform. Do not assume a Windows tool install implies compatible Linux runtime packaging, or prescribe a tool upgrade before inventory.
3. **Memory and resource mapping:** current flat local arrays and asynchronous reads may map to muxes/registers/distributed RAM. They are not evidence of banked BRAM or a specific DSP count. Keep the tiny arrays if timing/resource results are acceptable; avoid redesigning memory solely for presentation. In a banked implementation, document how all lanes receive operands each cycle.
4. **Measured constraint enforcement:** associate reports with a concrete artifact, N, L and clock. Rank only candidates with verified timing and resources as feasible hardware recommendations. If none qualify, say no verified feasible candidate. Zero-DSP requests can only be accepted after an actual zero-DSP implementation exists.
5. **Runner integration:** a single local runner owns programming and MMIO, checks identity, loads inputs while idle, starts, times out, reads every result and checks correctness. Never accept arbitrary RTL, shell commands or register addresses from public users. Board loading is serialized.
6. **Product claim:** AI drafts specs; deterministic code validates/ranks; tools produce evidence. No generated explanation overrides a failed check or invents resource/performance measurements.

## Two-person execution order

Tonight: hardware owner simulates edge cases and prepares a buildable integration; product owner finishes the editable spec, comparison, evidence export and customer task. Confirm tool versions when the partner returns. Avoid adding cloud orchestration, DMA, a camera pipeline or paid-account onboarding before the core loop works.

Tomorrow: inventory board → preserve boot media → known loader → custom scratch register → one-lane correct run → four-lane correct run → save reports and run manifests → connect result to UI. If deployment blocks, keep a truthful simulation demo while continuing the hardware fix; do not relabel simulation as board evidence.

Minimum convincing physical demo: one fresh job, correct outputs, hardware cycle count, exact bitstream identity, and a downloadable result. A second artifact improves the comparison but is subordinate to the first successful run. Capture a backup recording after a real run. Measured DSP-budget switching is optional until mapped counts differ; use the explicit lane constraint for the honest software-only interaction.

## AI-credit handoff

Ask only for provider, whether credits cover product API requests, and chosen model availability. The current adapter expects server-side `OPENAI_API_KEY` and `OPENAI_MODEL`; other providers need a compatible adapter. The owner enters secrets locally, never in chat or browser code. Make one successful supported extraction and one unsupported-request rejection before calling the integration live. Credits are optional to the deterministic demo.
