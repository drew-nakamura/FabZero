# Round 001 frozen claims packet

November 14, 2026, America/Los_Angeles. Freeze version 1. Research by independent read-only pitch_researcher; coordinator condensed its returned evidence. Current project baseline: copied SPEC 8.2 / D-025 / HANDOFF, teammate RTL b8d9fca, main HEAD 5ea8480 plus explicitly copied local records. This is an evidence snapshot, not inspection of the live application or a new hardware run. The eight small saved simulation logs were copied separately; no simulation was rerun.

## Rubric and review object

Use sources/hackathon-guide-2026-11-14.html and the user-confirmed https://cpvc-ai-hackathon-guide.vercel.app/#judging. Primary source fetched HTTP 200; guide says November 13 update and Discord may supersede. Judge current demonstrated readiness using the minimal narrative below and the exact evidence supplied, NOT the original draft's hypothetical completed demo. Original claims remain visible here so judges can attack the audit itself. Evidence unavailable to this round gets no invented credit. No actual user interview/use, pricing validation, timed rehearsal, complete matmul board receipt, or demonstrated novel AI value is established. Do not infer these are impossible or that a later owner has failed.

## Claim ledger

### C01: FPGA production escapes

- Original assertion: 87% of FPGA projects ship non-trivial bugs, implying costly robotic failures.
- Verdict: qualified historical survey context; exclude causal/customer extrapolation.
- Safe wording: Siemens' summary of the 2024 Wilson Research Group study reports non-trivial production bug escapes in 87% of surveyed FPGA projects.
- Primary evidence: https://resources.sw.siemens.com/en-US/white-paper-2024-wilson-research-group-fpga-functional-verification-trend-report/ explicitly gives the figure. Study introduction: https://verificationacademy.com/topics/planning-measurement-and-analysis/wrg-industry-data-and-trends/2024-siemens-eda-and-wilson-research-group-fpga-functional-verification-trend-report/ gives 597 eligible participants across the study, not the exposed FPGA-question subgroup size.
- Scope/limit: historical respondent population; not all global designs, all bugs, robotics-only evidence, or proof our tool prevents escapes.
- Next evidence: actual target engineer's failure/reconstruction example and whether this product addresses it.

### C02: FPGA schedule delays

- Original assertion: more than 67-70% delayed because verification/debugging loops consume weeks.
- Verdict: qualified 2022 context; causal linkage unsupported.
- Safe wording: Siemens' 2022 study reports 70% of surveyed FPGA projects finished behind their original schedule.
- Primary evidence: October 24, 2022, Design Completion Compared to Original Schedule: https://blogs.sw.siemens.com/verificationhorizons/2022/10/24/part-2-the-2022-wilson-research-group-functional-verification-study/ . Newer contextual countercheck, October 28, 2026: https://blogs.sw.siemens.com/verificationhorizons/2026/10/28/are-we-looking-beyond-the-numbers-in-the-2026-functional-verification-study/ describes widespread delays and cautions against a single-cause explanation.
- Limit: no isolation of artifact-tracking time and no validated SiliconeOS savings.
- Next evidence: observe the specific task and active time; do not blend survey years.

### C03: 47% debugging

- Original assertion: engineers lose 47% of total working time debugging.
- Verdict: exact number unverified against original chart in this audit; denominator overgeneralized.
- Safe wording: Siemens identifies debugging as the largest activity for FPGA verification engineers in its 2022 study.
- Primary evidence: November 6, 2022, Figure 4-2 discussion: https://blogs.sw.siemens.com/verificationhorizons/2022/11/06/part-4-the-2022-wilson-research-group-functional-verification-study/ . Attachment's 47% was located only in secondary Sigasi summary; primary 2024 gateway did not expose that chart.
- Limit: verification-engineer activity is not all FPGA-engineer hours, wasted hours, or automatable provenance work. Do not put 47% into the pitch.
- Next evidence: obtain original chart/denominator if necessary; prefer narrower wording.

### C04: Kria benchmark superiority

- Original assertion: our KV260 delivers 8x performance/watt, 3.5x latency, 5x productivity and nine months saved versus GPUs.
- Verdict: borrowed vendor results with mixed comparisons; remove from our performance claim.
- Safe wording: AMD published selected Kria-versus-Jetson ROS benchmarks in 2022; we have not reproduced them for our matmul demo.
- Primary evidence: AMD May 17, 2022 launch footnotes 2-4: https://www.amd.com/en/newsroom/press-releases/2022-5-17-amd-robotics-starter-kit-kick-starts-the-intellige.html . Rectify/Resize used KV260/K26, 2021.2-era tools, AGX Xavier for performance/watt and Nano for latency. Productivity was a separate vector-addition example; nine months compared SOM with chip-down development.
- Limit: no general GPU inferiority, SiliconeOS power, battery, latency, productivity or development-time result.
- Next evidence: own matched workload measurements and relevant alternatives, only if scope later needs them.

### C05: Amazon robotics scale

- Original assertion: over one million active robots demonstrate our fleet market.
- Verdict: milestone supported; active-count and demand inference unsupported.
- Safe wording: Amazon announced deployment of its millionth operations robot in June 2025; that is industry context, not demand for SiliconeOS.
- Primary evidence: June 30, 2025: https://www.aboutamazon.com/news/operations/amazon-million-robots-ai-foundation-model . Milestone robot in Japan; operations network over 300 facilities.
- Limit: not a current audited active count, no evidence of KV260 use or our kernel/workflow requirement.
- Next evidence: reachable engineer and actual variant-evidence task. Omit from the short pitch if it distracts.

### C06: Market forecasts

- Original assertion: warehouse/drone/FPGA forecasts establish our opportunity size.
- Verdict: source estimates are context; product TAM inference rejected.
- Safe wording: Our addressable engineering-tool market has not been sized.
- Primary evidence leads: September 24, 2026, https://www.marketsandmarkets.com/blog/SE/future-of-fpga-market-trends-growth-innovations displays FPGA semiconductor $11.73B in 2025 to $19.34B in 2030 at 10.5%; https://www.grandviewresearch.com/industry-analysis/warehouse-automation-market-report displays warehouse $27.4B in 2026 to $59.5B in 2030 with 18.7% labeled over 2024-2030.
- Limit: publisher forecasts not observed outcomes; neither measures this engineering-tool spend; do not add overlapping categories. Drone/AMR auxiliary figures have not been verified in this focused round.
- Next evidence: bottom-up relevant team counts, actual spend, willingness to pay, adoption assumptions.

### C07: Labor rates

- Original assertion: FPGA pay $130,220-$220,000+ and $110-$180/hour from BLS/consultancy sources.
- Verdict: FPGA attribution and contractor rate insufficiently established; omit from pitch.
- Safe wording: Our customer's relevant labor cost has not been measured.
- Primary countercheck: https://www.bls.gov/ooh/architecture-and-engineering/computer-hardware-engineers.htm currently reports May 2025 median $161,740/year, $77.76/hour for broad computer hardware engineers (per researcher retrieval November 14).
- Limit: broad occupation is not FPGA-specialist pay, contractor invoice rate, loaded labor cost or a SiliconeOS customer quote.
- Next evidence: relevant customer cost assumptions or quotes if a later ROI model needs them.

### C08: $8,800-$14,400 saved

- Original assertion: four profiles times twenty hours times $110-$180/hour represents savings per release.
- Verdict: arithmetic scenario only; no measured savings.
- Safe wording: We will test whether SiliconeOS reduces active engineering time assembling and checking a variant's evidence.
- Evidence: 4 x 20 = 80 hours and 80 x assumed rates yields those dollars. No source verifies the twenty hours, profile count, rates, fraction saved or setup overhead. SPEC marks time savings and demand unvalidated.
- Limit: debugging survey cannot fill the missing baseline; tool waiting time is not active engineer time.
- Next evidence: same-task baseline and product observation, labeled active/waiting time, setup/support costs and participant context.

### C09: One versus four lanes

- Original assertion: 512 to 128 clocks proves faster robot vision/control and four times arithmetic/DSP use.
- Verdict: narrow schedule supported in saved directed simulation; system implication rejected.
- Safe wording: Our checked-in N=8 design uses 512 and 128 compute clocks for one and four lanes in directed simulation. These exclude loading, launch, polling, readback and programming.
- Project evidence: docs/verification/matmul-xsim-2026-11-14/README.md, simulation_results.json, source_manifest.json and eight raw logs, pinned b8d9fca181acf007d96e8c15ecb298b944dab8b4; current SPEC/HANDOFF. Coordinator copied small accepted evidence, not a new run. Researcher read summary only; judges may inspect saved logs.
- Limit: not a physical measurement, total workflow speedup, fourfold mapped DSP increase, battery result or robot integration. Eight directed tests are bounded coverage, not exhaustive verification or full app Icarus regression.
- Next evidence: matching separate physical artifacts and measured outputs/cycles; relevant implementation reports.

### C10: Completed physical receipt and customer

- Original assertion: SiliconeOS automatically checks all outputs on KV260 and returns immutable board_measured receipt today for robotics users.
- Verdict: complete end-to-end result not established in this snapshot.
- Safe wording: SiliconeOS is being built to connect supported configurations to separate simulation, implementation and physical evidence. Diagnostic board bring-up and directed matmul simulations are recorded; the complete matmul board-to-application receipt is still being integrated.
- Project evidence: SPEC revision 8.2, DECISIONS D-021-D-025, HANDOFF, STATUS, review010. Diagnostic 3x+1 board success is platform evidence. Parent archive, hash/linkage agreement, physical tests and app import remain outstanding in the inspected records.
- Limit: persona, willingness to pay, observed usage and savings remain hypotheses. Active owners may produce newer evidence; do not assume completion or failure. Do not inspect/copy active build outputs for this round.
- Next evidence: parent archive, stage-specific implementation/timing and two physical passes with exact outputs/artifacts, independent app import/export/replay, observed engineer use.

### C11: Recorded-only judging

- Original plan: D-025 uses genuine labeled recordings/screenshots instead of a live board run.
- Verdict: accepted local plan conflicts with fresh public presentation requirement; unresolved critical readiness blocker.
- Safe wording: The presentation plan needs reconciliation with the event's live-hardware requirement.
- Primary/project evidence: guide sources/hackathon-guide-2026-11-14.html, hardware FAQ, judging and Sunday sections; DECISIONS D-025. Public guide requires hardware working live and judges execution from a live demo. No newer Discord exception inspected.
- Limit: audit cannot change accepted product/demo scope or fabricate organizer approval. A truthful recording remains valuable supporting evidence, but does not itself establish compliance.
- Next decision: Drew seeks organizer clarification/exception or accepts a scoped live proof; hardware owner then confirms feasibility. No contact, scope change or device action authorized by this research.

## Minimal narrative submitted to judges

An FPGA engineer changing a supported accelerator configuration needs to know which source, tests, build and board result belong together. SiliconeOS is building that traceable workflow around an explicit matrix-multiplication example. Our directed simulations compare one and four arithmetic lanes while keeping compute clocks separate from total workflow time. Physical evidence is a separate gate; the complete board-to-application receipt is still being integrated. Next we will observe a relevant engineer using the workflow and test whether it reduces evidence-assembly work.

Proposed four-minute structure for review only: first 30 seconds name the engineer and evidence-reconstruction job; next 30 seconds show the supported configuration and bounded promise; next 120 seconds show actual available flow/evidence with honest stage labels; last 60 seconds show provenance/receipt state, disclose unfinished gates, AI's demonstrated role if any, and concrete pilot question. No timed rehearsal or recording of this outline exists. Do not claim a working live flow from this proposed outline.

The raw attachment's ASIC first-silicon, drone, AMR and additional compliance statistics are not audited/approved for pitch use in round 001. Generically synthesized ASIC evidence is neither tapeout nor customer validation. The role of AI must be shown with actual evidence; agents doing this audit do not by themselves demonstrate novel product AI value.
