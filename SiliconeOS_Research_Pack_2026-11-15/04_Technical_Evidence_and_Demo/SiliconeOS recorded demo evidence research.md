> Pack note: Recording/claim guidance. Actual footage and current event-rule compliance remain separate checks. [Start here](../START_HERE.md) · [Latest reviewed state](../CURRENT_REVIEWED_STATE.md).

# Research to support the recorded SiliconeOS demo

November 14, 2026. Drew reaffirmed a recorded-only presentation and is gathering real result data. This supplement adds sources and conditional claim wording; it does not start round 002, replace the frozen first-round claims, or raise the 28/100 readiness estimate.

The strongest proposition to demonstrate is **one supported accelerator variant, its checked result, and a clear record of which inputs and artifact produced it**. Public evidence supports this as a real engineering concern. Whether SiliconeOS makes the task easier, saves time or attracts buyers still needs direct evidence.

## Stronger background than robot-fleet market size

Lunar Energy's named test leader describes fragmented testing making it difficult to correlate results across variants and revisions. This is a close analogy for our proposed problem, although its power-electronics workflow is different and uses existing NI products. [Lunar Energy case](https://www.ni.com/en/solutions/energy/case-studies/scaling-power-conversion-test-startup-speed.html)

Danfoss's named author describes frequently changing test configurations and programmable test sequences with automatically generated reports. This supports repeatability and traceability as established engineering jobs; it is not a SiliconeOS customer result. [Danfoss case](https://www.ni.com/en/solutions/transportation/case-studies/improve-test-coverage-documentation-and-traceability-by-integrating-python-automation-with-hil-testing.html)

A public OpenTitan issue makes the provenance concern concrete: its author warns that a source-file hash can omit command-line build settings. That motivates keeping the recipe and configuration with the artifact. It is a reported engineering concern, not a quantified failure rate or proof our product solves it. [Original issue](https://github.com/lowRISC/opentitan/issues/31264)

## Existing alternatives shape an honest claim

Vivado already archives project inputs and run outputs. FuseSoC and Edalize already describe reusable parameterized hardware workflows. OpenTitan already automates artifact loading and checks loaded-design metadata. These sources weaken any claim that packaging, parameter selection or bitstream identification is new. They support testing whether our bounded interface makes the full evidence trail easier for its intended engineer to inspect and hand off.

AMD already supplies matrix-multiplication libraries, so our small kernel should be presented as a controlled demonstration case. It does not establish a novel accelerator, robot application or full inference system. AMD's own HLS tutorial also shows that interface bottlenecks can limit the benefits of added parallelism; our measured compute, transfer and total-run times must remain separate.

The [twelve-source notes](../06_Sources_and_Data/research_notes/SiliconeOS%20pitch%20claim%20review/supplement-recorded-demo-sources.md) give original links, versions, exact sections, inspection provenance and limits for these statements, including matching Vivado 2025.2 stage/timing guidance. No new implementation stack or platform primitive is being proposed.

## Proposed claims and the evidence that unlocks them

These P-identifiers are preparation notes, not a new scored claim packet.

- **P01 — Background, usable now with attribution:** Named industrial test teams report difficulty maintaining traceable results across product variants. Use the two case studies as adjacent examples. Do not call either team a customer or claim they use this FPGA workflow.
- **P02 — Traceable supported result, conditional:** Our recorded run connects its supported configuration, source/build identity, exact inputs, checks and separate physical result. Use only after those links are visible and independently validated. A ZIP or status flag alone does not unlock this wording.
- **P03 — Physical correctness, conditional:** Both N=8 configurations matched all 64 independent expected outputs for the archived test cases shown. Requires each actual artifact's raw run, exact inputs/oracle, comparisons, repeat and reset evidence. It is bounded test evidence, not a guarantee of bug-free hardware.
- **P04 — Compute comparison, conditional:** For identical inputs, the one- and four-lane builds reported X and Y compute clocks. Fill from actual results. Until then, only saved directed simulation asserts reported counts of 512 and 128. Call the ratio a reported compute-cycle ratio; time speedup also depends on the verified clocks and timing boundary. It is not a fourfold end-to-end speed, DSP, power or battery result.
- **P05 — Receipt validation, conditional and separate from P03:** The application independently validates and imports a board result linked to its parent, then exports the evidence record. Requires actual app behavior, agreed hashing/linkage, replay and mismatch/failure handling. Correct board arithmetic alone does not establish this flow.
- **P06 — Usefulness, still a hypothesis:** We are testing whether an FPGA engineer can inspect and hand off the correct variant with less manual effort than their existing workflow. Requires observing a relevant engineer on the same bounded task and distinguishing active work from tool waiting. Do not replace that observation with industry statistics.

A possible final line, only if P02/P03/P05 are actually demonstrated: **SiliconeOS brings a supported configuration, its checks and matching physical-run evidence into one inspectable record. This recorded example shows which variant produced the result.** Until then, say the workflow is designed to do this and label the demonstrated stages.

## What the recording should preserve

The [capture checklist](recording-evidence-checklist.md) maps the existing accepted requirements to evidence worth retaining while the owner collects data. Keep both the presentation clip and original logs/result files; the clip explains the result while the files make it inspectable. Do not claim an external party independently reproduced the result merely because it can be downloaded.

For AI, retain an actual interaction and the deterministic checks that constrain it, if demonstrated. A catalog-only run is valid evidence for that path; it cannot be narrated as AI-generated RTL. No AI or new failure behavior needs implementing merely to match a proposed script.

## Presentation decision and next step

Drew's latest explicit instruction remains recorded-only; there is no live demo in this research plan. The earlier guide conflict is recorded and unresolved; no organizer exception is inferred. This supplement does not repeatedly request a different route or alter the rubric to remove its live requirements.

When result files/recording arrive, reconcile exactly what they establish against P02-P05, narrow or remove unsupported wording, then run one independent scored iteration only when Drew directs it. Product correctness, observed user value and event presentation compliance remain separate questions. No new score has been produced here.
