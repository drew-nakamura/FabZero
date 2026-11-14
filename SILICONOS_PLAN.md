# SiliconOS: decision and execution brief

Prepared Friday, November 13, 2026, approximately 6:10 PM Pacific. Research is a point-in-time review of primary documentation, not hands-on validation of competitor products. No product code, hardware builds, customer interviews, or measurements have been completed in this task. The repository initially contained only README.md; initial commit was Friday 17:33 Pacific.

**Verdict:** Build a narrowly scoped experiment: an open-source, AI-assisted architecture comparison workbench for developers already targeting AMD Kria. Do not pitch a general autonomous chip designer or a validated venture business. **Highest-risk assumption:** we can produce and load a compatible custom KV260 bitstream tonight. **First action:** establish board SSH access and identify an available, working FPGA build host before building the interface.

## 1. Strategic assessment

Recommended positioning: **“Choose an accelerator architecture using evidence from your own board.”** The first user is an embedded/FPGA engineer evaluating a small integer compute kernel under a resource budget. Beginners can enter an idea, but are not the initial commercial customer. A camera idea becomes a supported kernel experiment only with explicit user acknowledgement; the product must not imply it has built object recognition.

The broad vision is crowded: hardware generation, design-space exploration, and AI-assisted engineering already exist. The proposed advantage is integration: preserve user constraints, enumerate a small reproducible space, run candidates on a specific board, separate transfer time from compute time, and attach implementation provenance to the recommendation. Whether this saves enough engineering time to buy is unvalidated.

| Candidate business | Weekend feasibility | Commercial assessment | Decision |
|---|---|---|---|
| General AI chip architect | Poor | Major incumbents and substantial correctness/integration burden | Reject as MVP |
| Neural-network-to-FPGA compiler | Moderate with existing stacks | Strong FINN/hls4ml/Vitis AI alternatives | Integrate later rather than compete head-on |
| FPGA deployment/support service | Relatively practical | Concrete work, but services revenue may not recur or scale | Possible initial paid engagement |
| GPU inference cost optimizer | Different hardware path | Loses this team's FPGA advantage; market not researched here | Do not pivot this weekend |
| Board-backed kernel architecture workbench | Conditional on hardware bring-up | Narrow, testable time-saving proposition; weak moat today | Selected |

The hackathon is a product and customer competition. Spend at least as much attention on a real user's successful workflow as on demonstrating more multipliers. Novel optimization science is not required; claiming it without evidence hurts credibility.

## 2. Competitive research

Legend: **D** = documented capability; **N** = not advertised in the reviewed sources, not proof of absence; **U** = unverified. These sources establish offerings, not independent performance superiority. Open-source repositories can still require proprietary FPGA tools.

| Tool and primary evidence | Open source / commercial model | Hardware generation and search | Deployment, benchmark, feedback | Natural-language front end; limitation / implication |
|---|---|---|---|---|
| [ChipFoundry SoC Builder](https://chipfoundry.io/soc-builder) | Commercial design/fabrication service; builder source U | D guided IP/SoC configuration and area/I/O feedback; general automated DSE U | Fabrication service D; KV260 execution N; measured FPGA loop U | AI-powered service D, form-driven interface D; free-form NL U. Avoid “no expertise needed” as unique differentiation |
| [AMD FINN](https://github.com/Xilinx/finn) | Open BSD-3-Clause research framework | D customized quantized-network dataflow generation; exploration is already part of its purpose | FPGA examples D; automated feedback coverage depends on flow | NL N. Documented Docker-only compiler support and quantized-network focus; potential future backend |
| [hls4ml](https://github.com/fastmachinelearning/hls4ml), [configuration](https://fastmachinelearning.org/hls4ml/api/CONFIGURATION.html) | Open project; backend tools have separate terms | D HLS generation, precision/reuse/resource-latency controls; automated search coverage U | FPGA-oriented generation D; board deployment depends on backend/project | NL N. Model/input/backend constraints matter; not an arbitrary hardware generator |
| [Gemmini](https://github.com/ucb-bar/gemmini) | Open research generator | D configurable systolic arrays, scratchpad, dataflows, full-system exploration | D simulator benchmarks/counters and FireSim; direct KV260 port U | NL N. Chipyard/RISC-V/RoCC integration is a materially different starting point from our ARM board |
| [Timeloop](https://timeloop.csail.mit.edu/) | Open research framework | D tensor mapping and architecture exploration/optimization | D analytical performance/data-movement estimates; self-contained KV260 hardware loop N | NL N. Models and mapping search are already sophisticated; do not claim first architecture optimizer |
| [Accelergy](https://timeloop.csail.mit.edu/) | Open research framework | D component energy/area modeling within exploration workflows | Estimated energy/area D; board power measurement loop N | NL N. Technology models need calibration; estimates are not measured FPGA power |
| [Apache TVM](https://github.com/apache/tvm) | Open Apache project | D ML compilation and optimization; arbitrary accelerator RTL generation N | Target-specific compilation/runtime ecosystem D; this KV260 flow U | NL N. Compiler alternative/complement, not evidence of an empty market |
| [AMD Vitis AI](https://github.com/Xilinx/Vitis-AI) | Public stack; component licenses and hardware/tool terms vary | D AI inference development stack; arbitrary kernel architecture search U | D AMD deployment ecosystem, platform/version specific | NL N. Existing inference customers should first evaluate vendor tooling |
| [OpenROAD flow scripts](https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts) | Open RTL-to-GDS flow | D ASIC physical implementation; accelerator architecture generation N | ASIC flow metrics D; KV260 deployment outside documented scope | NL N. Not a replacement for Vivado or evidence that FPGA execution is unique |
| [Synopsys Platform Architect](https://www.synopsys.com/verification/virtual-prototyping/platform-architect.html) | Commercial; price not verified | D SystemC architecture, memory/interconnect, power/performance exploration and sweeps | D modeled evaluation; physical KV260 loop U | NL U. Direct competitor to broad architecture-exploration positioning |
| [Cadence Cerebrus](https://www.cadence.com/en_US/home/tools/digital-design-and-signoff/soc-implementation-and-floorplanning/cerebrus-intelligent-chip-explorer.html) | Commercial; price not verified | D ML-driven implementation optimization | D vendor-published customer results; custom FPGA loop U | NL U. Automated optimization is not a novel category |
| [ChipAgents](https://chipagents.ai/papers-and-guides/ic-star-technical-overview), [enterprise deployment](https://chipagents.ai/trust-center) | Commercial AI engineering platform; full source availability U | Advertises RTL design and PPA-aware optimization; exact architecture-search breadth U | Advertises engineering tool integration; physical KV260 closed-loop U | Agentic assistance D; exact NL-to-board flow U. Strong threat to any generic RTL assistant positioning |

No reviewed competitor's silence proves a missing feature. Benchmarking and hardware feedback also exist in research ecosystems; our hypothesis is less integration work for a narrow developer segment. An engineer should choose SiliconOS only if it gets a defensible, reproducible answer faster than their existing scripts. For network deployment, FINN/hls4ml may remain the better tool. For a new RISC-V accelerator SoC, Gemmini is more ambitious and mature than our weekend kernel.

Reference projects: [NVDLA](https://github.com/nvdla/hw) supplies accelerator RTL/C model/testbench but is too large an integration target for this weekend; [MLPerf Inference](https://github.com/mlcommons/inference) defines inference workloads and reference implementations, not certification for a toy GEMM. [PULP](https://pulp-platform.org/) and [OpenHW](https://openhwfoundation.org/projects/) are valuable processor/platform ecosystems, but a new processor subsystem is outside scope. Do not call our microbenchmark MLPerf or compare its numbers with published inference scores.

## 3. Customer and market analysis

Initial hypothesis: small embedded compute teams and FPGA consultancies already using Zynq/Kria, repeatedly comparing accelerator configurations. User: FPGA/embedded engineer. Champion: technical lead. Buyer: engineering manager or consultancy owner. Enterprise procurement also involves IP/security review and tool-license compatibility.

The costly job is turning an algorithm or changed resource requirement into a correct, deployable candidate and a trusted comparison. Existing substitutes are vendor tools, specialist engineers, internal scripts, and open generators. Switching costs include known-good deployment flows, private RTL, regression suites, licenses, and confidence in existing measurements. Offer an additive exportable report and local runner, rather than demand replacement of their toolchain.

Evidence levels:

- **Documented engineering problem:** Timeloop describes the coupled architecture/mapping search problem; commercial architecture products address performance/power exploration. FINN documents complex tool dependencies. These establish engineering work, not customers wanting our product.
- **Existing customers in the category:** Synopsys publishes a Ricoh testimonial for Platform Architect; Cadence publishes customer material including Broadcom. These are vendor-published examples, not SiliconOS prospects or independent validation. Sources: [Synopsys](https://www.synopsys.com/verification/virtual-prototyping/platform-architect.html), [Cadence](https://www.cadence.com/en_US/home/tools/digital-design-and-signoff/soc-implementation-and-floorplanning/cerebrus-intelligent-chip-explorer.html).
- **Current spending:** commercial products and engineering effort exist, but actual license prices, project labor costs, and contract values were not verified. Do not put invented EDA spending in the pitch.
- **Underserved segment:** hypothesis only. We have no direct customer complaint interviews yet. Obtain their last project's elapsed time, active engineering hours, failed experiments, and current alternatives.
- **Validated commercial demand:** none yet. A pilot request is stronger than a signup; a budget owner agreeing a paid scope is stronger again.

Weekend objective, not forecast: five qualified conversations, three observed users completing a spec-to-comparison workflow, two willing to share a non-confidential workload and schedule follow-up. A second session without coaching is especially valuable. Record refusals and reasons, not just favorable quotes.

## 4. KV260 technical plan

AMD documents 256,200 system logic cells, 117,120 LUTs, 234,240 flip-flops, 144 36-Kb BRAMs (about 5.1 Mb), 64 288-Kb UltraRAM blocks, and 1,248 DSP slices. System logic cells are not LUTs; these are whole-device resources, not a promise of all resources available to our kernel. [K26 DS987](https://docs.amd.com/r/en-US/ds987-k26-som/Programmable-Logic).

Carrier interfaces include gigabit Ethernet, USB, microSD, UART/JTAG, camera connections, display outputs, and Pmod. We need Ethernet and UART/JTAG only. The SOM's transceiver capabilities do not imply every interface is exposed on this carrier. [KV260 product brief](https://www.amd.com/content/dam/amd/en/documents/products/som/kria/k26/kv260-product-brief.pdf).

**Selected path:** parameterized RTL in Vivado, ARM-to-PL AXI-Lite control, memory-mapped operand/result storage using AXI BRAM Controller, a hardware cycle counter, and a Python runner over SSH. Reuse a compatible public board/platform template with attribution; build our kernel during the event. Use an already working PYNQ installation as the memory access/programming adapter if present. Otherwise use the installed Linux FPGA-manager/xmutil flow with matching overlay and a narrow UIO mapping. Do not install a second deployment stack just for aesthetics.

The primary deliverable is a pair of prebuilt full bitstreams (1 and 4 lanes); 8 and 16 are stretch candidates. Full reprogramming is visible and serialized. Runtime changes to scheduling within a bitstream are allowed, but lane disabling does not reduce allocated LUT/DSP/BRAM resources.

| Approach | Decision and reason |
|---|---|
| Vivado RTL | Selected for explicit counter, schedule, and small predictable kernel; AXI integration remains real work |
| Vitis HLS | Use only if the team already has a working HLS-to-board flow; C simulation alone does not solve deployment |
| AXI-Lite | Control/status and small transfers; simple, but cannot support credible large sustained bandwidth claims |
| Shared BRAM | Selected scratchpad; PS writes while idle, accelerator owns it while busy; avoids DDR cache-coherency work |
| AXI DMA | Defer unless already working; adds buffer allocation/coherency, stream framing and driver integration |
| PYNQ | Compatible in documented Kria configurations; conditional adapter, not automatic compatibility with any image |
| Precompiled bitstreams | Selected for live execution after building/validating during the event; search unbuilt configurations must say “build required” |
| Partial dynamic reconfiguration | Exclude; unnecessary shell/partition integration. Full image swapping is sufficient |
| Runtime-configurable lanes | Useful scheduling demonstration, but cannot claim area or allocated-DSP reduction |

Sources: [AXI BRAM Controller PG078](https://docs.amd.com/api/khub/documents/B6Uh5gbO0aGleXW3kIcXTA/content), [AXI DMA modes](https://docs.amd.com/r/en-US/pg021_axi_dma/Field-Descriptions), [Kria-PYNQ](https://github.com/Xilinx/Kria-PYNQ).

**Version policy:** pin a compatible set, not “latest everything.” AMD's documented custom-app recipe explicitly assumes 2022.1 tools. Kria-PYNQ documents Ubuntu 22.04 with boot firmware compatibility requirements; AMD also lists Ubuntu 24.04, PetaLinux, and Yocto support. That does not prove every PYNQ/Vitis/firmware combination works. If no existing flow is available, use the documented 2022.1 reference path as a compatibility starting point on a supported build host; confirm access and licenses before committing installation time. The exact version tuple remains blocked on the team's inventory. [Development overview](https://xilinx.github.io/kria-apps-docs/creating_applications/2022.1/build/html/docs/overview.html), [Ubuntu support](https://xilinx.github.io/kria-apps-docs/ubuntu_support.html).

Integration steps:

1. Inventory board model, OS, kernel, boot firmware, loaded applications, PYNQ/XRT versions if installed, and build-host OS/tool versions. Preserve the working boot image. The current workspace is on a Mac; do not assume it is a suitable native Vivado build host.
2. Prove a known public overlay loads, then prove a newly built identity/scratch-register block can be written and read. A stock example proves infrastructure, not our accelerator.
3. In Vivado select the verified KV260 board/part; create PS, fabric clock/reset, SmartConnect, AXI-Lite CSR slave, AXI BRAM Controller and memory. Start at a 100 MHz target, subject to implementation timing.
4. Use memory-mapped scratchpad staging plus explicitly banked local operand memories for parallel compute. A dual-port BRAM does not feed 16 independent operand pairs per cycle automatically. Count staging/preload time separately; include it in job latency.
5. Provide version/identity, start, busy, sticky done/error, size, schedule mode, repeat count, cycle count, and result checksum registers. Define reset/clear behavior and a timeout. Snapshot multiword counters coherently.
6. Simulate signed INT8 multiply and INT32 accumulation; then build baseline and 4-lane variants. Save timing/utilization reports and hashes. Reject timing violations before physical comparisons.
7. Package deployment artifacts for the chosen loader. PYNQ normally needs matching bitstream/metadata and any required device-tree overlay. The documented xmutil application packaging includes bitstream conversion, DTBO and shell metadata; XRT flows additionally need XCLBIN metadata. Do not mix an XRT platform recipe with an unrelated raw RTL driver. [AMD custom firmware recipe](https://xilinx.github.io/kria-apps-docs/kv260/2022.1/build/html/docs/generating_custom_firmware.html).
8. Upload via SSH/SCP; load a known manifest ID, verify identity, write input, start, wait with timeout, read output/counter, compare every element. Exact MMIO addresses come from the exported address map, never a guessed constant. [AMD deployment example](https://xilinx.github.io/kria-apps-docs/kv260/2022.1/build/html/docs/bist/docs/run.html).
9. Keep the board on a private network. A single runner serializes jobs and accepts only validated spec fields and known artifact IDs, not arbitrary shell commands or user RTL. The public app queues jobs; a local worker pulls them and returns results. No public SSH exposure is needed.

Power: AMD documents an INA260 at I2C address 0x40 on VCC_SOM and platformstats support in its images. This is SOM-rail telemetry, not isolated accelerator power. Treat energy measurement as stretch: repeat workloads long enough for sensor sampling, record idle and loaded rail power, sampling interval and temperature. No “low power” claim from DSP count alone. [AMD power specifications](https://docs.amd.com/r/en-US/ds986-kv260-starter-kit/Power-and-Electrical).

## 5. Workload selection

| Workload | Weekend assessment |
|---|---|
| INT8 GEMM | Selected: explicit arithmetic, simple golden result, clear lane/data-layout tradeoffs; tiny workloads can be transfer dominated |
| FIR | Fallback: MAC-based, streaming-friendly, easy stimulus/reference; weaker AI positioning but good real signal-processing story |
| Convolution | Reuse is interesting; padding/stride/layout enlarge implementation and validation scope |
| FFT | Good established workload, but fixed-point scaling/twiddle generation complicate a fresh implementation |
| Full neural inference | Strong application demo with a working vendor stack; fresh model/compiler/runtime integration too risky |
| Memory-intensive kernel | Potentially valuable, but needs trustworthy DMA/DDR measurement first |
| RISC-V component | Processor/toolchain integration is disproportionate to this deadline |

Primary contract: signed INT8 A and B, INT32 C = A×B, no activation, bias, saturation or quantization scales. Start with square sizes 8 and 16; extend only after correctness and interface capacity are proven. This is a compute microbenchmark, not complete inference.

Baseline: a sequential one-MAC implementation with no artificial delay. Alternative: four parallel MAC lanes with explicit banking and pipelining. Resource-matched comparison: on the same four-lane datapath/storage, compare straightforward serialized operand issue against a documented prefetch/banked schedule. Count the extra preload and all storage/control resources; describe the first as an unoptimized schedule, not state of the art. If the alternate schedule requires a different bitstream, compare actual resource reports and disclose differences. Do not manufacture a weak baseline to produce a large ratio.

Optimization: exhaustive enumeration over the implemented lane/schedule choices, filtering by actual resource reports. Execution: prebuilt full-image switching and local scratchpad, as above. A tiny GEMM is a feasibility wedge, not an independently defensible commercial accelerator.

## 6. AI and deterministic system architecture

Flow: Idea / engineer prompt / supported JSON or YAML → AI extraction → editable typed specification → deterministic validation → candidate registry and search → serialized board job → immutable result → comparison and explanation.

Next.js/Tailwind UI; Python service for search/validation/runner; a server-side LLM API for spec extraction and result explanation (now implemented against Groq chat completions). Use schema-constrained output with explicit handling for refusal, incomplete response and timeout. Schema conformance does not establish semantic correctness. [Groq Structured Outputs](https://console.groq.com/docs/structured-outputs).

Every field carries value, source (`user`, `inferred`, `default`, `unresolved`) and supporting user text when applicable. Preserve explicit requirements; never silently replace an impossible DSP budget. Suggested defaults: matrix size 16, INT8, INT32 accumulation, KV260, 100 MHz target, minimize latency; label all as defaults unless supplied. Exact numbers are editable within the advertised supported set.

AI extracts intent, flags unsupported applications, proposes assumptions and explains tradeoffs using result IDs. Deterministic code validates shapes/ranges, resource/timing feasibility, counts operations, computes metrics and selects Pareto candidates. The LLM cannot write measurement fields or run arbitrary deployment commands. If the API fails, manual spec editing remains available with “AI unavailable”; do not disguise a rules parser as an LLM.

Grid search is the choice for at most a handful of built candidates. Heuristics become useful only if build costs force pruning. Bayesian search needs a larger expensive space and enough observations. LLM-guided search is not justified for four configurations; use AI for meaningful requirement elicitation and grounded interpretation instead.

Evidence states: analytical estimate → simulated → synthesized → implemented/timing-passed → measured on board. Never compare these as if interchangeable. Historical measurements show date, board, artifact and workload; live runs get a fresh job ID. An unmatched configuration is estimated/build-required, not executable.

For a hosted prototype use Supabase only if provisioning is fast: specs, jobs, results and opt-in contacts, with private contact access and public aggregate/demo data. A local SQLite/JSONL backend is acceptable during bring-up, but must not be deployed on ephemeral serverless storage. Analytics may be simple server events; PostHog is optional. Public try mode can explore without a connected board and clearly report “runner offline.”

## 7. MVP boundary

Must have: one supported kernel; three entry tabs converging on the same editable spec (existing design accepts supported config only); natural-language extraction; honest unsupported-state handling; actual parameterized hardware source; baseline plus alternative physical execution; resource-matched comparison; two built lane counts; constraint-based ranking; live/cached/estimated labels; correctness and reproducible export; accessible polished UI; working hosted try link; opt-in pilot form and usage events; open-source core with selected license and third-party credits.

Six screens can be one guided page: idea, spec, candidates, execution, comparison, report. Plain language first; cycles, DSP/LUT/BRAM and provenance in expandable details. Changing a constraint must deterministically alter feasibility, or clearly explain why no candidate meets it.

Stretch: 8/16 lanes, additional shapes, measured SOM power, DMA, additional boards, team accounts, report PDF. Exclude arbitrary RTL optimization, ASIC tapeout, on-demand synthesis in the pitch, full neural models, Bayesian optimization, partial reconfiguration, unsupported power optimization, and cloud FPGA provisioning.

Open-source requirement means publish the core source with a clear license and reproducible build instructions; proprietary Vivado tooling remains an external dependency. Public release is a later execution step; this brief does not claim a release has occurred.

## 8. Schedule and event constraints

The [official guide](https://cpvc-ai-hackathon-guide.vercel.app/) was read in the browser November 13. Discord updates override it. Verified: build window Fri 5 PM–Sun noon Pacific; teams 2–4 registered/checked-in students, no solo projects; team lock Fri 8:50 PM; project-history link Sat 2 PM; Sunday commitment plus live try link Sat 8 PM; final submission Sun noon; judging-room check-in Sun 10 AM and return by 12:55. Four-minute demo plus three-minute Q&A. No feature work or fixes after noon. Preserve this repository/project history. Public templates/libraries are permitted with credit; pre-event work made for this idea cannot be reused.

Rubric: execution/design 25, real problem/user 25, path to customers 20, pitch/demo 15, creative AI use 15. Technical difficulty is not scored. Final submission needs live link, project/history link, short problem/user/build description and credits, AI tools/disclosure, and optional challenge selection. A publicly viewable video under two minutes is required for a challenge and useful as backup. Deck optional. No mass email lists; do not collect sensitive data or take money without the event's required clearance.

Schedule assumes two people minimum, ideally three: H hardware, P product/backend, C customer/pitch. These are human workstreams, not delegated agents. With two people combine P+C and cut all stretch work. Around 42 hours remained at research time, including mandatory sessions and sleep. The table is a plan, not a claim that all blocks are free build time.

| Pacific time | H: hardware / critical dependency | P+C: product and customer / event |
|---|---|---|
| Fri 18–19 | Inventory during available time; attend opening until 18:55 | Confirm team and rubric; dinner |
| 19–20 | SSH, identify OS/tool tuple; load known public example | Confirm target user; spec and result contract |
| 20–21 | Build/read identity register if tools ready | Team lock by 20:50; sketch workflow |
| 21–22 | Required Codex workshop 21–21:40; leave venue 21:45 | Same workshop; preserve project history |
| 22–23 | Simulate baseline and start implementation off-site | AI spec schema and supported-state UI |
| 23–00 | Load baseline; golden-output/counter check | Basic search/results registry; no fake data |
| Sat 00–01 | Gate: custom baseline works; start 4-lane build | Capture blocker list; prepare user-test script |
| 01–07 | Sleep; unattended build only if stable | Sleep |
| 07–08 | Verify 4-lane result and counter | Integrate typed spec editor |
| 08–09 | Add resource-matched scheduling comparison | Candidate visualization and evidence badges |
| 09–10 | Arrive 09:15; repeat board tests; walk to workshop | Recruit relevant users individually |
| 10–11 | Customer discovery workshop 10–10:45 | Attend; allow travel |
| 11–12 | OpenAI industry talk 11–11:45 | Attend; allow travel |
| 12–13 | Run comparison suite; parse reports | First observed user sessions; deploy initial try link |
| 13–14 | Freeze two reliable hardware candidates | Submit project-history link before 14:00; lunch |
| 14–15 | Hardware/backend integration and failure handling | Collect user feedback; use mentor slot if booked |
| 15–16 | Measure host transfer versus kernel times | Fix confusing UI; interview buyer/champion |
| 16–17 | Gate: complete spec→board→report workflow | Verify hosted link; walk to workshop |
| 17–18 | Business Model Canvas workshop | Attend and test buyer/revenue assumptions |
| 18–19 | Dinner; stability only | Consolidate genuine evidence; dinner |
| 19–20 | Sunday instructions; no risky new hardware | Submit Sunday commitment and live link before 20:00 |
| 20–21 | Final repeatability suite, archive artifacts | Polish report and pitch; observed user test |
| 21–22 | Leave venue 21:45; preserve working setup | Record under-two-minute backup demo |
| 22–23 | Fix only critical failures; feature freeze | Pitch run-through; export evidence backup |
| Sun 23–07* | Sleep (Saturday 23:00 to Sunday 07:00) | Sleep |
| Sun 07–08 | Cold-start demo and local network check | Submission checklist and breakfast |
| 08–09 | Pitch workshop starts 08:30 | Attend |
| 09–10 | Workshop ends 09:30; move with hardware | Check in judging room by 10:00 |
| 10–11 | Full rehearsal, known-good images and hashes | Link permissions, credits, customer counts |
| 11–12 | Final test, stop changes; submit by 11:30 target | Check final submission before noon; retain buffer |

*Sleep row labels a cross-midnight interval, not Sunday night. At noon, freeze submitted artifacts. Return to room by 12:55; keep the board powered and bring Ethernet, power supply, HDMI adapter, hotspot, and backup recording. Do not change the product after submission.

Go/no-go and contingencies:

| Risk | Gate / mitigation |
|---|---|
| No compatible build host | Within two hours identify a usable host/tool/license or borrow team-accessible infrastructure. A FIR fallback does not fix missing Vivado. If unavailable, explicitly downgrade to a software/simulation demo; the physical-FPGA requirement remains unmet |
| Baseline won't deploy | By Saturday 01:00 target, require new kernel identity, correct output and plausible counter. Debug minimal registers before compute; preserve known-good image |
| GEMM datapath fails despite working shell | Switch to FIR using the same host/control/counter; do not add a new platform stack |
| Bitstream/timing failures | Reduce lane count/clock, rebuild and report actual frequency; no fresh OS/tool upgrade during final hours |
| Resource assumptions wrong | Use post-implementation counts; reject unbuilt candidates for strict budget claims; no MAC=DSP assumption |
| Board unreliable | By Sat 16:00 require ten consecutive successful end-to-end jobs. Local Ethernet, serialized access, timeouts, recovery procedure; recorded real run as labeled backup |
| No meaningful speedup | Report both kernel and job-level results. If transfer dominates, say so; stop the acceleration headline. Investigate batching only with equivalent workloads |
| No fixed-resource improvement | Show capacity scaling honestly, mark architectural improvement unproven, and narrow claims. Do not claim the original stronger requirement is satisfied |
| Weak AI | Show two materially different prompts and a constraint edit that produce valid changed specs; manual fallback labeled |
| Low signups | Seek qualified observed use, not vanity volume. Report exact counts and zero commercial commitments if none |
| Competitive overlap | Ask users to compare against their scripts/tool; continue commercially only if they identify concrete recurring time saved |
| Deadline failure | Named team member owns 14:00/20:00/noon submissions; submit early; mandatory sessions are in the plan |

## 9. Benchmarking protocol

Use identical matrix dimensions, signed input bytes, arithmetic/overflow semantics and output checks across designs. INT32 accumulation is safe for the selected small shapes, but validate bounds if scope expands. CPU oracle accumulates in a wider integer type. Test zeros, identity, negative/extreme INT8 values, and at least 100 seeded randomized cases before reporting speedup. Record every output mismatch and suppress performance recommendation on failure.

For each candidate: 10 warmups, then 100 timed trials across multiple seeded inputs; report count, median, p95 and range. Preserve raw samples. Use a PL counter from accepted start through final output commit; if a separate compute-only interval excludes preload, label it and also report total accelerator cycles. Record actual configured clock, timing report, tool versions and bitstream identity. A 100 MHz constraint is not evidence of a running 100 MHz clock or closed timing.

Timing layers: programming/image-switch time; input preparation/packing; transfer-in; local staging; compute; transfer-out; validation; full host job; browser/queue round trip. Report kernel and end-to-end speedup separately. Reconfiguration can be amortized for a persistent service, but first-use cost must remain visible. Linux/Python/SSH wall time is not a hardware cycle count.

For M×K by K×N, count MKN MACs and, under the declared conventional two-ops-per-MAC convention, 2MKN operations. Report MAC/s too. Time = cycles / actual Hz; throughput = operations / corresponding time; speedup = baseline time / candidate time. Performance/DSP uses actual mapped DSPs and is undefined if DSP count is zero. Include LUT, FF, BRAM and URAM; FPGA resources are not an ASIC area measurement. Compare total design and kernel hierarchy separately.

Baselines: A sequential FPGA kernel; B same-lane/same-datapath scheduling comparison; C optional compiled C/NEON CPU comparator with stated compiler flags, threads and timing boundary. Python or NumPy overhead is not a credible claim of beating optimized ARM GEMM. No established-library superiority claim until a matched implementation is actually run.

Result bundle: original prompt, reviewed spec/provenance, test seed and input/output hashes, source commit, dirty-source snapshot if any, artifact hash, target board/part, OS/driver/tool tuple, actual clock configuration, timing/utilization reports, raw cycles/times, correctness result, failure logs, comparison scope, and timestamp. Recommendation records which candidates were evaluated and why others were excluded.

Power/energy only when measured: integrate rail power over a sufficiently long repeat window, divide by completed operations; report whole-SOM energy and separately labeled idle-subtracted estimate if used. Keep CPU load and thermal conditions comparable. Never extrapolate isolated nanosecond kernels from a slow sensor reading.

## 10. Customer validation plan

Landing promise: “Describe your compute kernel. Compare architectures. Inspect the evidence.” Primary CTA Try SiliconOS; secondary Request a Pilot. Keep “From Idea to Optimized Silicon” as a vision tagline with explicit current scope: KV260 INT8 matrix kernel prototype.

Collect email with opt-in, role, organization optional, hardware platform, current tools, recent bottleneck and pilot interest. State this is a student hackathon prototype. Keep raw contacts private; aggregate only in the pitch. Never collect confidential RTL, credentials or sensitive workloads for validation.

Ask individually among embedded/FPGA lab contacts, relevant student hardware teams, mentors with industry experience, and engineers in existing personal networks. Students establish usability, not enterprise willingness to pay. No mass campus/club email. Outreach copy to send manually: “We're testing a student prototype that compares small accelerator designs on a Kria board. Could you show us how you last chose a hardware configuration, then try our workflow for ten minutes? We're looking for failure points, not endorsements.”

Interview sequence: describe last project; actual duration and effort; tools and hardest bottleneck; consequences of delay; what existing tooling fails to solve; observe a task without coaching; ask for their workload and follow-up; identify buyer and budget process. Ask price questions only after a concrete deliverable is clear. Record consent for attribution.

Events: anonymous session, spec created/reviewed, search completed, benchmark requested/succeeded/failed, report exported, returning session, pilot interest. Unique visitors are approximate; exclude team/test sessions. A run is successful only after the server records board completion and correctness. Keep separate counts for visitors, contacts, qualified users, repeat users, pilots and paid commitments.

Pilot proposal hypothesis: use one customer-approved kernel on their board, compare against their current flow, deliver reproducible recommendations and measure engineering hours saved. Success threshold and price must be agreed with an actual buyer. No outreach has been sent and no demand is claimed by this brief.

## 11. Open-source business model and venture test

Open core includes spec schema/UI, search, templates, local runner, report parser and benchmark format. Charge potentially for managed private runners, scheduled experiments, team result history, supported tool/version combinations and response-time commitments. Customers would pay for reduced operational work and reliable recurring integration; if a one-time self-hosted script solves the problem, a recurring subscription is weak.

Recurring value needs repeated design revisions, multiple engineers/boards, and trustworthy comparable experiment history. A potential advantage is a high-quality corpus of reproducible measurements and maintained integrations, subject to customer permission; neither is a moat today. Incumbents can add NL interfaces, and generic agents can generate glue scripts. Professional services can discover demand but are not automatically software ARR.

Bottom-up sensitivity only: let N be paying organizations and A be annual recurring contract value. ARR=N×A. The numbers below are hypothetical arithmetic, not observed market pricing, reachable customer counts, or a forecast.

| ARR objective | At hypothetical $10k/year | At hypothetical $50k/year | Required evidence |
|---|---:|---:|---|
| $1m | 100 customers | 20 customers | Repeatable paid pilot conversion, retention, manageable support |
| $10m | 1,000 | 200 | Several supported segments/platforms, acquisition channel, enterprise deployment |
| $100m | 10,000 | 2,000 | Much broader hardware ecosystem and major recurring value; not justified by a KV260 niche |

Do not extrapolate the entire semiconductor market into our addressable market. Validate accounts we can reach, purchase authority, cycle length, margin after compute/tool licenses/support, and renewal. Commercial continuation gate after the event: multiple qualified teams offer real workloads, at least one budget owner agrees a paid pilot scope, and observed time savings exceed setup/support burden. A weekend signup list does not meet this gate.

## 12. Four-minute pitch and demo

Use the following only after replacing every bracket with verified evidence. If a claim is unmet, use the failure wording rather than implying success.

**0:00–0:30 — Person and problem.** “An embedded engineer choosing an accelerator has to answer a practical question: which design meets the constraints on our actual board? A code generator gives you another design to investigate. SiliconOS connects that decision to a reproducible experiment.” Add one specific customer incident only if obtained with permission.

**0:30–1:00 — Scope and AI.** “Today we support one deliberately narrow workload: signed eight-bit matrix multiplication on AMD Kria. Describe the requirement in plain English. The AI drafts an editable specification and shows which details you supplied and which it assumed. Unsupported ideas stay unsupported.” Show generated spec and source badges.

**1:00–1:30 — Compare.** Enter an actual supported prompt. “We enumerate the available designs and enforce the resource budget against implementation reports. These entries are built; these are estimates requiring a build.” Show baseline and candidate with honest state labels.

**1:30–2:00 — Execute.** “This job runs on the board here. We check every output and count hardware cycles. Here are [actual median kernel latency], [actual full-job latency] and [actual resources].” Show fresh job ID and traceable artifact. If disconnected: “This is the recorded run from [time], not a live measurement.”

**2:00–2:30 — Change the constraint.** Change budget across the actual measured DSP threshold of two candidates, rather than assuming lanes equal DSPs. “That removes this design; this one now wins among the feasible candidates.” Show reconfiguration explicitly. Fixed-resource scheduling result: “[measured improvement or no improvement], using [resource comparison].” Do not promise a ratio in advance.

**2:30–3:00 — Differentiation.** “FINN, hls4ml and Gemmini already generate capable accelerators. Our hypothesis is that developers need an easier path from their constraints to repeatable evidence on their own boards. We aim to connect those tools, with every conclusion traceable to a run.”

**3:00–3:30 — Evidence.** “[N] relevant engineers spoke with us; [N] completed the workflow; [N] returned or requested a pilot. Their clearest problem was [specific finding].” If none: “We have not validated commercial demand yet. The next test is whether teams will bring their workloads and pay for a supported pilot.” Never substitute visitors for engineers.

**3:30–4:00 — Business and close.** “The core stays open source. We will test paid private runners and maintained experiment infrastructure for teams repeating this work. This weekend proves [only achieved capability]. Our next milestone is [specific customer pilot]. SiliconOS: describe the requirement, compare the designs, inspect the proof.”

Rehearse at 3:40 to leave room for latency. Questions to prepare: why not FINN; whether the CPU wins end-to-end; whether more lanes just use more hardware; exact AI role; what was built this weekend; who pays; what remains estimated. Bring raw reports and an under-two-minute backup showing the real board run.

## 13. First five actions, in risk-reduction order

1. Power/SSH the KV260 and identify a working FPGA build host. Send board address/login name (not password), OS/image, installed Vivado/Vitis versions, and any public reference flow already proven on the board. Preserve existing boot media.
2. Confirm the official team roster/Friday check-in and deadlines; lock team before 20:50. Check Discord for updates and preserve project history. Do not reuse pre-event project-specific implementations.
3. Prove host-to-PL communication with a newly built identity/scratch register, then correct baseline arithmetic and a hardware counter. This is the first implementation gate, ahead of UI polish.
4. Build a second lane count and the fixed-resource scheduling comparison; run identical inputs and archive reports. The DSP constraint interaction must use actual mapped counts.
5. Connect AI spec→deterministic search→board result in one user flow, then immediately observe a relevant user trying it. Publish the try link in time for Saturday's commitment and capture evidence without inventing traction.

Confirmed user updates: two team members so far; AI credits are available for potential product use. Plan for two people, with one owning hardware and the other combining product/backend and customer discovery. Commit only to one- and four-lane variants; eight/sixteen lanes remain excluded from the committed delivery. Credits remove some potential API cost pressure but their provider, API eligibility and account access remain unverified. Use them for specification extraction and grounded explanations, not additional speculative features.

Pending user inputs: team roles, board reachability and image, build host/tool availability, credit provider/API eligibility, any updated Discord rules. Until those are supplied, the exact deployment commands/version tuple and hardware feasibility cannot honestly be finalized.
