# SiliconOS demo product and FPGA integration specification

**Revision:** 1.0  
**Date:** November 14, 2026 (America/Los_Angeles)  
**Status:** Scope-frozen implementation specification  
**Audience:** Product/web owner and Windows/Vivado/FPGA owner  
**Hackathon target:** AMD Kria KV260, SKU SK-KV260-G  
**Confirmed build host:** Windows 11, Vivado/Vitis 2025.2, visible KV260 board preset  
**Physical evidence status at this revision:** Vivado synthesis, implementation, timing closure, bitstream loading, and board execution remain unverified

---

## 1. Executive decision

SiliconOS will demonstrate one narrow product promise:

> **SiliconOS helps an edge-hardware engineer configure an accelerator, prove it correct, deploy an identified version to an FPGA, and export a reproducible receipt.**

The demo is not a fleet manager, federated-learning implementation, arbitrary chip generator, camera application, or production deployment service. A heterogeneous edge-device fleet is the motivating scenario. The implemented product addresses one concrete step in that larger workflow:

> **Changing an accelerator configuration is easy. Producing a correct, traceable variant that another engineer can trust is the expensive part.**

The proof uses one signed INT8 matrix-multiplication kernel with two supported sizes and two supported lane counts. The product preserves the requirement, selects a qualified RTL recipe, checks every output, identifies the resulting artifacts, and returns evidence to the website.

### One-sentence pitch

> **From requirement to verified accelerator variant, with a receipt.**

### Product principle

AI may interpret intent, draft a specification, and generate a candidate. Deterministic code decides what is supported, checks arithmetic, controls evidence, and rejects failures. Tool reports and physical execution create measurements. AI never creates measurement fields.

---

## 2. User, buyer, and provable problem

### 2.1 Representative user

“Maya” is an edge-platform or FPGA engineer at a small robotics or embedded-vision company. Maya is a representative persona, not a real interviewed customer.

Maya supports several device profiles:

- a throughput-oriented profile can allocate four arithmetic lanes;
- a capacity-constrained profile permits one lane;
- a model experiment needs a different supported matrix tile size;
- each variant needs a trustworthy source, configuration, test result, build, and deployment record.

The demo uses a KV260 development board. It does not claim that SiliconOS manages a fleet or performs over-the-air updates.

### 2.2 Buyer hypothesis

The likely buyer is an engineering manager, hardware lead, technical founder, or FPGA consultancy owner responsible for prototype schedules and trustworthy design handoffs.

### 2.3 Job to be done

> When a supported workload constraint changes, produce a correct accelerator variant and a reviewable evidence package without manually reconstructing which RTL, inputs, parameters, reports, and deployed artifact belong together.

### 2.4 Problem hypothesis

Without SiliconOS, an engineer typically has to:

1. interpret a requirement;
2. select or edit the hardware configuration;
3. run simulation and vendor tools;
4. compare results against an independent reference;
5. track source, parameters, reports, bitstream, and board results;
6. repeat the process for each device profile.

SiliconOS directly demonstrates that steps 3–5 can be joined into an inspectable workflow for the committed kernel. The commercial claim that this is a top customer pain remains unvalidated until a relevant engineer is observed using the workflow.

### 2.5 Customer-validation requirement

A teammate should observe at least one FPGA, embedded, robotics, or hardware engineer attempting the configuration-and-evidence workflow without coaching. Ask:

1. What accelerator configuration did you most recently change?
2. How did you prove the new version was correct?
3. How did you track which source and reports belonged to the deployed artifact?
4. Where did active work or waiting time accumulate?
5. Would you test SiliconOS on a non-confidential workload in a follow-up?

Record role, existing workflow, task outcome, confusion, and actual follow-up commitment. One conversation is directional evidence, not market validation. If no participant is reached, state that demand remains unvalidated.

---

## 3. Committed technical scope

### 3.1 Kernel contract

- Operation: square matrix multiplication, `C = A × B`
- Operand type: signed INT8
- Accumulation and output type: signed INT32
- Matrix layout: row-major
- Matrix size `N`: 8 or 16
- Arithmetic lanes `LANES`: 1 or 4
- Constraint: `N` must be divisible by `LANES`
- No bias, scaling, activation, saturation, convolution, camera processing, model compilation, training, or dynamic dimensions

### 3.2 Accepted product specification

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

Accepted values:

| Field | Accepted values | Evidence meaning |
|---|---|---|
| `operation` | `matrix_multiply` | Fixed workload |
| `size` | 8 or 16 | Compile-time parameter |
| `precision` | `int8` | Fixed signed INT8 operands |
| `target` | `kv260` or `asic` | FPGA prototype or generic ASIC exploration |
| `frequency_mhz` | integer 1–200 | Requested target, not achieved frequency |
| `max_dsps` | integer 0–1248 | Retained budget; not certified without matching Vivado reports |
| `max_lanes` | 1, 2, or 4 | Architecture limit; not mapped DSP count |
| `objective` | `minimize_latency` or `minimize_lanes` | Ranks supported candidates only |

### 3.3 Exact checked-in schedule

The kernel executes:

`N rows × (N / LANES) column groups × N inner-product positions`

Expected compute clocks:

| N | LANES | Compute clocks |
|---:|---:|---:|
| 8 | 1 | 512 |
| 8 | 4 | 128 |
| 16 | 1 | 4096 |
| 16 | 4 | 1024 |

These counts exclude operand loading, the launch edge, host communication, polling, result readback, and FPGA programming.

One lane versus four lanes is a **capacity trade**. Four lanes use four times the arithmetic parallelism. It is not a fixed-resource optimization. A lane is not a mapped DSP.

### 3.4 Scope exclusions

The following are outside this demo:

- FP16 or precision conversion
- N other than 8 or 16
- lane counts other than 1 or 4
- complete neural inference or federated learning
- fleet orchestration or over-the-air deployment
- Raspberry Pi or CPU benchmark claims
- power optimization or isolated accelerator power measurement
- camera integration
- arbitrary user RTL deployment
- live Vivado builds during judging
- ASIC power, timing, physical area, signoff, or tapeout claims from generic synthesis

---

## 4. Product workflow

### 4.1 Define the requirement

The user can:

- enter a plain-language request and ask AI to draft a specification; or
- set the supported configuration directly.

Direct controls are always available and are the source of truth. AI output is an editable draft and must be explicitly applied.

Example supported prompt:

> Build an 8×8 signed INT8 matrix-multiplication accelerator for KV260. Prioritize kernel latency and permit up to four arithmetic lanes at a requested 100 MHz.

Example unsupported prompt:

> Build a real-time camera object detector using FP16 and optimize power.

The unsupported request must remain unsupported. The product must not silently convert it to INT8 GEMM.

### 4.2 Validate the specification

`siliconos.engine.validate` is authoritative. It rejects unknown fields, unsupported workloads, unsupported sizes, unsupported lane choices, and unsupported objectives.

AI provenance is shown per field as one of:

- `user`
- `inferred`
- `default`
- `unresolved`

### 4.3 Select a qualified recipe

The required demo path is:

> **Prompt or controls → reviewed specification → deterministic catalog recipe → parameterized RTL**

`POST /api/plan` selects an allowlisted catalog block and returns:

- block ID;
- accepted specification;
- N and LANES parameters;
- exact source snapshots;
- SHA-256 source hashes;
- recipe hash;
- limitations.

The source is `hardware/matmul.sv`. Size and lane changes select compile-time parameters and require matching builds.

AI-generated RTL through `/api/generate-rtl` is an optional advanced path, not required for the primary demo. Generated source may be shown only after it passes `rtlgen.gate`, real simulation with the unchanged `hardware/tb.sv`, the Python integer oracle, and the trusted cycle monitor. ASIC generation additionally requires Yosys and netlist oracle verification before one atomic run commit.

### 4.4 Explore the two supported architectures

`POST /api/explore` deterministically enumerates one and four lanes.

For each candidate, the website shows:

- analytical schedule cycles;
- projected kernel microseconds at the requested clock;
- analytical throughput;
- lane-limit status;
- provisional selection;
- unknown FPGA DSP/LUT/BRAM values;
- unverified timing and DSP-budget status.

Changing `max_lanes` to one excludes the four-lane candidate. Changing the objective to `minimize_lanes` selects one lane. Neither interaction proves FPGA resource use or power.

### 4.5 Verify the RTL

`POST /api/simulate` runs real SystemVerilog with Icarus Verilog. It uses deterministic signed inputs and compares every output against the independent Python reference.

A simulation result is accepted only when:

- compilation succeeds;
- simulation succeeds;
- every output equals the oracle output;
- one valid cycle count is returned;
- source, input, and output hashes are recorded.

The result remains `rtl_simulation` evidence. It is not physical FPGA evidence.

### 4.6 Prepare the FPGA handoff

`GET /api/runs/<run-id>/handoff.zip` exports:

- exact accepted `matmul.sv`;
- exact `tb.sv`;
- trusted cycle monitor for generated source;
- exact inputs and expected outputs;
- expected parameters and cycles;
- source and file hashes;
- replay instructions;
- separately labeled current integration aids: `matmul_axi.sv`, `synth.tcl`, and `BRINGUP.md`.

The handoff manifest must continue to state:

- `physical_fpga: false`
- `integration_status: unverified for this run`

until a separate physical child result is accepted.

### 4.7 Execute on the KV260

The target physical loop is:

1. Select a previously verified software run and its known N/LANES configuration.
2. Select a prebuilt, allowlisted FPGA artifact matching that configuration.
3. Verify artifact metadata and source hashes.
4. Program or load the artifact using the confirmed board software flow.
5. Read identity, compiled N, and compiled LANES.
6. Reject any mismatch.
7. Load the exact archived input vectors while the accelerator is idle.
8. Start one job.
9. Poll with a finite timeout.
10. Read every signed INT32 result and the hardware cycle counter.
11. Compare every result against the server-side Python oracle.
12. Return a separate immutable `board_measured` child report to the website.

Vivado is not rebuilt live during the audience-facing demo.

### 4.8 Export the final receipt

The final report should preserve separate evidence objects rather than relabeling simulation as hardware:

- parent verified RTL run;
- implementation artifact manifest;
- physical board child run;
- optional generic ASIC synthesis report.

---

## 5. Website and demo experience

### 5.1 Hero copy

**Reconfigure. Verify. Deploy. Keep the receipt.**

Supporting copy:

> Edge teams need multiple hardware variants, but every change creates a new correctness and provenance burden. SiliconOS turns a supported requirement into a checked accelerator experiment.

### 5.2 Primary interaction

Direct configuration controls are the reliable primary interaction. AI specification drafting remains visible as an optional assist and a creative-AI proof point.

The main user sequence is:

1. Load the supported example or draft a specification with AI.
2. Review and edit N, lane limit, requested clock, DSP budget, and objective.
3. Explore one-lane and four-lane candidates.
4. Run both with matching inputs.
5. Inspect the oracle match and provenance.
6. Download the handoff.
7. Run the matching physical artifact if board integration is available.
8. Inspect the separate board result.
9. Export the complete receipt.

### 5.3 Pipeline stages

The interface displays:

1. Requirement
2. Reviewed specification
3. Catalog recipe
4. RTL verification
5. FPGA implementation
6. Board execution
7. Evidence export

ASIC generic synthesis appears as a small branch after RTL verification.

Each stage must be one of:

- ready;
- running;
- passed;
- failed;
- unavailable;
- recorded real run;
- not yet verified.

A timer or animation never marks a stage passed. Real backend data controls pass/fail state.

### 5.4 Evidence vocabulary

| UI label | Permitted claim |
|---|---|
| Analytical | Deterministic schedule projection only |
| RTL simulated | Real RTL execution passed the recorded vectors and oracle |
| AI-generated RTL | Generated source passed gate, simulation, oracle, and cycle monitor |
| Generic synthesis | Yosys produced generic cells and the netlist passed oracle simulation |
| FPGA synthesized | Real Vivado synthesis report exists for the identified source |
| Implemented / timing met | Real matching place-and-route reports pass the requested clock constraint |
| Board measured | The identified physical artifact executed correctly on the KV260 |
| Projected | Derived from a stated assumption rather than hardware measurement |
| Estimated | External model with source and assumptions shown |

### 5.5 Comparison panel

The required comparison is N=8, one lane versus four lanes, using identical inputs.

Display:

- simulated cycles for both candidates;
- oracle match status;
- source and input identity;
- projected kernel time at the requested clock;
- physical cycles only when returned by the board;
- mapped DSP/LUT/BRAM only when matching Vivado reports exist.

Required text:

> **Four lanes finish this schedule in one quarter of the cycles by using four times the arithmetic capacity. Loading and host communication are excluded.**

Do not label the result “optimized.” Do not display power. Do not display a Raspberry Pi speedup.

### 5.6 Stale evidence

Changing the active specification makes previous matching results visibly stale. Changing the workload prompt also makes AI-generated results stale. Stale reports may remain downloadable but cannot appear to prove the current configuration.

### 5.7 Board state

`GET /api/status` currently reports `board: false`. It may report a board available only when a real local runner has a recent successful health check and knows at least one allowlisted artifact.

A historical imported board result is labeled **recorded board measurement**, not “board connected.”

---

## 6. Existing application API

The following routes already exist and must be reused:

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/status` | AI, simulator, board, and ASIC-synthesis availability |
| GET | `/api/catalog` | Qualified recipe catalog |
| GET | `/api/runs` | Recent lightweight run summaries |
| GET | `/api/runs/<id>` | Full run report |
| GET | `/api/runs/<id>/handoff.zip` | Provenance-checked FPGA handoff |
| POST | `/api/spec` | Groq structured specification draft |
| POST | `/api/explore` | Deterministic architecture enumeration |
| POST | `/api/plan` | Deterministic catalog recipe selection |
| POST | `/api/simulate` | Checked-in RTL simulation |
| POST | `/api/generate-rtl` | Gated and verified AI-generated RTL |
| POST | `/api/asic/synthesize` | Generic Yosys synthesis and netlist verification |
| POST | `/api/build` | One-click catalog verification/build path |

The application has an outbound handoff and a signed physical-result import path:
`POST /api/runs/<id>/board-result`. It intentionally has no direct board-runner
connection yet; a runner health/job interface remains pending.

---

## 7. Board integration topology

### 7.1 Preferred direct topology

For the lowest-risk seamless demo, run the following on one trusted presentation/build host when practical:

- browser;
- `server.py` bound to loopback;
- fixed board runner;
- allowlisted FPGA artifact registry.

The runner communicates with the KV260 through the confirmed local board loading and MMIO path. It does not expose arbitrary shell commands, arbitrary RTL, arbitrary MMIO addresses, or user-selected loader commands.

This preserves the loopback-only server and avoids unauthenticated cross-machine callbacks.

### 7.2 Safe fallback topology

If the website remains on a different machine from the Windows/Vivado runner:

1. Download `handoff.zip` from the website.
2. Transfer it to the trusted Windows runner.
3. Run the fixed board procedure.
4. Produce `board-result.json`.
5. Import that result into the website.
6. Validate it against the immutable parent run before persistence.

This fallback is less seamless but safer and smaller than exposing the development server over the LAN. Do not change the server bind address merely to save a file-transfer step.

### 7.3 Future direct cross-machine topology

A remote callback requires authenticated runner registration, a short-lived per-job token, replay protection, and strict artifact allowlisting. Same-origin checks are not runner authentication. This is outside tonight’s required path.

---

## 8. New board-result contract

### 8.1 Required endpoint

Add one endpoint:

`POST /api/runs/<parent-run-id>/board-result`

It accepts a physical result produced by the fixed trusted runner or imported from its output file. It creates a new immutable child run. It never mutates or relabels the parent simulation run.

### 8.2 Authenticated result envelope

The import endpoint accepts `board_measured` evidence only when the file is signed by the configured trusted runner. The runner and server share a local secret through `SILICONOS_RUNNER_KEY`; the result identifies that secret through `SILICONOS_RUNNER_KEY_ID`. The secret never appears in the JSON, browser, Git, logs, or screenshots.

The result includes the complete implementation manifest and lifecycle evidence:

```json
{
  "schema_version": 1,
  "runner_result_id": "uuid",
  "parent_run_id": "uuid",
  "evidence": "board_measured",
  "recorded_at": "RFC3339 timestamp",
  "source_sha256": {
    "matmul.sv": "parent source digest",
    "tb.sv": "parent testbench digest"
  },
  "build": {
    "bitstream_sha256": "64 lowercase hex characters",
    "vivado_version": "2025.2",
    "target_part": "exact installed part",
    "top": "matmul_axi",
    "parameters": {"N": 8, "LANES": 1},
    "configured_clock_hz": 100000000,
    "timing_met": true,
    "implementation_manifest": {
      "schema_version": 1,
      "bitstream_sha256": "same bitstream digest",
      "vivado_version": "2025.2",
      "target_part": "same exact part",
      "top": "matmul_axi",
      "parameters": {"N": 8, "LANES": 1},
      "configured_clock_hz": 100000000,
      "timing_met": true,
      "source_sha256": {
        "matmul.sv": "parent source digest",
        "tb.sv": "parent testbench digest"
      },
      "wrapper_sha256": "matmul_axi.sv digest",
      "reports": {
        "timing": "timing report digest",
        "utilization": "utilization report digest",
        "drc": "DRC report digest"
      }
    },
    "implementation_manifest_sha256": "canonical manifest digest"
  },
  "board": {
    "sku": "SK-KV260-G",
    "board_revision": "reported board revision",
    "image_identity": "OS or runtime image identifier",
    "kernel_version": "reported kernel version",
    "firmware_identity": "reported firmware identity",
    "loader": "fixed loader and version"
  },
  "interface_check": {
    "identity": 1397312513,
    "compiled_n": 8,
    "compiled_lanes": 1
  },
  "run": {
    "input_sha256": "parent input hash",
    "outputs": [],
    "output_sha256": "canonical output-vector digest",
    "cycles": 512,
    "kernel_timing_boundary": "accelerator busy clocks",
    "host_elapsed_ns": null,
    "programming_elapsed_ns": null
  },
  "lifecycle": {
    "repeat_without_reload": {
      "outputs": [],
      "output_sha256": "canonical output-vector digest",
      "cycles": 512
    },
    "reset_recovery": {
      "outputs": [],
      "output_sha256": "canonical output-vector digest",
      "cycles": 512
    }
  },
  "runner_auth": {
    "key_id": "configured runner key ID",
    "hmac_sha256": "HMAC-SHA256 over canonical JSON excluding runner_auth"
  }
}
```

Every `outputs` array must contain exactly N² signed INT32 values and match the independent oracle. Output hashes use compact JSON UTF-8 with no spaces; `[1,-2,3]` hashes to `291bbc895d1412460556618bc33cfcc323cac88cbfae4a2062ccfbd2afb51ec7`. Objects used for manifest hashes and HMAC signatures use UTF-8 JSON with keys sorted and separators `,` and `:`.

Generate a secret locally with an approved cryptographic random source, configure the same value only in the trusted runner and server processes, and choose a non-secret key ID. Sign an unsigned result without printing the secret:

```sh
python3 -m siliconos.board unsigned-board-result.json board-result.json
```

### 8.3 Deterministic server acceptance rules

The server must:

1. authenticate the result HMAC using the configured runner key and key ID;
2. require the route ID, body `parent_run_id`, and stored parent ID to match;
3. require an accepted parent with `correct: true` and supported simulation evidence;
4. require exact N/LANES agreement;
5. require source hashes to match the parent snapshots;
6. recompute the canonical implementation-manifest hash;
7. require the manifest to bind the source, wrapper, reports, bitstream, part, top, parameters, clock, and timing status;
8. require runner input hash to equal the parent input hash;
9. recompute expected outputs from the parent inputs using `engine.reference`;
10. require the initial, repeat-without-reload, and reset-recovery outputs to match exactly;
11. recompute and verify each canonical output hash;
12. require identity `0x53494c01` and matching compiled N/LANES;
13. require positive bounded cycle counts matching the checked-in schedule or the verified generated-source observation;
14. require a valid timestamp, exact target part, Vivado version, bitstream hash, and board/image identity;
15. keep mapped resource values absent unless a later parser validates them from the bound report contents;
16. create a new UUID and server timestamp;
17. set `physical_fpga: true` only after all checks pass;
18. serialize imports and make `runner_result_id` unique so retries are idempotent;
19. save the child run, runner index, and event atomically;
20. preserve failed submissions as errors, not partial successful evidence.

A digest-shaped string or `timing_met` boolean alone is insufficient. Authentication and the canonical manifest bind the trusted runner's claims to named artifacts and reports; the matching files must still be retained for audit.

### 8.4 UI behavior

The website must render board evidence separately from simulation and show:

- recorded versus currently connected state;
- parent run ID;
- artifact/bitstream hash;
- exact part and N/LANES;
- board and image identity;
- configured clock;
- physical cycle count;
- complete oracle match;
- timestamp;
- host timing only if genuinely measured;
- programming timing separately if genuinely measured.

A physical one-versus-four-lane ratio may be displayed only after two compatible board reports exist with identical inputs, matching timing boundaries, and separately identified artifacts.

---

## 9. RTL kernel contract for FPGA owner

### 9.1 `matmul` interface

```systemverilog
module matmul #(parameter N=8, parameter LANES=1)(
 input wire clk, reset, start, load,
 input wire operand_b,
 input wire [15:0] address,
 input wire signed [7:0] data_in,
 output reg busy, done,
 output reg [63:0] cycles,
 output wire signed [31:0] data_out
);
```

- `reset` is synchronous active-high.
- `load && !busy && address < N*N` writes one operand.
- `operand_b=0` selects A; `operand_b=1` selects B.
- `address` is an element index, not a byte address.
- `start && !busy` begins a job, clears done and cycles, and resets control/accumulators.
- Start and load while busy are ignored by the kernel.
- `done` is sticky until reset or the next accepted start.
- `cycles` increments once per busy compute edge, including the final edge.
- `data_out` asynchronously selects C at `address`; out-of-range reads return zero.
- A, B, and C memories are not cleared on reset.
- Reload operands after reset for a reproducible host sequence.
- Read results only after the new job completes.

The flat arrays and asynchronous reads do not establish BRAM inference or suitable physical banking. Do not redesign memory before establishing the first working board run unless synthesis makes the current design unusable.

### 9.2 AXI4-Lite wrapper interface

`hardware/matmul_axi.sv` is the current generic slave wrapper.

- Data width: 32 bits
- Address width: 8 bits
- Reset: synchronous active-low `aresetn`
- One clock domain, `aclk`
- Independent AW and W handshakes
- One buffered write and one outstanding read response
- Responses remain stable under backpressure
- OKAY response: `2'b00`
- SLVERR response: `2'b10`
- No clock-domain crossing logic

The wrapper must connect to an appropriate synchronized peripheral reset and matching AXI clock domain.

### 9.3 Register map

| Offset | Register | Behavior |
|---:|---|---|
| `0x00` | Identity | Read-only `0x53494c01` |
| `0x04` | Control | Write bit 0 with `WSTRB[0]` to pulse start; reads zero |
| `0x08` | Status | Bit 0 busy, bit 1 sticky done; other bits zero |
| `0x0c` | Address | Bits 15:0 element index; bit 16 selects B; byte strobes honored |
| `0x10` | Operand | Low-byte write loads signed INT8; read returns last operand byte zero-extended |
| `0x14` | Result | Signed INT32 selected result; SLVERR before completion or while busy |
| `0x18` | Cycles low | Read-only; SLVERR while busy |
| `0x1c` | Cycles high | Read-only; SLVERR while busy |
| `0x20` | Compiled N | Read-only 8 or 16 |
| `0x24` | Compiled LANES | Read-only 1 or 4 |

Unknown and unaligned addresses return SLVERR. Writes to read-only registers return SLVERR. Effective start, address, and operand writes while protected busy return SLVERR. Zero-strobe writes are no-ops.

The identity/N/LANES registers identify interface and compile-time configuration. They are not a cryptographic bitstream identity; the runner must separately hash and identify the deployed artifact.

### 9.4 Host transaction sequence

1. Read `0x00`; require `0x53494c01`.
2. Read `0x20`; require expected N.
3. Read `0x24`; require expected LANES.
4. Require status busy bit clear.
5. For every A element, write the element index to `0x0c`, then its low signed byte to `0x10`.
6. For every B element, write `0x10000 | index` to `0x0c`, then its low signed byte to `0x10`.
7. Write `1` to `0x04` with low-byte strobe.
8. Poll `0x08` with a finite timeout until `(status & 3) == 2`.
9. For each output index, write the index to `0x0c` and read signed INT32 from `0x14`.
10. Read `0x18` and `0x1c` while idle and combine into the 64-bit cycle count.
11. Compare every output with the independent oracle.
12. Repeat the job once without reloading.
13. Exercise reset, reload, and successful recovery.

Serialize host access so another job cannot start between cycle-half reads.

---

## 10. Vivado implementation contract

### 10.1 Tool and part discovery

On the Windows host, record:

```tcl
version -short
get_board_parts *kv260*
get_parts *xck26*
```

Select the exact installed part verified against the physical board and board preset. Do not substitute a similar part.

Record:

- Vivado/Vitis versions;
- exact part;
- board part and revision;
- source commit and hashes;
- build timestamp;
- top and parameters.

### 10.2 Out-of-context checkpoint

Run both wrapper candidates into separate directories:

```bat
vivado -mode batch -source hardware/synth.tcl -tclargs EXACT_INSTALLED_PART 8 1 10 build/axi1 matmul_axi
vivado -mode batch -source hardware/synth.tcl -tclargs EXACT_INSTALLED_PART 8 4 10 build/axi4 matmul_axi
```

Preserve:

- `utilization_synth.rpt`
- `timing_synth.rpt`
- `drc_synth.rpt`
- `matmul_synth.dcp`
- `build_metadata.txt`
- full Vivado console log
- SHA-256 hashes of `matmul.sv` and `matmul_axi.sv`

This is out-of-context synthesis only. It is not a board bitstream or timing closure.

### 10.3 Board block design

Start with N=8, LANES=1.

1. Create or reuse a project matched to the confirmed KV260 board and software image.
2. Configure the Zynq UltraScale+ processing system.
3. Add `matmul_axi` as a module reference or packaged custom IP.
4. Connect a supported PS-to-PL AXI master through the required interconnect/conversion.
5. Connect wrapper and interconnect to the intended AXI clock domain.
6. Drive `aresetn` from an appropriately synchronized peripheral reset.
7. Allocate a non-overlapping address segment in Address Editor.
8. Record the actual base address. Never guess it.
9. Validate the block design and resolve relevant address, clock, reset, and interface warnings.
10. Generate output products and the HDL wrapper.
11. Synthesize the complete design.
12. Implement/place and route.
13. Review final timing, utilization, unconstrained paths, and DRC.
14. Reject timing failure before physical comparison.
15. Generate the bitstream and matching platform/loader metadata.
16. Hash all deployment artifacts.

The requested 10 ns period is a target. It becomes achieved timing evidence only after the matching implemented design passes the appropriate timing checks.

### 10.4 Board software and loader discovery

Before loading:

- identify the board Linux/runtime image;
- record kernel version;
- record boot firmware identity;
- determine whether the compatible flow is PYNQ, `xmutil`, XRT, FPGA manager, or another verified local path;
- preserve known-working media and firmware;
- confirm required bitstream, metadata, and device-tree artifacts.

Do not mix unrelated loader recipes. Do not overwrite boot media as an assumed first step.

### 10.5 Physical acceptance sequence

First prove the interface:

1. Load the identified one-lane artifact.
2. Read identity/N/LANES.
3. Write `0x0c = 5`, read it back, then clear it.
4. Reject any mismatch.

Then prove arithmetic:

1. Load A as the 8×8 identity matrix.
2. Load B element `i` as `i - 32` for `i=0..63`.
3. Start the kernel.
4. Poll until done with a finite timeout.
5. Read all 64 outputs as signed INT32.
6. Require output `i = i - 32` exactly.
7. Require 512 cycles for LANES=1.
8. Repeat without reloading and require the same result.
9. Reset, reload, and prove recovery.
10. Run the exact seeded vectors exported by SiliconOS and compare every output with the Python oracle.

Only after the one-lane image passes should the partner build/load LANES=4 and repeat identical tests. Require 128 cycles for N=8, LANES=4.

### 10.6 Physical evidence package

For each implemented artifact preserve:

- source commit and hashes;
- exact part and board revision;
- block-design/project export;
- actual address map;
- Vivado version;
- clock/reset configuration;
- whole-design and kernel utilization reports;
- final timing and DRC reports;
- bitstream and metadata hashes;
- board image, kernel, and firmware identity;
- loader identity/version;
- inputs, all outputs, and cycle count;
- run timestamp;
- host elapsed time if measured;
- programming elapsed time if measured;
- limitations.

Kernel cycles, host/MMIO time, and programming time remain separate.

---

## 11. Runner safety contract

The runner is trusted local software, not a general remote execution agent.

It may accept only:

- a validated parent run ID or handoff archive;
- an allowlisted artifact ID;
- supported N/LANES values;
- exact archived input vectors.

It must not accept:

- arbitrary shell commands;
- arbitrary RTL text from a public request;
- arbitrary file paths;
- arbitrary loader commands;
- arbitrary MMIO addresses;
- arbitrary bitstream URLs.

The runner must:

- use one active board job at a time;
- enforce finite programming and execution timeouts;
- verify hashes before loading;
- verify identity/N/LANES after loading;
- reject stale or mismatched artifacts;
- capture all outputs before creating a result;
- preserve diagnostics on failure;
- never submit `board_measured` evidence when any required check fails.

---

## 12. ASIC supporting branch

The ASIC branch is not the main demo.

`POST /api/asic/synthesize` runs Yosys generic synthesis and then simulates the generated netlist against the Python integer oracle.

Approved claim:

> **The same verified RTL also produces an inspectable generic netlist, giving the team a starting point for custom-ASIC exploration.**

Required qualifier:

> **Generic cells only. No PDK mapping, physical area, power, achieved timing, layout, signoff, or tapeout is established by this app result.**

The repository also contains separate SKY130 research evidence for an exact N=8/LANES=1 source/configuration. It is not the output of the application’s generic-synthesis button and must remain separately labeled. Its recorded timing/electrical violations prevent any signoff claim.

---

## 13. Evidence and claim contract

| Evidence state | Permitted statement | Forbidden inference |
|---|---|---|
| `analytical` | This schedule is projected to take N³/L cycles | Hardware latency or feasibility |
| `rtl_simulation` | Checked-in RTL passed these vectors and recorded these simulated cycles | FPGA execution or universal correctness |
| `ai_generated_rtl` | Generated RTL passed gate, real simulation, oracle, and cycle monitor | Physical resource use or autonomous correctness beyond tested vectors |
| `generic_synthesis` | Yosys produced generic cells and the netlist passed seeded oracle simulation | ASIC area, power, timing, or tapeout readiness |
| Out-of-context FPGA synthesis | This source mapped to these synthesis estimates for this part | Board bitstream, placement/routing, or timing closure |
| Implemented | This artifact mapped to these resources and met this constraint | Board execution |
| `board_measured` | This identified artifact produced these outputs/cycles on this board | Full application latency unless loading/communication are included |

Missing values remain `null` or unknown, never zero.

Projected microseconds equal simulated or analytical cycles divided by a requested clock. They are not measured hardware latency.

---

## 14. Work ownership and handoff

### Product/web owner

Owns:

- problem framing and direct configuration flow;
- optional AI specification drafting;
- deterministic catalog selection;
- simulation/oracle pipeline;
- evidence labels and stale-state behavior;
- handoff export;
- board-result validation endpoint/import;
- separate board-result rendering;
- generic ASIC aside;
- end-to-end QA and four-minute rehearsal.

Must provide the FPGA owner:

- exact parent run ID;
- handoff ZIP;
- accepted N/LANES;
- source hashes;
- exact input vectors and expected outputs;
- expected schedule cycles;
- proposed board-result schema;
- no secrets.

### FPGA/Vivado owner

Owns:

- exact part and board discovery;
- tool reports;
- board block design;
- clock/reset/address integration;
- implementation and timing review;
- bitstream and metadata generation;
- board image/loader discovery;
- MMIO runner;
- physical correctness and lifecycle tests;
- artifact/run evidence package;
- genuine backup recording after success.

Must return:

- actual base address;
- exact part, board, tool, clock, and loader identity;
- source and artifact hashes;
- implementation/timing/utilization reports;
- complete physical run outputs and cycles;
- failure diagnostics if any gate fails;
- no passwords or API keys.

### Shared decisions

Both owners must agree before changing:

- RTL ports or register offsets;
- N/LANES schedule;
- reset/start/done semantics;
- API fields or evidence labels;
- presentation claim boundaries;
- deployment topology.

Any schedule change requires updated simulation expectations and cycle assertions before physical comparison.

---

## 15. Ten-hour execution order

### Gate 1: preserve the working software spine

Before new UI or board integration:

- run the existing test suite;
- run N=8 one and four lanes;
- confirm 512/128 simulated cycles;
- confirm matching inputs, outputs, specification, simulator, and source hashes;
- confirm export and replay;
- test one supported and one unsupported AI request if Groq is used.

### Parallel track A: product/web

1. Make direct controls the reliable primary path.
2. Keep AI as optional spec drafting.
3. Add truthful pipeline states tied to API responses.
4. Make the one-versus-four-lane capacity trade visually clear.
5. Surface the handoff ZIP.
6. Add physical result import/validation and separate rendering.
7. Keep board status false until a runner is genuinely healthy.
8. Show ASIC generic synthesis only after the core path is stable.

### Parallel track B: FPGA

1. Tool and part discovery.
2. OOC wrapper synthesis for one and four lanes.
3. N=8/LANES=1 block design and implementation.
4. Register identity/read-write smoke test.
5. One-lane arithmetic and repeated-run/reset acceptance.
6. Exact exported-vector run.
7. Produce board result and recording.
8. Only then attempt N=8/LANES=4.

### Cut order when time is short

Cut in this order:

1. extra animation;
2. ASIC UI polish;
3. AI-generated RTL path in the presentation;
4. second physical lane artifact;
5. live board operation in favor of a genuine recorded run;
6. recorded run in favor of honest implementation or simulation evidence.

Never cut:

- deterministic validation;
- independent output checking;
- evidence labels;
- artifact identity;
- failure visibility;
- one truthful four-minute rehearsal.

---

## 16. Four-minute presentation

### 0:00–0:30 — Problem

> “An edge team rarely ships one perfect hardware configuration. Different device profiles need different throughput and capacity. Changing a parameter is easy; proving the new variant is correct and tracking exactly what was deployed is the expensive part.”

Show:

- before: requirement → manual edits → separate tools → scattered files;
- SiliconOS: requirement → reviewed recipe → verification → identified FPGA artifact → receipt.

Do not call the problem customer-validated without an observed real user.

### 0:30–1:05 — Requirement to reviewed design

Use a supported prompt or direct controls. Show AI provenance briefly if live AI is working. Emphasize that deterministic validation controls what can run.

### 1:05–1:40 — Configuration decision

Show N=8 one and four lanes. Set lane limit to one and show four lanes excluded, then restore it.

> “This is a capacity decision, not a free optimization. SiliconOS keeps the trade visible.”

### 1:40–2:30 — Trust step

Run both RTL variants on identical inputs. Show 512 and 128 simulated cycles, output matches, and hashes.

> “The model did not grade its own answer. Deterministic code and an independent oracle did.”

### 2:30–3:15 — Physical proof

If physical integration passed, show live or genuinely recorded execution. Display artifact identity, board identity, physical cycles, and complete oracle match.

If one configuration passed, show only that one as board measured. Keep the other labeled simulated.

If no board run passed, show the exact pending gate. Never animate a fake board completion.

### 3:15–3:30 — ASIC aside

> “The same verified RTL also produces a checked generic netlist. Physical ASIC implementation remains future work.”

### 3:30–4:00 — Receipt and next customer test

Download the evidence bundle.

> “The engineer leaves with the source, tests, inputs, outputs, hashes, reports, and replay instructions. Our next validation is to watch an FPGA engineer use this on a non-confidential configuration decision without coaching.”

End on the strongest completed evidence state.

---

## 17. Demo acceptance criteria

### 17.1 Software acceptance

- Supported configuration reaches a passing RTL result through the website.
- N=8/LANES=1 returns 512 simulated cycles.
- N=8/LANES=4 returns 128 simulated cycles.
- Paired comparison requires identical inputs, outputs, specification, simulator, and source hashes.
- Lane limit one excludes four lanes.
- Unsupported FP16, N=32, camera, and power-optimization requests remain unsupported.
- Projected microseconds always show requested clock and “not measured.”
- Missing DSP/LUT/BRAM values remain unknown.
- Export preserves exact source and replay materials.
- Failed generation or simulation never replaces prior accepted evidence.

### 17.2 FPGA acceptance

A configuration is board verified only when:

- exact Vivado version and target part are recorded;
- implementation and timing reports belong to the deployed artifact;
- bitstream/deployment artifact hash is recorded;
- actual address map is recorded;
- identity register equals `0x53494c01`;
- compiled N/LANES match the expected artifact;
- all outputs match the independent oracle;
- repeated execution and reset recovery pass;
- cycle count matches the checked-in schedule;
- actual configured clock is verified before converting cycles to measured kernel time;
- result is persisted as separate `board_measured` evidence.

### 17.3 Presentation acceptance

- Demo is under four minutes.
- Every number has an evidence label.
- “Optimization,” “measured,” “power,” “area,” “timing closed,” and “deployed” are used only with supporting evidence.
- Team can explain which steps use AI and which use deterministic code.
- Team can explain that four lanes spend more arithmetic capacity.
- Team states customer demand is unvalidated unless a real observed session occurred.

---

## 18. Verification commands

On the macOS application host:

```sh
python3 -m unittest discover -s tests -v
node --test tests/test_web.js
git diff --check
```

Start the local application:

```sh
python3 server.py
```

Browser-check the complete path at approximately 390 px and 1440 px widths. Verify that no stale report appears to support the active specification.

On Windows/Vivado, preserve the exact commands and logs used. Do not report a stage complete solely because a command exited successfully; inspect the expected artifact, reports, identity, outputs, and hashes.

---

## 19. Open facts to fill during FPGA bring-up

| Field | Current status |
|---|---|
| Exact installed device part | Pending tool discovery |
| Board revision | Pending physical inspection |
| Vivado `version -short` | User reports 2025.2; command output pending |
| PS/block design | Pending |
| PL clock configuration | Pending |
| Actual MMIO base address | Pending Address Editor export |
| Board OS/runtime image | Pending inventory |
| Kernel version | Pending inventory |
| Boot firmware identity | Pending inventory |
| Loader/package format | Pending inventory |
| One-lane implementation reports | Saved partner reports; hash-gated comparison available |
| One-lane bitstream and hash | Saved partner artifact; validate against matching manifest |
| One-lane physical run | Saved partner result; authenticated import requires matching parent run |
| Four-lane implementation reports | Saved partner reports; hash-gated comparison available |
| Four-lane bitstream and hash | Saved partner artifact; validate against matching manifest |
| Four-lane physical run | Saved partner result; authenticated import requires matching parent run |
| Website board-result import | Implemented; requires a signed trusted-runner result |
| Direct runner health/job connection | Pending Windows/KV260 runner implementation |

Unknown fields must remain pending. Do not fill them from assumptions.

---

## 20. Final positioning

The hackathon proof is intentionally narrow:

> **For one signed INT8 matrix kernel and two architecture choices, SiliconOS can preserve a requirement, select qualified RTL, prove tested correctness, prepare an FPGA handoff, and export a reproducible receipt. Physical deployment is added only when the exact board evidence passes.**

The roadmap is broader:

> **Apply the same evidence-first workflow to more kernels, precisions, boards, and eventually technology-specific ASIC implementation.**

The narrow proof earns the right to tell the broader story. The broader story must never be presented as already built.
