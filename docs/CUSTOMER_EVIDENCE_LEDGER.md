# Customer evidence ledger

**Last updated:** November 14, 2026 (America/Los_Angeles)  
**Owner:** customer/problem and pitch workstream  
**Privacy rule:** Keep names, contact details, and confidential workload details out of this repository. Use an anonymous participant ID unless the participant gives written permission for attribution.

## Current evidence summary

No qualified customer interview, observed usability session, quote permission, follow-up workload offer, buyer conversation, or paid commitment has been recorded in this ledger. Customer demand therefore remains **unvalidated**.

No individual outreach has been sent from this workstream. The repository rules require user authorization before outreach; no named contact or approved one-to-one channel has been supplied. This is a limitation, not a negative customer response.

| Claim | Evidence today | Status | What it does not establish |
|---|---|---|---|
| Engineers may find configuration provenance difficult | Product hypothesis only | Unvalidated | A real user's problem, urgency, or frequency |
| SiliconOS supports a useful workflow | Checked-in product and RTL-simulation documentation | Technical scope documented | Usability, desirability, or customer value |
| A qualified engineer will test a follow-up workload | None | Unvalidated | Interest, a pilot, or payment |
| A buyer will pay for SiliconOS | None | Unvalidated | Pricing, budget ownership, or demand |

## Next qualified test

**Participant criterion:** One FPGA, embedded, robotics, accelerator, or hardware engineer who has personally made a recent accelerator or hardware-configuration decision. A student may provide usability feedback, but is not evidence of enterprise buying intent.

**Requested session:** 20 minutes, individual and unrecorded by default. Start with the participant's recent work before showing SiliconOS. Then ask them to attempt the supported workflow: configure signed INT8 square matrix multiply (N=8 or 16; one or four lanes), inspect the comparison, and explain what the evidence receipt proves. Do not coach the first attempt.

**Exact next action once authorized:** Send the following one-to-one invitation to a named, relevant contact through the approved channel:

> We are testing a student prototype for a narrow hardware workflow: configuring a small accelerator variant and keeping the simulation/build/deployment evidence together. Could we ask about the last accelerator or configuration decision you made, then watch you try our supported workflow for about 20 minutes? We are looking for failures and missing evidence, not an endorsement. We will not ask for confidential RTL or credentials.

## Interview record template

Create one row only after a real session. “Not provided” and “declined” are valid findings. Keep any identifying details in a private consented record, not here.

| Field | Record |
|---|---|
| Participant ID / date | — |
| Qualification and role | — |
| Platform / relevant experience | — |
| Attribution permission | No permission by default; record exact scope if granted |
| Most recent accelerator/configuration change, before demo | — |
| Existing tools and artifacts | — |
| Active engineering work | — |
| Elapsed waiting (if known) | — |
| First failure or setback | — |
| Correctness process | — |
| Artifact/build/deployment tracking process | — |
| Supported SiliconOS task attempted, without coaching | — |
| Observed outcome and confusion | — |
| Evidence required before reuse or deployment | — |
| Non-confidential follow-up workload offered? | — |
| Second session proposed / scheduled | — |
| Buyer, approval, or budget knowledge | — |
| Verbatim quote and quote permission | Do not record/use without explicit permission |
| Refusal, limitation, or negative feedback | — |
| Team interpretation (clearly labeled) | — |

## Interview sequence

Ask these questions in order before demonstrating the product:

1. “Tell me about the most recent accelerator or configuration change you made.”
2. “Which tools did you use, and what required active work versus elapsed waiting?”
3. “What was the first failure or surprise, and how did you respond?”
4. “How did you decide the result was correct?”
5. “How did you track the exact source, parameters, reports, and deployed artifact?”

Then say: “Here is the supported scope: signed INT8 square matrix multiply, N=8 or 16, with one or four lanes. Please try to configure and evaluate it as you would normally.” Observe silently during the first attempt. Record clicks, questions, incorrect assumptions, task completion, and help requested; do not translate those observations into endorsement.

After the attempt, ask:

1. “What evidence would you need before reusing or deploying this output?”
2. “What is missing compared with your current tools or scripts?”
3. “Would you provide a non-confidential workload for a follow-up?”
4. “May we schedule a second session to test it?”
5. “May we use any of your words or role in the pitch? If so, what exact attribution is permitted?”

## Reporting rules

- Count qualified interviews, observed attempts, workload offers, scheduled follow-ups, and paid commitments separately.
- Record refusals, “not applicable,” inability to complete the task, and requests for capabilities outside scope as evidence, not omissions.
- Do not treat a persona, a form submission, a visitor, or an unobserved claim as customer validation.
- Do not ask for confidential RTL, customer data, credentials, or a promise to buy.
- A future pilot must agree its workload, board/toolchain, acceptance criteria, schedule, and buyer authority with the participant. It may measure time saved only with a defined before/after method.
