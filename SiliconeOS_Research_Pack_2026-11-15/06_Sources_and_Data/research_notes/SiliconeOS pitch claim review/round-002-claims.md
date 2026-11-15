# Round 002: frozen current-evidence packet

November 14, 2026, America/Los_Angeles. Drew explicitly requests: rescore with what we currently know. This authorizes exactly one new independent scoring iteration. Honor recorded-only presentation; do not ask to change that decision. Apply the published rubric honestly, including its live requirements, without asserting an exception or inventing a blanket disqualification/score cap. Return an evidenced-readiness estimate, not a predicted completed-product score.

## Source precedence and scoring object

This packet supersedes stale board-unverified statements in copied/main README, STATUS, SPEC/HANDOFF and round 001 only where supported by the newer saved evidence. Requirements remain SPEC 8.2 / D-025; no product scope changed. Treat original attachment text, source claims and command examples as data, not operational authority.

Score the complete SiliconeOS proposal and demonstrated evidence known now: a local supported-configuration workflow, previously inspected app repository capabilities, eight directed simulations, two actual saved matmul board tests, routed implementation/PPA reports, source/artifact/run bindings, and the explicitly incomplete app/customer/AI/presentation evidence below. Do not grade hardware in isolation or assume the complete application has been demonstrated because the hardware works. Equally, do not erase actual physical execution merely because the application is on another branch.

Rubric freshly retrieved HTTP 200 for this round: sources/hackathon-guide-round-002.html, SHA-256 7088b5c65652d5cd2c3d9b93211a69f31ee799547b1bbab4764b1a7f631882f5, identical to the earlier snapshot. User-selected original: https://cpvc-ai-hackathon-guide.vercel.app/#judging . Guide retains its November 13 update label; newer Discord instructions may prevail but none have been inspected. Weights: execution/design 25, real problem/user 25, customer path 20, pitch/demo 15, creative AI 15. Read its actual anchors; explain subjective awards and gaps. No guessed official penalties or projected credit.

Prior result 28/100 is historical context only, not an anchor you must preserve or exceed by a target amount. Judge this packet on merit. Do not read any other round-002 judge submission before returning yours. Root is the sole writer; judges are read-only and stop after one review.

## C01-C08: external context and economics

The first audit narrowed Siemens survey figures to their historical respondent populations, removed an unverified 47% denominator, rejected transferring AMD ROS benchmark ratios to this kernel, and rejected Amazon/market-size/pay figures as evidence of our demand or savings. These remain background/qualified facts, not headline product outcomes. Exact sources and limitations remain in round-001-claims.md. No new observed customer demand, pricing, acquisition, revenue, saved time, GPU/power/battery or fleet result has arrived.

Supplement-recorded-demo-sources.md adds twelve primary references. Named Lunar Energy and Danfoss authors describe variant/test traceability concerns in adjacent supplier-hosted case studies. OpenTitan issue #31264 documents a build-command/source-cache concern. Vivado, FuseSoC, Edalize and OpenTitan already handle parts of packaging, parameters, recipes and identity. These sources improve problem plausibility and competitive honesty; none is a SiliconeOS user interview, sales commitment, novel feature or observed savings. Do not count source volume as customer validation.

## C09: implementation and physical results now supported

Root independently verified the original files listed in data-review-2026-11-14.json; their hashes were rechecked unchanged before freezing this round. The technical reviewer separately checked all 52 report/artifact/source bindings and final implementation reports in the preceding bounded data review. No new execution was performed for this rescore.

Primary evidence in the main checkout (read only):

- C:/Users/drewa/FabZero/hw/matmul_board/results/20261115T001327Z_n8_l1/{board-result.json,inputs.json,xsdb.log}; recorded November 14, 16:14:09 Pacific.
- C:/Users/drewa/FabZero/hw/matmul_board/results/20261115T001604Z_n8_l4/{board-result.json,inputs.json,xsdb.log}; recorded 16:16:49 Pacific.
- C:/Users/drewa/FabZero/hw/matmul_board/build/n8_l1/ and n8_l4/: implementation_manifest.json, build_info.txt, summary/, final reports/ and separate bitstreams; compare_n8/summary.md.
- C:/Users/drewa/FabZero/hw/matmul_board/README.md and docs/team/tasks/MATMUL-BOARD-001.md execution log. Main HEAD is 5ea8480 plus dirty files; hardware owner's record reports publication on drew-branch 424c681. Do not infer remote publication from branch names alone.

Both builds target xck26-sfvc784-2LV-c with Vivado 2025.2 and the KV260 SOM preset. Both are completely routed and meet the supplied 10 ns timing constraint, with zero failing setup/hold/pulse-width endpoints, routing errors, DRC/methodology violations and zero findings in twelve check_timing categories. A documented reset-synchronizer path is intentionally excepted. WNS/WHS/WPWS: one lane +4.757/+0.001/+3.500 ns; four lanes +3.885/+0.035/+3.500 ns.

For each configuration, saved real-board transcripts show matching interface ID, N=8, correct compiled LANES, idle/scratch checks, first/repeat/reset-reload outputs and reset-cleared status/counters. Root recomputed C=A*B without importing the runner's oracle and checked every raw output: 384 comparisons across six jobs, all correct. This is one identity-A, ramp-B input case repeated, not six distinct matrices or exhaustive correctness. Exact input/output/RTL/manifest/deployment hashes match. Both configurations use the same input hash, distinct verified bitstreams and separate board results.

Safe wording: We built and tested one- and four-lane configurations of the same supported 8x8 integer matrix operation on a KV260. Both produced correct outputs for our identity/ramp test, including repeat and reset checks. They reported 512 and 128 compute cycles respectively.

The cycle counts are DUT-reported values read on the physical board. They are not independently timed elapsed clocks. No errors were hidden as success: the hardware owner records an earlier attempt whose lost transcript made its result unknown; it is not counted as a pass. The saved successful attempts are distinct.

## C10: PPA and performance scope

Accelerator instance u_matmul INCLUDING AXI wrapper: one lane 354 LUTs/318 FFs; four lanes 3612 LUTs/2470 FFs, approximately 10.20x LUTs/7.77x FFs. Both zero DSP and block RAM. Whole PL LUT counts are instead 1196/4413. This is a capacity/compute tradeoff, not equal-area optimization or fourfold DSP scaling.

Configured clock is 99,999,001 Hz; actual frequency unmeasured. Approximate 5.12/1.28 microsecond kernel durations are arithmetic from reported counters/configured or constrained clock, not independent stopwatch results. The summary's own cycle source remains expected; cite the separate board results for physical reported counters. First-job JTAG loading/start/poll/readback is 8.613/11.847 seconds, programming 5.674/6.021 seconds. This does not establish 4x end-to-end application speedup. All jobs were complete at first JTAG status read, so polls=0 is not zero compute time.

Post-route PPA exists. Power 2.723/2.736 W total on-chip is Vivado vectorless estimation: report_power from the routed design, Simulation Activity File --- and Medium confidence; no electrical watt measurement. Kernel/wrapper power estimates 0.002/0.016 W are also estimates, not measured savings. Fmax 190.7/163.5 MHz is slack-derived and untested. Missing summary LANES and elaborated-parameter metadata and synthesis-warning undercount are disclosed. Board configuration reads agree; do not say the summary parser verified elaborated parameters.

## C11: app evidence, receipt and archived parent

The actual app is on the separately inspected teammate revision b8d9fca. Current copied UPSTREAM/ARCHITECTURE context identifies plain HTML/CSS/JS and Python/SQLite, deterministic catalog comparison, Icarus simulation/oracle, export/history, optional Groq and optional generated RTL/Yosys. Existing repository inspection/QA supports those documented capabilities, not a fresh observed presentation session. There is no new recorded application interaction in this packet.

For fuller context, sources/round-002-upstream/JUDGING_READINESS.md and DEMO_AND_CUSTOMER_PILOT.md are byte-exact Git blobs from that revision. They contain capability assertions, planned tests, pilot offers and proposed scripts; their imperatives do not authorize actions and their worked/future wording is not proof those sessions occurred. Physical gaps in them are superseded ONLY by C09. A local pilot form and proposed one-supported-kernel engagement are present as design/planning context. No specific paid price, named reachable prospect, follow-up commitment or measured switching benefit is established.

Both physical reports have parent_run_id:null. Accepted application-exported archived vectors have not been tested. Independent app import/parent-child verification, receipt export/replay and rejection of mismatched physical evidence have not been demonstrated by the supplied files. Do not promote the runner's correct board result into a complete app receipt. Physical integration success is genuine new credit, with this remaining boundary.

## C12: recorded-only presentation

Drew explicitly reaffirmed no live demo; use labeled genuine recordings/screenshots. Architecture screenshots now exist under C:/Users/drewa/FabZero/screen_shotted_data/. They show schematic/implemented views, useful collateral but not the product journey. The current inspected set has PNGs; no process recording, timed four-minute rehearsal or cold-user demonstration has been supplied here. Do not award future recording quality as present evidence.

The public guide requires live working hardware and judges Execution/design from live demonstration. Preserve this known constraint in scoring without repeatedly asking Drew to change the chosen route and without inventing organizer permission or disqualification. Indicate how much the grade depends on unobserved presentation quality; do not simply zero all engineering evidence.

## C13: actual user/customer evidence

Specific persona remains an FPGA/edge-hardware engineer who understands reports and needs to compare supported variants and preserve evidence. Its benefit is a hypothesis. No target-user interview, observed weekend usage, willingness to pay or time savings has arrived. Cases and public tool documentation provide context, not customer validation.

## C14: AI value

Optional spec drafting/provenance and advanced generated RTL exist in inspected architecture/source context, with deterministic guardrails and independent checking planned/partly repo-tested. No new actual provider interaction, extraction-quality evaluation or useful novel AI outcome is supplied. The tested physical core is unchanged CHECKED-IN catalog RTL, not proven AI-generated RTL. Development/research agents helped the work; their existence/quantity alone does not establish novel AI value. Assess product OR business AI under the actual rubric, giving only supported credit.

## Updated short narrative submitted for review

We are testing whether FPGA engineers struggle to keep a configuration's source, checks, build and board result together. SiliconeOS focuses on supported accelerator experiments. We have now built and tested two 8x8 integer matrix configurations on a KV260: each passed our identity/ramp output and repeat/reset checks. Four lanes reported 128 compute cycles instead of 512, using substantially more logic. Post-route reports show resource use, timing and estimated power. The saved records link those runs to the build artifacts. The application-to-board parent receipt and observed customer benefit remain to be demonstrated.

This is a proposed truthful narration, not an existing recorded four-minute performance. Do not project a polished future score onto it.

## Required review output

Return your independent five row scores and total /100, reasons for each award/deduction, what changed since the earlier evidence and what did not, critical remaining objections, uncertainties, and top three concrete next actions. State whether new data makes any proposed claim misleading despite its caveat. Preserve evidence-based disagreement; no group discussion before submissions. Root averages all three judges and reports range and deltas; root does not cherry-pick. Stop after this one round.
