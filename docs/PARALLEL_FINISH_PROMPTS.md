# SiliconOS parallel finish prompts

**Purpose:** Complete the highest-value hackathon work in parallel without overlapping ownership or expanding the committed workload.

## Frozen decisions

- Do not add a PULP block during the hackathon.
- Use the existing catalog recipes:
  - `siliconos.matmul.serial.v1`
  - `siliconos.matmul.parallel4.v1`
- The catalog path is the reliable product backbone.
- Groq drafts an editable specification and explains unsupported requirements.
- Deterministic code validates the specification, selects catalog RTL, verifies outputs, and controls evidence.
- AI-generated RTL is optional and may appear only after its complete verification gates pass.
- The FPGA owner owns `hardware/`, Vivado projects, bitstreams, board access, and physical evidence.
- The application coordinator owns `server.py`, `siliconos/`, integration, and end-to-end QA.
- The UI owner owns `web/` and `tests/test_web.js`.
- The customer/pitch owner owns new customer and presentation documents only.
- No agent may overwrite another owner’s active files.

---

## Response to the agent asking about PULP

Copy this response:

```text
1. Do not select or vendor a PULP block for the hackathon build. The committed workload is the existing signed INT8 matrix-multiplication kernel, N=8/16 and LANES=1/4. Adding PULP now would require a new interface wrapper, license/provenance review, independent oracle integration, regression suite, Vivado synthesis, and physical validation. Treat PULP as post-hackathon catalog expansion only.

2. Make the curated catalog path the primary demo-safe path. The live story is: plain-language requirement or direct controls → reviewed spec → deterministic catalog recipe → real RTL simulation and independent oracle → FPGA handoff → physical board result → receipt. Groq specification drafting is the bounded AI contribution. AI-generated RTL is a secondary flourish only when the gate, unchanged testbench, Python oracle, trusted cycle monitor, and any target-specific synthesis checks all pass.

3. Ownership is already assigned. The coordinator is implementing backend and board-result integration; a separate UI workstream owns web files; the FPGA partner owns hardware/Vivado. Do not edit those files. Help with a read-only review, customer/pitch work, or post-hackathon PULP research instead.
```

---

# Prompt 1: FPGA owner after synthesis

Use this prompt if the partner has already completed some form of Vivado synthesis.

```text
You are the FPGA/Vivado owner for the SiliconOS hackathon demo. Continue from the synthesis work already completed. Do not restart working stages without first inspecting and preserving their artifacts.

Own only:
- `hardware/`
- Vivado project/build outputs
- board-loading/MMIO scripts
- physical evidence files
- hardware-specific tests

Do not modify `server.py`, `siliconos/`, `web/`, API fields, evidence names, or the register map without coordinating with the application owner.

Read first:
- `AGENTS.md`
- `docs/DEMO_PRODUCT_AND_FPGA_SPEC.md`
- `docs/FPGA_PARTNER_EXECUTION_PROMPT.md`
- `hardware/BRINGUP.md`
- `hardware/matmul.sv`
- `hardware/matmul_axi.sv`
- `hardware/synth.tcl`

Primary goal:
Produce one reproducible physical N=8, LANES=1 KV260 run with all 64 signed INT32 outputs matching the independent oracle and a hardware cycle count of 512. Secure and record that result before attempting LANES=4.

First determine exactly what “synthesis completed” means. Report one of:
A. Out-of-context `matmul_axi` synthesis only
B. Full block-design synthesis
C. Implemented/place-and-routed design with timing reports
D. Bitstream generated
E. Bitstream loaded and registers accessed
F. Complete physical arithmetic run

Do not describe A or B as implementation, timing closure, bitstream generation, or board execution.

## Inspect and preserve existing artifacts

Return:
- exact `version -short` output;
- exact FPGA part;
- exact board part/preset;
- top module;
- N and LANES;
- requested clock period;
- source commit and SHA-256 hashes;
- full Vivado log;
- utilization report;
- timing report;
- DRC report;
- checkpoint/project path;
- whether the result is OOC or full-design synthesis.

If the source hashes do not match the current `hardware/matmul.sv` and `hardware/matmul_axi.sv`, stop and report the mismatch.

## Continue from the highest completed gate

If only OOC synthesis exists:
1. Create or reuse a KV260 board-matched project.
2. Configure the Zynq UltraScale+ PS.
3. Integrate `matmul_axi` with N=8, LANES=1.
4. Connect a supported PS-to-PL AXI master and required interconnect.
5. Connect one intended AXI clock domain.
6. Connect a correctly synchronized active-low peripheral reset.
7. Allocate a non-overlapping address segment.
8. Record the actual MMIO base address immediately.
9. Validate the block design and resolve clock/reset/address/interface errors.

Then:
1. Generate output products and HDL wrapper.
2. Synthesize the whole design.
3. Implement/place and route.
4. Review timing, unconstrained paths, utilization, clocking, and DRC.
5. Reject timing failure before claiming the requested frequency.
6. Generate the bitstream and all metadata required by the actual board loader.
7. Hash the bitstream and reports.

## Discover the actual runtime path

Record:
- board revision;
- OS/runtime image;
- kernel version;
- boot firmware identity;
- available loader;
- available MMIO method.

Do not assume PYNQ, `xmutil`, XRT, FPGA manager, UIO, or `/dev/mem` is available. Select only the path compatible with the observed image. Preserve working boot media and firmware.

## Register smoke test

At the actual Vivado-assigned base address, require:
- `base + 0x00 = 0x53494c01`
- `base + 0x20 = 8`
- `base + 0x24 = 1`

Then:
1. Write 5 to `base + 0x0c`.
2. Read it back and require 5.
3. Clear it to zero.
4. Read it back and require zero.

Stop if identity, N, LANES, address, clock, reset, loader, or MMIO access does not match.

## Arithmetic acceptance

Use A as the 8×8 identity and B element `i` as `i - 32` for `i=0..63`.

1. Load all A and B elements using the documented address and operand registers.
2. Start with `base + 0x04 = 1`.
3. Poll with a finite timeout until `(status & 3) == 2`.
4. Read all 64 signed INT32 outputs.
5. Require output `i = i - 32` exactly.
6. Read the 64-bit cycle counter while idle.
7. Require exactly 512 cycles.
8. Repeat without reloading and require identical outputs/cycles.
9. Reset, reload, rerun, and require recovery.
10. Run the exact vectors from a SiliconOS `handoff.zip` and compare every output against `expected.json`.

Kernel cycles exclude loading, polling, readback, and programming. Record host and programming time separately only if actually measured.

## Physical evidence return

Preserve:
- source hashes;
- wrapper hash;
- exact part and board revision;
- block-design/project export;
- actual address map;
- configured clock;
- implementation timing/utilization/DRC reports and hashes;
- bitstream/deployment package and hash;
- board image/kernel/firmware identity;
- loader identity;
- all inputs and outputs;
- physical cycle count;
- repeat and reset/recovery results;
- timestamp;
- exact commands/logs.

The application owner will provide the final authenticated `board-result.json` schema and signing command. Do not invent a different evidence format. Never put the signing secret in Git, chat, logs, or screenshots.

After the one-lane result and recording are secure, attempt a distinct N=8, LANES=4 artifact. Use identical inputs and require 128 cycles. Call it added arithmetic capacity, not a fixed-resource optimization.

Send progress at these gates:
A. Existing synthesis classified and preserved
B. Full implementation completed, with timing pass/fail
C. Bitstream and loader ready
D. Identity/address smoke test passed
E. Arithmetic/repeat/reset/exported-vector tests passed
F. Physical evidence package returned

For any blocker, send the first exact error and surrounding log. Do not silently retry broad upgrades or speculative RTL rewrites.
```

---

# Prompt 2: customer/problem and pitch owner

This work can proceed while software and FPGA integration continue.

```text
You own customer validation and the four-minute SiliconOS pitch. Do not edit application, RTL, Vivado, API, or evidence files. Create new documents under `docs/` only, and coordinate filenames before writing.

Read:
- `AGENTS.md`
- `docs/DEMO_PRODUCT_AND_FPGA_SPEC.md`
- `docs/JUDGING_READINESS.md`
- `docs/DEMO_AND_CUSTOMER_PILOT.md`

Goal:
Turn the current problem hypothesis into the strongest truthful customer and pitch evidence possible today.

The product claim is:
“SiliconOS helps an edge-hardware engineer configure an accelerator, prove it correct, deploy an identified FPGA version, and export a reproducible receipt.”

The problem hypothesis is:
“Changing an accelerator parameter is easy. Proving the resulting variant is correct and tracking exactly what was deployed is expensive and error-prone.”

The edge-device fleet is a motivating scenario, not a built fleet-management or federated-learning capability.

Tasks:
1. Recruit one relevant FPGA, embedded, robotics, accelerator, or hardware engineer through individual outreach. Do not use mass lists.
2. Ask about their most recent accelerator/configuration change before showing SiliconOS.
3. Record their existing tools, elapsed waiting, active work, first failure, correctness process, and artifact-tracking process.
4. Observe them attempting the supported SiliconOS workflow without coaching.
5. Ask what evidence they would require before reusing or deploying the output.
6. Ask whether they will provide a non-confidential follow-up workload and schedule a second session.
7. Record refusals and limitations as carefully as positive feedback.
8. Obtain permission before using a quotation or identifiable attribution.

Do not claim:
- customer demand from a hypothetical persona;
- willingness to pay without a real buyer conversation;
- deployment savings without a measured before/after;
- federated learning, camera processing, FP16, fleet control, or arbitrary RTL support;
- physical FPGA evidence until the hardware owner returns it.

Create:
- `docs/CUSTOMER_EVIDENCE_LEDGER.md`
- `docs/FOUR_MINUTE_DEMO_SCRIPT.md`
- `docs/JUDGE_QA.md`

The four-minute script must reserve:
- 0:00–0:30 for the concrete user/problem;
- 0:30–1:05 for AI-assisted but reviewed specification drafting;
- 1:05–1:40 for the one-vs-four-lane capacity decision;
- 1:40–2:30 for real RTL simulation and independent oracle proof;
- 2:30–3:15 for the strongest physical FPGA evidence actually achieved;
- 3:15–3:30 for the generic ASIC aside;
- 3:30–4:00 for the evidence receipt and next customer test.

Prepare direct answers to:
- Why not Vivado alone?
- Why is AI necessary?
- Is this arbitrary RTL generation?
- Is four lanes an optimization or simply more hardware?
- Are DSP/LUT/BRAM numbers measured?
- Is latency measured or projected?
- Did you build federated learning or fleet management?
- Who has this problem?
- Who would pay?
- Why not use a CPU or Raspberry Pi?
- What exactly ran on the KV260?
- What does the ASIC branch prove?

Every number in the script must point to an artifact or be labeled as a target/hypothesis. If no qualified user is reached, state that demand remains unvalidated and describe the exact next test.
```

---

# Prompt 3: FPGA artifact and claim auditor

Run this only after the FPGA owner returns reports and board evidence. It is read-only.

```text
Act as an independent evidence auditor for the SiliconOS KV260 demo. Do not modify source code, RTL, reports, manifests, expected vectors, or results.

Read:
- `AGENTS.md`
- `docs/DEMO_PRODUCT_AND_FPGA_SPEC.md`
- the exact returned Vivado logs/reports;
- implementation manifest;
- address map;
- bitstream/deployment artifact metadata;
- board-result JSON;
- parent SiliconOS run and handoff manifest.

Verify:
1. Source hashes match the parent verified run.
2. Wrapper hash matches the implemented source.
3. N/LANES/top/part/clock agree across source, reports, manifest, bitstream metadata, and board result.
4. Timing reports are from full implementation rather than OOC synthesis.
5. Timing passes the claimed configured clock.
6. DRC and unconstrained-path status are reported accurately.
7. Utilization values are copied from the matching report.
8. Actual base address comes from the matching block design/address map.
9. Identity/N/LANES reads match the deployed artifact.
10. Inputs match the parent handoff hash.
11. Every physical output matches the independent expected output.
12. Checked-in RTL reports 512 cycles for N=8/LANES=1 or 128 for N=8/LANES=4.
13. Repeat-without-reload and reset/recovery evidence exists.
14. Kernel, host, transfer, and programming timing remain separate.
15. The recording shows the same artifact/result identity as the reports.
16. No simulation result is labeled physical and no synthesis result is labeled timing-closed or deployed.

Return:
- PASS, NEEDS_CHANGES, or INCOMPLETE;
- a claim-to-artifact table;
- missing or inconsistent evidence;
- exact claims permitted in the pitch;
- exact claims that must remain excluded.

Do not infer success from absent fields or successful command exit alone.
```

---

# Prompt 4: final demo QA owner

Use after software integration and the strongest available hardware result are ready.

```text
Perform final end-to-end QA for the SiliconOS hackathon demo. Do not add features or refactor unrelated code. Fix only defects that block the agreed demo, and coordinate before changing API/evidence semantics.

Read:
- `AGENTS.md`
- `docs/DEMO_PRODUCT_AND_FPGA_SPEC.md`
- `docs/FOUR_MINUTE_DEMO_SCRIPT.md` if present
- current application code and tests
- strongest accepted hardware evidence, if any

Run:
- `python3 -m unittest discover -s tests -v`
- `node --test tests/test_web.js` when Node is available
- `git diff --check`

Exercise the browser flow at desktop and mobile widths:
1. Load the direct N=8 KV260 configuration.
2. Confirm the supported catalog recipe.
3. Set lane limit to one and verify four lanes is excluded.
4. Restore four lanes.
5. Run both RTL candidates with identical inputs.
6. Confirm 512/128 simulated cycles and complete oracle matches.
7. Confirm projected microseconds are labeled assumed/not measured.
8. Confirm DSP/LUT/BRAM remain unknown without matching reports.
9. Download and inspect `handoff.zip`.
10. Import the authenticated physical board result if available.
11. Confirm it remains a separate immutable child of the simulation result.
12. Change the specification and confirm old evidence becomes stale.
13. Exercise one unsupported request and confirm no silent substitution.
14. Run the ASIC generic-synthesis aside and confirm it does not imply PDK mapping, area, power, timing, layout, or tapeout.
15. Export the final receipt.

Verify presentation language:
- four lanes are added capacity, not a fixed-resource optimization;
- the fleet is a motivating scenario, not implemented fleet management;
- AI drafts intent while deterministic code validates and verifies;
- simulated, synthesized, implemented, and board-measured evidence remain distinct;
- the physical claim matches the exact artifact actually demonstrated.

Run one timed four-minute rehearsal and one fallback rehearsal with the board disconnected. Return a short blocking-defect list and final demo verdict.
```

---

## Recommended assignment now

| Owner | Work now | Must not touch |
|---|---|---|
| Application coordinator | Board-result authentication/validation/API and integration QA | Vivado project and hardware RTL |
| UI owner | Direct-controls-first demo, pipeline, handoff/import, physical evidence rendering | Backend and hardware |
| FPGA partner | Continue from actual synthesis to implementation, board run, and evidence | Web/backend contracts |
| Customer/pitch owner | Real user observation, script, Q&A, evidence ledger | Product and RTL code |
| Auditor | Read-only report and claim verification after artifacts arrive | All source and expected results |

The fastest route to a strong demo is one complete physical N=8/LANES=1 loop plus the existing matched simulated one-versus-four-lane comparison. A second physical artifact, direct live runner, extra IP block, and visual polish are stretch work.
