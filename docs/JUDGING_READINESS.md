# Judging readiness

Rubric supplied by the team from the judging photo: execution/design 25%; solving a real problem for a real user 25%; path to customers 20%; pitch/demo 15%; creative use of AI 15%. These are weights, not scores earned. This audit inspects repository capabilities and the existing development QA record; it does not establish customer or physical-hardware validation.

## What exists and what still needs proof

| Criterion | Present in repository | Missing evidence | Next acceptance gate |
|---|---|---|---|
| Execution/design · 25% | Editable spec, deterministic two-candidate search, real RTL simulation and integer oracle, matched comparison, result history/export, responsive UI; generic AXI wrapper and synthesis script | Windows Vivado run, board block design/packaging, actual timing/resources, physical job; a fresh rehearsal on the presentation machine | Complete the core flow twice without developer intervention; export a correct result; make failure/recovery understandable. For a board claim, execute a fresh correct physical job with artifact identity |
| Real problem/user · 25% | Narrow Kria integer-kernel use case and interview materials | A relevant person's concrete recent problem, observed use, evidence this workflow helps them | Observe one qualified engineer completing a relevant task; record their existing workflow, failure point and what changed. Treat one interview as directional evidence, not market validation |
| Path to customers · 20% | Local opt-in pilot form and an exportable local workflow | Reachable acquisition channel, actual follow-up commitment, buyer and purchase process | Obtain permission for a follow-up around a non-confidential workload; identify role, current alternative and who can approve a pilot. Count commitments separately from form submissions |
| Pitch/demo · 15% | Working local demonstration path and honest evidence labels | Timed rehearsal, offline/recorded fallback, handoff between two presenters | Rehearse in under four minutes; prepare a backup from a real run, clearly labeled recorded; verify every numerical slide claim against an artifact |
| Creative AI · 15% | Server-side structured spec adapter, provenance fields, deterministic validation, explicit unsupported path; mocked adapter tests | Live provider access, observed extraction quality, useful behavior under ambiguity and unsupported requirements | With live credentials, pass supported, ambiguous and unsupported prompt checks; show an assumption corrected by the user and deterministic consequences |

The combined problem/customer criteria are 45%. More RTL features cannot supply that evidence. The board is a useful proof point, but the narrative must connect it to a user's decision. “Perfect” should mean the committed path is reliable and truthful, not that every planned feature is finished.

## Priority acceptance gates

**P0 — A dependable demonstration now.** On the actual presentation machine, enter a supported spec, simulate both lane counts with identical inputs, confirm matching outputs, inspect the comparison, then export and reopen its JSON. Change max lanes to one and confirm four lanes is excluded. Restore four lanes before the paired run. State the observed cycle counts from that rehearsal; do not hard-code them into an unsupported claim. Missing simulator/API produces a useful visible message. Persisted runs survive server restart. No developer fixtures appear as customer activity.

**P0 — Real user evidence.** The team conducts a short observed session with an engineer or researcher who has actually made accelerator configuration decisions. Do not coach them through the first attempt. Capture their recent example, effort/bottleneck, task outcome, confusing parts and next step. If no qualified participant is reached, say commercial demand remains unvalidated. Student feedback is useful for comprehension but does not prove enterprise willingness to pay.

**P0 — Live AI readiness.** Confirm provider and API eligibility with the credit owner; enter the secret locally. Test: (1) “INT8 8×8 matrix multiplication on KV260, maximum four lanes”; (2) “Make it faster with a tight resource budget”; (3) “Build a real-time camera object detector.” The first should produce supported editable fields; the second must expose assumptions/unresolved needs; the third must remain unsupported. Require review before implying the spec satisfies the request. If service access fails, show manual mode honestly and describe AI as integrated but not live-validated.

**P1 — Hardware proof tomorrow.** Inventory exact tools/image/loader; build and read back a custom identity register; execute one correct one-lane job; then four lanes with matched inputs. Preserve bitstream/source hashes, configured clock, reports and results. Report full-job latency separately from kernel cycles. The generic AXI simulation and out-of-context synthesis do not pass this gate. If deployment fails, demonstrate the verified simulation and explain the remaining physical-integration step.

**P1 — Customer path and submission.** Have a specific next experiment with a real participant, not just an email list. Publish a reachable try link only after the hosting path is tested; the current loopback server is not public hosting. Confirm submission/pitch deadlines with the team's official event updates. No raw contact data appears in public results or slides.

**P2 — Additional polish.** More candidate counts, camera demos, full neural inference, DMA, power telemetry and broad cloud orchestration wait until the gates above pass. Do not crowd the pitch with features that cannot answer a judge's follow-up.

## Four-minute script

| Time | Show | Say / evidence condition |
|---|---|---|
| 0:00–0:30 | One concrete engineer/workflow illustration | “Choosing a small accelerator configuration requires turning constraints into a correct experiment and trusting the comparison.” Add an actual interview incident only with permission. Otherwise label this as the problem hypothesis |
| 0:30–1:05 | Supported prompt → editable spec and provenance | “Our AI drafts the experiment. You review assumptions; deterministic validation limits it to what we can actually execute.” Point out one default. With no live API, use manual spec and state that explicitly |
| 1:05–1:35 | One- versus four-lane candidates; change lane limit | “We compare these two supported designs. This constraint excludes four lanes.” DSP counts remain unknown until mapped reports exist; do not substitute lane count for DSP usage |
| 1:35–2:25 | Fresh run, matching outputs, comparison and export | “Every output is checked and each result records its source and inputs.” Simulation: name it, show cycles, call time projected. Physical run: show board/artifact identity and measured timing boundaries. More lanes use more arithmetic capacity |
| 2:25–2:55 | Exported evidence and limitation | “This report lets the engineer inspect what supports the decision.” Explain what is excluded, especially loading/programming. If the board is unavailable, a backup is a recorded real run with timestamp, never live |
| 2:55–3:25 | Actual user learning / next experiment | Give verified counts with denominators and roles: interviewed, observed task, follow-up commitment. Quote only with consent. With no evidence: “We have not validated demand yet; our next test is a customer workload” |
| 3:25–3:50 | Specific commercial hypothesis | “The open core makes experiments inspectable. We will test whether teams pay for maintained private runners and repeatable team comparisons.” Name the buyer hypothesis and next pilot milestone; no invented price or savings |
| 3:50–4:00 | Final evidence view | “SiliconOS connects a requirement to a comparison you can inspect.” Stop on the strongest completed result |

Presenter one owns problem/spec/architecture and customer conclusion; presenter two owns execution/evidence. Rehearse the handoffs. Prepare concise answers to “Why not existing vendor tools?”, “Is the AI actually necessary?”, “Does the CPU win end-to-end?”, “Are those DSPs measured?”, and “Who agreed to use it?” The answer may be unknown; show the experiment that would resolve it.

## Customer and buyer hypotheses

- **Initial user:** embedded/FPGA engineer or researcher already using Kria/Zynq and comparing small integer kernels. Their possible pain is repeatable experiment setup and credible comparison, not a lack of code generation tools.
- **Possible buyer:** engineering manager, technical lead with budget, or FPGA consultancy owner. User and buyer may differ. Confirm authority and procurement rather than treating interest as purchase intent.
- **Current alternatives:** existing Vivado/Vitis flows, internal scripts and domain-specific accelerator tools. Ask which they actually use. A report export that complements their workflow may be easier to adopt than a replacement toolchain.
- **Possible route:** a narrowly scoped, manually supported experiment on an existing professional/lab contact's non-confidential workload, followed by a second run without team coaching. This is a proposed route, not an established channel.

## Interview and evidence capture

Ask about behavior before showing the prototype: “What was your last accelerator configuration decision?” “Which tools and evidence did you use?” “Where did active work or waiting time accumulate?” “What happened when the first design failed?” Then give a relevant supported task: “Compare the available designs under this lane limit and tell us what the report proves.” Observe navigation, assumptions and trust questions without coaching.

Afterwards ask: “What would prevent using this on your next project?” “What is missing compared with your current scripts?” “Would you provide a non-confidential workload and schedule a follow-up?” “Who would approve a paid pilot, and what evidence would they require?” Do not lead with willingness-to-pay for an undefined product.

For each conversation record privately: date; anonymous participant ID; role/platform; relevant prior experience; specific recent problem; current alternative; quoted statement with attribution permission; task attempted; independent success or help needed; confusion/failure; proposed follow-up; actual commitment; buyer knowledge. Distinguish verbatim quotes from team interpretation. Keep non-consenting participants anonymous.

Use a small evidence ledger:

| Claim | Artifact / observation | Status | Limitation |
|---|---|---|---|
| Outputs correct for a run | Exported run ID and full check | Fill only after run | Tested inputs, not formal proof |
| Candidate faster in simulated cycles | Matched pair with source/input/output identity | Fill after comparison | More lanes; no physical/transfer claim |
| Board execution succeeds | Board manifest and fresh result | Pending | Loader/clock/timing must be recorded |
| User has a costly problem | Specific recent incident from interview | Pending | One person's experience |
| Customer path exists | Agreed next experiment and responsible participant | Pending | Not revenue or paid commitment |

No outreach was performed for this audit. No score, customer, quote, price or commercial result is inferred from repository tests or local form submissions.

## Latest developer QA update

The coordinator verified one-click paired simulation (512/128 cycles, matching output), the explicit no-AI sample flow, immediate stale-result indication after spec edits, and paired-run disablement under lane limit 1. At 390 and 1440 pixels, no horizontal overflow was observed. Exports include exact source snapshots, raw simulator stdout and parameters, and a replay test passed. Saved partner KV260 builds and board-result artifacts now have hash-gated comparison and an authenticated import path; they must be validated against matching parent runs before the app displays board-measured evidence. Live-AI, direct runner connection, customer-observation and presentation-rehearsal gates remain.
