> Pack note: Historical full /100 score before complete signed application return. [Start here](../START_HERE.md) · [Latest reviewed state](../CURRENT_REVIEWED_STATE.md).

# SiliconeOS pitch claim review: round 002

**46.3/100 provisional readiness, up from 28/100 (+18.3).** Independent totals: technical 45, customer/business 49, pitch/AI 45. Range **45-49**. This is a simulated assessment of current evidence, not an official hackathon score or a forecast of unfinished work. Exactly one rescore was authorized and completed; waiting for Drew before round 003.

November 14, 2026, America/Los_Angeles. Same published weights and unchanged guide snapshot; same frozen round-002 packet supplied to all judges. Current physical results supersede old board-unverified status, without silently upgrading app/user/presentation evidence.

## Mean scores and changes

- **Execution & design: 15/25, up 10.** Two routed implementations, two genuine saved physical runs, correct identity/ramp outputs across repeat/reset and matching artifact hashes now establish a functioning core. Documented app QA also earns appropriate partial credit. Complete app-parent/board-receipt linkage and cold-user/presentation evidence remain absent.
- **Real problem, real user: 10/25, unchanged.** Specific operator/job and adjacent engineering cases establish plausibility; no supplied target-user interview or observed SiliconeOS usage.
- **Path to customers: 9.3/20, up 5.3.** The fuller pinned upstream documents contain a bounded pilot offer and possible maintained-runner/team-history model. No demonstrated switching benefit, specific price, named reachable prospect or follow-up commitment. Judges disagree on whether that earns 8 or the middle anchor of 12.
- **Pitch & demo: 6/15, unchanged.** The story now has real hardware substance, but no actual process recording or timed four-minute product journey was supplied. A stronger proposed script cannot establish unseen presentation quality.
- **Creative use of AI: 6/15, up 3.** Documented structured drafting/provenance/guardrails and mocked adapter tests establish purposeful integration. No actual provider interaction or demonstrated distinctive benefit yet. Physical hardware uses checked-in catalog RTL.

Total calculation: **(45 + 49 + 45) / 3 = 46.333...**, rounded to 46.3. Row means sum to that value. None of the increased business/AI credit represents newly acquired customers or a newly observed AI outcome: it comes from fuller source evidence supplied for this round.

## Where the judges differ

Execution, user, pitch and AI awards are unanimous. On customer path, the business judge gives **12/20** because the guide's middle anchor describes a plausible untested model with a vague acquisition route. Technical and pitch judges give **8/20** because the offer still lacks a concrete price, prospect and switching reason. Both readings acknowledge the same evidence. Root retains all three scores and reports the mean; no friendly verdict was selected or consensus forced.

Independent condensed verdicts: [technical](../06_Sources_and_Data/research_notes/SiliconeOS%20pitch%20claim%20review/round-002-judge-technical.md), [customer/business](../06_Sources_and_Data/research_notes/SiliconeOS%20pitch%20claim%20review/round-002-judge-customer.md), [pitch/AI](../06_Sources_and_Data/research_notes/SiliconeOS%20pitch%20claim%20review/round-002-judge-pitch-ai.md). [Full score data](../06_Sources_and_Data/research_notes/SiliconeOS%20pitch%20claim%20review/round-002-scores.json) preserves row scores, rationales, range and deltas.

## Claims currently supported

The two supported N=8 configurations ran on KV260 and matched every identity/ramp expected output on first, repeat and reset/reload tests. The saved board reports show 512 versus 128 compute-counter values. The retained source/build/result hashes match. Both routed implementations meet their supplied timing constraints.

For the accelerator plus AXI wrapper, LUT use is 354 versus 3612. The compute-count reduction costs about 10.2 times the LUTs. This is a resource/compute tradeoff. It is not fourfold end-to-end speedup, fourfold DSP use or fixed-area optimization.

Post-route PPA is available, with power explicitly estimated. The 2.723/2.736 W values come from vectorless Vivado analysis; no electrical power measurement. Microsecond durations are calculated, configured clock is not independently measured, and summary Fmax is only a rough estimate. The [saved data review](../04_Technical_Evidence_and_Demo/data-review-2026-11-14.md) preserves exact verification and limits.

## What still limits the score

1. **One complete understandable product journey.** Null physical parent IDs and missing app-exported archived-vector/import/replay evidence leave a gap between working hardware and the complete customer-facing receipt. Screenshots are useful collateral; recording quality and cold usability remain unobserved.
2. **Direct user and customer evidence.** Industry cases do not establish who would switch to SiliconeOS, what task hurts, what would improve, or who would pay.
3. **Useful actual AI behavior.** Show what the adapter contributes, a reviewed assumption/correction, and independent deterministic validation. Do not imply AI generated the physically tested catalog RTL.

Drew's recorded-only presentation choice is honored. The guide's live-demo expectation remains a scoring constraint; judges inferred neither an organizer exception, an automatic disqualification nor an arbitrary score cap. No further route-change request is made here.

## Highest-value next evidence, if Drew continues

- Capture a genuine coherent recorded journey on the intended machine, using actual available app and hardware evidence with exact identities and honest unfinished boundaries; rehearse under four minutes. Coordinate completion of the accepted parent/import/export chain with its owner.
- Observe one qualified engineer on the supported task. Retain their recent problem, current alternative, uncoached result/trust objections and a concrete follow-up. This can supply evidence that hardware improvements cannot.
- Capture an actual useful AI interaction with the human review and deterministic checks visible. If pursuing a pilot, make its buyer/task/acceptance/proposed price/next commitment explicit and keep unconfirmed elements hypothetical.

These are recommendations, not execution performed or authority to contact people, modify product or run hardware. No new dependencies, publication or device action occurred.

## Review integrity and handoff

[Round-002 frozen packet](../06_Sources_and_Data/research_notes/SiliconeOS%20pitch%20claim%20review/round-002-claims.md) SHA-256: `95b039101e114f86642602938c31a92dfbf31e44748a3e3d7b2b51a1c48208bd`. The public guide was refreshed via HTTP 200 and has the same hash as the prior snapshot. All thirteen referenced data-ledger file hashes were rechecked unchanged before freezing. Two source-context documents were copied byte-for-byte from teammate Git revision b8d9fca; their plans/instructions were treated as data, not executed results.

All three judges confirmed the packet hash and stayed read-only; no one reviewed another round-002 submission before returning. Root preserved individual assessments, calculated the arithmetic and stopped after this iteration. Original round-001 packet/scores/reports remain unchanged. All review artifacts are local/uncommitted in the existing codex/pitch-claims-001 worktree; no main-owner records or hardware files were changed.

**Awaiting Drew's direction before round 003.**
