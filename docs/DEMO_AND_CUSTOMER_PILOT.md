# SiliconOS demo and customer pilot

## The claim to test

“Compare small accelerator designs and inspect reproducible evidence from your board.” The initial user hypothesis is an embedded/FPGA engineer already evaluating integer kernels on Kria/Zynq. We have no confirmed customer demand, pricing, or time savings. Students can test usability; they do not establish enterprise purchase intent.

A beginner can understand the demo without being promised a full application: show two small matrices, ask for the fastest supported architecture with at most four lanes, and display the numerical result alongside its evidence. Explain that matrix multiplication is a component used in larger applications; this prototype does not deploy those applications.

## Three-minute demonstration

1. **Requirement (30 seconds):** “Compare signed INT8 8×8 matrix multiplication on KV260, at most four lanes.” If AI is configured, show its draft and provenance; otherwise edit the same specification manually. Explain assumed clock and unverified DSP budget.
2. **Architecture (30 seconds):** show one- and four-lane candidates. More lanes use more arithmetic capacity. Switch the lane constraint to one and show deterministic exclusion. Do not pretend this is a measured DSP-budget decision.
3. **Evidence (60 seconds):** run the real available execution path. Tonight that is RTL simulation; tomorrow board execution only after integration succeeds. Show exact output correctness, cycles, source/artifact identity and result export. Projected time and measured time remain distinct.
4. **Decision (30 seconds):** explain what the result answers and what it leaves open: implementation resources, clock feasibility, and transfer overhead until measured. With real board results, show kernel and full-job timing separately.
5. **Customer test (30 seconds):** state the specific user problem learned in interviews, if any. Ask for a non-confidential workload and a follow-up experiment. If interviews have not happened, say demand is still a hypothesis.

Keep a fresh live run distinguishable from a recorded run. A visible failure with useful diagnostics is better evidence of a real system than a fabricated success. Do not promise a fourfold measured speedup before testing: clock closure, staging and transfers can change the outcome.

## Ten-minute discovery script

The team sends any invitations manually; no outreach has been sent by this document.

- “Tell me about the last time you chose between accelerator configurations. Which board and tools did you use?”
- “What steps took the most active engineering time? What took the most elapsed time?”
- “What did you compare, and which evidence convinced you it was the right choice?”
- “Show us how you would express that requirement here.” Observe without coaching; record mistakes.
- “What is missing before you would trust this report?”
- “Would you bring a non-confidential kernel to a follow-up? Who would approve a paid experiment if it saved meaningful time?”

Record role, platform, current workflow, concrete recent incident, observed task success/failure, missing requirement and agreed next step. Obtain permission before quoting someone by name. Record negative feedback too. Do not collect confidential RTL, passwords or API keys.

## Pilot offer to negotiate

One supported integer kernel, one identified board/toolchain, a baseline and a small candidate set. Deliver source/build provenance, correctness checks, implementation reports and repeatable board measurements. Compare active engineering time against the customer's current process. Agree scope, acceptance criteria, schedule and price with a real buyer; no assumed price or savings is presented as validated.

Track qualified conversations, observed completed tasks, follow-up workload offers, repeat sessions and paid commitments separately. Visits, button clicks and student signups are not equivalent to customers. For a two-person weekend, prioritize a few detailed observations over a large signup count.

Potential paid value is maintained private runners, reproducible team experiment history and supported tool/board combinations. If a one-time script solves the need, recurring subscriptions may not be justified. The pilot should test that uncertainty rather than hide it.
