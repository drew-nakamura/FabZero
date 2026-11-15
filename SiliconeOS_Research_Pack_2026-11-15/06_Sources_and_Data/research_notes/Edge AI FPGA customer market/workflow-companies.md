# FPGA workflow company research

Checked November 15, 2026. Serialized faithful synthesis of completed read-only researcher findings; source facts, timing, counterevidence and hypotheses preserved. No outreach/interest established.

### LogicTronix — Expert evaluator / potential future user or partner

**Public evidence.** It identifies as an AMD-Xilinx design-services and Kria SoM AI/ML design partner. Public services explicitly include KV260/VVAS, multi-channel/multi-model inference, RTL, embedded Linux and carrier work. Its IP portfolio confirms FPGA solution work. ([Services and inquiry](https://logictronix.com/fpga-design-services/), [FPGA IP portfolio](https://logictronix.com/solutions-ip-cores/logictronix-fpga-ip-cores/))

**Use hypothesis.** Possible operator: **Senior FPGA / ML engineer**. Buyer hypothesis: **Engineering lead or customer-project owner**. Trigger: A customer-specific Kria configuration requiring repeatable PL/model/implementation/deployment checks. It already sells the integration work and likely has tooling; partnership/competition may be more realistic than seat sales.

**Gap beyond today.** Real VVAS/Vitis-AI, model integration, memory/stream interfaces, Linux packaging and customer IP handling. **Discovery question:** “For the last KV260 customer variation, what changed and was rechecked between the model, PL integration, implementation and deployment?” Public route: [Official services inquiry form](https://logictronix.com/fpga-design-services/). Evidence timing: Pages undated; checked2026-11-15.

### Starware Design — Expert evaluator / small-firm user hypothesis

**Public evidence.** Current services cover FPGA/ASIC verification, board bring-up, embedded software and edge AI. Its DevOps article describes source/bitstream mismatch, unreproducible environments and dependence on one release engineer. The article lists admin and no clear date; current site material also describes GitLab CI/Vivado/Cocotb work. ([Company services](https://www.starwaredesign.com/), [First-person FPGA DevOps account](https://www.starwaredesign.com/fpga-meets-devops-introduction/))

**Use hypothesis.** Possible operator: **FPGA project lead / principal consultant**. Buyer hypothesis: **Founder/principal or project owner**. Trigger: A customer handoff requiring proof that source, build and physical result belong together. It already knows and uses CI; an earlier pain account does not prove the problem is still unsolved.

**Gap beyond today.** Existing CI integration, customer-owned designs, reproducible environments and actual project checks. **Discovery question:** “Which part of a recent source-to-tested-board handoff still required reconstruction after your existing CI work?” Public route: [Official Get in touch route; contact page timed out in this pass](https://www.starwaredesign.com/). Evidence timing: DevOps article undated; current site checked2026-11-15.

### hema electronic — Platform / qualification partner hypothesis

**Public evidence.** The German electronics firm’s AMD-coordinated platform supplements K26/KV260 development. KV260 and EVB2 both use K26; EVB2 is positioned for customizable embedded vision/sensor/AI work toward production. Shared silicon does not make bitstreams interchangeable. ([AMD FPGA platform](https://www.hema.de/loesungen/amd-fpga-plattform), [Official contact](https://www.hema.de/unternehmen/kontakt))

**Use hypothesis.** Possible operator: **Platform FPGA / embedded-vision engineer**. Buyer hypothesis: **Platform engineering or business-development lead**. Trigger: Moving a feasibility variant from KV260 to EVB2/custom carrier with transferrable acceptance evidence. Platform reuse already addresses part of development effort; no numerical saving established.

**Gap beyond today.** Carrier constraints, sensors/interfaces, clocks/drivers and production validation. **Discovery question:** “What configuration and validation steps repeat between KV260 feasibility work and an EVB2/custom carrier?” Public route: [Official sales/contact](https://www.hema.de/unternehmen/kontakt). Evidence timing: Pages undated; checked2026-11-15.

### Enclustra — Platform partner / established orchestration competitor

**Public evidence.** Services include specifications, HDL, verification, software and prototyping for edge AI. Its Sep 21,2026 announcement pairs MakarenaLabs MuseBox, branded Lira, with its portfolio for hardware-accelerated local edge-AI pipelines. Its wider SoC/MPSoC/MLSoC portfolio is not all FPGA. ([Design services](https://www.enclustra.com/en/design-services/), [Lira orchestration partnership](https://www.enclustra.com/en/company/news-events/news/enclustra-partner-with-makarenalabs-on-edge-ai-orchestration/))

**Use hypothesis.** Possible operator: **FPGA platform architect / services engineer**. Buyer hypothesis: **Design-services or platform lead**. Trigger: An experiment/evidence gap complementary to existing Lira orchestration. An existing orchestration partner directly weakens a generic one-workflow sales pitch.

**Gap beyond today.** Actual module/tool recipes and a demonstrably complementary function. **Discovery question:** “What remains manual in custom RTL verification and physical acceptance after Lira and your design-services tooling?” Public route: [Official design-services route](https://www.enclustra.com/en/design-services/). Evidence timing: Partnership2026-09-21; services checked2026-11-15.

### Missing Link Electronics — Automation competitor / interoperability partner

**Public evidence.** MLE lists reduced-precision neural networks, vision, RTL/HLS, AXI, timing closure and automated builds. Its company-owned FPGA-vbs automates Vivado variants, reports and Git/dirty-state identity. ([Competencies](https://www.missinglinkelectronics.com/design-services/competence-areas/), [FPGA-vbs source](https://github.com/missinglinkelectronics/fpga-vbs))

**Use hypothesis.** Possible operator: **FPGA tooling / design-services engineer**. Buyer hypothesis: **Tooling or services lead**. Trigger: An acceptance/physical-result step outside the existing variant-build system. Already provides substantial automation; no evidence it wants a paid prompt wrapper.

**Gap beyond today.** Interoperability with its subsystems, streaming/data-movement interfaces and CI. **Discovery question:** “Which physical acceptance/handoff step remains outside FPGA-vbs, and would reviewed specifications improve it?” Public route: [Official technical inquiry](https://www.missinglinkelectronics.com/contact/). Evidence timing: Current pages/repository checked2026-11-15.

### Antmicro — Open-source tooling competitor / collaboration candidate

**Public evidence.** Its FPGA work includes AI accelerators and VEDLIoT. Topwrap connects and parameterizes HDL modules and generates top-level wrappers through CLI/graphical workflows. Announcement Aug 19,2024; documentation updated Sep 1,2026. ([FPGA technology work](https://antmicro.com/technologies/fpga/), [Topwrap announcement](https://antmicro.com/blog/2024/08/parameterizable-digital-logic-design-with-the-topwrap-toolkit/), [Topwrap documentation](https://antmicro.github.io/topwrap/))

**Use hypothesis.** Possible operator: **FPGA tooling / project engineer**. Buyer hypothesis: **Tooling or project lead**. Trigger: A real experiment still hard after Topwrap and current simulation/CI. Already builds integration infrastructure; generic HDL-tool orchestration is insufficient differentiation.

**Gap beyond today.** Open-interface interoperability, co-simulation and broader IP validation. **Discovery question:** “What customer task remains difficult after Topwrap and your simulation/CI stack when physical evidence is required?” Public route: [Official contact / contact@antmicro.com](https://antmicro.com/about/contact/). Evidence timing: Announcement2024-08-19; docs2026-09-01; checked2026-11-15.

### TOPIC Embedded Systems — T&S platform supplier / legacy automation benchmark

**Public evidence.** TOPIC joined Technology & Strategy in March2023. Current Miami platforms include Zynq-7000, Zynq UltraScale+ and Versal. Legacy Dyplo material describes software-to-FPGA deployment, streaming/DMA and partial reconfiguration, but its old product link now redirects to a general portfolio; current standalone Dyplo availability was not verified. ([2023 T&S integration](https://topic.nl/nieuws/integration-of-topic-with-ts-group), [Current platforms](https://topic.nl/products), [Legacy Dyplo route](https://topic.nl/us/dyplo))

**Use hypothesis.** Possible operator: **FPGA platform / services engineer**. Buyer hypothesis: **Platform or design-services lead**. Trigger: A customer-specific Miami accelerator with unautomated acceptance/evidence steps. Existing supplier platform/deployment expertise; legacy Dyplo is not confirmed current paid software.

**Gap beyond today.** Actual Miami profiles, Linux/DMA interfaces and project-level acceptance. **Discovery question:** “Which requirements-to-verified-artifact steps remain manual beyond the platform and deployment tools you already provide?” Public route: [Current product/contact route; info@topic.nl](https://topic.nl/products). Evidence timing: T&S integration2023-03-30; current portfolio checked2026-11-15.

**Company scale, not software demand.** 2023 acquisition announcement cited more than 100 professionals. This is historical total employment, not current FPGA seats.

## Direct incumbent alternatives

On **September16,2026**, Lattice introduced **Lattice Prompt as a free download** for its Radiant ecosystem. Its announcement describes natural-language access to simulation, synthesis, mapping, place-and-route, timing and bitstream generation, through an LLM/agentic IDE and MCP. Its10 ×-or-greater common-task productivity claim is supplier marketing, not an independently verified benchmark or a SiliconeOS result. This is close competition, not merely a general coding assistant. ([Lattice launch](https://ir.latticesemi.com/news-releases/news-release-details/lattice-advances-fpga-design-new-leadership-ai-driven))

Altera's **October21,2026 QuartusIQ announcement** similarly describes contextual natural-language design/debug/validation/timing assistance with MCP, skills and an agent harness. Availability was scheduled for Quartus Prime Pro 26.3 on October28; researchers did not install or independently test it. Altera **expects up to1.5 × faster total design cycles**, illustrating a 24-month project; expectation is not a measured result. Its separate FPGA AI Suite release describes trained-network spatial compilation and a100,000-consecutive-inference early-development license limit, which is an entitlement restriction rather than adoption data. ([QuartusIQ](https://www.altera.com/newsroom/altera-launches-quartusIQ), [FPGA AI Suite 2026.1.1](https://www.altera.com/newsroom/altera-fpga-ai-suite-26-1-1-deterministic-physical-ai-spatial-architecture))

The independent baseline is also capable: Antmicro's Topwrap assembles parameterized HDL, MLE's FPGA-vbs automates variants/build identity, and Basler/Enclustra already pursue higher-level programming/orchestration. Some tool/device/IP combinations cost money, but AMD's current BASIC tier is free with annual renewal and Windows/Linux support. A subscription does not remove tool/IP entitlements. ([AMD licensing](https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/vivado/vivado-licensing-options.html), [FAQ](https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/licensing-faq.html))

The differentiation to test is narrower: **a reliable supported experiment, reviewed constraints, independent checks and inspectable physical-result identity within the engineer's existing workflow**. A paid independent tool must demonstrate incremental value against vendor assistants and existing scripts. Source confidentiality, deterministic failure handling, integration burden and maintenance across tool/board versions may matter more than prompt fluency. Latency and local-data requirements can motivate edge inference, but do not establish that FPGA is preferable to GPU/NPU/ASIC for every task. ([AMD edge-AI architecture discussion](https://www.amd.com/content/dam/amd/en/documents/solutions/automotive/wp-designing-for-the-ai-defined-vehicle.pdf))

