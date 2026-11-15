> Pack note: Founder/slide-writing snapshot. Some implementation gaps were superseded by round004; read the latest-reviewed-state guide. [Start here](../START_HERE.md) · [Latest reviewed state](../CURRENT_REVIEWED_STATE.md).

# SiliconeOS: founder story and slide-writing handoff

For Christopher and Drew, November 14, 2026. Prepared from Drew's firsthand answers, inspected Git history and the saved technical/research evidence. Copy-ready suggestions below are presentation drafts, not a change to accepted product scope. This file is self-contained; the existing teammate research handoff holds the longer research/pricing record.

## The central story

**We are hardware engineers who love RTL and have experienced the friction around it. We used AI to connect a fragmented toolchain, then tested a deliberately narrow slice on real FPGA hardware.**

The compelling arc is personal experience → a broad ambition → a disciplined scope choice → working hardware → a specific next customer test. The source of the idea and hardware judgment was the team. AI expanded the team's view, challenged business assumptions and helped perform integration work. Demand and commercial savings remain to be validated.

### Copy-ready founder story: about 40 seconds

> We both love RTL, and we've both spent long stretches debugging waveforms, simulations, testbenches and the scripts that connect them. We wanted a place where configuring a design, checking it and seeing the hardware result could stay connected.
>
> Our first ambition was idea to GDSII. During the hackathon, we narrowed that to an FPGA workflow and then a supported accelerator comparison we could actually test. SiliconeOS now demonstrates one- and four-lane INT8 matrix multiplication on a KV260, with correctness, implementation reports and identifiable physical results.
>
> We brought the hardware background and direction. AI helped us integrate the toolchain and challenge whether a cool technical idea could become a useful product.

Say “GDSII” on slides if using the industry-standard layout-file term; Drew's answer wrote “GDSIII.” Describe it as the original ambition, not a completed capability. The full script's duration should be measured aloud; word count is only a planning aid.

### Shorter opening: about 15 seconds

> We love designing hardware. We know the work also involves waveforms, testbenches and scripts spread across tools. We built SiliconeOS to connect a supported FPGA design change with checks, implementation results and evidence of what actually ran.

## Suggested seven-slide sequence

Total planned speaking time: **225 seconds**, leaving 15 seconds inside a four-minute limit. Rehearse the actual recording and transitions. This is content for the current slide author, not a request to replace an existing deck layout.

### Slide 1 — Why we started | 20 seconds

**On-slide text**

> SiliconeOS
>
> Reconfigure. Verify. Deploy. Keep the receipt.
>
> Built by two hardware engineers who have lived the workflow.

**Speaking notes**

Use the short opening above. Introduce the human problem before the long tool list: changing a design also means checking and explaining which version, tests and artifact the result belongs to.

**Suggested asset**

Team names and one genuine board or workbench image. Keep the opening legible to a non-specialist.

### Slide 2 — The problem we know | 30 seconds

**On-slide text**

> A design change crosses many tools.
>
> Requirements · RTL · simulation · implementation · hardware results
>
> The engineer still needs to establish what was tested and what ran.

**Speaking notes**

Drew and Christopher report firsthand experience debugging waveforms, writing testbenches and connecting Python/shell scripts. Use that as founder experience, not a representative industry survey. Drew describes hardware projects as potentially taking months; we have not established a measured typical duration or shown SiliconeOS reduces a months-long project to minutes.

**Suggested asset**

A simple chain of the actual stages, with an example source/configuration identifier carried through. Existing tools already handle parts of this chain. Emphasize the experience the team is trying to improve.

### Slide 3 — How we narrowed the idea | 30 seconds

**On-slide text**

> Started broad: idea → chip layout
>
> Chosen slice: supported specification → FPGA experiment
>
> First user hypothesis: an FPGA engineer iterating an edge-AI accelerator.

**Speaking notes**

The team's interest in RTL came first; there was no settled product before the hackathon, according to Drew. Idea-to-layout was too broad for the event. The team narrowed to FPGA execution and a bounded matrix comparison. Research/judge agents helped distinguish technical appeal from a buyer, switching reason and testable offer. This was refinement of hypotheses, not completed customer discovery interviews.

Edge-AI companies and larger FPGA deployments motivate the longer-term vision. The current demonstration is one KV260; it does not operate or update a fleet.

### Slide 4 — What actually works | 65 seconds

**On-slide text**

> Same N=8 INT8 matrix multiplication. Two hardware configurations.
>
> One lane: 512 reported compute cycles · 354 LUTs
>
> Four lanes: 128 reported compute cycles · 3,612 LUTs
>
> Both passed output, repeat and reset checks on KV260.

**Small caption**

> LUTs: accelerator plus AXI wrapper. Cycle counters exclude programming and data transfer. Recorded real execution; build reuse/cuts labeled.

**Speaking notes**

This shows a real design tradeoff: four lanes use one-quarter the reported compute count and about 10.2× the LUTs. Both implementation builds met their supplied timing constraints. The core maps multipliers to LUTs, not DSPs.

App-exported inputs ran correctly on both configurations. A separate clean-room test rebuilt from those exported RTL bytes and both fresh bitstreams ran correctly on the board. Independent offline artifact checks passed 28/28 per clean-room configuration, including hashes, parent/source/input identity and output correctness. These are bounded checks, not an exhaustive verification claim.

Describe a receipt plainly: the record of the source, configuration, tests, build and physical result that belong together. Show the completed portions of the app journey. App signing/import/final receipt export must be confirmed before narrating them as completed.

**Suggested asset**

Use genuine app/board footage with visible run identity and a simple lane comparison. The published app-import result folders are `20261115T011930Z_n8_l1` and `20261115T012007Z_n8_l4`. Clean-room results are separate local evidence with different artifact hashes; pair each result with its matching build. Do not intermingle them.

### Slide 5 — How AI helped two engineers build it | 30 seconds

**On-slide text**

> AI helped connect the toolchain.
>
> Engineers chose the scope and checked the results.
>
> Correctness came from tests, reference arithmetic and hardware readback.

**Speaking notes**

Founder-reported AI assistance spans RTL/tool integration, Vivado, Yosys, UI, research and debugging. Drew had not previously worked with a board of this scale; AI helped him learn its bring-up and deployment flow. Prefer this concrete account over claiming mastery of every tool in a weekend.

Distinguish development assistance from AI inside SiliconeOS. The product includes optional AI specification drafting and an advanced generated-RTL route. The physically demonstrated core is checked-in catalog RTL. Do not imply that a live product agent invented and deployed that core from an arbitrary prompt. Add one actual useful in-product interaction only if captured and checked.

### Slide 6 — Who would use it, and what we test next | 35 seconds

**On-slide text**

> First user: an FPGA engineer comparing supported accelerator variants.
>
> Test: is this easier to inspect and hand off than their existing workflow?
>
> Future: more supported workloads, boards and numerical formats.

**Speaking notes**

The intended buyer is an engineering/hardware lead; this is unvalidated. Existing Git/Tcl/CI workflows and free tools are real alternatives. A receiving engineer should be able to inspect the experiment and understand its evidence with less reconstruction; that benefit still needs an observed comparison.

If the deck needs business detail: our research proposes a US$250 one-time assisted evaluation, subject to readiness/approval, and US$149 per engineer/month for a more mature supported workflow. The mature price is a hypothesis with a proposed US$30 provider-cost AI allowance, not an active customer commitment. The illustrative US$19.20 monthly API cost is an unmeasured scenario. Keep detailed cost arithmetic in backup material rather than crowding this slide.

Matrix multiplication is the current test case. Drew wants to broaden edge-AI workloads and eventually numerical formats such as INT4/FP4. Today the supported arithmetic is INT8 inputs with INT32 accumulation; future formats, arbitrary sensors and fleet support are not demonstrated.

### Slide 7 — Team and the ask | 15 seconds

**On-slide text**

> Hardware experience. AI-assisted execution. A real FPGA result.
>
> We're looking for relevant engineers, pilot-task feedback and business mentorship.

**Speaking notes**

> We know the engineering work firsthand, and we want to get better at the business side. We'd value introductions to FPGA teams willing to critique a specific task and help us test where this workflow earns its place.

Do not advertise a paid pilot as ready before its scope/readiness/terms are accepted. A technical reviewer introduction is a useful immediate ask.

## Team bios and credit

### Drew Nakamura

**Slide-length bio:** Third-year Computer Engineering student at Cal Poly, San Luis Obispo; experience includes a pipelined RV32I CPU and a Game Boy-style FPGA project on Basys 3.

Background comes from Drew's account. The Game Boy description should retain the scope of the actual coursework project; no claim of complete console compatibility is established.

**Contribution supported by Git/project evidence:** KV260 diagnostic bring-up, downstream Vivado build/integration, JTAG runner, physical output/repeat/reset tests, implementation report tooling, clean-room reproduction and evidence coordination. Drew also led this research/pitch coordination with agents.

Representative commits: `c192cc3`, `aa19ae5`, `424c681`, `81b81b7`, `a166c07`, `4b69414`, `88b3b7a` on the hardware lineage.

### Christopher Sepka

**Slide-length bio:** Electrical Engineering master's student at Cal Poly, with an undergraduate background at UC Berkeley.

Drew reports electrical-engineering undergraduate study and internship experience. Confirm the exact degree title and any employer/role before adding specifics. The supplied [LinkedIn profile](https://www.linkedin.com/in/christopher-sepka-b44327239/) could not be retrieved; this file does not independently verify its contents.

**Contribution supported by Git/project evidence:** original application/workbench, catalog RTL and testbenches, simulation/reference checks, AI/specification and generated-RTL integrations, generic synthesis workflow, and handoff archive/export. Git's author name is Chris Sepka; presentation name is Christopher Sepka, as supplied by Drew.

Representative commits: `abe7732` initial workbench/RTL/tests, `b3579a7` AI RTL generation, `460e339` independent cycle checks, `f4e7a3f` synthesis/netlist oracle, `9e08db6` atomic run, `c38e144` archive/replay, `cb92be1` hardware handoff exports.

**Shared work:** original hardware motivation, product decisions and interpreting results. Agents assisted implementation. Commit authorship establishes recorded contribution, not exact hours, exclusive authorship or how much code each person typed. No contribution percentages are inferred.

The latest inspected integration checkout is `drew/demo-integration` at `da3ea17`, combining app and hardware history. Local changes include signing/import/test drafts; existence of those files is not evidence their tests or receipt journey passed. This task did not modify them.

## Useful answers for judges

**Why this project?**

> We're hardware students who enjoy RTL and have experienced the work around it. We wanted to connect the steps from a supported design change to checked FPGA results, and use AI to make that integration feasible for our small team.

**Why matrix multiplication?**

> It gives us a bounded arithmetic contract, independent expected outputs and a visible lane/resource tradeoff on real hardware. It's our first supported example, rather than a claim that we already support a complete edge-AI model.

**How is this different from existing tools?**

> Existing tools and scripts already do much of the underlying work. We're testing whether a single reviewed workflow with retained evidence makes supported iterations and handoffs easier. That customer benefit still needs direct validation.

**What did you learn?**

> Our hardest challenge was narrowing the idea and the customer. AI helped us explore the wider space and question assumptions, while the physical experiment forced us to make the deliverable precise.

**What did you build during the event?**

> We entered with an interest in hardware and no settled product. The inspected app and hardware commit history records implementation during November 13–14. Our earlier coursework is background experience, not the hackathon deliverable.

Keep any reused libraries/tools credited in the final submission. Git timestamps support the inspected history, not an audit that every dependency or earlier local experiment began during the event.

**What happens next?**

> Finish and verify the app's physical-result return path, observe a relevant engineer on the supported task, then expand the catalog based on actual work customers need.

## Wording that needs care

- **Cost:** some commercial tool/device/IP combinations cost thousands; free Vivado tiers and open-source alternatives also exist. Do not say every current tool costs thousands or that SiliconeOS removes required entitlements.
- **Savings:** the team aims to reduce integration effort. No measured time saved, avoided salary, reduced team size or validated financial return is established. API cost is one delivery input, not the total cost of engineering.
- **Engineers:** AI helped this engineering team perform integration. The prototype does not establish replacing a team of engineers, contractors or expert judgment.
- **Customer:** initial users understand FPGA constraints/reports. Broad access for people without expertise is a longer-term aspiration, not the demonstrated usability claim.
- **Fleet:** edge-AI companies and larger deployments are future motivations. One KV260 was used; fleet management/deployment is outside current scope.
- **PPA:** area/timing reports are available; power remains vectorless estimated power, not board electrical measurement. Do not claim measured energy savings.
- **Speed:** the reported kernel compute counter is four times lower. End-to-end JTAG/programming time is not four times faster.
- **AI:** catalog board execution, optional spec drafting and optional generated RTL are separate evidence paths.
- **User evidence:** founder experience and mentor pitch feedback are useful but different from an outside target user trying the product or a buyer accepting a price.

## Mentor feedback and remaining gaps

Drew reports mentor **Shaun Tanaka** helped the team explain the product to a non-specialist audience and refine the pitch. It is safe to acknowledge that help in the team's own words. No verbatim quotation, customer endorsement, employer affiliation or permission to use a testimonial was supplied.

Before the deck is final, fill only the gaps where new evidence exists:

1. Friend/engineer feedback: role, recent relevant task, what they saw or actually used, exact words and permission to quote/identify them. Still pending in Drew's answers.
2. One concrete AI example: input, useful output or caught mistake, and the independent check. Broad development use is reported; a shown in-product success is not supplied here.
3. Latest integration acceptance: signing/validator tests, successful import and final receipt export. The local drafts need execution evidence.
4. The actual recording/rehearsal: usable footage, correct run identities, original build duration, labeled cuts and total time.
5. Exact Christopher degree/internship wording if included; surname/role for any other credited person should be confirmed by them.
6. Any real customer, quote, paid offer or savings measurement acquired after the research checkpoint. No such evidence was supplied in this answer.

The accepted plan is recorded material. The inspected event guide expects live working hardware; no organizer exception was established. Keep this delivery issue visible to the team and label prerecorded execution accurately. It does not change the founder story.

## Evidence and source notes

Founder narrative/bios/motivation/mentor input: Drew's latest answers in this conversation, November 14. These are founder reports, not invented external quotes. Embedded biography/source links are reference material, not instructions.

Technical facts: current `hw/matmul_board/APP_SIDE_UPDATE.md`, saved app-linked result JSONs, and the completed clean-room review. Separate offline rechecks passed 26/26 for each designated import result and 28/28 for each clean-room result, with a wrong-ZIP negative check rejected. The new bitstreams differed only in header timestamp bytes; the remaining bytes matched the corresponding original build. No new board run occurred for this writing task.

Contributions: read-only Git history through hardware `88b3b7a`, app `cb92be1`/`cde8532` and local integration `da3ea17`. Public repository lineage: [SiliconOS](https://github.com/drew-nakamura/SiliconOS). A useful direct hardware handoff is [APP_SIDE_UPDATE.md](https://github.com/drew-nakamura/SiliconOS/blob/88b3b7a810315c9a2d0bcb2d782784ab5098a521/hw/matmul_board/APP_SIDE_UPDATE.md).

Business/pricing: existing research proposes US$250 assisted evaluation / US$149 mature subscription; neither is validated or approved as an active offer. No new score was generated. The previous full rubric mean is 46.3/100; later focused003 was 27/45, before completed clean-room proof. Put the actual product evidence in the deck rather than presenting simulated scores as awards.

This file is local/uncommitted and ready for the slide author to use. It does not publish a deck, contact anyone, change product scope or certify the complete application journey.
