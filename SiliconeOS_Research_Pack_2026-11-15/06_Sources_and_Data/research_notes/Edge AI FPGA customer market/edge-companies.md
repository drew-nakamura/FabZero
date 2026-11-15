# Edge AI product company research

Checked November 15, 2026. Serialized faithful synthesis of completed read-only researcher findings; source facts, timing, counterevidence and hypotheses preserved. No outreach/interest established.

### Leopard Imaging — Potential future user / imaging partner

**Public evidence.** Its AUTOMATE 2026 announcement describes ASTRO stereo cameras with two 5.1 MP RGB-IR sensors, FPGA processing and 10GigE for AI perception, navigation and reconstruction. A separate 25 MP demonstration combines FPGA processing with Jetson Thor. Its AMD camera interface supports ZCU102/ZCU104. This is hybrid FPGA preprocessing plus AI compute, not proof all inference is in programmable logic. ([2026 AI-perception announcement](https://leopardimaging.com/leopard-imaging-to-showcase-advanced-ai-perception-and-vision-solutions-at-automate-2026/), [AMD-platform camera interface](https://leopardimaging.com/product/platform-partners/amd/li-multi-sensor-cphy-fmc-101h/))

**Use hypothesis.** Possible operator: **FPGA/embedded-imaging engineer**. Buyer hypothesis: **Imaging or embedded engineering lead**. Trigger: A sensor, synchronization, buffering or preprocessing change requiring a reproducible lab experiment. Sophisticated internal integration and NVIDIA-based platforms; product configuration may matter more than new RTL.

**Gap beyond today.** MIPI/FMC, video streams, clock-domain crossing, DMA, external memory and real image kernels; none is established by the present small GEMM. **Discovery question:** “Which repeated FPGA/sensor variation requires the most manual reconstruction of tests, constraints and deployment evidence?” Public route: [Official inquiry page](https://leopardimaging.com/contact-us/). Evidence timing: 2026 announcement; other product page undated; checked 2026-11-15.

### Basler — Expert / collaborator / competing framework

**Public evidence.** Basler publicly describes an innovation-stage Python framework for programming FPGAs in cameras/frame grabbers, with image functions and simulation. It explicitly invites feedback on applications, Python and low-code approaches. Its engineering article discusses multi-camera timing, buffers, unsupported formats and insufficient FPGA expertise. This is explicit workflow relevance and evidence of an existing competing approach. ([Python-to-FPGA innovation project](https://www.baslerweb.com/en-us/innovation/fpga-programming-python/), [AI vision engineering constraints](https://www.baslerweb.com/en-us/learning/computing-power-ai-vision-systems/))

**Use hypothesis.** Possible operator: **Applications engineer / FPGA framework engineer**. Buyer hypothesis: **Relevant applications or platform engineering lead**. Trigger: A customer-specific preprocessing function that must be simulated and deployed on a supported camera/frame grabber. Basler is already building an abstraction; it is not a greenfield prompt-tool prospect.

**Gap beyond today.** Basler targets, interfaces, stream-processing functions, existing framework integration and acceptance tests. **Discovery question:** “Where would reviewed natural-language intent and retained evidence improve your Python-to-FPGA flow, and where would they add risk?” Public route: [Innovation project; public invitation and innovation@baslerweb.com](https://www.baslerweb.com/en-us/innovation/fpga-programming-python/). Evidence timing: Innovation pages undated; 9M report covers Jan–Sep 2026; checked 2026-11-15.

**Company scale, not software demand.** Jan–Sep 2026 sales €227.4m (+35% against adjusted €168.0m), orders €278.6m (+62%), average 838 FTE. Prior-year figures restated; €295–300m FY2026 sales is guidance, not achieved annual revenue. ([Primary 9M2026 report](https://assets-ctf.baslerweb.com/dg51pdwahxgw/1AGM8lfcGmEoRVpaKP5waH/a857cd4fc412656a7801939ecbb75da4/20261001_Q3_final_e.pdf))

### Ouster — Potential future engineering user

**Public evidence.** A company-hosted FPGA Design Engineer role explicitly names RTL, verification, testbenches, synthesis, timing closure and lidar integration, with Verilog/SystemVerilog, Vivado or Quartus, FPGA SoCs, AXI and Git. HLS/Vitis and Python/Tcl/Bash are additional skills. Its current platform spans lidar, cameras, compute and software. The job verifies the workflow, not tool-buying interest. ([Official FPGA engineering role](https://ouster.applytojob.com/apply/PvWk0ZFwbL/FPGA-Design-Engineer), [Q3 company release filed with SEC](https://www.sec.gov/Archives/edgar/data/1816581/000162828026069487/exhibit991-9302026.htm))

**Use hypothesis.** Possible operator: **Firmware/FPGA engineer**. Buyer hypothesis: **Firmware or hardware engineering leadership**. Trigger: A deterministic lidar-data preprocessing/interface variant requiring independently checked outputs and exact build identity. An expert team and mature stack create a high trust/integration bar; the job is not evidence of replacing engineers.

**Gap beyond today.** Lidar interfaces, calibration, throughput/latency contracts, reliability, enterprise source handling and proprietary RTL. **Discovery question:** “Which repeated RTL-to-lab validation step is painful enough for a third-party tool, and what evidence would your team require?” Public route: [Official company contact](https://ouster.com/company/contact-us). Evidence timing: Job publication date not shown; release Nov 3,2026 for quarter ended Sep 30; checked 2026-11-15.

**Company scale, not software demand.** Q3 2026 revenue approximately $59m, +50% YoY/+9% sequential. More than27,000 lidar AND camera sensors shipped for revenue; about 27% were lidar. Stereolabs contributes to the combined platform, so growth and units are not organic FPGA metrics. ([Primary investor release](https://investors.ouster.com/node/12271/pdf))

### Xnext — Later industrial acquisition-workflow candidate

**Public evidence.** AMD’s 2023 XSpectra case describes Zynq real-time sensor acquisition/firmware in an X-ray inspection system combining sensing and AI/CNN software. Xnext’s current site still presents AI/deep-learning hyperspectral contaminant inspection. The case does not establish that the CNN runs in FPGA fabric. ([2023 vendor/customer case](https://www.amd.com/content/dam/amd/en/documents/resources/case-studies/xnext-pbx.pdf), [Current company product site](https://www.x-next.com/))

**Use hypothesis.** Possible operator: **FPGA/embedded acquisition engineer**. Buyer hypothesis: **R&D or embedded systems lead**. Trigger: A detector acquisition, filter or buffer change with a known test input and reference output. Existing custom electronics, firmware and trained inspection software; small GEMM is far from complete inspection.

**Gap beyond today.** Detector interfaces, streaming, acquisition semantics, quality/latency constraints and production qualification. **Discovery question:** “When acquisition/preprocessing firmware changes, how do you validate and preserve the detector-to-result evidence across variants?” Public route: [Official site / info@x-next.com](https://www.x-next.com/). Evidence timing: FPGA evidence2023; current site checked2026-11-15.

**Unresolved unit:** Do not quote the case acquisition throughput: extraction/search representations disagree between GBps and Gbps.

### SICK — Later enterprise user / expert benchmark

**Public evidence.** AMD’s 2024 case documents Kintex UltraScale+, FINN and deep-learning processing in Lector/Inspector machine vision, including capture, compression and pre-segmentation. A 2025 case documents Zynq UltraScale+ in picoScan lidar for mobile robots. Performance claims in the first case were supplied by SICK and not independently verified by AMD. ([2024 machine-vision case](https://www.amd.com/content/dam/amd/en/documents/resources/case-studies/sick-case-study.pdf), [2025 lidar case](https://www.amd.com/content/dam/amd/en/documents/resources/case-studies/sick-2d-lidar.pdf))

**Use hypothesis.** Possible operator: **Embedded FPGA / accelerator engineer**. Buyer hypothesis: **Platform or R&D engineering manager**. Trigger: A supported preprocessing/quantized-network block revision within an existing qualified toolchain. Substantial existing platform and open-source FPGA ML compiler; strong use evidence is not an easy first sale.

**Gap beyond today.** FINN/network/streaming integration, exact sensor targets and quality/latency qualification. **Discovery question:** “What repeated experiment remains inconvenient after FINN and your current tools, and would an external orchestrator preserve qualification?” Public route: [Official US contact / info@sick.com](https://www.sick.com/us/en/contact/w/contactflyout_general_contacts). Evidence timing: FPGA cases2024/2025; FY2025 figures; checked2026-11-15.

**Company scale, not software demand.** 2025 continuing-operations sales €1.850bn versus €1.7368bn in2024, reported6.5% growth;10,158 employees at Dec 31,2025. Accounting exclusions make older group-total comparisons unsafe. Employees are not FPGA seats. ([Official IFRS figures](https://www.sick.com/us/en/ifrs-figures-for-the-sick-group/w/key), [2025 annual report](https://tools.sick.com/annual-report/SICK_Geschaeftsbericht_2025_EN.pdf))

### IDS Imaging — Model-specific user hypothesis

**Public evidence.** IDS describes its deep ocean FPGA core for NXT cameras. Its component material distinguishes rio/rome deep ocean from malibu’s Ambarella accelerator; newer malibu/oslo material explicitly describes an Ambarella SoC/NPU. The entire IDS edge-AI camera family cannot be counted as FPGA hardware. ([FPGA technical article](https://en.ids-imaging.com/technical-articles-details/items/ids-nxt-ai-for-all.html?label=53), [System component distinction](https://www.ids-imaging.us/ids-nxt-system-components.html), [Current malibu/oslo NPU products](https://en.ids-imaging.com/ids-nxt-malibu-oslo.html))

**Use hypothesis.** Possible operator: **Engineer for the actual programmable-fabric camera family**. Buyer hypothesis: **Relevant camera-platform engineering lead**. Trigger: An active FPGA-camera core/preprocessing update, if that product family remains relevant. Existing training/app deployment tools; newer NPU products may remove custom FPGA work.

**Gap beyond today.** Proprietary core/toolchain, camera I/O, network support and production evaluation. **Discovery question:** “Which active products still use programmable fabric, and where does custom RTL remain necessary rather than the NPU/app workflow?” Public route: [Official contact](https://www.ids-imaging.us/contact.html). Evidence timing: Technical pages undated/current family material; company milestone2025; checked2026-11-15.

**Company scale, not software demand.** Company page says more than 320 employees; history records2 million IDS cameras in use in2025. These cover all camera families, not FPGA/AI units or tool seats. ([Company overview and milestones](https://en.ids-imaging.com/history-of-the-company.html), [Official company overview](https://www.ids-imaging.us/about-us.html))

### Prophesee — Historical KV260 partner / requalification

**Public evidence.** Its May 6,2024 announcement and AMD case document Metavision event-based sensing/AI with Kria KV260. However, its official product page says the kit was discontinued Aug 31,2026 and is no longer available. Historical same-board fit is not a current purchasable product/channel. ([Official kit and discontinued status](https://www.prophesee.ai/event-based-metavision-amd-kria-starter-kit/), [AMD customer case](https://www.amd.com/en/resources/case-studies/prophesee.html))

**Use hypothesis.** Possible operator: **Event-stream FPGA / embedded engineer, if current architecture uses fabric**. Buyer hypothesis: **Current evaluation/platform engineering lead**. Trigger: A present event-stream processing experiment only after confirming the new architecture. Existing SDK/reference apps and a shift to more integrated systems may remove the close fit.

**Gap beyond today.** Current platform, event sensor/SDK and real stream processing; discontinued KV260 kit cannot establish compatibility. **Discovery question:** “After discontinuing the KV260 kit, where does programmable logic remain in the current evaluation/product flow?” Public route: [Official contact](https://www.prophesee.ai/contact-us/). Evidence timing: Original2024 collaboration; discontinued2026-08-31; company facts checked2026-11-15.

**Company scale, not software demand.** Company overview lists65 people, three offices and nearly €150m cumulative funding; newsroom reports a June15,2026€20m financing. Funding is not revenue or a software budget. ([Company overview](https://www.prophesee.ai/about-prophesee/), [Company newsroom / financing](https://www.prophesee.ai/newsroom/))

