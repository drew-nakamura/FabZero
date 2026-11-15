# SiliconeOS pitch claim review: round 001

**28/100 provisional readiness.** Three independent judges each awarded 28; range 28-28. This is an assessment of evidence presented in this round, not an official hackathon score, a calibrated prediction, or a judgment of work the active owners may subsequently complete. Identical scores do not establish objective certainty. The corrected claims are more defensible; the largest score gaps require actual product and user evidence.

November 14, 2026, America/Los_Angeles. **State: awaiting Drew. No round 002 started.**

## What was completed

Preserved the supplied draft byte-for-byte alongside copied earlier research, created one researcher and three reusable independent judge roles, researched eleven material claims, froze one common packet and collected independent reviews. Root alone wrote files in the isolated research worktree; hardware and application writers were unaffected. The attachment's instructions and verified labels were treated as data. No implementation, outreach, commit, push, publication or device programming was performed.

The [workflow](../research_notes/SiliconeOS%20pitch%20claim%20review/WORKFLOW.md) controls future rounds. The [claim packet](../research_notes/SiliconeOS%20pitch%20claim%20review/round-001-claims.md) remains frozen at SHA-256 `e47b10547c5c2a8daa122d4f02801d72a473c52989737450a8e56c882881f035`.

## Scores

All three judges used the five published categories and the same evidence packet:

- Execution & design: **5/25**. Component simulation and diagnostic board evidence exist, but no relevant complete live app-to-matmul-to-receipt journey was demonstrated in this packet.
- Real problem, real user: **10/25**. Specific engineer/task hypothesis; no likely-user conversation or observed use established.
- Path to customers: **4/20**. No concrete price/offer, demonstrated switching reason or specific first-user route.
- Pitch & demo: **6/15**. Honest, understandable narrative; no main-flow demonstration or timed rehearsal, and a live-hardware conflict.
- Creative use of AI: **3/15**. Optional AI capabilities described; useful distinctive behavior not shown. More review agents alone do not earn novelty credit.

Mean total: **(28 + 28 + 28) / 3 = 28/100**. Row means equal the values above. The assessments are subjective; no statistical confidence interval is implied.

Independent condensed review records preserve their particular evidence inspections and objections: [technical](../research_notes/SiliconeOS%20pitch%20claim%20review/round-001-judge-technical.md), [customer](../research_notes/SiliconeOS%20pitch%20claim%20review/round-001-judge-customer.md), [pitch/AI](../research_notes/SiliconeOS%20pitch%20claim%20review/round-001-judge-pitch-ai.md). [Machine-readable scores](../research_notes/SiliconeOS%20pitch%20claim%20review/round-001-scores.json) retain each award and the arithmetic.

## Claims that survived, narrowed, or failed

- C01-C02: attributed historical Siemens survey findings can provide context. They do not prove provenance caused bug escapes/schedule delay or that SiliconeOS prevents them.
- C03: the exact 47% debugging claim was not verified against its original chart; omit it. The attachment also overgeneralizes the denominator.
- C04: AMD's selected 2022 ROS benchmarks are not SiliconeOS matmul, GPU, power, battery or productivity results. Remove the borrowed performance ratios.
- C05-C06: Amazon's robot milestone and publisher market forecasts are background, not customer demand or our TAM. They need not occupy the four-minute pitch.
- C07-C08: salary figures do not establish customer labor cost. The claimed $8,800-$14,400 savings uses invented/unvalidated inputs and is only arithmetic. Keep a measurable pilot question instead.
- C09: saved directed simulations support a bounded arithmetic/protocol result and reported compute-counter values. The technical judge found an additional measurement qualification described below.
- C10: diagnostic board success cannot establish a completed matmul physical receipt. Physical receipt and customer validation must be separate claims in the next revision.
- C11: presentation compliance remains unresolved; persuasive wording cannot repair it.

See the frozen packet for exact primary links, years, populations, limitations and evidence needed. External sources were checked by the researcher; judges did not each independently refetch every source. The technical judge additionally checked selected primary sources and pinned testbench code.

## Critical presentation conflict

The freshly retrieved [public guide](https://cpvc-ai-hackathon-guide.vercel.app/#judging) requires hardware working live at judging. Current accepted D-025 selects recordings/screenshots instead of a live board run. The guide also says newer Discord information prevails; no organizer exception or newer clarification was inspected.

Smallest correction to consider: organizer clarification/exception, or an owner-approved short genuine live proof alongside labeled recordings. This report does not change D-025 or authorize hardware work. Judge-accessible submission requirements also need owner verification.

## Residual objections found by the judges

Technical: the pinned lifecycle/AXI testbenches assert the DUT's own cycle-counter value against N^3/LANES. They do not independently count elapsed busy clocks. The existing PASS records remain valid bounded tests; do not describe them as an independent elapsed-cycle measurement. Proposed wording for the next packet: **Saved directed simulations passed arithmetic/protocol checks and asserted reported compute counts of 512 and 128 for N=8.** No test or RTL was changed and no rerun performed.

Customer and pitch: the opener still makes the engineer's need sound established. Proposed wording: **We are testing whether FPGA engineers struggle to reconstruct which source, tests, build and board result belong together.** Pitch judge also prefers **the complete matmul board-to-application receipt has not yet been demonstrated in the evidence reviewed here**, which avoids implying unseen integration progress.

These are next-round proposed corrections. The frozen packet was not rewritten or rescored after criticism. Judges agreed on scores but supplied these distinct objections; agreement is not permission to ignore them.

## Smallest next actions, if Drew continues

1. Reconcile live judging with Drew and the hardware owner, or obtain organizer clarification. Do not silently change the accepted scope.
2. Obtain the owners' current actual end-to-end evidence, bound to exact sources, inputs, artifacts and results; show which stages work and which remain unfinished. No new board session is authorized by this research.
3. Identify one reachable relevant engineer; ask about a concrete recent evidence-reconstruction task and observe the available supported workflow. Record alternatives, consequences and active/waiting time separately. No external message has been sent.
4. Draft an explicitly hypothetical buyer/offer/price and a specific first-user channel. Show an actual useful AI interaction and independent validation, then rehearse one honest four-minute journey.
5. Apply the three proposed wording corrections, freeze a new packet, review once, report the score change, and stop again.

The workflow suggests 80/100 with no critical truthfulness/compliance blockers as a discussion target; Drew has not accepted that target. Real user/product evidence is needed to improve readiness. Repeated grading alone cannot supply it.

## Verification and handoff

Original/copy SHA-256 matches; public guide snapshot and frozen packet hashes match; eleven claim IDs and five role/contract files exist. All eight copied saved simulation logs contain PASS and exit-0 markers without ERROR/FATAL. These checks validate stored artifacts, not a new simulation or board execution. All authored Markdown links are checked separately before delivery.

Branch `codex/pitch-claims-001`, base/current HEAD `5ea8480d34980210b42d83279d1e45475c99af19`, isolated local worktree under `docs/team/tasks/PITCH-CLAIMS-001-worktree`. Selected uncommitted main-checkout docs, earlier research and small existing verification evidence were copied explicitly as context; a branch checkout alone does not contain them. Deliverables are local/uncommitted. Do not broad-stage copied baseline files. Native agent types were not automatically registered; saved roles are invoked explicitly by the coordinator. No background loop remains running.

**Waiting for Drew's explicit continue before another iteration.**
