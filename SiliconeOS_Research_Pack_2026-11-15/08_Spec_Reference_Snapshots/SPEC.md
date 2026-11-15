# SiliconeOS current product scope

## Accepted demo route (D-025)

November 14, 2026: the selected demonstration uses a local application, JTAG + xsdb on KV260, and [result files](BOARD_RESULT_FILE.md). Both N=8 one-lane and four-lane artifacts require their own board verification. The presentation uses labeled recordings/screenshots of genuine runs. Linux and a website upload endpoint are outside the current route. Application design remains with the application owner; hash serialization and parent-run linkage still need agreement. See [decisions](DECISIONS.md).

- Revision: 8.2, D-025 route and completed simulation evidence reconciled November 14, 2026 (America/Los_Angeles).
- Authority: founder's scope-alignment request, explicit D-025 decisions, and November 14 request to synchronize completed work into drew-branch without disturbing the active hardware writer. This revision reconciles documentation; it adds no workload or verification requirement.
- Detailed requirements: [DEMO_PRODUCT_AND_FPGA_SPEC.md](DEMO_PRODUCT_AND_FPGA_SPEC.md), imported byte-for-byte. Its “scope-frozen” label is the teammate's document status, not proof of implementation or permission to execute commands in this documentation task.
- Reconciliation: this file and [DECISIONS.md](DECISIONS.md) identify current authority, source conflicts and local evidence. [HANDOFF.md](HANDOFF.md) defines the next integration gates. Prior [revision 7](SPEC-revision-007.md) is historical research, not the current contract.

## Customer, problem and outcome

The initial user is an edge-platform, embedded or FPGA engineer who can interpret tool reports and needs to iterate supported accelerator configurations. Representative scenario: a robotics/embedded-vision team has throughput-oriented and capacity-constrained device profiles. The job is preserving which requirement, source, parameters, tests, build and deployed artifact belong together when a configuration changes.

The promise is: **from requirement to verified accelerator variant, with a receipt**. The persona is hypothetical. No interviewed customer, validated willingness to pay, measured engineering time saved or general startup demand is established. Manager/hardware lead/consultancy owner is a buyer hypothesis. Observe a relevant engineer using the workflow before claiming customer validation.

This supersedes the earlier no-RTL-expertise startup/component-generator positioning and sensor/camera workload proposals. Different device profiles are motivation; the demo operates on one KV260 and does not manage heterogeneous hardware or a fleet.

## Required slice

1. Direct controls or optional AI drafting produce an explicitly reviewed supported specification. Preserve user/inferred/default/unresolved provenance and reject unsupported explicit requirements.
2. Deterministic catalog selection provides parameterized checked-in RTL, exact source snapshots and hashes. AI-generated RTL is an optional advanced route with its own gate, unchanged testbench, independent arithmetic oracle and trusted cycle monitor.
3. Compare N=8 with one and four lanes using identical inputs and matching source/spec/simulator provenance. Lane limit one excludes four lanes. Validate every output; preserve failures and stale-result labels.
4. Export the accepted parent run as a provenance-checked handoff ZIP.
5. Build and allowlist matching physical artifacts, run the archived vectors on KV260, and return a separate immutable board-measured child report. Never relabel the simulation parent.
6. Export the receipt: source/recipe/test/input/output identity, implementation reports/artifact identity and separate physical evidence when available.

The full supported software set is signed INT8 row-major A/B, signed INT32 C=A×B, N=8 or 16, LANES=1 or 4; parameters are compile-time. For the checked-in schedule, N³/L compute clocks are 512/128 at N=8 and 4096/1024 at N=16. These are expected schedule counts, asserted by the [completed directed XSIM tests](../verification/matmul-xsim-2026-11-14/README.md); they exclude loading, launch, polling, readback and programming and are not physical measurements. Four lanes spend more arithmetic capacity. A lane is not a mapped DSP.

Requested frequency is 1–200 integer MHz, DSP budget 0–1248, lane limit 1/4, objective minimize_latency/minimize_lanes. These are accepted input ranges, not proof of feasible clocks/resources. `target=asic` enables supporting generic synthesis; the main physical target is KV260. Unknown resources remain null. DSP feasibility needs matching reports.

## Architecture and integration boundary

The inspected app uses plain HTML/CSS/JavaScript, Python standard-library backend, local SQLite history, Icarus simulation, optional Groq and optional Yosys. Earlier Next.js/React/FastAPI proposals are not instructions to rewrite it. Use existing APIs/catalog/handoff; see [architecture](ARCHITECTURE.md) and [upstream provenance](UPSTREAM.md).

D-025 replaces the emailed website upload endpoint with the [local result-file contract](BOARD_RESULT_FILE.md). The fixed JTAG runner writes an immutable folder per run; the application independently validates and imports it as separate physical evidence, preserving the simulation parent. Local result import/display is absent from the inspected application revision. Hash serialization, parent linkage, manifest verification and replay/idempotency rules still need joint agreement; proposed fields are not silently finalized. Remote callbacks and public hosting are outside the current route.

Reuse compatible PS/JTAG pieces from the proven diagnostic baseline in the separately owned matmul integration. The existing two-GPIO diagnostic is not a drop-in implementation of matmul_axi. Matmul needs its own clock/reset/interconnect/address integration, reports, bitstream and complete output tests. D-025 selects JTAG/xsdb with no Linux image for this demo; it does not require a new application framework or native-GUI rewrite.

## Acceptance and evidence

Software: supported path passes real RTL/oracle checks; N=8 returns expected 512/128 simulated cycles; paired runs match required provenance; exports replay; unsupported FP16/N=32/camera/power requests remain unsupported; prior reports become stale after edits; errors never become success.

Physical, per configuration: record exact source/build/part/tool/clock/address/loader identities; pass implementation/timing and review DRC/unconstrained paths; hash deployment artifacts; require identity 0x53494c01 and matching N/LANES; compare every physical output against the independent oracle; pass repeated execution and reset recovery; retain cycles and distinct host/programming timing; accept a separate board-result child. Start N=8/LANES=1, then four lanes. N=16 support in software does not establish N=16 board validation.

Presentation: under four minutes, honest per-stage labels, receipt export and clear AI/deterministic roles. Per D-025, use labeled recordings/screenshots of genuine runs as the planned presentation, not a live board run. Retain run IDs; mark time-compressed footage and disclose the original duration. A one-artifact or simulation-only fallback is a disclosed reduced outcome, not a completed two-artifact physical comparison. Cut order follows the email without weakening correctness or evidence identity.

Analytical, RTL simulation, generated RTL verification, generic synthesis, Vivado synthesis, implementation/timing, bitstream and board execution remain distinct. Generic ASIC cells are not physical area/power/timing/signoff. Separate SKY130 research with unresolved checks does not upgrade the app result.

## Exclusions and current gaps

No full inference, federated learning, fleet/OTA management, camera integration, FP16, arbitrary RTL deployment, live judging builds, CPU/Raspberry Pi speedup, power optimization or ASIC tapeout claims.

Diagnostic board bring-up and eight directed matmul simulations are recorded as passed. Matmul integration/build is active; completed implementation/timing, bitstreams, physical execution and local result import are not established by this documentation update. Do not copy diagnostic addresses, resources or slack into matmul results. The active build is a pinned checked-in-RTL integration pilot; its accepted parent archive is still outstanding. Before claiming an end-to-end receipt, bind the exact archived candidate and inputs to the physical artifact. [Review 010](reviews/round-010.md) records the current reconciliation; review 009 is historical. No source merge, commit, push or hardware execution is performed by this documentation task.

Use the [standing judging reference](research/JUDGING.md) with its recorded-date caveat. Customer/problem evidence and a usable presentation remain required alongside technical proof; no score is inferred.
