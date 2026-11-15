> Pack note: Broad historical compilation. Pending clean-room/import wording was superseded by later verified evidence. [Start here](../START_HERE.md) · [Latest reviewed state](../CURRENT_REVIEWED_STATE.md).

# SiliconeOS: teammate research, decisions and evidence handoff

Snapshot: November 14, 2026, America/Los_Angeles. Prepared for Drew and Christopher. This file compiles the existing research and project records; it does not approve new product scope or claim unfinished work passed. Sources and prices reflect the November 14 research checkpoint, rather than a fresh supplier quote. Later hardware work may supersede this snapshot.

## 1. Where we are

SiliconeOS has a working, physically tested KV260 matrix-multiply core in two configurations. The strongest defensible demonstration is a supported configuration change, independent correctness checks, the resulting compute/resource tradeoff, and evidence identifying the source, build and physical result.

The product story is **“Reconfigure. Verify. Deploy. Keep the receipt.”** A receipt means a retained record binding requirements, source/configuration, tests, implementation artifacts and physical results. The arithmetic kernel alone is not the entire product.

Research supports a plausible first-user and commercial experiment. It does not establish customer demand, willingness to pay, engineering time saved or recurring revenue. Our latest full simulated judging average is **46.3/100**. A later focused customer-path review reached **12/20 from all three judges**.

**Focused-003 update (evening Nov 14):** Drew authorized a reduced research loop (Execution + Path only, /45; Pitch, Real problem, Creative AI, and outreach left out). Newer app-linked board JSONs were verified; public first-user places were sharpened (Matteo Vit/Starware, CERN FDF, qcrate, pccx). Hard mean **27/45** (same as the 15+12 baseline) — **plateau, Δ0**. Path mean fell slightly to **11.3/20** because free-stack counterevidence got stronger. Full write-up: `reports/SiliconeOS focused score 003.md`. Desk research stopped; further movement needs receipt-path and/or real user/budget evidence.

## 2. Accepted decisions and current boundaries

The accepted product baseline is **SPEC revision 8.2**, reconciled through decision D-025. Product spelling is **SiliconeOS**; the project folder/repository was named FabZero, and historical materials/code sometimes say SiliconOS.

- **User:** an FPGA/edge-hardware engineer who understands reports and iterates supported accelerator configurations. The persona remains unvalidated. Older camera-first and no-RTL-expertise customer assumptions are historical proposals.
- **Workload:** signed INT8 row-major square matrix multiplication with INT32 accumulation; software configurations N=8/16, LANES=1/4, selected at compile time. Physical comparison is N=8, one versus four lanes, using separate matching artifacts on KV260.
- **Primary route:** checked-in parameterized RTL catalog. AI can draft a reviewed supported specification. Optional generated RTL is an advanced path requiring its own independent gate, unchanged tests/oracle and trusted cycle checks. The physically tested core is catalog RTL, not evidence of successful AI-generated hardware.
- **Demonstration route:** local application, JTAG/xsdb and immutable result files. No Linux image or website upload endpoint for this slice. Use labeled recordings/screenshots of genuine execution; disclose cuts, reused builds and original duration. Target presentation is under four minutes.
- **Existing app:** plain HTML/CSS/JavaScript, Python standard-library backend, SQLite history, Icarus simulation, optional Groq/Yosys. Earlier framework suggestions are not instructions to rewrite it.
- **Excluded claims/features:** full inference, cameras/sensor integration, fleet/OTA, FP16, arbitrary RTL/board deployment, CPU/GPU superiority, measured power savings and ASIC signoff.

For the **future product pricing exercise**, Drew clarified that customers own their FPGA, sensors and accessories and specify what they have; SiliconeOS handles the Vivado/configuration/integration work. That direction describes the imagined product. It does not make those integrations current capabilities or expand the hackathon build automatically. Local customer-machine execution is our costing assumption, not a founder-approved deployment architecture.

## 3. What the technical evidence establishes

### Simulation, build and timing

Eight native XSIM 2025.2 directed lifecycle/AXI tests passed for N=8/16 × LANES=1/4, using unchanged RTL/testbenches and an explicit 1 ns/1 ps elaboration timescale. This is bounded directed evidence, separate from the app's complete Icarus regression or generated-RTL acceptance.

Vivado 2025.2 produced separate N=8 one-/four-lane routed builds for `xck26-sfvc784-2LV-c`, KV260 SOM board definition 1.4. Both met the supplied 10 ns timing constraint, with no failing setup/hold/pulse-width endpoints or reported DRC/routing violations in the reviewed artifacts. A reset path is intentionally excepted; this is not a claim that every possible path is timed.

| Reviewed implementation metric | One lane | Four lanes |
|---|---:|---:|
| Accelerator plus AXI wrapper LUTs | 354 | 3,612 |
| Accelerator plus AXI wrapper flip-flops | 318 | 2,470 |
| Accelerator plus AXI wrapper DSP / BRAM | 0 / 0 | 0 / 0 |
| Whole programmable-logic LUTs | 1,196 | 4,413 |
| Worst setup slack | 4.757 ns | 3.885 ns |
| Board-reported compute counter | 512 | 128 |
| Vectorless estimated total on-chip power | 2.723 W | 2.736 W |

The four-lane accelerator uses about **10.2× LUTs and 7.77× flip-flops** for one-quarter the reported compute count. A lane is not a mapped DSP; these multipliers map into LUTs. Keep accelerator, wrapper and whole-design area scopes explicit.

The configured PS clock is 99,999,001 Hz, not an independently measured frequency. About 5.12/1.28 microseconds follows from reported cycles and that configured clock. Summary Fmax values are slack-derived estimates, not tested clocks. JTAG programming/loading/polling/readback take seconds and do not show a fourfold end-to-end speedup.

### Why power is estimated even though we have PPA

We have implementation resource/timing reports and a Vivado power estimate. The power report uses **vectorless activity**, without a workload-derived SAIF activity file, and reports Medium confidence. It is an estimate of on-chip power, not a meter reading of board input power or measured energy per task. Accelerator-hierarchy dynamic estimates are 0.002/0.016 W; do not confuse these with total on-chip estimates. PPA does not imply all three quantities were electrically measured. Review report-generation code at `hw/tools/collect_reports.tcl` and the [AMD design-analysis documentation](https://docs.amd.com/r/2025.2-English/ug906-vivado-design-analysis/Report-Timing-Summary) for stage-specific reporting context.

### Physical results: initial and newer app-linked evidence

Initial board runs used A=identity and B[i]=i−32. Each configuration passed all 64 signed outputs on first run, repeat without reload and reset/reload, with counters 512 or 128 and reset counter/status clearing. The reviewed 384 value comparisons cover repeated execution of the **same input pair**, not 384 independent matrix cases. The earlier diagnostic `3x+1` bring-up is a separate platform baseline.

**Newer progress found during this handoff:** actual app-exported handoff ZIPs from `codex/demo-pipeline` revision `cb92be1` were accepted by the runner and executed on KV260. Both saved result JSON files say `pass` / `board_measured`, contain the parent run IDs, match the same input hash, and include all first/repeat/reset outputs and expected counters.

| Configuration | Physical result folder under `hw/matmul_board/results/` | App parent run |
|---|---|---|
| N8 / L1 | `20261115T011930Z_n8_l1` | `6bccf63e-f83a-4e12-88e6-78b20d120b65` |
| N8 / L4 | `20261115T012007Z_n8_l4` | `3abe54e6-25d2-4eb7-90bf-dd3b39f3a4e9` |

These recorded at 17:20:02 and 17:20:32 Pacific on November 14; UTC folder names are November 15. Outputs span −28,735 to 25,995. The hardware owner records independently checking all outputs against the ZIP and reference arithmetic, input/source/output hashes, identity/configuration and repeat/reset behavior. This compilation directly reread the result JSONs; it did not rerun board execution or independently repeat that whole checker.

**Important remaining boundary:** these app-linked runs reused matching pinned bitstreams. They establish source-byte compatibility and parent-linked execution, but not a fresh build made from each specific ZIP. The owner's new independent product-fit checker correctly rejects the earlier run for missing “manifest records this ZIP” and “Vivado used ZIP bytes” evidence. A clean-room fresh-build test was running at the latest checkpoint; no successful completion is established here. App signing/import and final receipt export also remain unverified.

## 4. Current integration decisions and ownership

The hardware owner's latest record supersedes older “parent ZIP missing” notes for the two received runs. Drew accepted **Drew as hardware merge owner and Christopher as application integration owner**, plus the manual first end-to-end path: **app ZIP → hardware runner → app-side signing adapter → app import**. App side owns the signing/import adapter.

Current agreements/deltas recorded by the hardware owner:

- Input identity uses SHA256 of raw bytes `x & 255` for A followed by B, not serialized input JSON. The original identity/ramp result folders predate this rule.
- Result source maps preserve the parent map, including `tb.sv`; wrapper identity is separate. The runner checks ZIP entries, parameters, independently expected outputs/cycles and RTL/build compatibility before deployment.
- App-side HMAC signing uses a sorted-key compact JSON envelope. Configuration variable names are `SILICONOS_RUNNER_KEY` and `SILICONOS_RUNNER_KEY_ID`; this document contains no key values. The exact pushed adapter/validator schema still needs receiver verification.
- Windows CRLF conversion can change RTL hashes. LF-normalized source and byte-preserving checkout rules matter; do not bypass a hash mismatch.
- The runner now supports `--handoff` and a read-only board-presence `--check`. The owner reports **21 offline tests passing**, including tampered ZIP/source, bad expected values and mismatches. This compilation did not rerun those tests.

Publication checkpoints recorded by the hardware owner: `424c681` initial hardware data; `81b81b7` handoff/check support; `a166c07` two app-linked result folders. Latest local drew-branch HEAD observed here is `4b69414`, adding ZIP-driven build support; owner records it as **not pushed**. Remote publication was not freshly verified by this compilation. Do not assume newer local files are available to the teammate just because a branch exists.

The clean-room rebuild is separate ongoing hardware-owner work, not a research-agent process. Obtain its latest outcome before declaring the fresh ZIP-to-build path complete. Older shared README/STATUS/spec handoff and hardware README contain stale progress sentences; use the specific current artifacts and owner log for newer evidence.

## 5. Research findings and claims to use carefully

**Relevant problem evidence:** [Starware's first-person FPGA/DevOps account](https://www.starwaredesign.com/fpga-meets-devops-introduction/) describes source-tag/bitstream mismatch, environment reproduction and release bottlenecks. It is a concrete account of pain, not a prevalence study or proof SiliconeOS solves it. [Wouter van Verre's Tcl/Git workflow](https://www.electrickoala.dev/posts/zynq-7000-command-line/) demonstrates a practical existing alternative.

**Competition includes free engineering workflows.** [fpga-vbs](https://github.com/missinglinkelectronics/fpga-vbs) handles variants/flavors, reports and Git identity. [FuseSoC](https://github.com/olofk/fusesoc), [Edalize](https://edalize.readthedocs.io/en/latest/edam/api.html) and [Vivado project archives](https://docs.amd.com/r/2025.2-English/ug835-vivado-tcl-commands/archive_project) already cover substantial build/metadata/archive work. SiliconeOS must prove a more useful complete workflow; “nobody preserves FPGA provenance” is indefensible. AMD also provides existing [BLAS libraries](https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/vitis/vitis-libraries/vitis-blas.html).

**Adjacent traceability cases:** NI's supplier-hosted [Lunar Energy case](https://www.ni.com/en/solutions/energy/case-studies/scaling-power-conversion-test-startup-speed.html) and [Danfoss HIL/Python case](https://www.ni.com/en/solutions/transportation/case-studies/improve-test-coverage-documentation-and-traceability-by-integrating-python-automation-with-hil-testing.html) support variant/test-documentation relevance in other settings. They are not SiliconeOS customers or validation of our small matrix catalog.

**Original pitch claims we corrected or excluded:**

- Siemens' [2024 FPGA verification study summary](https://resources.sw.siemens.com/en-US/white-paper-2024-wilson-research-group-fpga-functional-verification-trend-report/) reports 87% of surveyed FPGA projects with nontrivial production bug escapes; its [2022 study discussion](https://blogs.sw.siemens.com/verificationhorizons/2022/10/24/part-2-the-2022-wilson-research-group-functional-verification-study/) reports 70% behind schedule. Attribute year/sample and avoid claiming provenance caused those outcomes or that we prevent them. The precise 47% debug claim was not verified sufficiently for use.
- AMD's [2022 robotics-kit comparisons](https://www.amd.com/en/newsroom/press-releases/2022-5-17-amd-robotics-starter-kit-kick-starts-the-intellige.html) concern specific other workloads/systems. Their performance, latency, productivity or development-time ratios are not SiliconeOS benchmarks.
- Amazon's [millionth-robot announcement](https://www.aboutamazon.com/news/operations/amazon-million-robots-ai-foundation-model) is a June 2025 milestone, not a current fleet count or evidence of demand for us.
- Warehouse/FPGA forecasts are not our reachable market. Salary arithmetic and invented hours saved are not measured ROI. The earlier US$8,800–14,400 saving example depended on assumed hours/rates and should not be pitched as a result.

The supplied `siliconos_pitch_deck_research.md` was preserved as source material and audited. Its embedded “verified” labels and suggested instructions were treated as claims to inspect, not authority or evidence.

## 6. Customer path: proposal and actual evidence

Proposed first user: a small FPGA team's engineer comparing supported KV260 integer variants and handing evidence to another engineer. Proposed buyer: the engineering/hardware lead, consultancy owner or funded lab lead who actually controls evaluation spending. Trigger: deciding which source/configuration/build/result belongs to a review or handoff.

The switching hypothesis is less manual reconstruction and explanation than existing Git/Tcl/CI/report workflows. Reject it if current scripts are sufficient, our catalog is irrelevant, or setup/support costs outweigh the benefit. Need for traceability does not automatically mean someone will buy an 8×8 matrix example.

Proposed entry: a free 20-minute workflow/evidence review, then—after readiness and founder approval—a **US$250 one-time assisted N8 one-/four-lane evaluation** using existing supported artifacts and agreed non-confidential inputs. This is a test price, not an accepted offer or market quote. Manual assistance must be disclosed. No new board port, arbitrary kernel, certification, measured-energy claim or performance guarantee is included. Two/four active delivery hours imply US$125/US$62.50 per hour before costs, purely arithmetic.

Researched acquisition routes, with no implication of interest:

1. [element14 FPGA Group/Kria workshop discussion](https://community.element14.com/technologies/fpga-group/f/forum/55068/seeking-feedback-on-your-preference-for-an-amd-kria-workshop): relevant community; seek a current moderator-compliant research route rather than promoting in an old thread.
2. [LogicTronix](https://logictronix.com/fpga-design-services/) and [hema](https://www.hema.de/loesungen/amd-fpga-plattform): named Kria experts, potential expert/referral contacts and competitors.
3. [AISeQ Lab KV260 demos](https://github.com/AISeQLab/RESEARCH---Demos_on_KV260_FPGA) and [lab site](https://aiseqlab.github.io/): potential evaluator route, not a known buyer.
4. AMD forum referral through its [K26 page](https://www.amd.com/en/products/system-on-modules/kria/k26.html): fallback; direct forum access/rules were not verified.

**Actual outreach, replies, observed target users, paid quotes and payments: all zero in this research.** The first-ten activity queue has three organization requests and seven unfilled community slots, not ten identified prospects. No messages were sent.

## 7. Future monthly price and credit-cost model

Recommendation to test **US$149 per engineer/month**, month-to-month, research band **US$99–199**, for a mature reliable product with tested supported board/interface/accessory combinations. Proposed boundaries: one creating engineer, one concurrent local pipeline, free read-only evidence recipients, and **US$30 provider-cost AI allowance**. New board/sensor qualification is separately scoped/quoted engineering. These features, boundaries and prices are proposals, not implemented controls or accepted scope.

A possible later **US$499/month five-editor workspace with US$100 pooled provider-cost allowance** requires real team functionality and validated support economics. One-off setup users may need a service rather than a subscription. The earlier US$250 assisted prototype offer and US$149 recurring mature-software proposal have different deliverables and billing units.

Adjacent price references checked November 14: [GitHub Copilot](https://docs.github.com/en/copilot/get-started/plans) Business US$19 / Enterprise US$39 per seat/month; [AllSpice](https://allspice.io/plans) Enterprise Core starts US$34,800/year for 5+ designers, equivalent to US$2,900/month on annual terms, not a cancellable monthly/per-seat quote. Inspected [ChipAgents](https://chipagents.ai/ic-star) and [Cadence ChipStack](https://newsroom.cadence.com/press-releases/press-release-details/2026/Cadence-Expands-ChipStack-AI-Super-Agent-with-a-New-Agent-for-RTL-Generation-and-Early-PPA-Optimization/default.aspx) materials had no numerical public subscription price. These are context, not proof a customer will pay us US$149.

### API assumptions and costs

Saved standard uncached US-dollar rates per million input/output tokens: Sol 2/10; Terra 1/5; Astra 10/50; Claude Sonnet 5.5 2/10; Opus 5.5 4/20; Groq GPT-OSS120b 0.15/0.60. Sources: [OpenAI pricing](https://developers.openai.com/api/docs/pricing.md), [Terra](https://developers.openai.com/api/docs/models/gpt-6.1-terra.md), [Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing), [Groq model](https://console.groq.com/docs/model/openai/gpt-oss-120b). Recheck before committing spend. Cheaper equal-token footprints do not establish equal capability.

The model includes reasoning/retries/repair output and assumes no caching discount or paid hosted tools. Each request stays below applicable long-context surcharges; cumulative tokens across many calls are not a single oversized prompt. [Reasoning can consume billed output](https://developers.openai.com/api/docs/guides/reasoning) even without a useful result.

| Unmeasured attempt class | Cumulative input / output | Calls | Sol API cost | Terra API cost |
|---|---|---:|---:|---:|
| Established template | 50k / 10k | 4 | $0.20 | $0.10 |
| Integration, including repairs | 1M / 200k | 20 | $4.00 | $2.00 |
| Stress case, no success guarantee | 10M / 2M | 100 | $40.00 | $20.00 |

| Illustrative month | Sol | Terra, same token footprint |
|---|---:|---:|
| 8 template + 2 integration attempts | $9.60 | $4.80 |
| 16 template + 4 integration attempts | $19.20 | $9.60 |
| 40 template + 10 integration attempts | $48.00 | $24.00 |
| 20 integration attempts | $80.00 | $40.00 |
| Default 16+4, plus 2 stress attempts | $99.20 | $49.60 |

These are planning scenarios, not measured typical usage. Local compilation itself uses no model tokens; sending logs to a model does. Define **one internal AI-cost unit = US$0.10 provider-rated model/paid-tool spend**: US$30 allowance = 300 units; default US$19.20 = 192. This is not a provider credit, retail top-up price or conversion from desktop Codex credits. BYOK shifts the provider bill to the customer.

Meter failures, retries and reasoning. Stop at a budget boundary or obtain authorized additional spend; never weaken independent checks to make a job pass. Measure **cost per accepted result**, including unsuccessful attempts.

### Delivery cost and local versus hosted builds

Default illustration at US$149 revenue: API 19.20 + shared backend/storage allocation 5 + 15 support minutes at an assumed US$60/hour = 15 + assumed 3% payment allowance 4.47 = **US$43.67 direct delivery cost**. Contribution is **US$105.33 / 70.7%**, before R&D, acquisition, tax, compliance, fixed overhead and other salaries. It is not net profit. Full US$30 model allowance gives US$54.47 direct cost / 63.4% contribution; one support hour instead of 15 minutes gives US$88.67 / 40.5%. Support assumptions and usage remain unmeasured.

For a customer-local Vivado runner, our hosted build CPU charge is US$0; the customer still bears capacity/electricity and required tool/IP entitlements. Current [AMD licensing](https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/vivado/vivado-licensing-options.html) supports Linux/Windows and Kria in free BASIC; older Windows-only research was corrected. CORE's listed US$1,200 node-locked / US$1,800 floating annual licenses apply only where needed; IP and hosted rights need separate review. A board/accessory name alone is not validated electrical, pin, clock, protocol or driver integration; see [AMD board flow](https://docs.amd.com/r/2025.2-English/ug994-vivado-ip-subsystems/Using-the-Platform-Board-Flow-in-IP-Integrator).

If we host compilation, the saved official Azure East US Linux rates are E8s_v5 US$0.504/hour (8 vCPU/64 GiB), E16s_v5 US$1.008/hour (16 vCPU/128 GiB). An assumed 20 requests × 2 variants × 1 hour × 1.25 attempts = 50 worker-hours costs **US$25.20 / US$50.40 CPU only**, plus disks, idle time, egress, licensing and operations. Keeping an E8 worker allocated 730 hours costs US$367.92 CPU alone. No hosted benchmark was run; the real customer board still needs validation. Sources: [Microsoft retail rate query](https://prices.azure.com/api/retail/prices?%24filter=serviceName%20eq%20%27Virtual%20Machines%27%20and%20armRegionName%20eq%20%27eastus%27%20and%20%28armSkuName%20eq%20%27Standard_E8s_v5%27%20or%20armSkuName%20eq%20%27Standard_E16s_v5%27%29&currencyCode=USD), [VM specifications](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/memory-optimized/esv5-series?tabs=sizebasic).

## 8. Judging history and honest presentation

The [published hackathon rubric](https://cpvc-ai-hackathon-guide.vercel.app/#judging) weights execution/design 25, real problem/user 25, path to customers 20, pitch/demo 15 and creative AI 15. Research used a saved November 14 guide snapshot; organizer updates could supersede it.

| Review checkpoint | Result | Meaning |
|---|---|---|
| Full round 001 | All three 28/100 | Earlier limited evidence |
| Full round 002 | 45, 49, 45; mean 46.3/100 | Hardware proof and fuller source context improved readiness |
| Later customer-path-only iteration 001 | All three 12/20 | Plausible untested model; requested threshold reached |
| Focused-003 (Execution + Path only) | 26, 27, 28; mean **27/45** (Δ0) | App-linked parents verified; desk Path research plateaued; see focused report |

Round002 mean rows were execution 15/25, problem/user 10/25, customer path 9.3/20, pitch/demo 6/15 and AI 6/15. The later 12/20 review changed only the customer-path assessment. Focused-003 rescored Execution+Path only after Drew excluded Pitch, Real problem, Creative AI, and outreach from the research loop; **no new whole-product /100 score was issued**. Focused-003 means: Execution **15.7/25**, Path **11.3/20**. These are AI judge assessments, not official awards or probabilities.

The review process froze a shared claim/evidence packet, obtained independent technical, customer/business and pitch/integrity challenges, retained every score and reported mean/range. Earlier packets remain unchanged. Focused-003 stopped on plateau. More desk research can improve an argument but cannot replace an actual user observation, completed receipt path or product demonstration.

Drew chose recordings instead of a live demo (synthesis ~40 minutes). The inspected guide expects a live working-hardware demonstration; this remains an unresolved presentation/rubric conflict. No organizer exception or automatic disqualification was established. Keep the founder's route and disclose prerecorded material accurately; do not invent compliance. No complete process recording, timed rehearsal, cold-user test or actual useful provider interaction was reviewed in these rounds.

## 9. Pick up here (after focused-003 plateau)

Desk-only Path/Execution research has plateaued. Prefer actions before another score:

1. **Obtain the hardware owner's fresh clean-room outcome.** Verify each ZIP → extracted RTL → Vivado manifest/reports/bitstream → result binding. App-linked reused-bitstream runs are a distinct, already-documented stage.
2. **Complete and independently check the app return path.** Verify signing adapter/validator, null/failed-result handling, parent linkage, manifest/report identity, stale labels, replay/idempotency and receipt export. Use both real parent ZIPs/results.
3. **Capture the genuine product journey and rehearse under four minutes** (presentation work; was out of focused-003). Show requirement, lane change, checks, resource tradeoff and receipt. Label stage, cached build, time compression and run identities.
4. **Observe one qualified engineer with a recent relevant task.** Named public candidates now include Matteo Vit/Starware, CERN FDF attendees, element14, LogicTronix, hema, AISeQ — still zero contacts. Compare evidence against their method; test the exact US$250 offer after readiness. Interest is not payment.
5. **Show useful actual AI behavior.** Retain a real reviewed drafting/correction interaction and deterministic validation. Do not imply catalog hardware was AI-generated.
6. **Measure commercial inputs.** Tokens/retries/cost per accepted result, support effort, repeat use, exact price responses. Revisit US$149/allowances if usage breaks the model.
7. **Only then freeze a new review packet and score once.** Preserve earlier rounds; do not silently substitute proposals for results.

## 10. Source/artifact index for the teammate

This Markdown is self-contained for decisions, findings and numerical assumptions. Raw evidence is separate. Paths below are repository/worktree-relative identifiers, not promises that every file has been committed or transferred.

- Accepted contract: `docs/spec/SPEC.md`, `DECISIONS.md`, `HANDOFF.md`, `BOARD_RESULT_FILE.md`, `DEMO_PRODUCT_AND_FPGA_SPEC.md`, `UPSTREAM.md`; review `docs/spec/reviews/round-010.md`.
- Simulation: `docs/verification/matmul-xsim-2026-11-14/`.
- Hardware: `hw/matmul_board/README.md`, `INTEGRATION_QUESTIONS.md`, `FPGA_INTEGRATION_RESPONSE.md`, `build/n8_l1/`, `build/n8_l4/`, `build/compare_n8/`, `results/` and `tests/product_fit_check.py`. The latter checker/new clean-room changes may be local only.
- Initial physical folders: `20261115T001327Z_n8_l1` and `20261115T001604Z_n8_l4`. New app-linked folders appear in section 3.
- Research reports: `reports/SiliconeOS pitch claim review round 001.md`, `SiliconeOS recorded demo evidence research.md`, `SiliconeOS pitch claim review round 002.md`, `SiliconeOS customer path iteration 001.md`, `SiliconeOS subscription pricing and costs.md`, **`SiliconeOS focused score 003.md`** (latest research findings + /45 plateau). The earlier `FabZero customers and RTL value.md` is historical context, not current accepted customer scope.
- Detailed notes: `research_notes/SiliconeOS pitch claim review/` holds the original attached research, source ledgers, data review, recording checklist, frozen packets and individual judge verdicts, including `focused-003-*`. `research_notes/SiliconeOS subscription pricing and costs/` holds comparable/model/build source notes, `cost-model.json` and verification records.

Research files above currently live locally in the isolated research worktree and are **uncommitted/unpublished**. This handoff does not send or publish them. The pricing calculator previously passed 53 offline JavaScript assertions and syntax/artifact checks; browser visual QA was not performed. This compilation adds no new hardware, app or customer validation.

Source identities for matching hardware: `matmul.sv` SHA256 `f81498d1fdb9a73a32e7f70a5d55c09b6198d2f03f00ab27d9099a63d82f418c`; wrapper `matmul_axi.sv` SHA256 `26d5eca5ea16bf81336cece4f9a76617cfaf5444cc4b92a734a656cff4dc080c`. Initial/reused L1 bitstream `63c19180aa6ea09513a2b5ec4fb8a2966af64161de3c400614f42cc191909bfc`; L4 `500cc93bf500fc0b3f8fbe19f727ecf7493f97f8886a31bb709a8934155ce770`. Fresh rebuilt artifacts require their own identities and checks.
