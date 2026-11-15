# SiliconeOS decisions and assumptions

Updated: 2026-11-14 (America/Los_Angeles). Current scope reconciliation revision 8.2. D-021–D-025 supersede incompatible earlier customer/workload/architecture assumptions; D-025 settles the route questions recorded in D-024. Historical entries remain for traceability; they do not override current scope.

Current accepted product name remains **SiliconeOS**, per D-020. The unchanged emailed source uses SiliconOS; repository and technical identifiers retain literal names.

## Current reading rule

Use [SPEC.md](SPEC.md), the [emailed revision 1.0](DEMO_PRODUCT_AND_FPGA_SPEC.md), [source ledger](UPSTREAM.md) and [HANDOFF.md](HANDOFF.md). The founder requests aligning our docs with that changed scope. This documentation task performs no implementation, build, board programming, commit or push. Earlier spec-agent rounds remain historical; this is a direct user-requested reconciliation, not an invented founder acceptance of an agent-generated build revision.

## D-025 — Local application, JTAG runner, result file, both lane counts, recorded demo

- Explicit founder decision (Drew, 2026-11-14), answering the D-024 open questions:
  1. **No website.** SiliconeOS is presented as a local application. Board results appear in that application.
  2. **Board route: JTAG + xsdb** from the build laptop (the proven bring-up path). No Linux image for now.
  3. **Results go to a file.** The runner writes one folder per run, specified in [BOARD_RESULT_FILE.md](BOARD_RESULT_FILE.md). This replaces the `POST /api/runs/<id>/board-result` endpoint (emailed spec §8.1); the §8.2 envelope is kept, with JTAG-specific values.
  4. **Both 1-lane and 4-lane** (N=8) builds go to the board, each with its own artifact and result.
  5. **Presentation uses labeled recordings/screenshots** of genuine runs, not a live board run.
- Supersedes D-024 on the selected demo route: the visible demo uses the supported matmul flow in a local application. The audience-facing application design belongs to the application owner.
- Impacts: the emailed spec's website sections (§5), the endpoint (§8.1) and server rules (§8.3) become local-application equivalents; the teammate must be told. MATMUL-BOARD-001 scope now includes the 4-lane build. Hash serialization and parent-run linkage remain to be agreed (BOARD_RESULT_FILE.md "TO AGREE").
- Not changed: RTL, register contract, oracle/evidence rules, the 512/128 cycle expectations, separation of kernel time and host time.
- Reopen if the application needs live board control, or a Linux route becomes necessary.

## D-024 — Physical demo and runtime are still being decided

Historical decision, superseded on demo/runtime selection by D-025 above. Retained to explain the sequence of founder decisions.

- Explicit founder clarification: the team still needs to figure out the physical hardware demonstration. The current matmul script and integration order are candidates, not acceptance of a final demo or deployment route.
- Decide the visible scenario, audience interaction, FPGA computation, input/result transport and website connection before selecting the runtime.
- JTAG/xsdb is verified only as the existing diagnostic baseline. Linux is an open option, neither required nor excluded; establish its prerequisites if the chosen demo needs it.
- This clarification takes precedence over earlier wording that sounded like PS/JTAG reuse was already selected. The emailed original stays unchanged. No replacement workload or feature is selected by this clarification.
- Next action: discuss and agree the physical demo and then record the corresponding integration/runtime choice. No hardware execution authorized by this documentation correction.

## D-021 — Engineer-focused configuration and evidence workflow

- Source: founder's November 14 scope-change request, corrected to the emailed DEMO_PRODUCT_AND_FPGA_SPEC.md revision 1.0.
- Current direction: help an edge-hardware/FPGA engineer iterate supported accelerator variants and preserve a reproducible requirement/source/test/build/deployment receipt. The operator understands hardware reports; no-RTL-expertise startup intake is superseded as primary positioning.
- Kernel boundary from the supplied scope: signed INT8 row-major square GEMM, INT32 outputs, N=8/16 and LANES=1/4. KV260 physical priority is N=8/one lane, then four. Device profiles motivate the problem; multi-board/fleet/OTA/full inference/camera/FP16/power claims remain excluded.
- Catalog-based checked-in parameterized RTL is the primary demo; AI draft optional, generated RTL advanced/optional. One/four lanes show a capacity trade, not measured DSP scaling or fixed-resource optimization.
- Supersedes incompatible D-001/D-004/D-006/D-009 framing and A-005/A-006/A-008 sensor/camera proposals. Other historical requirements apply only where compatible with the current source.
- Demand, buyer, customer urgency and engineering time saved remain hypotheses. Existing customer research is background, not proof.

## D-022 — Reconcile physical baseline without borrowing its evidence

Evidence update, November 14: eight directed XSIM matmul tests passed; see the [portable evidence record](../verification/matmul-xsim-2026-11-14/README.md). The active integration pilot is separate from physical matmul acceptance. The original reconciliation below describes its earlier inspection point.

- BRINGUP-001 and published c192cc330c2a89718db1dba5625a66ff08349b0d record actual diagnostic build/timing/bitstream/JTAG/PL success, repeated after power cycle. The email's blanket hardware-unverified header predates that baseline.
- Recorded platform: Windows/Vivado 2025.2, xck26-sfvc784-2LV-c, xilinx.com:kv260_som:part0:1.4, factory U-Boot, JTAG/xsdb. No Linux image/kernel/SSH is established. Do not demand installing an OS merely because an older plan assumed it.
- Matmul's wrapper/build/address map/timing/bitstream/physical outputs remain unverified in the inspected records. Preserve the diagnostic design; reuse compatible platform pieces in a separately identified integration. No diagnostic resource/slack/address/hash substitution.
- This task reviews existing evidence; it does not claim a new hardware test. New physical work requires accepted package, live ownership and bounded execution authorization.

## D-023 — Current software and missing physical receipt return

D-025 replaces the endpoint/fallback choice below with the local result-file route; independent verification and immutable evidence remain required.

- Existing teammate branch implements plain HTML/CSS/JS + Python standard library/SQLite, Icarus/oracle, optional Groq/Yosys, catalog and verified handoff export. Do not replace it with prior Next.js/React/FastAPI proposals as part of scope alignment. No teammate source is merged by this task.
- Email section 8 specifies a new board-result endpoint and immutable child evidence. It is not present in the inspected branch. Parent simulation stays unchanged; artifact/source/input/config/outputs and implementation provenance must be validated before physical evidence is accepted.
- Preferred loopback app/local fixed runner; file handoff/result import is the cross-machine fallback. Agree schema/hashing/report bindings and JTAG not-applicable OS fields before implementing both ends.
- Generic ASIC synthesis is supporting evidence; separate SKY130 research failures prevent a closure/signoff claim. Optional generated RTL does not become primary merely because it exists.
- Prior fact D-015 remains: Drew's reported 500 credits are Codex usage, not app API funding. Teammate's provider configuration does not establish this machine's access or current live generation quality.

## D-001 — Product intent

Historical entry; clarified by D-004 and D-005. The unresolved endpoint statement below is no longer current.

- Accepted from founder: help startups/companies turn an idea plus constraints into a working RTL / synthesis-ready Vivado deliverable toward an FPGA demo.
- Unresolved alternatives: synthesis endpoint versus physical KV260 execution. Neither interpretation is silently selected.
- Reason: faithful framing of initial request; exact completion promise needs clarification.
- Affects: FR-003, FR-005, FR-007, FR-008, FR-009.
- Reopen when: founder clarifies deliverable or changes concept.

## D-002 — Resources

- Accepted from founder: KV260, two students, 1.5 days.
- Unknown: exact deadline, skill distribution, actual working hours, board/tool readiness.
- Reason: explicit user constraints; no inferred installation or working hardware.
- Affects: entire scope, B-003, R-003.
- Reopen when: founder reports changed resources or measured platform evidence.

## D-003 — Specification-only first round

- Accepted from founder: run first critique, save useful draft, wait for feedback.
- Scope: write only docs/spec planning artifacts; no implementation, hardware builds or programming, commits or publication.
- Revision 1 is not approved. No build handoff created.
- Reopen when: founder explicitly accepts a specific executable revision for building or requests another review.

## A-001 — First customer slice

- Proposed hypothesis, not user accepted: embedded-hardware startup engineer/technical founder with one known digital function and no available RTL capacity.
- Alternative: broad chip-design customers. Rejected as a proposed hackathon scope because output behavior and integration cannot yet be bounded; founder has not accepted that narrowing.
- Evidence: reasoning from two-person, 1.5-day constraint; no customer interviews or willingness-to-pay evidence.
- Affects: FR-001, FR-002, R-001.
- Reopen when: founder supplies actual customer/workload or customer evidence contradicts this hypothesis.

## A-002 — Narrow execution path

Superseded in part by D-005 and A-005: synthesis-only is no longer a proposed successful endpoint. Narrow family/fixed integration remains proposed.

- Proposed: one workload family, fixed interface/platform wrapper, independently verified RTL and reproducible Vivado export. Start with synthesis endpoint while board readiness is unknown.
- Alternative: mandatory board endpoint, conditional on a proven integration path and founder's endpoint choice. Arbitrary idea-to-chip is deferred in this proposal.
- Tradeoff: less breadth and no automatic proof of board execution; more time for correctness and demonstrable evidence.
- Workload, language, interface and frameworks are not selected. Threshold example in SPEC.md is illustrative only.
- Affects: FR-001 through FR-009 and B-001 through B-003.
- Reopen when: founder picks endpoint/workload or platform evidence establishes a feasible physical path.

## A-003 — Reliability boundary

- Proposed: independent frozen behavior/tests, separate stage evidence, initial generation plus at most two repair attempts, and a wall-time limit to be agreed before builds.
- Reason: avoid false success and unbounded debugging during the hackathon. Retry count is a proposal, not a measured optimum.
- Affects: FR-004, FR-005, FR-006.
- Reopen when: workload or measured execution time requires a different bound; cannot weaken accepted behavior merely to pass.

## A-004 — Local platform is unverified

- Observed: read-only command lookup found no vivado command in this shell. This is not proof of absence or licensing failure.
- Official evidence: [UG1089](https://docs.amd.com/r/en-US/ug1089-kv260-starter-kit/Vivado-Board-Flow) documents the board-file route; [DS986](https://docs.amd.com/r/en-US/ds986-kv260-starter-kit/Product-Details) documents customization support. Neither establishes this machine's compatibility.
- Unknown: executable location/version, target support/licenses, simulator, board boot/access, prior working project.
- Affects: B-003 and FR-003, FR-007, FR-008.
- Reopen with: actual tool manifest, logs, and, where required, observed board outputs.

## D-004 — Pre-chip functional prototype customer

- Accepted founder clarification: hardware startups/companies that cannot yet afford a custom chip want to see whether a component idea works, potentially for an investor demo, without commissioning the entire design workflow.
- Sensor-data processing is an example direction. No specific sensor, algorithm, company, interview or buying behavior is established.
- Reason: direct founder feedback; replaces the need to justify FPGA primarily through acceleration. Demand and economic claims remain hypotheses.
- Affects: product outcome, FR-001, FR-002, FR-009, R-001; clarifies D-001 and partially supports A-001's customer hypothesis without selecting the operator persona.
- Reopen when: founder changes target job or actual customer evidence contradicts it.

## D-005 — Physical KV260 execution is mandatory

- Accepted founder decision: the hackathon demo must run on the available KV260. Synthesis is a required stage, not the deliverable endpoint.
- Alternatives considered in round 001: synthesis-only versus board execution. Founder selected board execution; earlier synthesis-only recommendation is superseded.
- Impacts: FR-007/AC-007 and FR-008/AC-008 now require actual board completion. B-002 resolved. Board failure is an incomplete result, even if earlier-stage artifacts are shown honestly.
- No spec revision is approved for implementation by this clarification alone.
- Reopen only with an explicit founder change to the demo goal.

## D-006 — No verified baseline yet

- Accepted report from founder: nothing is working/verified yet; still specifying the hackathon.
- Meaning: do not infer boot, access, tool install, license availability, reference project or data transport from possession of the board. Also do not infer the tools are absent or broken.
- Impacts: B-003 remains a prerequisite to build readiness. A-004 remains unverified.
- Reopen with actual discovery evidence, not repository folder names.

## A-005 — Sensor alarm with labeled replay

Historical recommendation, superseded by A-006's contract-inspired hysteresis proposal. Founder did not accept either workload. Replay remains tentative until confirmed.

- Proposed, not accepted: generate a small stateful event detector for unsigned 16-bit samples; assert alarm after at least three consecutive samples > 1000; clear on <= 1000 or reset. Exact temporal interface remains open.
- Proposed source: host-replayed recorded/synthetic sensor samples routed to actual KV260 programmable logic; generated logic returns alarm results. Replay must be disclosed. Specific transport is not selected or known working.
- Alternative: a physical sensor if an identified compatible device is available and integration can be bounded; another small sensor processing function if more useful to founder/customer.
- Reason/tradeoff: demonstrate idea-to-component behavior while avoiding unbounded acquisition/driver work. Does not prove physical sensing or ASIC properties.
- Impacts: B-001; FR-001, FR-002, FR-004, FR-008, FR-009; new FR-010 requires evidence that generated source is the deployed component. A-002's fixed-interface/narrow-family proposals persist, but its synthesis endpoint is superseded.
- Reopen with founder workload/source choice or platform discovery showing a different path is necessary.

## D-007 — Judging guide governs subsequent specification reviews

- Accepted founder instruction: use [the exact rubric](https://cpvc-ai-hackathon-guide.vercel.app/#judging) in all future iterations.
- Saved paraphrased source reference and delivery constraints: [research/JUDGING.md](research/JUDGING.md). Five categories total 100: execution/design 25, real problem/user 25, customer path 20, pitch/demo 15, creative AI use 15.
- Impacts: FR-013/AC-013; review all categories, prioritize usable live prototype and checkable customer evidence, preserve guide deadlines and project history. No score or challenge choice is inferred.
- Source retrieval: direct public HTTP read succeeded after web reader failed and shell sandbox blocked networking; no login or external writing. Newer organizer/Discord directions may override guide; none inspected.
- Reopen when: founder supplies changed rules, organizer clarification or updated source. Do not silently omit the rubric on later rounds.

## D-008 — Board-aware adaptation and connection planning

- Accepted product direction: research the FPGA board the customer has, potentially recommend a suitable board, and generate using its capabilities with hookup instructions the customer is expected to follow.
- Unresolved scope: arbitrary automatic board support/recommendation versus validated profiles. Board recommendation was tentative in founder feedback; it is not a required hackathon feature yet.
- Technical correction: following a plan cannot compensate for a missing interface, conversion stage or carrier routing. Validate plan first; distinguish research findings, support and actual deployment evidence.
- Impacts: FR-001, FR-003, FR-011, FR-012 and R-005. A-007 proposes one validated target for this event without dropping long-term adaptation.
- Reopen with founder scope decision or actual platform evidence.

## D-009 — Research a real-world contract subset

- Accepted exploration instruction, not selected workload: find a public contract someone paid for and consider reproducing all or a demonstrable subset. Founder explicitly remains uncertain and wants research.
- Tentative founder data-source direction: Ethernet is available and emulated real data may suffice; no physical sensor is identified and no network path is verified.
- Findings: two relevant completed/awarded listings, but no independently established payment. See [round-003 research](research/round-003-findings.md). Do not equate budget, bid, award or completion label with a verified paid amount or a SiliconeOS customer.
- Impacts: FR-014; source evidence and implemented subset must remain visible in pitch/spec.
- Reopen with verified payment evidence, accepted workload or founder change to evidence threshold.

## A-006 — Contract-inspired hysteresis with Ethernet replay

- Proposed replacement for A-005: digitized proximity samples -> stateful Near/Far decision with two thresholds. Reference is completed/awarded Freelancer project 40005124; payment is unverified and displayed $0 award entry does not prove funds paid.
- Proposed example: unsigned 16-bit input, NEAR >=1200, FAR <=1000, retain prior state between; reset FAR. Numbers are our illustrative proposal, not sourced calibration values.
- Proposed subset omits physical sensor, ADC front end and original UART transport. Ethernet delivers emulated digitized readings to board software, which bridges them to actual generated programmable logic.
- Reason: concrete public job with narrow, observable stateful behavior and a clear noise/chatter demonstration. No real-world efficacy, paid savings or exact full-contract replication is claimed.
- Impacts: FR-001/FR-004 behavioral oracle, FR-008/FR-009 data-path evidence, FR-010 build identity and FR-014 attribution. Founder acceptance pending.
- Reopen with workload choice, better evidence or infeasible integration path.

## A-007 — Sourced KV260 profile first

KV260 event-boundary proposal accepted in D-010; detailed profile implementation remains proposed. Other text below records the original rationale.

- Proposed hackathon boundary: validated KV260 build path and evidence-backed profile schema; unknown boards stop or remain advisory. Broad board recommendation/automated adaptation is deferred pending capacity.
- Profile binds carrier/device, physical/electrical interfaces, clock/reset, wrapper, tool/version/license and deployment prerequisites to sources and actual evidence. A web lookup alone cannot certify support.
- Supporting fact: AMD documents existing KV260 Ethernet on processor side, so sample transport needs a processor-to-logic bridge. No GEM instance or working bus implementation is selected.
- Reason/tradeoff: preserves adaptable product structure while protecting the required one-board demo inside a two-student, 1.5-day effort budget.
- Impacts: FR-003, FR-011, FR-012, B-003 and R-005. Not accepted narrowing yet.
- Reopen with founder scope choice or verified second target after complete first demo.

## D-010 — Broad board roadmap, constrained hackathon target

- Accepted founder clarification, November 14: future product is intended for customers' different FPGA boards; this hackathon focuses on the stated available hardware and team/time constraints.
- Resolves A-007 event-boundary question; does not convert broad board support into a currently implemented or universally feasible claim.
- Impacts: product roadmap, MVP boundary, FR-011/AC-011. Do not ask the founder to choose this boundary again without a new change.
- Reopen with explicit change to event target or later supported-board expansion.

## D-011 — Available board and accessory bundle

- Accepted founder report: SK-KV260-G plus HW-BACCP01-SK-G, linked exact DigiKey products. SPEC.md now lists documented board capabilities and bundle contents with sources.
- Includes K26/vision-carrier/fansink assembly; accessory pack documents power/adapters, USB-A/micro-B, Ethernet, HDMI, microSD/SD adapter and 13 MP AR1335 IAS autofocus camera.
- Important distinction: ownership/availability confirmed by founder; physical completeness, carrier/card/module revision, installed images/tools, boot/capture/programming/logic operation remain unverified. One of each is a planning assumption, not physically counted.
- Supersedes “no identified sensor” at inventory level in D-009/round 003; no working sensor path is established.
- Impacts: inventory, FR-003/FR-011/FR-012 and B-003. No external sensor purchase is necessary for the proposed replay core.
- Reopen with actual labels, missing/substituted bundle items or measured setup evidence.

## A-008 — Best event demo: generated sensor switch first, camera gated

- Proposed continuation of A-006: a polished end-to-end noise-resistant sensor switch with independently checked hysteresis logic and labeled Ethernet samples processed on the actual KV260.
- Product story includes plain-language need, cited board profile, confirmed semantics, generation/test/build evidence, live noisy signal and board-state comparison, and export. Exact deployed build identity stays visible; full live Vivado build during four-minute pitch is not promised.
- New camera option: stretch only after core works and rehearseable. A proven capture path may derive a disclosed brightness sample in processor software to drive the same generated logic as a light-level trigger. No claim of capacitive distance sensing or FPGA pixel processing for that extension.
- Alternatives: full camera inspection pipeline has more visual impact but greater setup/platform scope; synthesis-only cannot meet accepted goal. Recommendation prioritizes rubric completion over technical breadth.
- Planning caps proposed: initial approximately 90-minute platform discovery, camera investigation at most 60 minutes after core completion, protect final available hours for tests/history/submission/rehearsal. These are not measured runtimes or accepted schedule commitments.
- Impacts: FR-001/FR-004 keep A-006's proposed example; FR-008/FR-010 require generated logic to remain deployed when adding camera; FR-013 rubric/timing; R-007 captures camera integration risk.
- Reopen with founder workload choice, verified camera/custom-logic baseline or changed remaining capacity. No implementation acceptance or builder handoff yet.

## D-012 — Limited API access and reported subscriptions

- Accepted founder report: approximately 500 Codex credits per teammate; unsure whether they are API credits; hackathon API grant not identified/claimed as far as founder knows.
- Reported tools/accounts: Cursor Pro, Claude Pro, Gemini Pro, Kiro student, current Codex account and separate .edu ChatGPT account. Exact eligible models, rate limits and provider API balances are not verified.
- Evidence distinction: [OpenAI help](https://help.openai.com/en/articles/12642688-using-credits-for-flexible-usage-in-chatgpt-plus-pro) separates ChatGPT/Codex flexible usage credits from API credits. [API credit benefit](https://developers.openai.com/api/docs/guides/chatgpt-api-credits) is separate and eligibility-dependent; event grant is separately unverified. Do not assume 500 units equals $500 or pool two accounts as app funding.
- Impacts: B-004, model adapter, FR-001/FR-003/FR-006; ordinary tests/build/deployment do not require model calls by default.
- Reopen with service/balance type and supported route verified; never ask founder to paste credentials.

## D-013 — Build host and experience report

- Accepted founder report: Windows 11 build machine; approximately 32 GB RAM, estimated. Both know FPGA/Vivado; founder has Basys3/CPU experience, teammate has substantially greater experience.
- Unknown: exact Vivado installation/version/path, free storage, license/device support, board firmware/runtime and working integration. Read-only PATH/common-root checks in this session do not prove no install exists anywhere or on teammate's computer.
- Proposed responsibility alignment: teammate leads platform/build/board; founder leads surface/LLM adapter/evidence. No assignment accepted or file ownership granted yet.
- Impacts: B-003, stack/platform proposal and eventual ownership handoff. Do not ask again for the already-reported OS or imply the founder lacks all FPGA experience.
- Reopen with actual machine inventory or agreed role division.

## D-014 — Prefer API-driven automation; fallback permitted

- Accepted founder preference: a customer-facing app calling an LLM API and automating the flow is optimal; another mechanism is acceptable if necessary.
- Alternatives remain unselected: verified API adapter, conditional private authenticated coding-CLI adapter, explicit manual prompt/import delivery.
- This is not acceptance of a model/provider/framework, automatic board deployment, or promise that a fresh full flow completes during the four-minute judging slot.
- Impacts: FR-005/FR-006/FR-009/FR-010/FR-013 and B-004. Manual work must be visible and cannot be presented as autonomous operation.
- Reopen with verified access and founder selection of automation/demo boundaries.

## A-009 — One local controller with replaceable model access

- Proposed: React/TypeScript/Vite interface; Python/FastAPI controller, one active hardware job, filesystem manifests/logs; bounded model adapter, trusted verification/build runner and board bridge. No extra database/cloud/agent framework for first slice.
- Model tasks: behavior extraction, RTL generation and bounded repair suggestions. Controller owns actual status, test oracle preservation, process execution, artifact identity and deployment evidence.
- Prefer direct API through verified grant/balance. Gemini free-tier route is conditional on actual quota/representative output; CLI fallback requires separate supported authentication. A manual adapter remains disclosed fallback, not equivalent automation.
- Local evidence: Codex 0.169.0-alpha.11.1 has exec/JSON/schema flags; login status is not authenticated in this shell. No model generation, SDK, login, paid API request or hardware tool test run.
- Proposed tiny kernel uses synthesizable Verilog/SystemVerilog in fixed wrapper with a low-volume AXI-Lite bridge; physical platform/contracts still unknown. Separate browser UI, host build execution and board processor/logic locations explicitly.
- Impacts: [ARCHITECTURE.md](ARCHITECTURE.md) stages 1–11, FR-001 through FR-013, B-003/B-004 and R-008. All technical choices remain recommendations until reconciled with actual installed tools and team preferences.
- Reopen with account/machine checks, measured latency or founder scope feedback.

## D-015 — Reported 500 credits are Codex usage only

- Accepted founder clarification: approximately 500 credits per student are Codex usage, not API credits.
- Resolves uncertainty in D-012; does not establish a separate organizer grant or general API account balance. Do not re-ask credit type or treat it as $500 of API funding.
- Impacts: B-004/model-route choice and ARCHITECTURE.md. API-first objective remains; actual API access or supported fallback is still unresolved.
- Reopen only with new API funding/access evidence or corrected account report.

## D-016 — Vivado and Vitis 2025.2 reported installed

- Accepted founder report: both Vivado and Vitis are version 2025.2. Combined with D-013 Windows 11/estimated 32 GB, this establishes the intended reported development baseline.
- Remaining verification: actual host/path, supported device/board packages, licenses, free storage, simulator invocation, board firmware/image/runtime compatibility and tiny integrated build/deployment. Earlier PATH/common-root lookup does not override this report.
- Impacts: FR-003/FR-007/FR-011 and B-003. Start discovery against 2025.2; no upgrade or exact command is prescribed by this decision.
- Reopen with executable/version evidence or a demonstrated platform incompatibility.

## D-017 — Real recording for long stages plus live matching hardware

- Accepted founder presentation decision: product should operate during judging where practical; if a complete run exceeds the slot, use a recording and show the working physical component.
- Contract: recording must show actual product operation, identify recorded/time-compressed stages, preserve actual elapsed duration, and match confirmed request/generated source/build identity to the design demonstrated live on KV260. Recording alone does not satisfy required physical execution.
- Resolves open four-minute full-build promise in round 005. Does not weaken automation objective, waive actual end-to-end evidence, approve fake progress, or imply a recording/build already exists.
- Impacts: FR-009/FR-010/FR-013, ARCHITECTURE.md stage 11 and R-008. No new workload/stack accepted.
- Reopen with founder change or organizer guidance conflicting with the plan.

## D-018 — Main spec belongs to teammate; this task owns RTL-to-demo scope

- Accepted founder instruction: teammate is making the main spec. This user's task is taking completed RTL to a working FPGA demonstration; first update research notes and produce one consolidated file to send to teammate, then begin demo work separately.
- The current three documents become clearly labeled exploratory inputs. Do not overwrite, supersede or presume acceptance of teammate's main specification, whose path/content has not been provided.
- Impacts: current scope/readiness, ARCHITECTURE.md and B-001/B-004 ownership; existing RTL-generation/app proposals remain suggestions for upstream owner.
- Current action: documentation/consolidation only. No implementation, hardware builds/programming, external sending, commit or publishing authorized by this packaging step.
- Reopen with agreed main-spec handoff or explicit reassignment.

## D-019 — Defer unresolved product choices; do not block supplied-RTL demo on API

- Accepted: mark uncertain API budget/provider, first product workload and React/Python stack choice as TBD/deferred to teammate, rather than requiring answers now.
- Product-time LLM access is an upstream concern; generating/funding a model is not inherently needed to build and exercise completed supplied RTL.
- Next demo intake: actual source/top module, behavioral contract and expected vectors, clocks/reset, data interface, dependencies/IP, applicable constraints and intended observable KV260 input/output. Exact transport/deployment is chosen against that package and actual baseline.
- B-003 remains a physical platform dependency; no success inferred from the tool installation report. No requirement for the specific proposed hysteresis detector, AXI-Lite bridge, Linux route or camera extension is imposed by this decision.
- Impacts: future task boundary and research brief; no full product or hardware implementation spec approved.
- Reopen if user is also assigned generation/model integration or completed RTL contract changes.

## D-020 — Accepted name: SiliconeOS

- Accepted explicit user decision: the new product name is **SiliconeOS**. Preserve this exact spelling, including the final “e” in “Silicone”.
- Replaces previous product-name references in this chat's planning/research documents and shareable brief. Earlier names such as `FabZero` and `SiliconOS` are historical aliases, not current branding.
- Existing checkout paths, Git URLs/branches, file/module identifiers and externally supplied teammate documents retain their literal names so links and technical instructions continue to work. Renaming those mechanisms or the remote repository was not performed.
- Current chat title updated to “SiliconeOS — FPGA demo planning”. No scope, workload, architecture, test result or build approval changes as part of this naming update.
- Impacts: current product headings/prose, consolidated brief and future references in this conversation. Teammate's separate main-spec work is not edited here.
- Reopen only on another explicit user naming decision.
