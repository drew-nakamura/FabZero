# Build and board data review: November 14

**Yes. This materially strengthens the technical pitch.** Both N=8 configurations now have saved physical board-result evidence for the identity/ramp workload, in addition to fully routed implementation evidence. This supersedes the older unverified-board snapshot used by the first pitch review. It does not retroactively change that frozen review or establish the complete application receipt.

This review checked existing files; it did not run a new simulation, build, board test or application session. Root independently checked saved arithmetic/transcripts/hashes, and the technical reviewer independently checked build reports and bindings. Research worktree remains on codex/pitch-claims-001 at base 5ea8480; main hardware evidence was read only.

## What was verified

- One lane: saved board run [20261115T001327Z_n8_l1](C:/Users/drewa/FabZero/hw/matmul_board/results/20261115T001327Z_n8_l1/board-result.json), recorded November 14 at 16:14:09 Pacific, reports 512 compute cycles.
- Four lanes: [20261115T001604Z_n8_l4](C:/Users/drewa/FabZero/hw/matmul_board/results/20261115T001604Z_n8_l4/board-result.json), recorded at 16:16:49 Pacific, reports 128 compute cycles.
- For each configuration, the first, repeat-without-reload and reset/reload transcript has all 64 expected outputs. Root independently calculated C=A*B from the input files: **384 raw-output comparisons matched**, across six jobs using the same identity/ramp input case. Status/done, no-timeout, identity/N/LANES, scratch-register and reset-zero checks agree with the JSON.
- Input/output hashes, unchanged RTL hashes, each build manifest and all seven listed deployment/summary artifacts per build match. Current build-source hashes also match. The technical reviewer independently checked 52 report/artifact/source bindings across both builds; all matched.
- Both implementations are fully routed, with zero reported routing errors, timing failures, DRC/methodology violations and zero findings across the twelve check_timing categories. Supplied constraints are met at 10 ns. The intentionally excepted reset-synchronizer path is not a claim that every physical path was timed.

## What the resource comparison means

For accelerator instance u_matmul **including its AXI wrapper**, one lane uses 354 LUTs and 318 FFs; four lanes use 3,612 LUTs and 2,470 FFs. That is approximately 10.20 times the LUTs and 7.77 times the FFs, with one quarter of the reported compute cycles. Both implementations use zero DSP and block-RAM resources.

These figures are not whole-design resources. Whole PL LUT counts are 1,196 and 4,413. The [comparison summary](C:/Users/drewa/FabZero/hw/matmul_board/build/compare_n8/summary.md) labels the accelerator-instance scope; keep that scope in captions. This is a capacity/compute tradeoff, not fixed-resource optimization or a fourfold DSP increase.

## Timing and summary qualifications

- The summary's cycle source is explicitly **expected**. Use the separate board result/transcript for the physical reported-counter claim.
- Both configured clocks are 99,999,001 Hz, approximately 100 MHz. Actual board frequency was not measured. The approximately 5.12 and 1.28 microsecond kernel durations are calculated from counter values and configured/constrained clocks; they were not independently timed.
- First-run host loading/start/polling/readback times are 8.613 and 11.847 seconds; programming times are 5.674 and 6.021 seconds. JTAG overhead dominates. These two observations do not support a fourfold end-to-end speedup or prove the four-lane system is generally slower.
- All jobs show polls=0: completion was already visible at the first JTAG status read. That does not mean zero compute work or zero kernel duration.
- Summary Fmax values 190.7/163.5 MHz are rough slack-derived estimates, not tested operating clocks. Power 2.723/2.736 W is a Vivado estimate with no simulation activity file, not measured board energy/power.
- Summary LANES=n/a and manifest elaborated_parameters=unknown are metadata gaps. Build info and physical configuration-register reads agree on lanes 1/4; do not say the parser itself verified elaborated parameters. Its synthesis warning count is also incomplete, per the hardware owner's record. Leave corrections with the report-tool owner.

## What can now be said

**We built and tested two configurations of the same supported 8x8 integer matrix operation on a KV260. Both produced the correct outputs for our identity/ramp test, including repeat and reset checks. Four lanes reported 128 compute cycles versus 512 for one lane, using more logic resources. The retained files link each result to its build artifact.**

Qualify the last sentence as saved artifact/result traceability, not independent app receipt validation. The existing runner verifies hashes before programming; this review checked those saved bindings rather than witnessing a new run.

Two of the [supplement's conditional claims](../../reports/SiliconeOS%20recorded%20demo%20evidence%20research.md) now have bounded support: P03 for this physical test case and P04 for reported physical counters plus routed resource comparison. P02 has substantial source/build/board linkage evidence, but not the accepted application's complete parent-to-receipt chain. P05 and P06 remain unestablished.

## What remains separate

Both parent_run_id values are null. The hardware owner confirms the accepted application's archived vectors have not run. These files therefore do not establish full application export/import, parent/child validation and receipt replay. The identity matrix case is a valuable integration test but narrow arithmetic coverage; it is not a substitute for varied/non-identity archived inputs or a bug-free guarantee.

No customer observation, engineering time saved, willingness to pay or novel AI contribution follows from hardware success. The reviewed screenshots show schematic/placement views useful for explaining the implementation; they do not replace raw run evidence. A recording of the genuine process remains to be supplied for presentation review.

Main README/shared STATUS still contain the older board-unverified snapshot. Their integration owner should reconcile them with MATMUL-BOARD-001's execution log and the actual artifacts. This research review did not edit another owner's shared/hardware files. The owner continues to choose a recorded-only presentation; no new live-demo request or organizer exception is implied.

No full rubric rescore was performed. The earlier 28/100 review predates this hardware evidence. Next: retain these bound results, complete/review the recorded journey and application evidence, then perform one new scored iteration when Drew directs it.

Verification provenance: [file hashes and checks](data-review-2026-11-14.json). Local documentation only; original first-round packet, scores and source attachment remain unchanged.
