# Evidence to retain while recording

Research handoff, November 14, 2026. This maps existing SPEC 8.2 / D-025 and BOARD_RESULT_FILE.md evidence requirements to presentation capture; it adds no hardware run authorization, software feature or finalized hash/schema decision. The hardware/application owners retain execution responsibility. Drew has chosen a recorded presentation.

## Capture the work once; keep the original evidence

1. **Identify the exact run.** Show N, LANES, supported workload and a visible run ID. Keep the source snapshots/hashes, full build recipe, constraints/dependencies and actual tool/part/board identities. Record the parent-run identity if agreed; do not invent one to complete a display.
2. **Retain each implementation separately.** Keep each one-/four-lane bitstream hash and its matching implementation manifest, routed timing, route status, DRC/methodology and utilization reports. Show actual configured clocks. A requested clock, synthesis-only estimate or successful file creation cannot stand for these checks. Do not borrow diagnostic reports.
3. **Make board execution identifiable.** Retain the full JTAG/xsdb transcript connecting the programmed artifact, interface identity and compiled N/LANES to the run. The common interface ID 0x53494c01 alone is not a unique build identity. Do not add a new identity primitive just for this recording.
4. **Save exact inputs and every comparison.** Keep A/B, independent expected outputs and all 64 signed observed N=8 outputs for the archived test cases. A readable summary may show mismatch count, but keep the full arrays and comparison evidence. Retain repeat-without-reload and reset/reload checks required by the existing handoff. Preserve failed attempts as separate records.
5. **Keep timing boundaries separate.** Save the design-reported cycle counter, verified build clock, host loading/start/polling/readback elapsed time and programming time. Without a separate trusted elapsed-cycle check, call the value reported compute clocks. At different clocks, a count ratio is not a time speedup. Do not equate four arithmetic lanes to four mapped DSPs.
6. **Show the application's real evidence handling if available.** Capture actual independent import/validation and export, preserving the simulation parent and board child separately. Retain agreed hash serialization and parent linkage, failures/rejections and replay evidence. If this is unavailable, show the board result as board evidence and disclose the missing application step.
7. **Label the presentation clip.** Show run ID and recorded date/time; label Recorded real run. If cuts or speed changes compress the process, identify that and retain original durations. Keep a full original capture where practical. Build footage from one artifact cannot imply that a different artifact produced the displayed outputs. This is recorded evidence, not a live demo.
8. **Retain AI provenance only for actual AI use.** Keep the user request, provider/model identity where available, proposed configuration or RTL and independent checks. State whether the run used checked-in catalog RTL, optional drafting or genuinely generated RTL. Unsupported/failed suggestions must retain honest status. Do not reconstruct a successful model response after the fact.

## Practical handoff bundle

Use existing owner-defined artifacts, without inventing a second schema: each run's board-result.json, inputs.json and full xsdb.log; matching implementation manifest/reports and hashed deployment artifact; accepted parent archive/source/expected-output evidence when available; app validation/export evidence; original recording plus the short labeled clip. Flag missing or TO AGREE fields rather than filling plausible values. Keep secrets out of clips and exports.

The result contract and accepted scope are [BOARD_RESULT_FILE.md](../../docs/spec/BOARD_RESULT_FILE.md), [SPEC.md](../../docs/spec/SPEC.md) and [HANDOFF.md](../../docs/spec/HANDOFF.md). Their unresolved agreement items remain unresolved; this checklist does not approve them.

## If measuring usefulness later

Choose a real engineer's bounded task, such as identifying which variant/result is safe to hand off. Record their existing method, errors/uncertainties and active effort. Observe the same task with the available SiliconeOS path, including setup and checking. Label participant/task/order and avoid interpreting familiarity or build waiting as product savings. This is a proposed observation, not a result or a requirement for the current recording.

## Claim boundaries after the data arrives

- Physical test outputs establish only the tested inputs/configurations and documented checks.
- A complete evidence linkage can support traceability for that example; reusable files alone do not prove independent reproduction.
- A recorded successful run establishes past execution; it does not establish live-demo compliance or present availability.
- No CPU/GPU, energy, battery, fleet, customer, revenue or time-savings claim follows automatically.

No result has been received or verified in this supplement. Keep these notes alongside the [supplemental research](../../reports/SiliconeOS%20recorded%20demo%20evidence%20research.md), and wait for actual evidence before upgrading claims or scores.
